from django.contrib import admin
from .models import Order, OrderItem, Payment, Coupon, CouponUsage


# Inline Admin Classes
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ['product', 'quantity', 'price', 'total_price']
    readonly_fields = ['total_price']


# Main Admin Classes
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'user', 'status', 'payment_status', 
        'total_amount', 'created_at'
    ]
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['order_number', 'user__first_name', 'user__last_name', 'user__email']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'payment_status')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'tax_amount', 'shipping_cost', 'total_amount')
        }),
        ('Addresses', {
            'fields': ('shipping_address', 'billing_address')
        }),
        ('Tracking', {
            'fields': ('tracking_number', 'shipped_at', 'delivered_at')
        }),
        ('Additional Information', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'order', 'payment_method', 'amount', 'status', 
        'transaction_id', 'created_at'
    ]
    list_filter = ['payment_method', 'status', 'created_at']
    search_fields = ['order__order_number', 'transaction_id']
    readonly_fields = ['created_at', 'completed_at']


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'description', 'discount_type', 'discount_value', 
        'is_active', 'used_count', 'valid_until'
    ]
    list_filter = ['discount_type', 'is_active', 'valid_from', 'valid_until']
    search_fields = ['code', 'description']
    readonly_fields = ['used_count', 'created_at']
    
    fieldsets = (
        ('Coupon Information', {
            'fields': ('code', 'description', 'is_active')
        }),
        ('Discount Details', {
            'fields': ('discount_type', 'discount_value', 'minimum_order_amount', 'maximum_discount')
        }),
        ('Validity', {
            'fields': ('valid_from', 'valid_until', 'usage_limit', 'used_count')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ['coupon', 'user', 'order', 'discount_amount', 'used_at']
    list_filter = ['used_at', 'coupon']
    search_fields = ['coupon__code', 'user__first_name', 'user__last_name', 'order__order_number']
    readonly_fields = ['used_at']