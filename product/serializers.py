from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Category, Product, ProductImage, Review, RecommendedProduct,
    Material, Gemstone, ProductGemstone,
    Cart, CartItem, Wishlist, WishlistItem
)

User = get_user_model()


# Basic serializers
class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent', 'description', 'subcategories']
        read_only_fields = ['slug']
    
    def get_subcategories(self, obj):
        if obj.subcategories.exists():
            return CategorySerializer(obj.subcategories.all(), many=True).data
        return []


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ['id', 'name', 'description', 'is_precious']


class GemstoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gemstone
        fields = ['id', 'name', 'color', 'hardness', 'description']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_main', 'order']


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'user_name', 'rating', 'comment', 'status', 'created_at']
        read_only_fields = ['user', 'created_at']


class ProductGemstoneSerializer(serializers.ModelSerializer):
    gemstone_name = serializers.CharField(source='gemstone.name', read_only=True)
    gemstone_color = serializers.CharField(source='gemstone.color', read_only=True)
    
    class Meta:
        model = ProductGemstone
        fields = [
            'id', 'gemstone', 'gemstone_name', 'gemstone_color',
            'carat_weight', 'cut', 'clarity', 'color_grade', 'quantity'
        ]


# Product serializers
class ProductListSerializer(serializers.ModelSerializer):
    """Serializer for product list views (minimal data)"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    primary_material_name = serializers.CharField(source='primary_material.name', read_only=True)
    main_image = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'category_name', 'primary_material_name',
            'price', 'jewelry_type', 'weight', 'dimensions', 'is_featured',
            'in_stock', 'main_image', 'average_rating', 'review_count'
        ]
    
    def get_main_image(self, obj):
        main_image = obj.images.filter(is_main=True).first()
        if main_image:
            return ProductImageSerializer(main_image).data
        return None
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.filter(status=1)
        if reviews.exists():
            return round(sum(review.rating for review in reviews) / reviews.count(), 1)
        return 0
    
    def get_review_count(self, obj):
        return obj.reviews.filter(status=1).count()


class ProductSerializer(serializers.ModelSerializer):
    """Detailed serializer for product detail views"""
    category = CategorySerializer(read_only=True)
    primary_material = MaterialSerializer(read_only=True)
    secondary_materials = MaterialSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    gemstones = ProductGemstoneSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'category', 'description', 'studio_notes',
            'price', 'cost_price', 'markup_percentage', 'stock_quantity', 'in_stock',
            'jewelry_type', 'weight', 'dimensions', 'primary_material', 'secondary_materials',
            'is_featured', 'is_customizable', 'customization_options', 'care_instructions',
            'status', 'images', 'gemstones', 'reviews', 'average_rating', 'review_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.filter(status=1)
        if reviews.exists():
            return round(sum(review.rating for review in reviews) / reviews.count(), 1)
        return 0
    
    def get_review_count(self, obj):
        return obj.reviews.filter(status=1).count()


# Cart and Wishlist serializers
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'total_price', 'added_at']
        read_only_fields = ['added_at']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_items', 'total_price', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']


class WishlistItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = WishlistItem
        fields = ['id', 'product', 'product_id', 'added_at']
        read_only_fields = ['added_at']


class WishlistSerializer(serializers.ModelSerializer):
    items = WishlistItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'items', 'created_at']
        read_only_fields = ['user', 'created_at']


# Search serializer
class ProductSearchSerializer(serializers.Serializer):
    query = serializers.CharField(required=False, allow_blank=True)
    category = serializers.CharField(required=False, allow_blank=True)
    jewelry_type = serializers.CharField(required=False, allow_blank=True)
    material = serializers.CharField(required=False, allow_blank=True)
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    is_featured = serializers.BooleanField(required=False, allow_null=True)
    in_stock = serializers.BooleanField(required=False, allow_null=True)
    sort_by = serializers.ChoiceField(
        choices=[
            ('newest', 'Newest'),
            ('oldest', 'Oldest'),
            ('price_asc', 'Price: Low to High'),
            ('price_desc', 'Price: High to Low'),
            ('rating', 'Rating'),
            ('popular', 'Popular')
        ],
        required=False,
        default='newest'
    )
    page = serializers.IntegerField(required=False, default=1, min_value=1)
    page_size = serializers.IntegerField(required=False, default=20, min_value=1, max_value=100)