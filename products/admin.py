from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Category, ProductImage, Wishlist, ProductColor



class ProductColorInline(admin.TabularInline):
    model = ProductColor
    extra = 3
    fields = ['name_en', 'name_ar', 'hex_code', 'stock', 'image', 'is_active', 'order']
    ordering = ['order']

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3
    fields = ['image', 'alt_text', 'is_primary', 'order']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name_en', 'category', 'price', 'discount_price', 'stock', 'is_active', 'is_featured', 'image_preview']
    list_filter = ['is_active', 'is_featured', 'is_new_arrival', 'category']
    search_fields = ['name_en', 'name_ar', 'sku']
    list_editable = ['is_active', 'is_featured', 'stock']
    prepopulated_fields = {'slug': ('name_en',)}
    inlines = [ProductImageInline, ProductColorInline]
    readonly_fields = ['views_count', 'created_at', 'updated_at', 'sku']
    fieldsets = (
        ('Basic Info', {'fields': ('category', 'name_en', 'name_ar', 'slug', 'sku')}),
        ('Descriptions', {'fields': ('description_en', 'description_ar')}),
        ('Pricing & Stock', {'fields': ('price', 'discount_price', 'stock')}),
        ('Details', {'fields': ('material_en', 'material_ar', 'weight', 'dimensions')}),
        ('Status', {'fields': ('is_active', 'is_featured', 'is_new_arrival')}),
        ('Stats', {'fields': ('views_count', 'created_at', 'updated_at')}),
    )

    def image_preview(self, obj):
        img = obj.get_primary_image()
        if img:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover;border-radius:4px"/>', img.image.url)
        return '—'
    image_preview.short_description = 'Image'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name_en', 'name_ar', 'slug', 'is_active', 'order']
    list_editable = ['is_active', 'order']
    prepopulated_fields = {'slug': ('name_en',)}


@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    list_display = ['product', 'color_swatch', 'name_en', 'name_ar', 'hex_code', 'stock', 'is_active']
    list_filter = ['is_active', 'product__category']
    search_fields = ['product__name_en', 'name_en', 'name_ar']
    list_editable = ['stock', 'is_active']

    def color_swatch(self, obj):
        from django.utils.html import format_html
        return format_html(
            '<div style="width:28px;height:28px;border-radius:50%;background:{};border:2px solid #3f3f46;display:inline-block;" title="{}"></div>',
            obj.hex_code, obj.hex_code
        )
    color_swatch.short_description = 'Color'
