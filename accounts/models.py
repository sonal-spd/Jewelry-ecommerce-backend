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
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    
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
    phone = models.CharField(max_length=20, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], null=True, blank=True)
    
    # Address Information
    bio = models.TextField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    
    # Preferences
    newsletter_subscription = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    email_notifications = models.BooleanField(default=True)
    
    # Social Media (optional)
    website = models.URLField(null=True, blank=True)
    instagram = models.CharField(max_length=100, null=True, blank=True)
    facebook = models.CharField(max_length=100, null=True, blank=True)
    
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
    company = models.CharField(max_length=100, null=True, blank=True)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    
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


# Appointment Model
class Appointment(models.Model):
    """Model for booking appointments"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    SUBJECT_CHOICES = [
        ('general_inquiry', 'General Inquiry'),
        ('product_consultation', 'Product Consultation'),
        ('custom_design', 'Custom Design'),
        ('repair_service', 'Repair Service'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments', null=True, blank=True)
    
    # Contact Information (for non-authenticated users)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    
    # Appointment Details
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES, default='general_inquiry')
    message = models.TextField(null=True, blank=True)
    
    # Appointment Scheduling
    appointment_date = models.DateTimeField()
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Additional Information
    notes = models.TextField(null=True, blank=True, help_text="Internal notes")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-appointment_date', '-created_at']
    
    def __str__(self):
        user_info = f"{self.first_name} {self.last_name}"
        if self.user:
            user_info = self.user.get_full_name()
        return f"Appointment for {user_info} on {self.appointment_date.strftime('%Y-%m-%d %H:%M')}"