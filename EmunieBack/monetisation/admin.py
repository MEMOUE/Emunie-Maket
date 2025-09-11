from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count
from django.utils import timezone
from .models import (
    Package, UserSubscription, AdBoost, PaymentMethod, Transaction,
    Coupon, CouponUsage, Revenue
)

@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    """Administration des packages"""
    list_display = (
        'name', 'package_type', 'price', 'currency', 'duration_days',
        'boost_multiplier', 'is_active', 'purchases_count'
    )
    list_filter = ('package_type', 'is_active', 'featured_placement', 'video_upload')
    search_fields = ('name', 'description')
    list_editable = ('is_active',)
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'package_type', 'description', 'price', 'currency', 'duration_days')
        }),
        ('Avantages', {
            'fields': (
                'boost_multiplier', 'max_ads', 'priority_support',
                'featured_placement', 'unlimited_photos', 'video_upload'
            )
        }),
        ('État', {
            'fields': ('is_active',)
        }),
    )
    
    def purchases_count(self, obj):
        return Transaction.objects.filter(package=obj, status='completed').count()
    purchases_count.short_description = 'Achats'

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    """Administration des méthodes de paiement"""
    list_display = (
        'name', 'payment_type', 'provider', 'is_active',
        'processing_fee', 'order', 'transactions_count'
    )
    list_filter = ('payment_type', 'is_active')
    search_fields = ('name', 'provider')
    list_editable = ('is_active', 'order')
    
    def transactions_count(self, obj):
        return obj.transactions.count()
    transactions_count.short_description = 'Transactions'

@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    """Administration des abonnements utilisateur"""
    list_display = (
        'user', 'package_name', 'status', 'start_date',
        'end_date', 'days_remaining_display', 'auto_renew'
    )
    list_filter = ('status', 'auto_renew', 'package__package_type', 'start_date')
    search_fields = ('user__username', 'package__name')
    raw_id_fields = ('user',)
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'start_date'
    
    def package_name(self, obj):
        return obj.package.name
    package_name.short_description = 'Package'
    
    def days_remaining_display(self, obj):
        days = obj.days_remaining
        if days > 0:
            return f"{days} jour(s)"
        elif days == 0:
            return "Expire aujourd'hui"
        else:
            return "Expiré"
    days_remaining_display.short_description = 'Temps restant'

