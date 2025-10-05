from django.urls import path
from . import views

app_name = 'product'

urlpatterns = [
    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category-detail'),
    
    # Products
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/create/', views.ProductCreateView.as_view(), name='product-create'),
    path('products/<slug:slug>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('products/<slug:slug>/update/', views.ProductUpdateView.as_view(), name='product-update'),
    path('products/<slug:slug>/delete/', views.ProductDeleteView.as_view(), name='product-delete'),
    
    # Featured and Related Products
    path('products/featured/', views.FeaturedProductsView.as_view(), name='featured-products'),
    path('products/<slug:product_slug>/related/', views.RelatedProductsView.as_view(), name='related-products'),
    
    # Product Reviews
    path('products/<slug:product_slug>/reviews/', views.ReviewListView.as_view(), name='review-list'),
    path('reviews/<int:pk>/', views.ReviewDetailView.as_view(), name='review-detail'),
    
    # Materials and Gemstones
    path('materials/', views.MaterialListView.as_view(), name='material-list'),
    path('gemstones/', views.GemstoneListView.as_view(), name='gemstone-list'),
    
    # Shopping Cart
    path('cart/', views.CartView.as_view(), name='cart'),
    
    # Wishlist
    path('wishlist/', views.WishlistView.as_view(), name='wishlist'),
    
    # Search
    path('search/', views.ProductSearchView.as_view(), name='product-search'),
    
    # Category Products
    path('get-products/', views.CategoryProductsView.as_view(), name='category-products'),
    
    # Product Images
    path('products/<slug:product_slug>/images/', views.ProductImageListView.as_view(), name='product-image-list'),
    path('products/<slug:product_slug>/images/upload/', views.ProductImageUploadView.as_view(), name='product-image-upload'),
    path('products/<slug:product_slug>/images/reorder/', views.ProductImageReorderView.as_view(), name='product-image-reorder'),
    path('products/<slug:product_slug>/images/<int:image_id>/', views.ProductImageDetailView.as_view(), name='product-image-detail'),
    path('products/<slug:product_slug>/images/<int:image_id>/set-main/', views.ProductImageSetMainView.as_view(), name='product-image-set-main'),
]
