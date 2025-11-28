from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.text import slugify
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
    
    def validate(self, attrs):
        """Validate unique slug before saving"""
        name = attrs.get('name', '')
        slug_value = attrs.get('slug', '')
        instance = self.instance
        
        # If slug is not provided, it will be auto-generated from name
        if not slug_value and name:
            slug_value = slugify(name)
        
        # Check if slug already exists (excluding current instance if updating)
        if slug_value:
            queryset = Category.objects.filter(slug=slug_value)
            if instance:
                queryset = queryset.exclude(pk=instance.pk)
            
            if queryset.exists():
                raise serializers.ValidationError({
                    'slug': [f'A category with the slug "{slug_value}" already exists. Please use a different name or slug.']
                })
        
        return attrs


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ['id', 'name', 'description', 'is_precious']
    
    def validate_name(self, value):
        """Validate unique material name"""
        instance = self.instance
        queryset = Material.objects.filter(name=value)
        if instance:
            queryset = queryset.exclude(pk=instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError(f'A material with the name "{value}" already exists.')
        return value


class GemstoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gemstone
        fields = ['id', 'name', 'color', 'hardness', 'description']
    
    def validate_name(self, value):
        """Validate unique gemstone name"""
        instance = self.instance
        queryset = Gemstone.objects.filter(name=value)
        if instance:
            queryset = queryset.exclude(pk=instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError(f'A gemstone with the name "{value}" already exists.')
        return value


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
    
    def validate(self, attrs):
        """Validate unique review per user per product"""
        instance = self.instance
        # Get product from attrs, context, or instance
        product = attrs.get('product') or self.context.get('product') or (instance.product if instance else None)
        # User is read-only, so get it from context or instance
        user = self.context.get('user') or (instance.user if instance else None)
        
        if product and user:
            queryset = Review.objects.filter(product=product, user=user)
            if instance:
                queryset = queryset.exclude(pk=instance.pk)
            
            if queryset.exists():
                raise serializers.ValidationError({
                    'non_field_errors': ['You have already reviewed this product.']
                })
        
        return attrs


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


class ProductDetailSerializer(serializers.ModelSerializer):
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
            'jewelry_type', 'weight', 'dimensions', 'primary_material',
            'secondary_materials', 'is_featured', 'is_customizable',
            'customization_options', 'care_instructions', 'status', 'images',
            'gemstones', 'reviews', 'average_rating', 'review_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields  # everything read-only for detail

    def get_average_rating(self, obj):
        reviews = obj.reviews.filter(status=1)
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 0

    def get_review_count(self, obj):
        return obj.reviews.filter(status=1).count()



class ProductCreateSerializer(serializers.ModelSerializer):

    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    primary_material = serializers.PrimaryKeyRelatedField(queryset=Material.objects.all())
    secondary_materials = serializers.PrimaryKeyRelatedField(
        queryset=Material.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = Product
        fields = "__all__"

    def validate(self, attrs):
        """Validate unique slug before saving"""
        # Determine the slug value
        slug_value = attrs.get('slug', '')
        title = attrs.get('title', '')
        
        # If slug is not provided, it will be auto-generated from title
        if not slug_value and title:
            slug_value = slugify(title)
        
        # Get the instance if updating (self.instance exists) or None if creating
        instance = self.instance
        
        # Check if slug already exists (excluding current instance if updating)
        if slug_value:
            queryset = Product.objects.filter(slug=slug_value)
            if instance:
                queryset = queryset.exclude(pk=instance.pk)
            
            if queryset.exists():
                raise serializers.ValidationError(f'A product with this name already exists. Please use a different title or slug.'
                )
        
        return attrs

    def create(self, validated_data):
        secondary_materials = validated_data.pop('secondary_materials', [])
        product = Product.objects.create(**validated_data)
        product.secondary_materials.set(secondary_materials)
        return product

    def update(self, instance, validated_data):
        secondary_materials = validated_data.pop('secondary_materials', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if secondary_materials is not None:
            instance.secondary_materials.set(secondary_materials)

        return instance


# Cart and Wishlist serializers
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'total_price', 'added_at']
        read_only_fields = ['added_at']
    
    def validate(self, attrs):
        """Validate unique cart item (one product per cart)"""
        instance = self.instance
        cart = attrs.get('cart') or (instance.cart if instance else None)
        product = attrs.get('product') or (instance.product if instance else None)
        product_id = attrs.get('product_id')
        
        # If product_id is provided, get the product
        if product_id and not product:
            from .models import Product
            try:
                product = Product.objects.get(pk=product_id)
            except Product.DoesNotExist:
                    raise serializers.ValidationError('Product not found.')
        
        if cart and product:
            queryset = CartItem.objects.filter(cart=cart, product=product)
            if instance:
                queryset = queryset.exclude(pk=instance.pk)
            
            if queryset.exists():
                raise serializers.ValidationError('This product is already in your cart.')
        
        return attrs


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
    
    def validate(self, attrs):
        """Validate unique wishlist item (one product per wishlist)"""
        instance = self.instance
        wishlist = attrs.get('wishlist') or (instance.wishlist if instance else None)
        product = attrs.get('product') or (instance.product if instance else None)
        product_id = attrs.get('product_id')
        
        # If product_id is provided, get the product
        if product_id and not product:
            from .models import Product
            try:
                product = Product.objects.get(pk=product_id)
            except Product.DoesNotExist:
                raise serializers.ValidationError('Product not found.')
        
        if wishlist and product:
            queryset = WishlistItem.objects.filter(wishlist=wishlist, product=product)
            if instance:
                queryset = queryset.exclude(pk=instance.pk)
            
            if queryset.exists():
                raise serializers.ValidationError('This product is already in your wishlist.')
        
        return attrs


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