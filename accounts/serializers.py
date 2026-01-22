from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from utils.token import email_token_generator
from .models import Address, UserProfile, Appointment

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['loginname', 'first_name', 'last_name', 'email', 'password']
    
    def validate_loginname(self, value):
        """Validate unique loginname"""
        user_id = self.instance.id if self.instance else None
        if User.objects.exclude(id=user_id).filter(loginname=value).exists():
            raise serializers.ValidationError(f'A user with the loginname "{value}" already exists.')
        return value
    
    def validate_email(self, value):
        """Validate unique email"""
        user_id = self.instance.id if self.instance else None
        if User.objects.exclude(id=user_id).filter(email=value).exists():
            raise serializers.ValidationError(f'A user with the email "{value}" already exists.')
        return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.status = 1  # Inactive until verified
        user.save()

        # Send email
        # token = email_token_generator.make_token(user)
        # uid = user.pk
        # verify_url = f"{settings.FRONTEND_URL}/verify-email/?uid={uid}&token={token}"

        # send_mail(
        #     subject="Verify your email",
        #     message=f"Click to verify: {verify_url}",
        #     from_email=settings.DEFAULT_FROM_EMAIL,
        #     recipient_list=[user.email],
        #     fail_silently=False
        # )

        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


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


# Appointment Serializers
class AppointmentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    subject_display = serializers.CharField(source='get_subject_display', read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'user', 'user_name', 'first_name', 'last_name', 'email', 'phone_number',
            'subject', 'subject_display', 'message', 'appointment_date',
            'status', 'status_display', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_appointment_date(self, value):
        """Validate that appointment date is in the future"""
        from django.utils import timezone
        if value < timezone.now():
            raise serializers.ValidationError("Appointment date must be in the future.")
        return value
    
    def validate(self, attrs):
        """Validate appointment data"""
        # If user is authenticated, use their info
        user = self.context.get('request').user if self.context.get('request') else None
        if user and user.is_authenticated:
            # Auto-fill user information if not provided
            if not attrs.get('first_name') and user.first_name:
                attrs['first_name'] = user.first_name
            if not attrs.get('last_name') and user.last_name:
                attrs['last_name'] = user.last_name
            if not attrs.get('email') and user.email:
                attrs['email'] = user.email
        
        return attrs


class AppointmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating appointments"""
    
    class Meta:
        model = Appointment
        fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'subject', 'message', 'appointment_date'
        ]
    
    def validate_appointment_date(self, value):
        """Validate that appointment date is in the future"""
        from django.utils import timezone
        if value < timezone.now():
            raise serializers.ValidationError("Appointment date must be in the future.")
        return value
    
    def validate(self, attrs):
        """Validate appointment data"""
        # If user is authenticated, use their info
        user = self.context.get('request').user if self.context.get('request') else None
        if user and user.is_authenticated:
            # Auto-fill user information if not provided
            if not attrs.get('first_name') and user.first_name:
                attrs['first_name'] = user.first_name
            if not attrs.get('last_name') and user.last_name:
                attrs['last_name'] = user.last_name
            if not attrs.get('email') and user.email:
                attrs['email'] = user.email
        
        return attrs

        