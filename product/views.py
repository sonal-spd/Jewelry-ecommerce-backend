from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Avg, Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.text import slugify
from decimal import Decimal
import os
import re
from django.conf import settings
from django.core.files.storage import default_storage
from Luli.utils import format_errors
from .models import (
    Category, Product, ProductImage, Review, Material, Gemstone,
    Cart, CartItem, Wishlist, WishlistItem, ProductGemstone
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
        queryset = Product.objects.select_related('category', 'primary_material').prefetch_related('images', 'reviews','gemstones')
        
        # Apply filters from query parameters
        filters = {}
        
        # Category filter
        if request.query_params.get('category'):
            filters['category__name__icontains'] = request.query_params.get('category')
        
        # Jewelry type filter - Removed as requested
        # if request.query_params.get('jewelry_type'):
        #    filters['jewelry_type__name__icontains'] = request.query_params.get('jewelry_type')
        
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
        # queryset = queryset.filter(status=1)
        
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
                'images', 'reviews', 'secondary_materials', 'gemstones'
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
    pagination_class = StandardResultsSetPagination

    def get(self, request, pk=None):

        if pk:
            try:
                review = Review.objects.select_related(
                    'product', 'user'
                ).get(pk=pk, user=request.user)

                serializer = ReviewSerializer(review)
                return Response(serializer.data)

            except Review.DoesNotExist:
                return Response(
                    {'error': 'Review not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

        queryset = Review.objects.select_related(
            'product', 'user'
        ).filter(user=request.user)

      
        filters = dict(request.query_params.items())
        if filters:
            queryset = queryset.filter(**filters)

        ordering = request.query_params.get('ordering', '-created_at')
        queryset = queryset.order_by(ordering)
   
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = ReviewSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = ReviewSerializer(queryset, many=True)
        return Response({"status": 200, "data": serializer.data}, status=status.HTTP_200_OK)


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
        product_slug = request.data.get('product')
        quantity = request.data.get('quantity', 1)
        
        try:
            product = Product.objects.get(slug=product_slug)
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
        product_id = request.data.get('product')
        
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
        product_slug = request.data.get('product')
        
        try:
            product = Product.objects.get(slug=product_slug)
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
        product_slug = request.data.get('product')
        
        try:
            wishlist_item = WishlistItem.objects.get(wishlist=wishlist, product_slug=product_slug)
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
        
        # if data.get('jewelry_type'):
        #    queryset = queryset.filter(jewelry_type__name__icontains=data['jewelry_type'])
        
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
        # if request.query_params.get('jewelry_type'):
        #    filters['jewelry_type__name__icontains'] = request.query_params.get('jewelry_type')
        
        if request.query_params.get('category'):
            filters['category__name__icontains'] = request.query_params.get('category')
        
        if request.query_params.get('primary_material'):
            filters['primary_material__name__icontains'] = request.query_params.get('primary_material')
        
        queryset = Product.objects.all()
        print("*********************")
        print(queryset.values('id', 'title', 'is_featured', 'in_stock', 'status'))

        
        if filters:
            queryset = queryset.filter(**filters)
        
        # Limit to 8 products
        queryset = queryset[:10]
        
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
                # jewelry_type=product.jewelry_type
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
            response_data.append({
                'id': product.id,
                'name': product.title,
                'slug': product.slug,
                'price': str(product.price),
                'image': product.featured_image
            })
        
        return Response(response_data)


# Product Image Views
class ProductImageUploadView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, product_slug):
        """Upload multiple images for a product"""
        try:
            product = Product.objects.get(slug=product_slug)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        # Must send files under `images`
        images = request.FILES.getlist('images')
        if not images:
            return Response({'error': 'No images provided'}, status=status.HTTP_400_BAD_REQUEST)

        alt_texts = request.data.getlist('alt_texts', [])   # optional list
        is_mains = request.data.getlist('is_mains', [])     # optional list

        created_images = []

        for index, image_file in enumerate(images):
            # Extract metadata per image
            alt_text = alt_texts[index] if index < len(alt_texts) else ""
            is_main = is_mains[index].lower() == "true" if index < len(is_mains) else False

            # If this image is main, unset others
            if is_main:
                ProductImage.objects.filter(product=product, is_main=True).update(is_main=False)

            # Create product image object
            product_image = ProductImage.objects.create(
                product=product,
                image=image_file,
                alt_text=alt_text,
                is_main=is_main
            )

            created_images.append(product_image)

        serializer = ProductImageSerializer(created_images, many=True)
        return Response({"message":"Product Images Upload Succesfully","details":serializer.data}, status=status.HTTP_201_CREATED)


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


class ProductUploadView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['file']
        if not file.name.endswith('.xlsx'):
            return Response({'error': 'File must be an Excel .xlsx file'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            import openpyxl
        except ImportError:
            return Response({'error': 'openpyxl library is missing'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            wb = openpyxl.load_workbook(file)
            sheet = wb.active
            
            headers = [cell.value for cell in sheet[1]]
            # Map headers to field names
            # Lowercase and strip for better matching
            header_map = {str(h).lower().strip(): i for i, h in enumerate(headers) if h}
            
            created_count = 0
            updated_count = 0
            errors = []

            for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
                try:
                    # Helper to get value by column name
                    def get_val(col_name, default=None):
                        # Try exact match first
                        idx = header_map.get(col_name.lower())
                        if idx is not None and idx < len(row):
                            return row[idx]
                        
                        # Try fuzzy match (contains)
                        for h, i in header_map.items():
                            if col_name.lower() in h:
                                if i < len(row):
                                    return row[i]
                        return default

                    title = get_val('Product Name')
                    if not title:
                        continue # Skip empty rows

                    # Prepare defaults for update_or_create
                    defaults = {}
                    
                    # Price
                    price = get_val('Price')
                    if price:
                        try:
                            defaults['price'] = Decimal(str(price).replace('$', '').replace(',', ''))
                        except:
                            defaults['price'] = Decimal('0.00')
                    
                    # Description (Overview)
                    description = get_val('Overview')
                    if description:
                        defaults['description'] = description

                    # Category (Default to 'Uncategorized' if not specified)
                    category_val = get_val('Category')
                    
                    category_name = category_val or 'Uncategorized'
                    category, _ = Category.objects.get_or_create(name=category_name, defaults={'description': 'Auto-created category'})
                    defaults['category'] = category

                    # Selling Price handling (if distinct from 'Price')
                    selling_price = get_val('Selling Price')
                    if selling_price:
                         try:
                            defaults['price'] = Decimal(str(selling_price).replace('$', '').replace(',', ''))
                         except:
                            pass # Fallback to 'Price' column handled above if valid

                    # Stock (Default to 1 if not specified)
                    defaults['stock_quantity'] = 1
                    defaults['in_stock'] = True
                    
                    # Primary Material (Metal)
                    material_name = get_val('Metal')
                    if material_name:
                        material, _ = Material.objects.get_or_create(name=material_name, defaults={'description': 'Auto-created material'})
                        defaults['primary_material'] = material

                    # Studio Notes (Product Code) -> Now Product Code
                    product_code = get_val('Product Code')
                    if product_code:
                        defaults['product_code'] = str(product_code)

                    # Dimensions (Length/Size)
                    dimensions = get_val('Length/Size')
                    if dimensions:
                        defaults['dimensions'] = dimensions

                    # Image Links handling (Image File, Drive Link, etc.)
                    # Scan multiple potential columns for images
                    image_potential_cols = ['Image File', 'Drive Link', 'Image Links', 'Images', 'Google Drive']
                    extracted_images = []

                    for col_name in image_potential_cols:
                        val = get_val(col_name)
                        if val:
                            # Handle multiple images separated by comma or newline
                            # Also handle potential "https" prefix issues if present like "httpsME002" -> assume valid for now or user specific
                            raw_links = str(val).replace('\n', ',').replace(';', ',').split(',')
                            for link in raw_links:
                                clean_link = link.strip()
                                if clean_link:
                                    extracted_images.append(clean_link)
                    
                    # Deduplicate images while preserving order
                    seen_imgs = set()
                    final_images = []
                    for img in extracted_images:
                        if img not in seen_imgs:
                            final_images.append(img)
                            seen_imgs.add(img)

                    if final_images:
                         defaults['featured_image'] = final_images[0]
                         defaults['image_links'] = final_images

                    # Create or Update
                    # Generate slug from Title + Product Code (if available) to ensure uniqueness
                    if not 'slug' in defaults:
                        slug_base = title
                        if 'product_code' in defaults and defaults['product_code']:
                            slug_base = f"{title}-{defaults['product_code']}"
                        
                        slug_candidate = slugify(slug_base)[:50]
                        defaults['slug'] = slug_candidate

                    # Logic update: Prefer updating by Product Code to avoid overwriting distinct products with same name
                    product_code = defaults.get('product_code')
                    
                    if product_code:
                        # Ensure title is in defaults so it gets updated/set
                        defaults['title'] = title
                        product, created = Product.objects.update_or_create(
                            product_code=product_code,
                            defaults=defaults
                        )
                    else:
                        # Fallback to Title if no product code provided (legacy behavior)
                        product, created = Product.objects.update_or_create(
                            title=title,
                            defaults=defaults
                        )
                    
                    # Handle Gemstones (Diamonds, Rubies, Other Stones)
                    gemstone_cols = ['Diamonds', 'Rubies', 'Other Stones']
                    for col in gemstone_cols:
                        gem_val = get_val(col)
                        if gem_val:
                            # Create a gemstone entry for this description
                            # Use the full string as name if short, otherwise just the column name and add description
                            gem_name = str(gem_val).split('(')[0].strip()[:99] # Truncate if too long
                            if len(gem_name) < 3: # Too short, use column name
                                gem_name = col
                            
                            # Ensure name is not too long for the field (max 100)
                            gem_name = gem_name[:100]

                            gemstone_obj, _ = Gemstone.objects.get_or_create(name=gem_name, defaults={'description': str(gem_val)})
                            # Update description if it was generic
                            if gemstone_obj.description is None:
                                gemstone_obj.description = str(gem_val)
                                gemstone_obj.save()

                            ProductGemstone.objects.get_or_create(product=product, gemstone=gemstone_obj)

                    if created:
                        created_count += 1
                    else:
                        updated_count += 1

                except Exception as e:
                    errors.append(f"Row {row_idx} ({title if 'title' in locals() else 'Unknown'}): {str(e)}")

            return Response({
                'message': f'Processed {created_count + updated_count} products',
                'created': created_count,
                'updated': updated_count,
                'errors': errors
            })

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



class UploadProductImagesAPI(APIView):

    def post(self, request):

        product_code = request.data.get("product_code")
        images = request.FILES.getlist("images")

        if not product_code:
            return Response({"error": "product_code required"}, status=400)

        if not images:
            return Response({"error": "No images uploaded"}, status=400)

        # --- DIRECTORY ---
        folder_path = os.path.join(settings.MEDIA_ROOT, "products", product_code)

        # Create product folder if missing
        os.makedirs(folder_path, exist_ok=True)

        # --- FIND LAST COUNT ---
        existing_files = os.listdir(folder_path)
        pattern = re.compile(rf"{re.escape(product_code)}_(\d+)\.")

        last_number = 0
        for filename in existing_files:
            match = pattern.search(filename)
            if match:
                num = int(match.group(1))
                if num > last_number:
                    last_number = num

        # Start from next available number
        count = last_number + 1

        saved_files = []

        # --- SAVE NEW IMAGES ---
        for img in images:
            ext = os.path.splitext(img.name)[1]
            new_filename = f"{product_code}_{count}{ext}"

            save_path = os.path.join(folder_path, new_filename)

            with open(save_path, "wb+") as destination:
                for chunk in img.chunks():
                    destination.write(chunk)

            # Return URL, not filesystem path
            file_url = f"https://api.lulibyveronica.com{settings.MEDIA_URL}products/{product_code}/{new_filename}"
            saved_files.append(file_url)

            count += 1

        return Response({
            "product_code": product_code,
            "uploaded_images": saved_files
        }, status=status.HTTP_200_OK)
