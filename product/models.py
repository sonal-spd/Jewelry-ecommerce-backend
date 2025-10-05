from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='subcategories',
        null=True,
        blank=True
    )
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Material(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_precious = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name


class Gemstone(models.Model):
    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=50, blank=True)
    hardness = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """Main product model for jewelry items"""
    
    # Basic Information
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    description = models.TextField()
    studio_notes = models.TextField(blank=True)
    
    # Pricing & Inventory
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    markup_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    stock_quantity = models.PositiveIntegerField(default=0)
    in_stock = models.BooleanField(default=True)
    
    # Product Status
    is_featured = models.BooleanField(default=False)
    status = models.SmallIntegerField(
        choices=((1, 'Available'), (2, 'Out of Stock'), (3, 'Discontinued')),
        default=1
    )
    
    # Jewelry-specific fields
    jewelry_type = models.CharField(max_length=50, choices=[
        ('ring', 'Ring'),
        ('necklace', 'Necklace'),
        ('bracelet', 'Bracelet'),
        ('earring', 'Earring'),
        ('pendant', 'Pendant'),
        ('brooch', 'Brooch'),
        ('anklet', 'Anklet'),
        ('choker', 'Choker'),
        ('tiara', 'Tiara'),
        ('cufflink', 'Cufflink'),
    ], blank=True)
    
    # Physical properties
    weight = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True, help_text="Weight in grams")
    dimensions = models.CharField(max_length=100, blank=True, help_text="e.g., '2cm x 1.5cm x 0.5cm'")
    
    # Materials and stones
    primary_material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, blank=True, related_name='primary_products')
    secondary_materials = models.ManyToManyField(Material, blank=True, related_name='secondary_products')
    gemstones = models.ManyToManyField(Gemstone, through='ProductGemstone', blank=True)
    
    # Customization
    is_customizable = models.BooleanField(default=False)
    customization_options = models.JSONField(default=dict, blank=True)
    
    # Care instructions
    care_instructions = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Automatically set slug from title if not provided
        if not self.slug:
            self.slug = slugify(self.title)

        # Update in_stock based on stock_quantity
        self.in_stock = self.stock_quantity > 0

        super().save(*args, **kwargs)

    def __str__(self):
        if self.jewelry_type:
            return f"{self.title} ({self.jewelry_type})"
        return self.title


class ProductGemstone(models.Model):
    """Through model for Product-Gemstone relationship with additional details"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    gemstone = models.ForeignKey(Gemstone, on_delete=models.CASCADE)
    carat_weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    cut = models.CharField(max_length=50, blank=True)
    clarity = models.CharField(max_length=50, blank=True)
    color_grade = models.CharField(max_length=50, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    
    class Meta:
        unique_together = ['product', 'gemstone']
    
    def __str__(self):
        return f"{self.product.title} - {self.gemstone.name}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=255, blank=True)
    is_main = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)  # For ordering images
    
    class Meta:
        ordering = ['order', 'id']
    
    def __str__(self):
        return f"{self.product.title} - Image {self.order}"


class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=5, choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.SmallIntegerField(
        choices=((1, 'Approved'), (2, 'Pending'), (3, 'Rejected')),
        default=2
    )
    
    class Meta:
        unique_together = ['product', 'user']  # One review per user per product
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.product.title} ({self.rating} stars)"


class RecommendedProduct(models.Model):
    """Model for product recommendations"""
    product = models.ForeignKey(Product, related_name='recommendations', on_delete=models.CASCADE)
    recommended = models.ForeignKey(Product, related_name='recommended_for', on_delete=models.CASCADE)
    reason = models.CharField(max_length=255, blank=True)  # Why this product is recommended
    
    class Meta:
        unique_together = ['product', 'recommended']
    
    def __str__(self):
        return f"{self.product.title} → {self.recommended.title}"


# Shopping Cart Models
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart for {self.user.get_full_name()}"
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())
    
    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['cart', 'product']
    
    def __str__(self):
        return f"{self.quantity}x {self.product.title}"
    
    @property
    def total_price(self):
        return self.product.price * self.quantity


# Wishlist Models
class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishlist')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Wishlist for {self.user.get_full_name()}"


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['wishlist', 'product']
    
    def __str__(self):
        return f"{self.product.title} in {self.wishlist.user.get_full_name()}'s wishlist"