from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, F
from django.db import transaction
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
import stripe
import json
import requests

from .models import Order, OrderItem, Payment, Coupon, CouponUsage
from .serializers import OrderSerializer, OrderCreateSerializer, OrderItemSerializer, PaymentSerializer, CouponSerializer, CouponUsageSerializer
from product.models import Cart, Product

# Custom pagination
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# Order Views
class OrderListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get(self, request):
        filters = request.query_params.dict()
        
        # Apply filters
        
        
        if request.query_params.get('date_from'):
            filters['created_at__gte'] = request.query_params.get('date_from')
        
        if request.query_params.get('date_to'):
            filters['created_at__lte'] = request.query_params.get('date_to')
        
        if request.user.is_superuser:
            queryset = Order.objects.all()
        else:
            queryset = Order.objects.filter(user=request.user)
        
        if filters:
            queryset = queryset.filter(**filters)
        
        queryset = queryset.order_by('-created_at')
       
        
        # Pagination
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = OrderSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data)


class OrderDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, user=request.user)
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)


class OrderCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # Get user's cart
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not cart.items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate stock availability before creating order
        insufficient_stock_items = []
        unavailable_items = []
        
        for cart_item in cart.items.all():
            product = cart_item.product
            
            # Check if product is discontinued
            if product.status == 3:  # Discontinued
                unavailable_items.append({
                    'product': product.title,
                    'reason': 'Product is discontinued'
                })
                continue
            
            # Check if product is out of stock
            if product.status == 2 or not product.in_stock:  # Out of Stock
                unavailable_items.append({
                    'product': product.title,
                    'reason': 'Product is out of stock'
                })
                continue
            
            # Check if sufficient available quantity (stock - reserved) is available
            available_qty = product.available_quantity if hasattr(product, 'available_quantity') else (product.stock_quantity - getattr(product, 'reserved_quantity', 0))
            if available_qty < cart_item.quantity:
                insufficient_stock_items.append({
                    'product': product.title,
                    'requested': cart_item.quantity,
                    'available': available_qty
                })
        
        if unavailable_items:
            return Response(
                {
                    'error': 'Some items are unavailable',
                    'items': unavailable_items
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if insufficient_stock_items:
            return Response(
                {
                    'error': 'Insufficient stock for some items',
                    'items': insufficient_stock_items
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Use transaction to ensure atomicity
        with transaction.atomic():
            # Calculate totals
            subtotal = cart.total_price
            tax_amount = Decimal('0.00')  # You can implement tax calculation logic
            shipping_cost = Decimal('0.00')  # You can implement shipping calculation logic
            total_amount = subtotal + tax_amount + shipping_cost
            
            # Create order
            order_data = {
                'user': request.user,
                'subtotal': subtotal,
                'tax_amount': tax_amount,
                'shipping_cost': shipping_cost,
                'total_amount': total_amount,
                'shipping_address': request.data.get('shipping_address'),
                'billing_address': request.data.get('billing_address'),
                'notes': request.data.get('notes', ''),
            }
            
            # Set payment expiry (15 minutes from now)
            from datetime import timedelta
            payment_expires_at = timezone.now() + timedelta(minutes=15)
            
            order = Order.objects.create(
                **order_data,
                payment_expires_at=payment_expires_at,
                status='pending',  # PENDING_PAYMENT
                payment_status='pending'
            )
            
            # Create order items and RESERVE stock (not permanently reduce)
            for cart_item in cart.items.all():
                product = cart_item.product
                
                # Create order item
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=cart_item.quantity,
                    price=product.price
                )
                
                # RESERVE stock quantity atomically using F() expression
                # This reserves stock but doesn't permanently reduce it
                Product.objects.filter(id=product.id).update(
                    reserved_quantity=F('reserved_quantity') + cart_item.quantity
                )
                
                # Refresh product from database to get updated reserved_quantity
                product.refresh_from_db()
                
                # Update product status based on available quantity
                available_qty = product.stock_quantity - product.reserved_quantity
                if available_qty <= 0:
                    product.status = 2 # Out of Stock
                
                # Save product (this will also update in_stock via the save method)
                product.save() 
            
            # Clear cart
            cart.items.all().delete()
        
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Payment Views
class PaymentListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get(self, request):
        filters = request.query_params.dict()
        
        # Apply filters
        
        
        if request.query_params.get('payment_method'):
            filters['payment_method'] = request.query_params.get('payment_method')
        
        if request.query_params.get('date_from'):
            filters['created_at__gte'] = request.query_params.get('date_from')
        
        if request.query_params.get('date_to'):
            filters['created_at__lte'] = request.query_params.get('date_to')
        
        if request.user.is_superuser:
            queryset = Payment.objects.all()
        else:
            queryset = Payment.objects.filter(order__user=request.user)
        
        if filters:
            queryset = queryset.filter(**filters)
        
        queryset = queryset.order_by('-created_at')
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = PaymentSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        serializer = PaymentSerializer(queryset, many=True)
        return Response({'data': serializer.data, 'count': queryset.count(),"message": "Payment list fetched successfully"})

class PaymentDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        try:
            payment = Payment.objects.get(pk=pk, order__user=request.user)
            serializer = PaymentSerializer(payment)
            return Response(serializer.data)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)


# Stripe Payment Views
class GetStripeConfigView(APIView):
    """Get Stripe publishable key for frontend"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        return Response({
            'publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
            'currency': 'usd'
        })


class CreateCheckoutSessionView(APIView):
    """Create Stripe Checkout Session - redirects to Stripe's hosted payment page"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Create a Stripe Checkout Session for an order"""
        # Ensure Stripe API key is set
        if not settings.STRIPE_SECRET_KEY:
            return Response(
                {'error': 'Stripe API key is not configured'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        order_id = request.data.get('order_id')
        coupon_code = request.data.get('coupon_code')
        success_url = request.data.get('success_url', 'https://lulijewelry.com/payment-success')
        cancel_url = request.data.get('cancel_url', 'https://lulijewelry.com/payment-failure')
        
        try:
            order = Order.objects.get(pk=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if payment already exists
        if hasattr(order, 'payment') and order.payment.status == 'completed':
            return Response(
                {'error': 'Payment already completed for this order'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate total amount (apply coupon if provided)
        amount = float(order.total_amount)
        discount_amount = Decimal('0.00')
        line_items = []
        
        # Build line items from order items
        for item in order.items.all():
            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': item.product.title,
                        'description': item.product.description[:500] if item.product.description else '',
                        'images': [img.image.url for img in item.product.images.filter(is_main=True)[:1]] if hasattr(item.product, 'images') else [],
                    },
                    'unit_amount': int(float(item.price) * 100),  # Convert to cents
                },
                'quantity': item.quantity,
            })
        
        # Add shipping as a line item if applicable
        if order.shipping_cost > 0:
            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Shipping',
                    },
                    'unit_amount': int(float(order.shipping_cost) * 100),
                },
                'quantity': 1,
            })
        
        # Add tax as a line item if applicable
        if order.tax_amount > 0:
            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Tax',
                    },
                    'unit_amount': int(float(order.tax_amount) * 100),
                },
                'quantity': 1,
            })
        
        # Apply coupon if provided
        discounts = []
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code)
                if coupon.is_valid() and (not coupon.minimum_order_amount or order.subtotal >= coupon.minimum_order_amount):
                    if coupon.discount_type == 'percentage':
                        discount_amount = (order.subtotal * coupon.discount_value) / 100
                        if coupon.maximum_discount:
                            discount_amount = min(discount_amount, coupon.maximum_discount)
                    else:
                        discount_amount = coupon.discount_value
                    
                    # Create Stripe coupon
                    try:
                        stripe_coupon = stripe.Coupon.create(
                            id=f"coupon_{coupon.code}_{order.id}",
                            percent_off=coupon.discount_value if coupon.discount_type == 'percentage' else None,
                            amount_off=int(float(coupon.discount_value) * 100) if coupon.discount_type == 'fixed' else None,
                            currency='usd',
                            duration='once',
                        )
                        discounts.append({'coupon': stripe_coupon.id})
                    except stripe.error.InvalidRequestError:
                        # Coupon already exists, use it
                        discounts.append({'coupon': f"coupon_{coupon.code}_{order.id}"})
            except Coupon.DoesNotExist:
                pass
        
        try:
            # Ensure Stripe is properly initialized
            if not stripe.api_key:
                return Response(
                    {'error': 'Stripe API key is not configured'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Workaround for stripe.checkout being None
            # Try to access checkout module directly
            try:
                from stripe import checkout
                checkout_module = checkout
            except ImportError:
                # Fallback: try to get it from stripe module
                checkout_module = getattr(stripe, 'checkout', None)
                if checkout_module is None:
                    # Force initialization by accessing a Stripe resource first
                    # This sometimes helps initialize submodules
                    _ = stripe.Coupon.list(limit=1)
                    checkout_module = getattr(stripe, 'checkout', None)
            
            if checkout_module is None:
                # Fallback: Use direct HTTP API call with JSON
                headers = {
                    'Authorization': f'Bearer {settings.STRIPE_SECRET_KEY}',
                    'Content-Type': 'application/json',
                }
                
                payload = {
                    # 'payment_method_types': ['card'],
                    'line_items': line_items,
                    'mode': 'payment',
                    'success_url': f"{success_url}?session_id={{CHECKOUT_SESSION_ID}}&order_id={order.id}",
                    'cancel_url': f"{cancel_url}?order_id={order.id}",
                    'customer_email': request.user.email,
                    'metadata': {
                        'order_id': str(order.id),
                        'order_number': order.order_number,
                        'user_id': str(request.user.id),
                    },
                }
                
                # Add discounts if any
                if discounts:
                    payload['discounts'] = discounts
                
                response = requests.post(
                    'https://api.stripe.com/v1/checkout/sessions',
                    headers=headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    return Response(
                        {
                            'error': 'Failed to create Stripe checkout session',
                            'details': response.text,
                            'solution': 'Please reinstall Stripe: pip install --upgrade --force-reinstall stripe'
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                
                checkout_session_data = response.json()
                # Create a simple object to mimic stripe.checkout.Session object
                class CheckoutSession:
                    def __init__(self, data):
                        self.id = data['id']
                        self.url = data['url']
                        self.payment_status = data.get('payment_status', 'unpaid')
                
                checkout_session = CheckoutSession(checkout_session_data)
            else:
                # Normal path - use Stripe SDK
                checkout_session = checkout_module.Session.create(
                    payment_method_types=['card'],
                    line_items=line_items,
                    mode='payment',
                    success_url=f"{success_url}?session_id={{CHECKOUT_SESSION_ID}}&order_id={order.id}",
                    cancel_url=f"{cancel_url}?order_id={order.id}",
                    customer_email=request.user.email,
                    metadata={
                        'order_id': order.id,
                        'order_number': order.order_number,
                        'user_id': request.user.id,
                    },
                    discounts=discounts if discounts else None,
                )
            
            # Create or update Payment record
            payment, created = Payment.objects.get_or_create(
                order=order,
                defaults={
                    'payment_method': 'credit_card',
                    'amount': order.total_amount,
                    'status': 'pending',
                    'transaction_id': checkout_session.id,
                    'gateway_response': {'checkout_session': checkout_session}
                }
            )
            
            if not created:
                payment.transaction_id = checkout_session.id
                payment.gateway_response = {'checkout_session': checkout_session}
                payment.save()
            
            # Apply coupon usage if used
            if coupon_code and discount_amount > 0:
                try:
                    coupon = Coupon.objects.get(code=coupon_code)
                    CouponUsage.objects.get_or_create(
                        coupon=coupon,
                        user=request.user,
                        order=order,
                        defaults={'discount_amount': discount_amount}
                    )
                    coupon.used_count += 1
                    coupon.save()
                except Coupon.DoesNotExist:
                    pass
            
            return Response({
                'checkout_url': checkout_session.url,
                'session_id': checkout_session.id,
                'order_id': order.id,
                'amount': amount - float(discount_amount),
            })
            
        except AttributeError as e:
            # Handle case where stripe.checkout is None
            return Response(
                {
                    'error': 'Stripe checkout module is not available',
                    'details': str(e),
                    'debug_info': {
                        'stripe_module': str(type(stripe)),
                        'has_checkout': hasattr(stripe, 'checkout'),
                        'stripe_checkout_type': str(type(stripe.checkout)) if hasattr(stripe, 'checkout') else None,
                        'api_key_set': bool(stripe.api_key),
                    },
                    'solution': 'Please ensure Stripe library is properly installed: pip install stripe'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except stripe.error.StripeError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class CreatePaymentIntentView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Create a Stripe Payment Intent for an order"""
        order_id = request.data.get('order_id')
        coupon_code = request.data.get('coupon_code')
        
        try:
            order = Order.objects.get(pk=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if payment already exists
        if hasattr(order, 'payment'):
            payment = order.payment
            if payment.transaction_id:
                try:
                    # Retrieve existing payment intent
                    payment_intent = stripe.PaymentIntent.retrieve(payment.transaction_id)
                    return Response({
                        'client_secret': payment_intent.client_secret,
                        'payment_intent_id': payment_intent.id,
                        'amount': float(order.total_amount),
                        'currency': 'usd',
                        'payment_id': payment.id,
                        'message': 'Using existing payment intent'
                    })
                except stripe.error.StripeError:
                    pass
            return Response(
                {'error': 'Payment already exists for this order'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate total amount (apply coupon if provided)
        amount = float(order.total_amount)
        discount_amount = Decimal('0.00')
        
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code)
                if coupon.is_valid() and (not coupon.minimum_order_amount or order.subtotal >= coupon.minimum_order_amount):
                    if coupon.discount_type == 'percentage':
                        discount_amount = (order.subtotal * coupon.discount_value) / 100
                        if coupon.maximum_discount:
                            discount_amount = min(discount_amount, coupon.maximum_discount)
                    else:
                        discount_amount = coupon.discount_value
                    
                    amount = float(order.total_amount - discount_amount)
            except Coupon.DoesNotExist:
                pass
        
        # Convert to cents for Stripe
        amount_in_cents = int(amount * 100)
        
        try:
            # Create Payment Intent
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_in_cents,
                currency='usd',
                metadata={
                    'order_id': order.id,
                    'order_number': order.order_number,
                    'user_id': request.user.id,
                },
                automatic_payment_methods={
                    'enabled': True,
                },
            )
            
            # Create Payment record
            payment = Payment.objects.create(
                order=order,
                payment_method='credit_card',
                amount=order.total_amount,
                status='pending',
                transaction_id=payment_intent.id,
                gateway_response={'payment_intent': payment_intent}
            )
            
            # Apply coupon if used
            if coupon_code and discount_amount > 0:
                try:
                    coupon = Coupon.objects.get(code=coupon_code)
                    CouponUsage.objects.create(
                        coupon=coupon,
                        user=request.user,
                        order=order,
                        discount_amount=discount_amount
                    )
                    coupon.used_count += 1
                    coupon.save()
                    
                    # Update order total
                    order.total_amount = amount
                    order.save()
                except Coupon.DoesNotExist:
                    pass
            
            return Response({
                'client_secret': payment_intent.client_secret,
                'payment_intent_id': payment_intent.id,
                'amount': amount,
                'currency': 'usd',
                'payment_id': payment.id
            })
            
        except stripe.error.StripeError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ConfirmPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Confirm payment after client-side confirmation"""
        payment_intent_id = request.data.get('payment_intent_id')
        order_id = request.data.get('order_id')
        
        if not payment_intent_id:
            return Response(
                {'error': 'payment_intent_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Retrieve payment intent from Stripe
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            # Get payment record
            try:
                payment = Payment.objects.get(transaction_id=payment_intent_id)
                order = payment.order
                
                # Verify order belongs to user
                if order.user != request.user:
                    return Response(
                        {'error': 'Unauthorized'},
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                # Update payment status based on Stripe status
                if payment_intent.status == 'succeeded':
                    payment.status = 'completed'
                    payment.completed_at = timezone.now()
                    payment.gateway_response = {
                        'payment_intent': payment_intent,
                        'status': payment_intent.status
                    }
                    payment.save()
                    
                    # Update order payment status
                    order.payment_status = 'paid'
                    order.status = 'confirmed'
                    order.save()
                    
                    # Confirm reservations (convert reserved stock to permanent deduction)
                    order.confirm_reservations()
                    
                    return Response({
                        'message': 'Payment confirmed successfully',
                        'payment': PaymentSerializer(payment).data,
                        'order': OrderSerializer(order).data
                    })
                elif payment_intent.status == 'processing':
                    payment.status = 'processing'
                    payment.gateway_response = {
                        'payment_intent': payment_intent,
                        'status': payment_intent.status
                    }
                    payment.save()
                    
                    return Response({
                        'message': 'Payment is processing',
                        'payment': PaymentSerializer(payment).data
                    })
                elif payment_intent.status == 'requires_payment_method':
                    payment.status = 'failed'
                    payment.gateway_response = {
                        'payment_intent': payment_intent,
                        'status': payment_intent.status
                    }
                    payment.save()
                    
                    # Update order payment status
                    order.payment_status = 'failed'
                    order.save()
                    
                    # Release reservations back to stock
                    order.release_reservations()
                    
                    return Response({
                        'error': 'Payment requires a payment method',
                        'payment': PaymentSerializer(payment).data
                    }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    payment.status = 'failed'
                    payment.gateway_response = {
                        'payment_intent': payment_intent,
                        'status': payment_intent.status
                    }
                    payment.save()
                    
                    # Update order payment status
                    order.payment_status = 'failed'
                    order.save()
                    
                    # Release reservations back to stock
                    order.release_reservations()
                    
                    return Response({
                        'error': f'Payment failed with status: {payment_intent.status}',
                        'payment': PaymentSerializer(payment).data
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            except Payment.DoesNotExist:
                return Response(
                    {'error': 'Payment not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
                
        except stripe.error.StripeError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class VerifyCheckoutSessionView(APIView):
    """Verify Stripe Checkout Session after user returns from Stripe payment page"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Verify checkout session and update payment status"""
        session_id = request.data.get('session_id')
        order_id = request.data.get('order_id')
        
        if not session_id:
            return Response(
                {'error': 'session_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Retrieve checkout session from Stripe
            checkout_session = stripe.checkout.Session.retrieve(session_id)
            
            # Get order
            try:
                if order_id:
                    order = Order.objects.get(pk=order_id, user=request.user)
                else:
                    order = Order.objects.get(pk=checkout_session.metadata.get('order_id'), user=request.user)
            except Order.DoesNotExist:
                return Response(
                    {'error': 'Order not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get or create payment record
            payment, created = Payment.objects.get_or_create(
                order=order,
                defaults={
                    'payment_method': 'credit_card',
                    'amount': order.total_amount,
                    'status': 'pending',
                    'transaction_id': session_id,
                    'gateway_response': {'checkout_session': checkout_session}
                }
            )
            
            if not created:
                payment.transaction_id = session_id
                payment.gateway_response = {'checkout_session': checkout_session}
            
            # Update payment status based on checkout session status
            if checkout_session.payment_status == 'paid':
                payment.status = 'completed'
                payment.completed_at = timezone.now()
                payment.save()
                
                # Update order
                order.payment_status = 'paid'
                if order.status == 'pending':
                    order.status = 'confirmed'
                order.save()
                
                # Confirm reservations (convert reserved stock to permanent deduction)
                order.confirm_reservations()
                
                return Response({
                    'message': 'Payment confirmed successfully',
                    'payment': PaymentSerializer(payment).data,
                    'order': OrderSerializer(order).data,
                    'payment_status': 'paid'
                })
            elif checkout_session.payment_status == 'unpaid':
                payment.status = 'pending'
                payment.save()
                
                return Response({
                    'message': 'Payment is pending',
                    'payment': PaymentSerializer(payment).data,
                    'payment_status': 'pending'
                })
            else:
                payment.status = 'failed'
                payment.save()
                
                # Update order payment status
                order.payment_status = 'failed'
                order.save()
                
                # Release reservations back to stock
                order.release_reservations()
                
                return Response({
                    'error': f'Payment status: {checkout_session.payment_status}',
                    'payment': PaymentSerializer(payment).data,
                    'payment_status': checkout_session.payment_status
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except stripe.error.StripeError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class StripeWebhookView(APIView):
    """Handle Stripe webhooks"""
    permission_classes = []  # No authentication for webhooks
    http_method_names = ['post']
    
    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        webhook_secret = settings.STRIPE_WEBHOOK_SECRET
        
        try:
            if webhook_secret:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, webhook_secret
                )
            else:
                # For testing without webhook secret
                event = json.loads(payload)
        except ValueError:
            return Response(
                {'error': 'Invalid payload'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except stripe.error.SignatureVerificationError:
            return Response(
                {'error': 'Invalid signature'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Handle the event
        event_type = event.get('type') if isinstance(event, dict) else event.get('type')
        event_data = event.get('data', {}).get('object') if isinstance(event, dict) else event.get('data', {}).get('object')
        
        # Handle Checkout Session completed
        if event_type == 'checkout.session.completed':
            checkout_session = event_data
            session_id = checkout_session.get('id')
            order_id = checkout_session.get('metadata', {}).get('order_id')
            
            try:
                if order_id:
                    order = Order.objects.get(pk=order_id)
                    payment, created = Payment.objects.get_or_create(
                        order=order,
                        defaults={
                            'payment_method': 'credit_card',
                            'amount': order.total_amount,
                            'status': 'completed',
                            'transaction_id': session_id,
                            'gateway_response': {
                                'webhook_event': event,
                                'checkout_session': checkout_session
                            },
                            'completed_at': timezone.now()
                        }
                    )
                    
                    if not created:
                        payment.status = 'completed'
                        payment.completed_at = timezone.now()
                        payment.transaction_id = session_id
                        payment.gateway_response = {
                            'webhook_event': event,
                            'checkout_session': checkout_session
                        }
                        payment.save()
                    
                    # Update order
                    order.payment_status = 'paid'
                    if order.status == 'pending':
                        order.status = 'confirmed'
                    order.save()
                    
                    # Confirm reservations (convert reserved stock to permanent deduction)
                    order.confirm_reservations()
                    
            except Order.DoesNotExist:
                pass
        
        # Handle Payment Intent succeeded
        elif event_type == 'payment_intent.succeeded':
            payment_intent = event_data
            transaction_id = payment_intent.get('id')
            
            try:
                payment = Payment.objects.get(transaction_id=transaction_id)
                payment.status = 'completed'
                payment.completed_at = timezone.now()
                payment.gateway_response = {
                    'webhook_event': event,
                    'payment_intent': payment_intent
                }
                payment.save()
                
                # Update order
                order = payment.order
                order.payment_status = 'paid'
                if order.status == 'pending':
                    order.status = 'confirmed'
                order.save()
                
                # Confirm reservations (convert reserved stock to permanent deduction)
                order.confirm_reservations()
                
            except Payment.DoesNotExist:
                pass
                
        elif event_type == 'payment_intent.payment_failed':
            payment_intent = event_data
            transaction_id = payment_intent.get('id')
            
            try:
                payment = Payment.objects.get(transaction_id=transaction_id)
                payment.status = 'failed'
                payment.gateway_response = {
                    'webhook_event': event,
                    'payment_intent': payment_intent
                }
                payment.save()
                
                # Update order
                order = payment.order
                order.payment_status = 'failed'
                order.save()
                
                # Release reservations back to stock
                order.release_reservations()
                
            except Payment.DoesNotExist:
                pass
        
        return Response({'status': 'success'})


# Coupon Views
class CouponListView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        filters = {}
        
        # Apply filters
        if request.query_params.get('is_active'):
            filters['is_active'] = request.query_params.get('is_active').lower() == 'true'
        
        if request.query_params.get('discount_type'):
            filters['discount_type'] = request.query_params.get('discount_type')
        
        if request.query_params.get('min_discount'):
            filters['discount_value__gte'] = request.query_params.get('min_discount')
        
        if request.query_params.get('max_discount'):
            filters['discount_value__lte'] = request.query_params.get('max_discount')
        
        queryset = Coupon.objects.filter(is_active=True)
        if filters:
            queryset = queryset.filter(**filters)
        
        serializer = CouponSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """Create a new coupon (Admin only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'You do not have permission to create coupons.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = CouponSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CouponDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        """Get coupon details"""
        try:
            coupon = Coupon.objects.get(pk=pk)
            serializer = CouponSerializer(coupon)
            return Response(serializer.data)
        except Coupon.DoesNotExist:
            return Response({'error': 'Coupon not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, pk):
        """Update a coupon (Admin only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'You do not have permission to update coupons.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            coupon = Coupon.objects.get(pk=pk)
        except Coupon.DoesNotExist:
            return Response({'error': 'Coupon not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CouponSerializer(coupon, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """Delete a coupon (Admin only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'You do not have permission to delete coupons.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            coupon = Coupon.objects.get(pk=pk)
            coupon.delete()
            return Response(
                {'message': 'Coupon deleted successfully'},
                status=status.HTTP_204_NO_CONTENT
            )
        except Coupon.DoesNotExist:
            return Response({'error': 'Coupon not found'}, status=status.HTTP_404_NOT_FOUND)


class CouponValidateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        code = request.data.get('code')
        order_amount = request.data.get('order_amount', 0)
        
        try:
            coupon = Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            return Response({'error': 'Invalid coupon code'}, status=status.HTTP_404_NOT_FOUND)
        
        if not coupon.is_valid():
            return Response({'error': 'Coupon is not valid'}, status=status.HTTP_400_BAD_REQUEST)
        
        if coupon.minimum_order_amount and order_amount < coupon.minimum_order_amount:
            return Response({
                'error': f'Minimum order amount of ${coupon.minimum_order_amount} required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate discount
        if coupon.discount_type == 'percentage':
            discount_amount = (order_amount * coupon.discount_value) / 100
            if coupon.maximum_discount:
                discount_amount = min(discount_amount, coupon.maximum_discount)
        else:
            discount_amount = coupon.discount_value
        
        return Response({
            'coupon': CouponSerializer(coupon).data,
            'discount_amount': discount_amount
        })


class CouponUsageListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        filters = {}
        
        # Apply filters
        if request.query_params.get('coupon_code'):
            filters['coupon__code__icontains'] = request.query_params.get('coupon_code')
        
        if request.query_params.get('date_from'):
            filters['used_at__gte'] = request.query_params.get('date_from')
        
        if request.query_params.get('date_to'):
            filters['used_at__lte'] = request.query_params.get('date_to')
        
        queryset = CouponUsage.objects.filter(user=request.user)
        if filters:
            queryset = queryset.filter(**filters)
        
        queryset = queryset.order_by('-used_at')
        serializer = CouponUsageSerializer(queryset, many=True)
        return Response(serializer.data)