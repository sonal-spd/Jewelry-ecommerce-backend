from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from utils.token import email_token_generator
from .models import Address, UserProfile

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['loginname', 'first_name', 'last_name', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.status = 2  # Inactive until verified
        user.save()

        # Send email
        token = email_token_generator.make_token(user)
        uid = user.pk
        verify_url = f"{settings.FRONTEND_URL}/verify-email/?uid={uid}&token={token}"

        send_mail(
            subject="Verify your email",
            message=f"Click to verify: {verify_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )

        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['id', 'status', 'staff', 'admin','password']


class UserListSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(source='profile.phone')
    
    class Meta:
        model = User
        fields = ['id', 'loginname', 'email', 'first_name', 'last_name', 'status','created_at','last_login','phone']


# Address serializers
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'id', 'address_type', 'first_name', 'last_name', 'company',
            'address_line_1', 'address_line_2', 'city', 'state', 
            'postal_code', 'country', 'phone', 'is_default', 
            'is_billing', 'is_shipping', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


# User profile serializer
class UserProfileSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)
    orders_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'loginname', 'email', 'first_name', 'last_name', 
            'status', 'addresses', 'orders_count'
        ]
        read_only_fields = ['loginname', 'status']
    
    def get_orders_count(self, obj):
        return obj.orders.count()


# Extended User Profile serializer
class ExtendedUserProfileSerializer(serializers.ModelSerializer):
    """Serializer for detailed user profile information"""
    
    class Meta:
        model = UserProfile
        fields = [
            'phone', 'date_of_birth', 'gender', 'bio', 'avatar',
            'newsletter_subscription', 'sms_notifications', 'email_notifications',
            'website', 'instagram', 'facebook', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


# Complete User Profile serializer
class CompleteUserProfileSerializer(serializers.ModelSerializer):
    """Complete user profile with extended information"""
    profile = ExtendedUserProfileSerializer(read_only=True)
    addresses = AddressSerializer(many=True, read_only=True)
    orders_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'loginname', 'email', 'first_name', 'last_name', 
            'status', 'created_at', 'updated_at', 'last_login',
            'profile', 'addresses', 'orders_count'
        ]
        read_only_fields = ['loginname', 'status', 'created_at', 'updated_at', 'last_login']
    
    def get_orders_count(self, obj):
        return obj.orders.count()