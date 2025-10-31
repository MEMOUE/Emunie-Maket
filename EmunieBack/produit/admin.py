from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import Ad, AdImage, Advertisement, Favorite, AdView, AdReport

class AdImageInline(admin.TabularInline):
    """Inline pour les images d'annonces"""
    model = AdImage
    extra = 1
    max_num = 3
    min_num = 1
    fields = ('image', 'image_preview', 'caption', 'order', 'is_primary')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.image.url)
        return 'Aucune image'
    image_preview.short_description = 'Aperçu'


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    """Administration des annonces"""
    list_display = (
        'title', 'user', 'category', 'city', 'price', 'status',
        'is_featured', 'is_urgent', 'images_count', 'views_count',
        'favorites_count', 'created_at', 'expires_at'
    )
    list_filter = (
        'status', 'ad_type', 'is_featured', 'is_urgent', 'is_negotiable',
        'category', 'city', 'created_at', 'is_moderated'
    )
    search_fields = ('title', 'description', 'user__username')
    readonly_fields = (
        'id', 'slug', 'views_count', 'favorites_count', 'created_at',
        'updated_at', 'published_at', 'images_count'
    )
    raw_id_fields = ('user', 'moderated_by')
    list_editable = ('is_featured', 'is_urgent')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Informations de base', {
            'fields': (
                'title', 'slug', 'description', 'user', 'category', 'city'
            )
        }),
        ('Détails de l\'annonce', {
            'fields': (
                'ad_type', 'price', 'currency', 'is_negotiable'
            )
        }),
        ('Localisation', {
            'fields': ('address', 'latitude', 'longitude'),
            'classes': ('collapse',)
        }),

        ('État et visibilité', {
            'fields': (
                'status', 'is_featured', 'is_urgent', 'expires_at'
            )
        }),
        ('Statistiques', {
            'fields': (
                'views_count', 'favorites_count', 'images_count',
                'created_at', 'updated_at', 'published_at'
            ),
            'classes': ('collapse',)
        }),
        ('Modération', {
            'fields': (
                'is_moderated', 'moderated_at', 'moderated_by', 'rejection_reason'
            ),
            'classes': ('collapse',)
        }),
    )

    inlines = [AdImageInline]

    actions = ['approve_ads', 'reject_ads', 'feature_ads', 'unfeature_ads']

    def images_count(self, obj):
        return obj.images.count()
    images_count.short_description = 'Nb Images'

    def approve_ads(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            status='active',
            is_moderated=True,
            moderated_by=request.user,
            moderated_at=timezone.now()
        )
        self.message_user(request, f'{updated} annonce(s) approuvée(s).')
    approve_ads.short_description = 'Approuver les annonces sélectionnées'

    def reject_ads(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            status='rejected',
            is_moderated=True,
            moderated_by=request.user,
            moderated_at=timezone.now()
        )
        self.message_user(request, f'{updated} annonce(s) rejetée(s).')
    reject_ads.short_description = 'Rejeter les annonces sélectionnées'

    def feature_ads(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} annonce(s) mise(s) en avant.')
    feature_ads.short_description = 'Mettre en avant'

    def unfeature_ads(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} annonce(s) retirée(s) de la mise en avant.')
    unfeature_ads.short_description = 'Retirer de la mise en avant'


@admin.register(AdImage)
class AdImageAdmin(admin.ModelAdmin):
    """Administration des images d'annonces"""
    list_display = ('ad_title', 'image_preview', 'caption', 'order', 'is_primary', 'created_at')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('ad__title', 'caption')
    raw_id_fields = ('ad',)
    list_editable = ('order', 'is_primary')

    def ad_title(self, obj):
        return obj.ad.title
    ad_title.short_description = 'Annonce'

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.image.url)
        return 'Aucune image'
    image_preview.short_description = 'Aperçu'


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    """Administration des publicités"""
    list_display = (
        'title', 'user', 'duration_days_display', 'total_price',
        'start_date', 'end_date', 'is_active', 'is_approved',
        'impressions', 'clicks', 'ctr_display'
    )
    list_filter = ('is_active', 'is_approved', 'created_at', 'start_date')
    search_fields = ('title', 'user__username', 'link')
    readonly_fields = (
        'total_price', 'impressions', 'clicks', 'ctr_display',
        'created_at', 'image_preview'
    )
    raw_id_fields = ('user',)
    list_editable = ('is_active', 'is_approved')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Informations de base', {
            'fields': ('user', 'title', 'link')
        }),
        ('Contenu visuel', {
            'fields': ('image', 'image_preview')
        }),
        ('Durée et tarification', {
            'fields': ('duration_hours', 'price_per_day', 'total_price', 'start_date', 'end_date')
        }),
        ('État', {
            'fields': ('is_active', 'is_approved')
        }),
        ('Statistiques', {
            'fields': ('impressions', 'clicks', 'ctr_display', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['approve_publicite', 'activate_publicite', 'deactivate_publicite']

    def duration_days_display(self, obj):
        return f"{obj.duration_hours / 24:.0f} jour(s)"
    duration_days_display.short_description = 'Durée'

    def ctr_display(self, obj):
        return f"{obj.ctr:.2f}%"
    ctr_display.short_description = 'CTR'

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 200px;"/>', obj.image.url)
        return 'Aucune image'
    image_preview.short_description = 'Aperçu de l\'affiche'

    def approve_publicite(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} publicité(s) approuvée(s).')
    approve_publicite.short_description = 'Approuver les publicités'

    def activate_publicite(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} publicité(s) activée(s).')
    activate_publicite.short_description = 'Activer les publicités'

    def deactivate_publicite(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} publicité(s) désactivée(s).')
    deactivate_publicite.short_description = 'Désactiver les publicités'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Administration des favoris"""
    list_display = ('user', 'ad_title', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'ad__title')
    raw_id_fields = ('user', 'ad')

    def ad_title(self, obj):
        return obj.ad.title
    ad_title.short_description = 'Annonce'


@admin.register(AdView)
class AdViewAdmin(admin.ModelAdmin):
    """Administration des vues d'annonces"""
    list_display = ('ad_title', 'user', 'ip_address', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('ad__title', 'user__username', 'ip_address')
    raw_id_fields = ('ad', 'user')
    readonly_fields = ('created_at',)

    def ad_title(self, obj):
        return obj.ad.title
    ad_title.short_description = 'Annonce'


@admin.register(AdReport)
class AdReportAdmin(admin.ModelAdmin):
    """Administration des signalements"""
    list_display = (
        'ad_title', 'reporter', 'reason', 'is_resolved',
        'resolved_by', 'created_at'
    )
    list_filter = ('reason', 'is_resolved', 'created_at')
    search_fields = ('ad__title', 'reporter__username', 'description')
    raw_id_fields = ('ad', 'reporter', 'resolved_by')
    readonly_fields = ('created_at',)

    actions = ['resolve_reports']

    def ad_title(self, obj):
        return obj.ad.title
    ad_title.short_description = 'Annonce'

    def resolve_reports(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            is_resolved=True,
            resolved_by=request.user,
            resolved_at=timezone.now()
        )
        self.message_user(request, f'{updated} signalement(s) résolu(s).')
    resolve_reports.short_description = 'Marquer comme résolu'


# Personnalisation de l'interface d'administration
admin.site.site_header = "Administration Emunie"
admin.site.site_title = "Emunie Admin"
admin.site.index_title = "Tableau de bord administrateur"