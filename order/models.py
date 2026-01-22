from django.db import models
from django.contrib.auth import get_user_model
from product.models import Product
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


# Order Models
class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True)
    
    # Order details
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Shipping information
    shipping_address = models.JSONField()
    billing_address = models.JSONField()
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_expires_at = models.DateTimeField(null=True, blank=True, help_text="Order expires if payment not completed by this time")
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Additional info
    notes = models.TextField(null=True, blank=True)
    tracking_number = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return f"Order {self.order_number} - {self.user.get_full_name()}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            import uuid
            self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def is_expired(self):
        """Check if order payment has expired"""
        if not self.payment_expires_at:
            return False
        from django.utils import timezone
        return timezone.now() > self.payment_expires_at
    
    def release_reservations(self):
        """Release reserved stock back to available inventory"""
        # Only release if order was pending/failed and not already confirmed/paid
        # This prevents double-release and ensures we only release for pending orders
        if self.payment_status in ['pending', 'failed'] and self.status in ['pending', 'cancelled']:
            for item in self.items.all():
                product = item.product
                # Only release if there are actually reservations (safety check)
                # Use atomic operation to prevent race conditions
                Product.objects.filter(
                    id=product.id,
                    reserved_quantity__gte=item.quantity
                ).update(
                    reserved_quantity=models.F('reserved_quantity') - item.quantity
                )
                # Refresh and update product status
                product.refresh_from_db()
                product.save()  # This will update in_stock
    
    def confirm_reservations(self):
        """Convert reserved stock to permanent deduction (on payment success)"""
        # Only confirm if payment is paid and order was previously pending
        # This prevents double-confirmation and ensures we only confirm once
        if self.payment_status == 'paid' and self.status in ['pending', 'confirmed']:
            for item in self.items.all():
                product = item.product
                # Only confirm if there are actually reservations (safety check)
                # Use atomic operation to prevent race conditions
                updated = Product.objects.filter(
                    id=product.id,
                    reserved_quantity__gte=item.quantity
                ).update(
                    stock_quantity=models.F('stock_quantity') - item.quantity,
                    reserved_quantity=models.F('reserved_quantity') - item.quantity
                )
                # Only refresh and save if update was successful
                if updated > 0:
                    product.refresh_from_db()
                    product.save()  # This will update in_stock


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of order
    
    def __str__(self):
        return f"{self.quantity}x {self.product.title} in Order {self.order.order_number}"
    
    @property
    def total_price(self):
        return self.price * self.quantity


# Payment Models
class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash_on_delivery', 'Cash on Delivery'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Payment gateway details
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    gateway_response = models.JSONField(default=dict, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Payment for Order {self.order.order_number} - {self.get_status_display()}"


# Coupon/Discount Models
class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    description = models.CharField(max_length=255)
    discount_type = models.CharField(max_length=10, choices=[
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ])
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    maximum_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Validity
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    # Usage limits
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Coupon {self.code} - {self.description}"
    
    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        return (
            self.is_active and
            self.valid_from <= now <= self.valid_until and
            (self.usage_limit is None or self.used_count < self.usage_limit)
        )


class CouponUsage(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coupon_usages')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='coupon_usages')
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    used_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['coupon', 'order']
    
    def __str__(self):
        return f"{self.coupon.code} used by {self.user.get_full_name()}"