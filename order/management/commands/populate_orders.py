from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
import random
from datetime import datetime, timedelta

from order.models import Order, OrderItem, Payment, Coupon, CouponUsage
from product.models import Product

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate orders, payments, and coupons'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing order data before populating',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing order data...')
            self.clear_data()

        self.stdout.write('Creating orders, payments, and coupons...')
        
        with transaction.atomic():
            # Get existing users and products
            users = User.objects.filter(is_superuser=False)
            products = Product.objects.all()
            
            if not users.exists() or not products.exists():
                self.stdout.write('No users or products found. Please run populate_db first.')
                return
            
            # Create coupons
            coupons = self.create_coupons()
            
            # Create orders
            orders = self.create_orders(users, products)
            
            # Create payments
            self.create_payments(orders)
            
            # Create coupon usages
            self.create_coupon_usages(orders, coupons)

        self.stdout.write(
            self.style.SUCCESS('Successfully populated orders, payments, and coupons!')
        )

    def clear_data(self):
        """Clear existing order data"""
        CouponUsage.objects.all().delete()
        Payment.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Coupon.objects.all().delete()

    def create_coupons(self):
        """Create sample coupons"""
        coupons_data = [
            {
                'code': 'WELCOME10',
                'description': 'Welcome discount for new customers',
                'discount_type': 'percentage',
                'discount_value': Decimal('10.00'),
                'minimum_order_amount': Decimal('50.00'),
                'maximum_discount': Decimal('25.00'),
                'valid_from': timezone.now() - timedelta(days=30),
                'valid_until': timezone.now() + timedelta(days=30),
                'usage_limit': 100,
                'used_count': 15
            },
            {
                'code': 'SAVE20',
                'description': '20% off on orders over $200',
                'discount_type': 'percentage',
                'discount_value': Decimal('20.00'),
                'minimum_order_amount': Decimal('200.00'),
                'maximum_discount': Decimal('100.00'),
                'valid_from': timezone.now() - timedelta(days=15),
                'valid_until': timezone.now() + timedelta(days=15),
                'usage_limit': 50,
                'used_count': 8
            },
            {
                'code': 'FIXED50',
                'description': '$50 off on orders over $500',
                'discount_type': 'fixed',
                'discount_value': Decimal('50.00'),
                'minimum_order_amount': Decimal('500.00'),
                'maximum_discount': None,
                'valid_from': timezone.now() - timedelta(days=7),
                'valid_until': timezone.now() + timedelta(days=7),
                'usage_limit': 25,
                'used_count': 3
            },
            {
                'code': 'FIRSTTIME',
                'description': 'First time buyer special',
                'discount_type': 'percentage',
                'discount_value': Decimal('15.00'),
                'minimum_order_amount': Decimal('100.00'),
                'maximum_discount': Decimal('50.00'),
                'valid_from': timezone.now() - timedelta(days=60),
                'valid_until': timezone.now() + timedelta(days=60),
                'usage_limit': 200,
                'used_count': 45
            },
            {
                'code': 'EXPIRED',
                'description': 'Expired coupon for testing',
                'discount_type': 'percentage',
                'discount_value': Decimal('25.00'),
                'minimum_order_amount': Decimal('75.00'),
                'maximum_discount': Decimal('30.00'),
                'valid_from': timezone.now() - timedelta(days=60),
                'valid_until': timezone.now() - timedelta(days=30),
                'usage_limit': 10,
                'used_count': 0
            }
        ]

        coupons = []
        for coupon_data in coupons_data:
            coupon = Coupon.objects.create(**coupon_data)
            coupons.append(coupon)

        self.stdout.write(f'Created {len(coupons)} coupons')
        return coupons

    def create_orders(self, users, products):
        """Create sample orders"""
        orders = []
        
        # Create orders for each user
        for user in users:
            # Create 1-3 orders per user
            num_orders = random.randint(1, 3)
            
            for order_num in range(num_orders):
                # Select random products for this order
                order_products = random.sample(list(products), random.randint(1, 4))
                
                # Calculate totals
                subtotal = sum(product.price for product in order_products)
                tax_amount = subtotal * Decimal('0.08')  # 8% tax
                shipping_cost = Decimal('15.00') if subtotal < Decimal('100.00') else Decimal('0.00')
                total_amount = subtotal + tax_amount + shipping_cost
                
                # Create order
                order = Order.objects.create(
                    user=user,
                    status=random.choice(['pending', 'confirmed', 'processing', 'shipped', 'delivered']),
                    payment_status=random.choice(['pending', 'paid', 'failed']),
                    subtotal=subtotal,
                    tax_amount=tax_amount,
                    shipping_cost=shipping_cost,
                    total_amount=total_amount,
                    shipping_address={
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'address_line_1': '123 Sample Street',
                        'city': 'Sample City',
                        'state': 'SC',
                        'postal_code': '12345',
                        'country': 'United States',
                        'phone': '+1-555-0123'
                    },
                    billing_address={
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'address_line_1': '123 Sample Street',
                        'city': 'Sample City',
                        'state': 'SC',
                        'postal_code': '12345',
                        'country': 'United States',
                        'phone': '+1-555-0123'
                    },
                    notes=f'Sample order #{order_num + 1} for {user.get_full_name()}',
                    created_at=timezone.now() - timedelta(days=random.randint(1, 30))
                )
                
                # Create order items
                for product in order_products:
                    quantity = random.randint(1, 3)
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=product.price
                    )
                
                orders.append(order)

        self.stdout.write(f'Created {len(orders)} orders')
        return orders

    def create_payments(self, orders):
        """Create payments for orders"""
        payment_methods = ['credit_card', 'debit_card', 'paypal', 'bank_transfer']
        
        for order in orders:
            if order.payment_status == 'paid':
                payment = Payment.objects.create(
                    order=order,
                    payment_method=random.choice(payment_methods),
                    amount=order.total_amount,
                    status='completed',
                    transaction_id=f'TXN{order.order_number}{random.randint(1000, 9999)}',
                    gateway_response={
                        'transaction_id': f'TXN{order.order_number}{random.randint(1000, 9999)}',
                        'status': 'success',
                        'gateway': 'stripe',
                        'processed_at': timezone.now().isoformat()
                    },
                    completed_at=order.created_at + timedelta(minutes=random.randint(5, 30))
                )
            elif order.payment_status == 'failed':
                Payment.objects.create(
                    order=order,
                    payment_method=random.choice(payment_methods),
                    amount=order.total_amount,
                    status='failed',
                    transaction_id=f'TXN{order.order_number}{random.randint(1000, 9999)}',
                    gateway_response={
                        'transaction_id': f'TXN{order.order_number}{random.randint(1000, 9999)}',
                        'status': 'failed',
                        'error': 'Insufficient funds',
                        'gateway': 'stripe'
                    }
                )
            else:  # pending
                Payment.objects.create(
                    order=order,
                    payment_method=random.choice(payment_methods),
                    amount=order.total_amount,
                    status='pending',
                    transaction_id=f'TXN{order.order_number}{random.randint(1000, 9999)}'
                )

        self.stdout.write(f'Created payments for {len(orders)} orders')

    def create_coupon_usages(self, orders, coupons):
        """Create coupon usages for some orders"""
        # Use coupons on some orders
        orders_with_coupons = random.sample(orders, min(len(orders) // 3, len(orders)))
        
        for order in orders_with_coupons:
            # Select a random coupon
            coupon = random.choice(coupons)
            
            # Calculate discount amount
            if coupon.discount_type == 'percentage':
                discount_amount = (order.subtotal * coupon.discount_value) / 100
                if coupon.maximum_discount:
                    discount_amount = min(discount_amount, coupon.maximum_discount)
            else:
                discount_amount = coupon.discount_value
            
            # Create coupon usage
            CouponUsage.objects.create(
                coupon=coupon,
                user=order.user,
                order=order,
                discount_amount=discount_amount,
                used_at=order.created_at
            )

        self.stdout.write(f'Created coupon usages for {len(orders_with_coupons)} orders')
