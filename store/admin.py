from django.contrib import admin

# Register your models here.
"""
تخصيص لوحة إدارة جلباب بالعربية
"""

from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import (
    Category, Product, Order, OrderItem,
    ContactMessage, HeroImage,
)


# ==========================================
# تخصيص عنوان لوحة الإدارة
# ==========================================
admin.site.site_header = "إدارة متجر جلباب"
admin.site.site_title = "جلباب"
admin.site.index_title = "مرحبًا بك في لوحة تحكم جلباب"


# ==========================================
# Category Admin
# ==========================================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'products_count', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at',)

    @admin.display(description='عدد المنتجات')
    def products_count(self, obj):
        return obj.products.count()


# ==========================================
# Product Admin
# ==========================================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'thumbnail', 'name', 'category', 'price',
        'old_price', 'stock', 'is_new', 'is_discounted', 'is_active'
    )
    list_filter = ('category', 'is_new', 'is_discounted', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('price', 'stock', 'is_new', 'is_active')
    readonly_fields = ('created_at', 'updated_at', 'image_preview')
    list_per_page = 20

    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('category', 'name', 'slug', 'description')
        }),
        ('الصورة', {
            'fields': ('image', 'image_preview')
        }),
        ('الأسعار', {
            'fields': ('price', 'old_price'),
            'description': 'إذا كان المنتج عليه خصم، ضع السعر قبل الخصم في "old_price".'
        }),
        ('المخزون والحالة', {
            'fields': ('stock', 'is_new', 'is_discounted', 'is_active')
        }),
        ('تواريخ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='الصورة')
    def thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:50px;height:50px;'
                'object-fit:cover;border-radius:6px;" />',
                obj.image.url
            )
        return "—"

    @admin.display(description='معاينة')
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width:250px;border-radius:8px;" />',
                obj.image.url
            )
        return "لا توجد صورة بعد."


# ==========================================
# OrderItem Inline (داخل صفحة الطلب)
# ==========================================
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'price', 'quantity', 'subtotal_display')
    can_delete = False

    @admin.display(description='الإجمالي الفرعي')
    def subtotal_display(self, obj):
        return f"{obj.subtotal} جنيه"


# ==========================================
# Order Admin
# ==========================================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number', 'full_name', 'phone',
        'governorate', 'status', 'total_price',
        'items_count', 'created_at'
    )
    list_filter = ('status', 'governorate', 'created_at')
    search_fields = ('order_number', 'full_name', 'phone')
    readonly_fields = ('order_number', 'total_price', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    list_per_page = 20
    date_hierarchy = 'created_at'

    fieldsets = (
        ('بيانات الطلب', {
            'fields': ('order_number', 'status', 'total_price', 'created_at', 'updated_at')
        }),
        ('بيانات العميل', {
            'fields': ('full_name', 'phone', 'governorate', 'city', 'address', 'notes')
        }),
    )


# ==========================================
# ContactMessage Admin
# ==========================================
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'short_message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('name', 'email', 'phone', 'message', 'created_at')
    list_editable = ('is_read',)
    actions = ['mark_as_read']

    @admin.display(description='الرسالة')
    def short_message(self, obj):
        return obj.message[:60] + ('...' if len(obj.message) > 60 else '')

    @admin.action(description='تحديد كمقروءة')
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)


# ==========================================
# HeroImage Admin
# ==========================================
@admin.register(HeroImage)
class HeroImageAdmin(admin.ModelAdmin):
    list_display = ('thumbnail', 'title', 'subtitle', 'is_active', 'created_at')
    list_filter = ('is_active',)
    list_editable = ('is_active',)
    readonly_fields = ('image_preview', 'created_at')

    fieldsets = (
        ('المحتوى', {
            'fields': ('title', 'subtitle')
        }),
        ('الصورة', {
            'fields': ('image', 'image_preview')
        }),
        ('زر التسوق', {
            'fields': ('button_text', 'button_url')
        }),
        ('الحالة', {
            'fields': ('is_active', 'created_at')
        }),
    )

    @admin.display(description='الصورة')
    def thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:60px;height:40px;'
                'object-fit:cover;border-radius:6px;" />',
                obj.image.url
            )
        return "—"

    @admin.display(description='معاينة')
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width:400px;border-radius:8px;" />',
                obj.image.url
            )
        return "لا توجد صورة بعد."

    def has_add_permission(self, request):
        # السماح بإضافة أكثر من Hero (المستخدم يفعّل واحدة فقط)
        return True