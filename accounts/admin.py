from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile, Address


# Custom User Admin
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = [
        'loginname', 'email', 'first_name', 'last_name', 
        'status', 'is_staff', 'is_active', 'created_at'
    ]
    list_filter = ['status', 'is_staff', 'is_active', 'created_at']
    search_fields = ['loginname', 'email', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('loginname', 'email', 'first_name', 'last_name', 'password')
        }),
        ('Status & Permissions', {
            'fields': ('status', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'created_at', 'updated_at')
        }),
    )
    
    add_fieldsets = (
        ('Basic Information', {
            'classes': ('wide',),
            'fields': ('loginname', 'email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
        ('Status & Permissions', {
            'fields': ('status', 'is_active', 'is_staff', 'is_superuser')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_login']


# User Profile Admin
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'phone', 'gender', 'newsletter_subscription', 
        'email_notifications', 'created_at'
    ]
    list_filter = ['gender', 'newsletter_subscription', 'email_notifications', 'created_at']
    search_fields = ['user__loginname', 'user__email', 'user__first_name', 'user__last_name', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'phone', 'date_of_birth', 'gender', 'bio', 'avatar')
        }),
        ('Preferences', {
            'fields': ('newsletter_subscription', 'sms_notifications', 'email_notifications')
        }),
        ('Social Media', {
            'fields': ('website', 'instagram', 'facebook')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


# Address Admin
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'first_name', 'last_name', 'city', 'state', 
        'address_type', 'is_default', 'is_billing', 'is_shipping'
    ]
    list_filter = ['address_type', 'is_default', 'is_billing', 'is_shipping', 'country', 'state']
    search_fields = [
        'user__loginname', 'user__email', 'first_name', 'last_name', 
        'city', 'state', 'postal_code', 'phone'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'address_type')
        }),
        ('Contact Information', {
            'fields': ('first_name', 'last_name', 'company', 'phone')
        }),
        ('Address Details', {
            'fields': ('address_line_1', 'address_line_2', 'city', 'state', 'postal_code', 'country')
        }),
        ('Address Flags', {
            'fields': ('is_default', 'is_billing', 'is_shipping')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )