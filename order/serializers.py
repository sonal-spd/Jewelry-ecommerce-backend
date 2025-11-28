from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Order, OrderItem, Payment, Coupon, CouponUsage
from product.serializers import ProductListSerializer

User = get_user_model()


# Order serializers
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_id', 'quantity', 'price', 'total_price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'user', 'user_name', 'order_number', 'status', 'status_display',
            'payment_status', 'payment_status_display', 'subtotal', 'tax_amount',
            'shipping_cost', 'total_amount', 'shipping_address', 'billing_address',
            'created_at', 'updated_at', 'shipped_at', 'delivered_at', 'notes',
            'tracking_number', 'items'
        ]
        read_only_fields = ['order_number', 'created_at', 'updated_at']


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating orders"""
    items = OrderItemSerializer(many=True)
    
    class Meta:
        model = Order
        fields = [
            'items', 'shipping_address', 'billing_address', 
            'notes', 'subtotal', 'tax_amount', 'shipping_cost', 'total_amount'
        ]
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        
        return order


# Payment serializers
class PaymentSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'order_number', 'payment_method', 'payment_method_display',
            'amount', 'status', 'status_display', 'transaction_id', 'gateway_response',
            'created_at', 'completed_at'
        ]
        read_only_fields = ['created_at', 'completed_at']


# Coupon serializers
class CouponSerializer(serializers.ModelSerializer):
    is_valid = serializers.SerializerMethodField()
    
    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'description', 'discount_type', 'discount_value',
            'minimum_order_amount', 'maximum_discount', 'valid_from', 'valid_until',
            'is_active', 'usage_limit', 'used_count', 'is_valid', 'created_at'
        ]
        read_only_fields = ['used_count', 'created_at']
    
    def validate_code(self, value):
        """Validate unique coupon code"""
        instance = self.instance
        queryset = Coupon.objects.filter(code=value)
        if instance:
            queryset = queryset.exclude(pk=instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError(f'A coupon with the code "{value}" already exists.')
        return value
    
    def get_is_valid(self, obj):
        return obj.is_valid()


class CouponUsageSerializer(serializers.ModelSerializer):
    coupon_code = serializers.CharField(source='coupon.code', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    
    class Meta:
        model = CouponUsage
        fields = [
            'id', 'coupon', 'coupon_code', 'user', 'user_name', 
            'order', 'order_number', 'discount_amount', 'used_at'
        ]
        read_only_fields = ['used_at']
    
    def validate(self, attrs):
        """Validate unique coupon usage per order"""
        instance = self.instance
        coupon = attrs.get('coupon') or (instance.coupon if instance else None)
        order = attrs.get('order') or (instance.order if instance else None)
        
        if coupon and order:
            queryset = CouponUsage.objects.filter(coupon=coupon, order=order)
            if instance:
                queryset = queryset.exclude(pk=instance.pk)
            
            if queryset.exists():
                raise serializers.ValidationError({
                    'non_field_errors': ['This coupon has already been used for this order.']
                })
        
        return attrs
