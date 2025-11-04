from django.contrib import admin
from .models import PremiumPlan, PremiumSubscription


@admin.register(PremiumPlan)
class PremiumPlanAdmin(admin.ModelAdmin):
    """Administration des plans Premium"""
    list_display = (
        'name', 'plan_type', 'price', 'currency', 'max_ads',
        'duration_days', 'is_active', 'order'
    )
    list_filter = ('is_active', 'plan_type')
    search_fields = ('name', 'description')
    list_editable = ('is_active', 'order', 'price')
    ordering = ['order', 'price']

    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'plan_type', 'description', 'order')
        }),
        ('Tarification', {
            'fields': ('price', 'currency', 'duration_days')
        }),
        ('Limites', {
            'fields': ('max_ads',)
        }),
        ('Fonctionnalités', {
            'fields': ('features',),
            'classes': ('collapse',)
        }),
        ('Statut', {
            'fields': ('is_active',)
        }),
    )


@admin.register(PremiumSubscription)
class PremiumSubscriptionAdmin(admin.ModelAdmin):
    """Administration des abonnements Premium"""
    list_display = (
        'user', 'plan', 'status', 'start_date', 'end_date',
        'days_remaining', 'payment_method', 'amount_paid', 'created_at'
    )
    list_filter = ('status', 'payment_method', 'created_at', 'plan')
    search_fields = ('user__username', 'user__email', 'transaction_reference')
    raw_id_fields = ('user', 'plan')
    readonly_fields = ('created_at', 'updated_at', 'days_remaining', 'is_active')
    date_hierarchy = 'created_at'

    actions = ['activate_subscriptions', 'cancel_subscriptions']

    fieldsets = (
        ('Utilisateur et Plan', {
            'fields': ('user', 'plan')
        }),
        ('Statut', {
            'fields': ('status', 'is_active', 'days_remaining')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'created_at', 'updated_at')
        }),
        ('Paiement', {
            'fields': ('payment_method', 'transaction_reference', 'amount_paid')
        }),
    )

    def days_remaining(self, obj):
        return obj.days_remaining

    days_remaining.short_description = 'Jours restants'

    def activate_subscriptions(self, request, queryset):
        """Activer les abonnements sélectionnés"""
        count = 0
        for subscription in queryset.filter(status='pending'):
            subscription.activate()
            count += 1

        self.message_user(request, f'{count} abonnement(s) activé(s) avec succès.')

    activate_subscriptions.short_description = 'Activer les abonnements'

    def cancel_subscriptions(self, request, queryset):
        """Annuler les abonnements sélectionnés"""
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} abonnement(s) annulé(s).')

    cancel_subscriptions.short_description = 'Annuler les abonnements'