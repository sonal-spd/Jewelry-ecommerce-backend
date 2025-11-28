from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Avg, Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.text import slugify
from decimal import Decimal
from django.core.files.storage import default_storage
from Luli.utils import format_errors
from .models import (
    Category, Product, ProductImage, Review, Material, Gemstone,
    Cart, CartItem, Wishlist, WishlistItem
)
from .serializers import (
    CategorySerializer, ProductDetailSerializer,ProductCreateSerializer, ProductListSerializer,
    ProductImageSerializer, ReviewSerializer, MaterialSerializer, GemstoneSerializer,
    CartSerializer, CartItemSerializer, WishlistSerializer, WishlistItemSerializer,
    ProductSearchSerializer
)


# Custom pagination
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


# Category Views
class CategoryListView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        filters = {}
        
        # Apply filters
        if request.query_params.get('parent'):
            filters['parent__name__icontains'] = request.query_params.get('parent')
        
        if request.query_params.get('search'):
            search_query = request.query_params.get('search')
            queryset = Category.objects.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        else:
            queryset = Category.objects.all()
        
        if filters:
            queryset = queryset.filter(**filters)
        
        serializer = CategorySerializer(queryset, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        formatted = format_errors(serializer.errors)
        errors_list = formatted.get('errors', [])
        error_message = ', '.join(errors_list) if errors_list else 'Validation error'
        return Response({'message': error_message}, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetailView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get(self, request, slug):
        try:
            category = Category.objects.get(slug=slug)
            serializer = CategorySerializer(category)
            return Response(serializer.data)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, slug):
        try:
            category = Category.objects.get(slug=slug)
            serializer = CategorySerializer(category, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            formatted = format_errors(serializer.errors)
            errors_list = formatted.get('errors', [])
            error_message = ', '.join(errors_list) if errors_list else 'Validation error'
            return Response({'message': error_message}, status=status.HTTP_400_BAD_REQUEST)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, slug):
        try:
            category = Category.objects.get(slug=slug)
            category.delete()
            return Response({'message': 'Category deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)


# Product Views
class ProductListView(APIView):
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultsSetPagination
    
    def get(self, request):
        # Base queryset
        queryset = Product.objects.select_related('category', 'primary_material').prefetch_related('images', 'reviews')
        
        # Apply filters from query parameters
        filters = {}
        
        # Category filter
        if request.query_params.get('category'):
            filters['category__name__icontains'] = request.query_params.get('category')
        
        # Jewelry type filter
        if request.query_params.get('jewelry_type'):
            filters['jewelry_type'] = request.query_params.get('jewelry_type')
        
        # Primary material filter
        if request.query_params.get('primary_material'):
            filters['primary_material__name__icontains'] = request.query_params.get('primary_material')
        
        # Featured filter
        if request.query_params.get('is_featured'):
            filters['is_featured'] = request.query_params.get('is_featured').lower() == 'true'
        
        # Stock filter
        if request.query_params.get('in_stock'):
            filters['in_stock'] = request.query_params.get('in_stock').lower() == 'true'
        
        # Price range filters
        if request.query_params.get('min_price'):
            filters['price__gte'] = request.query_params.get('min_price')
        if request.query_params.get('max_price'):
            filters['price__lte'] = request.query_params.get('max_price')
        
        # Material filter (searches both primary and secondary materials)
        if request.query_params.get('material'):
            material = request.query_params.get('material')
            queryset = queryset.filter(
                Q(primary_material__name__icontains=material) |
                Q(secondary_materials__name__icontains=material)
            ).distinct()
        
        # Apply filters
        if filters:
            queryset = queryset.filter(**filters)
        
        # Search functionality
        search_query = request.query_params.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(studio_notes__icontains=search_query)
            )
        
        # Ordering
        ordering = request.query_params.get('ordering', '-created_at')
        if ordering:
            queryset = queryset.order_by(ordering)
        
        # Only show available products
        queryset = queryset.filter(status=1)
        
        # Pagination
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(queryset, many=True)
        return Response(serializer.data)


class ProductDetailView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, slug):
        try:
            product = Product.objects.select_related('category', 'primary_material').prefetch_related(
                'images', 'reviews', 'secondary_materials', 'gemstones__gemstone'
            ).get(slug=slug)
            serializer = ProductDetailSerializer(product)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)


class ProductCreateView(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request):
        serializer = ProductCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        formatted = format_errors(serializer.errors)
        errors_list = formatted.get('errors', [])
        error_message = ', '.join(errors_list) if errors_list else 'Validation error'
        return Response({'message': error_message}, status=status.HTTP_400_BAD_REQUEST)


