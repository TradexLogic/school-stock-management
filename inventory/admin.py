from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, StockLog


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'product_count', 'description', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']

    def product_count(self, obj):
        count = obj.product_count()
        return format_html('<b>{}</b> products', count)
    product_count.short_description = 'Products'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'quantity', 'stock_status', 'purchase_price', 'selling_price', 'updated_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'category__name']
    readonly_fields = ['quantity', 'created_at', 'updated_at']
    list_per_page = 20

    def stock_status(self, obj):
        if obj.quantity == 0:
            return format_html('<span style="color:red; font-weight:bold;">❌ Out of Stock</span>')
        elif obj.is_low_stock:
            return format_html('<span style="color:orange; font-weight:bold;">⚠️ Low ({})</span>', obj.quantity)
        else:
            return format_html('<span style="color:green; font-weight:bold;">✅ OK ({})</span>', obj.quantity)
    stock_status.short_description = 'Stock Status'


@admin.register(StockLog)
class StockLogAdmin(admin.ModelAdmin):
    list_display = ['product', 'transaction_badge', 'quantity', 'created_by', 'note', 'created_at']
    list_filter = ['transaction_type', 'created_at', 'product__category']
    search_fields = ['product__name', 'note', 'created_by__username']
    readonly_fields = ['created_at', 'created_by']
    date_hierarchy = 'created_at'
    list_per_page = 25

    def transaction_badge(self, obj):
        if obj.transaction_type == 'IN':
            return format_html(
                '<span style="background:#28a745; color:white; padding:2px 8px; border-radius:4px;">📥 IN</span>'
            )
        else:
            return format_html(
                '<span style="background:#dc3545; color:white; padding:2px 8px; border-radius:4px;">📤 OUT</span>'
            )
    transaction_badge.short_description = 'Type'

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)