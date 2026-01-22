from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Category, Product, ProductImage, Review, RecommendedProduct,
    Material, Gemstone, ProductGemstone,
    Cart, CartItem, Wishlist, WishlistItem
)


# Inline Admin Classes
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_main', 'order']


class ProductGemstoneInline(admin.TabularInline):
    model = ProductGemstone
    extra = 1
    fields = ['gemstone', 'carat_weight', 'cut', 'clarity', 'color_grade', 'quantity']


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    fields = ['product', 'quantity', 'added_at']
    readonly_fields = ['added_at']


class WishlistItemInline(admin.TabularInline):
    model = WishlistItem
    extra = 0
    fields = ['product', 'added_at']
    readonly_fields = ['added_at']


# Main Admin Classes
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'product_count']
    list_filter = ['parent']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_precious', 'jewelry_count']
    list_filter = ['is_precious']
    search_fields = ['name', 'description']
    
    def jewelry_count(self, obj):
        return obj.primary_products.count() + obj.secondary_products.count()
    jewelry_count.short_description = 'Jewelry Items'


@admin.register(Gemstone)
class GemstoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'hardness', 'jewelry_count']
    list_filter = ['color']
    search_fields = ['name', 'color', 'description']
    
    def jewelry_count(self, obj):
        return obj.productgemstone_set.count()
    jewelry_count.short_description = 'Jewelry Items'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'category', 'primary_material', 
        'price', 'stock_quantity', 'in_stock', 'is_featured', 'status'
    ]
    list_filter = [
        'category', 'primary_material', 'is_featured', 
        'in_stock', 'status', 'created_at'
    ]
    search_fields = ['title', 'description', 'studio_notes']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProductImageInline, ProductGemstoneInline]
    filter_horizontal = ['secondary_materials']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'category', 'description', 'studio_notes','product_code','featured_image','image_links')
        }),
        ('Jewelry Details', {
            'fields': ('weight', 'dimensions', 'primary_material', 'secondary_materials')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'cost_price', 'markup_percentage', 'stock_quantity', 'in_stock', 'status')
        }),
        ('Features', {
            'fields': ('is_featured', 'is_customizable', 'customization_options')
        }),
        ('Care Instructions', {
            'fields': ('care_instructions',)
        }),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'status', 'created_at']
    list_filter = ['rating', 'status', 'created_at']
    search_fields = ['product__title', 'user__first_name', 'user__last_name', 'comment']
    readonly_fields = ['created_at']


@admin.register(RecommendedProduct)
class RecommendedProductAdmin(admin.ModelAdmin):
    list_display = ['product', 'recommended', 'reason']
    list_filter = ['product__category', 'recommended__category']
    search_fields = ['product__title', 'recommended__title', 'reason']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_items', 'total_price', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CartItemInline]


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'item_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    readonly_fields = ['created_at']
    inlines = [WishlistItemInline]
    
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'


# Register ProductImage separately
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'alt_text', 'is_main', 'order']
    list_filter = ['is_main']
    search_fields = ['product__title', 'alt_text']


# Customize admin site
admin.site.site_header = "Luli Jewelry Admin"
admin.site.site_title = "Luli Admin"
admin.site.index_title = "Welcome to Luli Jewelry Administration"