class ProductUpdateView(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    def put(self, request, slug):
        try:
            product = Product.objects.get(slug=slug)
            serializer = ProductCreateSerializer(product, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            formatted = format_errors(serializer.errors)
            errors_list = formatted.get('errors', [])
            error_message = ', '.join(errors_list) if errors_list else 'Validation error'
            return Response({'message': error_message}, status=status.HTTP_400_BAD_REQUEST)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    
   
class ProductDeleteView(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    def delete(self, request, slug):
        try:
            product = Product.objects.get(slug=slug)
            product.delete()
            return Response({'message': 'Product deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)


# Review Views
class ReviewListView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get(self, request, product_slug):
        try:
            product = Product.objects.get(slug=product_slug)
            filters = {}
            
            # Apply filters
            if request.query_params.get('rating'):
                filters['rating'] = request.query_params.get('rating')
            
            if request.query_params.get('status'):
                filters['status'] = request.query_params.get('status')
            
            queryset = Review.objects.filter(product=product)
            if filters:
                queryset = queryset.filter(**filters)
            
            queryset = queryset.order_by('-created_at')
            serializer = ReviewSerializer(queryset, many=True)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request, product_slug):
        try:
            product = Product.objects.get(slug=product_slug)
            serializer = ReviewSerializer(data=request.data, context={'user': request.user, 'product': product})
            if serializer.is_valid():
                serializer.save(user=request.user, product=product)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            formatted = format_errors(serializer.errors)
            errors_list = formatted.get('errors', [])
            error_message = ', '.join(errors_list) if errors_list else 'Validation error'
            return Response({'message': error_message}, status=status.HTTP_400_BAD_REQUEST)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)


class ReviewDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        try:
            review = Review.objects.get(pk=pk, user=request.user)
            serializer = ReviewSerializer(review)
            return Response(serializer.data)
        except Review.DoesNotExist:
            return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, pk):
        try:
            review = Review.objects.get(pk=pk, user=request.user)
            serializer = ReviewSerializer(review, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            formatted = format_errors(serializer.errors)
            errors_list = formatted.get('errors', [])
            error_message = ', '.join(errors_list) if errors_list else 'Validation error'
            return Response({'message': error_message}, status=status.HTTP_400_BAD_REQUEST)
        except Review.DoesNotExist:
            return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, pk):
        try:
            review = Review.objects.get(pk=pk, user=request.user)
            review.delete()
            return Response({'message': 'Review deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Review.DoesNotExist:
            return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)


# Material and Gemstone Views
class MaterialListView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        filters = {}
        
        # Apply filters
        if request.query_params.get('is_precious'):
            filters['is_precious'] = request.query_params.get('is_precious').lower() == 'true'
        
        if request.query_params.get('search'):
            search_query = request.query_params.get('search')
            queryset = Material.objects.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        else:
            queryset = Material.objects.all()
        
        if filters:
            queryset = queryset.filter(**filters)
        
        serializer = MaterialSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = MaterialSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        formatted = format_errors(serializer.errors)
        errors_list = formatted.get('errors', [])
        error_message = ', '.join(errors_list) if errors_list else 'Validation error'
        return Response({'message': error_message}, status=status.HTTP_400_BAD_REQUEST)


class GemstoneListView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        filters = {}
        
        # Apply filters
        if request.query_params.get('color'):
            filters['color__icontains'] = request.query_params.get('color')
        
        if request.query_params.get('min_hardness'):
            filters['hardness__gte'] = request.query_params.get('min_hardness')
        
        if request.query_params.get('max_hardness'):
            filters['hardness__lte'] = request.query_params.get('max_hardness')
        
        if request.query_params.get('search'):
            search_query = request.query_params.get('search')
            queryset = Gemstone.objects.filter(
                Q(name__icontains=search_query) |
                Q(color__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        else:
            queryset = Gemstone.objects.all()
        
        if filters:
            queryset = queryset.filter(**filters)
        
        serializer = GemstoneSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = GemstoneSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        formatted = format_errors(serializer.errors)
        errors_list = formatted.get('errors', [])
        error_message = ', '.join(errors_list) if errors_list else 'Validation error'
        return Response({'message': error_message}, status=status.HTTP_400_BAD_REQUEST)


# Cart Views
class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    def post(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    def put(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')
        
        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            if quantity <= 0:
                cart_item.delete()
            else:
                cart_item.quantity = quantity
                cart_item.save()
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found in cart'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    def delete(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product_id')
        
        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            cart_item.delete()
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found in cart'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CartSerializer(cart)
        return Response(serializer.data)


# Wishlist Views
class WishlistView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        serializer = WishlistSerializer(wishlist)
        return Response(serializer.data)
    
    def post(self, request):
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        product_id = request.data.get('product_id')
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        
        wishlist_item, created = WishlistItem.objects.get_or_create(
            wishlist=wishlist,
            product=product
        )
        
        if not created:
            return Response({'error': 'Product already in wishlist'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = WishlistSerializer(wishlist)
        return Response(serializer.data)
    
    def delete(self, request):
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        product_id = request.data.get('product_id')
        
        try:
            wishlist_item = WishlistItem.objects.get(wishlist=wishlist, product_id=product_id)
            wishlist_item.delete()
        except WishlistItem.DoesNotExist:
            return Response({'error': 'Item not found in wishlist'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = WishlistSerializer(wishlist)
        return Response(serializer.data)


# Search and Filter Views
class ProductSearchView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = ProductSearchSerializer(data=request.data)
        if not serializer.is_valid():
            formatted = format_errors(serializer.errors)
        errors_list = formatted.get('errors', [])
        error_message = ', '.join(errors_list) if errors_list else 'Validation error'
        return Response({'message': error_message}, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        queryset = Product.objects.select_related('category', 'primary_material').prefetch_related('images', 'reviews')
        
        # Apply filters
        if data.get('query'):
            queryset = queryset.filter(
                Q(title__icontains=data['query']) |
                Q(description__icontains=data['query']) |
                Q(studio_notes__icontains=data['query'])
            )
        
        if data.get('category'):
            queryset = queryset.filter(category__name__icontains=data['category'])
        
        if data.get('jewelry_type'):
            queryset = queryset.filter(jewelry_type=data['jewelry_type'])
        
        if data.get('material'):
            queryset = queryset.filter(
                Q(primary_material__name__icontains=data['material']) |
                Q(secondary_materials__name__icontains=data['material'])
            ).distinct()
        
        if data.get('min_price'):
            queryset = queryset.filter(price__gte=data['min_price'])
        
        if data.get('max_price'):
            queryset = queryset.filter(price__lte=data['max_price'])
        
        if data.get('is_featured') is not None:
            queryset = queryset.filter(is_featured=data['is_featured'])
        
        if data.get('in_stock') is not None:
            queryset = queryset.filter(in_stock=data['in_stock'])
        
        # Apply sorting
        sort_by = data.get('sort_by', 'newest')
        if sort_by == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort_by == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort_by == 'oldest':
            queryset = queryset.order_by('created_at')
        elif sort_by == 'rating':
            queryset = queryset.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
        elif sort_by == 'popular':
            queryset = queryset.annotate(review_count=Count('reviews')).order_by('-review_count')
        
        # Apply pagination
        page = data.get('page', 1)
        page_size = data.get('page_size', 20)
        start = (page - 1) * page_size
        end = start + page_size
        
        products = queryset[start:end]
        serializer = ProductListSerializer(products, many=True)
        
        return Response({
            'products': serializer.data,
            'total_count': queryset.count(),
            'page': page,
            'page_size': page_size,
            'total_pages': (queryset.count() + page_size - 1) // page_size
        })


# Featured Products View
class FeaturedProductsView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        filters = {}
        
        # Apply filters
        if request.query_params.get('jewelry_type'):
            filters['jewelry_type'] = request.query_params.get('jewelry_type')
        
        if request.query_params.get('category'):
            filters['category__name__icontains'] = request.query_params.get('category')
        
        if request.query_params.get('primary_material'):
            filters['primary_material__name__icontains'] = request.query_params.get('primary_material')
        
        queryset = Product.objects.filter(
            is_featured=True, 
            in_stock=True, 
            status=1
        ).select_related('category', 'primary_material').prefetch_related('images')
        
        if filters:
            queryset = queryset.filter(**filters)
        
        # Limit to 8 products
        queryset = queryset[:8]
        
        serializer = ProductListSerializer(queryset, many=True)
        return Response(serializer.data)


# Related Products View
class RelatedProductsView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, product_slug):
        try:
            product = Product.objects.get(slug=product_slug)
            filters = {}
            
            # Apply additional filters
            if request.query_params.get('limit'):
                limit = int(request.query_params.get('limit'))
            else:
                limit = 6
            
            queryset = Product.objects.filter(
                category=product.category,
                jewelry_type=product.jewelry_type
            ).exclude(slug=product_slug).filter(
                in_stock=True, 
                status=1
            ).select_related('category', 'primary_material').prefetch_related('images')
            
            if filters:
                queryset = queryset.filter(**filters)
            
            queryset = queryset[:limit]
            serializer = ProductListSerializer(queryset, many=True)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)


# Category-wise Products View
class CategoryProductsView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Get products by category with specified count"""
        category_slug = request.query_params.get('category')
        count = request.query_params.get('count', 4)  # Default to 4 products
    
        if not category_slug:
            return Response({'error': 'Category parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            count = int(count)
            if count <= 0:
                return Response({'error': 'Count must be a positive integer'}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({'error': 'Count must be a valid integer'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Find category by slug
            category = Category.objects.get(slug=category_slug)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        # Get products for the category
        products = Product.objects.filter(
            category=category,
            status=1,  # Only active products
            stock_quantity__gt=0  # Only products in stock
        ).select_related('category', 'primary_material').prefetch_related('images')[:count]
        
        # Create simplified response with only required fields
        response_data = []
        for product in products:
            # Get the main image or first image
            main_image = None
            if product.images.exists():
                main_image_obj = product.images.filter(is_main=True).first()
                if not main_image_obj:
                    main_image_obj = product.images.first()
                main_image = main_image_obj.image.url if main_image_obj.image else None
            
            response_data.append({
                'id': product.id,
                'name': product.title,
                'slug': product.slug,
                'price': str(product.price),
                'image': main_image
            })
        
        return Response(response_data)


# Product Image Views
class ProductImageUploadView(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request, product_slug):
        """Upload a new image for a product"""
        try:
            product = Product.objects.get(slug=product_slug)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if image file is provided
        if 'image' not in request.FILES:
            return Response({'error': 'No image file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        image_file = request.FILES['image']
        alt_text = request.data.get('alt_text', '')
        is_main = request.data.get('is_main', False)
        
        # If this is set as main image, unset other main images
        if is_main:
            ProductImage.objects.filter(product=product, is_main=True).update(is_main=False)
        
        # Create the product image
        product_image = ProductImage.objects.create(
            product=product,
            image=image_file,
            alt_text=alt_text,
            is_main=is_main
        )
        
        serializer = ProductImageSerializer(product_image)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProductImageListView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get(self, request, product_slug):
        """Get all images for a product"""
        try:
            product = Product.objects.get(slug=product_slug)
            images = ProductImage.objects.filter(product=product).order_by('order', 'id')
            serializer = ProductImageSerializer(images, many=True)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)


class ProductImageDetailView(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request, product_slug, image_id):
        """Get specific product image"""
        try:
            product = Product.objects.get(slug=product_slug)
            image = ProductImage.objects.get(id=image_id, product=product)
            serializer = ProductImageSerializer(image)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({'error': 'Product or image not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, product_slug, image_id):
        """Update product image details"""
        try:
            product = Product.objects.get(slug=product_slug)
            image = ProductImage.objects.get(id=image_id, product=product)
            
            # Check if is_main is being set to True
            is_main = request.data.get('is_main', False)
            if is_main and not image.is_main:
                # Unset other main images
                ProductImage.objects.filter(product=product, is_main=True).update(is_main=False)
            
            serializer = ProductImageSerializer(image, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            formatted = format_errors(serializer.errors)
            errors_list = formatted.get('errors', [])
            error_message = ', '.join(errors_list) if errors_list else 'Validation error'
            return Response({'message': error_message}, status=status.HTTP_400_BAD_REQUEST)
        except Product.DoesNotExist:
            return Response({'error': 'Product or image not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, product_slug, image_id):
        """Delete product image"""
        try:
            product = Product.objects.get(slug=product_slug)
            image = ProductImage.objects.get(id=image_id, product=product)
            
            # Delete the file from storage
            if image.image:
                default_storage.delete(image.image.name)
            
            image.delete()
            return Response({'message': 'Image deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Product.DoesNotExist:
            return Response({'error': 'Product or image not found'}, status=status.HTTP_404_NOT_FOUND)


class ProductImageSetMainView(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request, product_slug, image_id):
        """Set a specific image as the main image for a product"""
        try:
            product = Product.objects.get(slug=product_slug)
            image = ProductImage.objects.get(id=image_id, product=product)
            
            # Unset all other main images for this product
            ProductImage.objects.filter(product=product, is_main=True).update(is_main=False)
            
            # Set this image as main
            image.is_main = True
            image.save()
            
            serializer = ProductImageSerializer(image)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({'error': 'Product or image not found'}, status=status.HTTP_404_NOT_FOUND)


class ProductImageReorderView(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request, product_slug):
        """Reorder product images"""
        try:
            product = Product.objects.get(slug=product_slug)
            image_orders = request.data.get('image_orders', [])
            
            if not image_orders:
                return Response({'error': 'No image orders provided'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Update image orders
            for item in image_orders:
                image_id = item.get('image_id')
                order = item.get('order')
                
                if image_id and order is not None:
                    ProductImage.objects.filter(
                        id=image_id, 
                        product=product
                    ).update(order=order)
            
            # Return updated images
            images = ProductImage.objects.filter(product=product).order_by('order', 'id')
            serializer = ProductImageSerializer(images, many=True)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)