@admin.register(AdBoost)
class AdBoostAdmin(admin.ModelAdmin):
    """Administration des boosts d'annonces"""
    list_display = (
        'ad_title', 'user', 'boost_type', 'price_paid',
        'start_date', 'end_date', 'is_active', 'effectiveness_display'
    )
    list_filter = ('boost_type', 'is_active', 'start_date')
    search_fields = ('ad__title', 'user__username')
    raw_id_fields = ('ad', 'user', 'package')
    readonly_fields = ('created_at',)
    date_hierarchy = 'start_date'
    
    def ad_title(self, obj):
        return obj.ad.title
    ad_title.short_description = 'Annonce'
    
    def effectiveness_display(self, obj):
        views_increase = obj.views_after - obj.views_before
        return f"+{views_increase} vues"
    effectiveness_display.short_description = 'Efficacité'

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Administration des transactions"""
    list_display = (
        'reference', 'user', 'package_name', 'payment_method_name',
        'total_amount', 'currency', 'status', 'created_at'
    )
    list_filter = (
        'status', 'transaction_type', 'payment_method__payment_type',
        'currency', 'created_at'
    )
    search_fields = ('reference', 'external_reference', 'user__username')
    readonly_fields = (
        'reference', 'total_amount', 'created_at', 'processed_at', 'completed_at'
    )
    raw_id_fields = ('user', 'package', 'subscription', 'ad_boost')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Identification', {
            'fields': ('reference', 'external_reference', 'user')
        }),
        ('Détails de la transaction', {
            'fields': (
                'package', 'subscription', 'ad_boost', 'payment_method',
                'transaction_type'
            )
        }),
        ('Montants', {
            'fields': ('amount', 'processing_fee', 'total_amount', 'currency')
        }),
        ('État', {
            'fields': ('status', 'description', 'failure_reason')
        }),
        ('Contact', {
            'fields': ('phone_number',)
        }),
        ('Dates', {
            'fields': ('created_at', 'processed_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_completed', 'mark_as_failed']
    
    def package_name(self, obj):
        return obj.package.name if obj.package else '-'
    package_name.short_description = 'Package'
    
    def payment_method_name(self, obj):
        return obj.payment_method.name
    payment_method_name.short_description = 'Méthode de paiement'
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.filter(status='pending').update(
            status='completed',
            completed_at=timezone.now()
        )
        self.message_user(request, f'{updated} transaction(s) marquée(s) comme complétée(s).')
    mark_as_completed.short_description = 'Marquer comme complétées'
    
    def mark_as_failed(self, request, queryset):
        updated = queryset.filter(status='pending').update(
            status='failed',
            failure_reason='Marqué comme échoué par l\'administrateur'
        )
        self.message_user(request, f'{updated} transaction(s) marquée(s) comme échouée(s).')
    mark_as_failed.short_description = 'Marquer comme échouées'

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    """Administration des coupons"""
    list_display = (
        'code', 'name', 'discount_type', 'discount_value',
        'current_uses', 'max_uses', 'is_valid_display', 'valid_until'
    )
    list_filter = (
        'discount_type', 'is_active', 'new_users_only',
        'valid_from', 'valid_until'
    )
    search_fields = ('code', 'name', 'description')
    filter_horizontal = ('applicable_packages',)
    raw_id_fields = ('created_by',)
    readonly_fields = ('current_uses', 'created_at')
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('code', 'name', 'description', 'created_by')
        }),
        ('Réduction', {
            'fields': ('discount_type', 'discount_value', 'max_discount')
        }),
        ('Conditions d\'utilisation', {
            'fields': (
                'min_amount', 'max_uses', 'max_uses_per_user',
                'current_uses', 'new_users_only'
            )
        }),
        ('Validité', {
            'fields': ('valid_from', 'valid_until', 'is_active')
        }),
        ('Restrictions', {
            'fields': ('applicable_packages',),
            'classes': ('collapse',)
        }),
    )
    
    def is_valid_display(self, obj):
        if obj.is_valid:
            return format_html('<span style="color: green;">✓ Valide</span>')
        else:
            return format_html('<span style="color: red;">✗ Invalide</span>')
    is_valid_display.short_description = 'Validité'

@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    """Administration de l'utilisation des coupons"""
    list_display = ('coupon_code', 'user', 'discount_amount', 'used_at')
    list_filter = ('used_at', 'coupon__discount_type')
    search_fields = ('coupon__code', 'user__username')
    raw_id_fields = ('coupon', 'user', 'transaction')
    readonly_fields = ('used_at',)
    
    def coupon_code(self, obj):
        return obj.coupon.code
    coupon_code.short_description = 'Code coupon'

@admin.register(Revenue)
class RevenueAdmin(admin.ModelAdmin):
    """Administration des revenus"""
    list_display = (
        'date', 'total_revenue', 'package_revenue', 'boost_revenue',
        'subscription_revenue', 'transactions_count', 'growth_display'
    )
    list_filter = ('date',)
    readonly_fields = (
        'package_revenue', 'boost_revenue', 'subscription_revenue',
        'total_revenue', 'transactions_count', 'new_subscriptions',
        'ad_boosts', 'created_at', 'updated_at'
    )
    date_hierarchy = 'date'
    
    def growth_display(self, obj):
        # Calculer la croissance par rapport au jour précédent
        try:
            from datetime import timedelta
            previous_day = Revenue.objects.get(date=obj.date - timedelta(days=1))
            if previous_day.total_revenue > 0:
                growth = ((obj.total_revenue - previous_day.total_revenue) / previous_day.total_revenue) * 100
                color = 'green' if growth > 0 else 'red'
                return format_html(
                    '<span style="color: {};">{:+.1f}%</span>',
                    color, growth
                )
        except Revenue.DoesNotExist:
            pass
        return '-'
    growth_display.short_description = 'Croissance'
    
    def has_add_permission(self, request):
        return False  # Les revenus sont générés automatiquement
    
    def has_delete_permission(self, request, obj=None):
        return False  # Ne pas permettre la suppression des données de revenus

# Personnalisation de l'interface d'administration
admin.site.site_header = "Administration Emunie"
admin.site.site_title = "Emunie Admin"
admin.site.index_title = "Tableau de bord administrateur"