from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from decimal import Decimal

from .models import Order, OrderItem, Payment, Coupon, CouponUsage
from .serializers import OrderSerializer, OrderCreateSerializer, OrderItemSerializer, PaymentSerializer, CouponSerializer, CouponUsageSerializer
from product.models import Cart


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
        filters = {}
        
        # Apply filters
        if request.query_params.get('status'):
            filters['status'] = request.query_params.get('status')
        
        if request.query_params.get('payment_status'):
            filters['payment_status'] = request.query_params.get('payment_status')
        
        if request.query_params.get('date_from'):
            filters['created_at__gte'] = request.query_params.get('date_from')
        
        if request.query_params.get('date_to'):
            filters['created_at__lte'] = request.query_params.get('date_to')
        
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
        
        order = Order.objects.create(**order_data)
        
        # Create order items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
        
        # Clear cart
        cart.items.all().delete()
        
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Payment Views
class PaymentListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        filters = {}
        
        # Apply filters
        if request.query_params.get('status'):
            filters['status'] = request.query_params.get('status')
        
        if request.query_params.get('payment_method'):
            filters['payment_method'] = request.query_params.get('payment_method')
        
        if request.query_params.get('date_from'):
            filters['created_at__gte'] = request.query_params.get('date_from')
        
        if request.query_params.get('date_to'):
            filters['created_at__lte'] = request.query_params.get('date_to')
        
        queryset = Payment.objects.filter(order__user=request.user)
        if filters:
            queryset = queryset.filter(**filters)
        
        queryset = queryset.order_by('-created_at')
        serializer = PaymentSerializer(queryset, many=True)
        return Response(serializer.data)


class PaymentDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        try:
            payment = Payment.objects.get(pk=pk, order__user=request.user)
            serializer = PaymentSerializer(payment)
            return Response(serializer.data)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)


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