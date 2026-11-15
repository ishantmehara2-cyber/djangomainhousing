from django.contrib import admin
from apps.billing.models import Package, Subscription, Transaction, Invoice, PropertyPromotion, ProductCategory, Product

@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'target_role', 'price', 'validity_days', 'max_listings', 'featured_listings_count', 'is_active')
    list_filter = ('target_role', 'is_active')
    search_fields = ('name', 'description')

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'package', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'package')
    search_fields = ('user__username', 'user__email', 'package__name')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'package', 'amount', 'status', 'razorpay_order_id', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'user__email', 'razorpay_order_id', 'razorpay_payment_id')

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'transaction', 'total_amount', 'issued_at')
    search_fields = ('invoice_number', 'transaction__user__username')

@admin.register(PropertyPromotion)
class PropertyPromotionAdmin(admin.ModelAdmin):
    list_display = ('property', 'purchaser', 'promotion_type', 'start_date', 'end_date', 'is_active')
    list_filter = ('promotion_type', 'is_active')
    search_fields = ('property__title', 'purchaser__username')

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'display_order')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_published', 'is_active', 'created_at')
    list_filter = ('category', 'is_published', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('price', 'is_published', 'is_active')
