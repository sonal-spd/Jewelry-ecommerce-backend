from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone

# Custom User Manager
class UserManager(BaseUserManager):
    """Custom user manager for our User model"""
    
    def create_user(self, loginname, email, password=None, **extra_fields):
        """Create and return a regular user with the given loginname and email"""
        if not loginname:
            raise ValueError('The loginname field must be set')
        if not email:
            raise ValueError('The email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(loginname=loginname, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, loginname, email, password=None, **extra_fields):
        """Create and return a superuser with the given loginname and email"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('status', 1)  # Active status
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(loginname, email, password, **extra_fields)

# Custom User Model
class User(AbstractUser):
    """Custom user model extending Django's AbstractUser"""
    
    # Remove the default username field
    username = None
    
    # Additional fields
    loginname = models.CharField(max_length=150, unique=True, help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.")
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    
    # User status
    STATUS_CHOICES = [
        (1, 'Active'),
        (2, 'Inactive'),
        (3, 'Suspended'),
        (4, 'Pending Verification'),
    ]
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=4)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    # Override username field to use loginname
    USERNAME_FIELD = 'loginname'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
    
    # Use our custom manager
    objects = UserManager()
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.loginname})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        return self.first_name


# User Profile Model
class UserProfile(models.Model):
    """Extended user profile information"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Personal Information
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], blank=True)
    
    # Address Information
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    
    # Preferences
    newsletter_subscription = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    email_notifications = models.BooleanField(default=True)
    
    # Social Media (optional)
    website = models.URLField(blank=True)
    instagram = models.CharField(max_length=100, blank=True)
    facebook = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profile for {self.user.get_full_name()}"


# Address Models
class Address(models.Model):
    ADDRESS_TYPE_CHOICES = [
        ('home', 'Home'),
        ('work', 'Work'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPE_CHOICES, default='home')
    
    # Address fields
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    company = models.CharField(max_length=100, blank=True)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    
    # Flags
    is_default = models.BooleanField(default=False)
    is_billing = models.BooleanField(default=False)
    is_shipping = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.city}, {self.state}"
    
    def save(self, *args, **kwargs):
        # Ensure only one default address per user
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)