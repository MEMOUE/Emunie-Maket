from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from mptt.admin import MPTTModelAdmin
from .models import (
    Category, Location, Ad, AdImage, AdVideo, AdAttribute,
    AdAttributeChoice, AdAttributeValue, Favorite, AdView, AdReport
)

@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    """Administration des catégories"""
    list_display = ('name', 'slug', 'parent', 'icon', 'ads_count', 'is_active', 'order')
    list_filter = ('is_active', 'parent')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active', 'order')
    
    def ads_count(self, obj):
        return obj.ads.filter(status='active').count()
    ads_count.short_description = 'Annonces actives'

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Administration des localisations"""
    list_display = ('name', 'parent', 'latitude', 'longitude', 'ads_count', 'is_active')
    list_filter = ('is_active', 'parent')
    search_fields = ('name',)
    list_editable = ('is_active',)
    
    def ads_count(self, obj):
        return obj.ads.filter(status='active').count()
    ads_count.short_description = 'Annonces actives'

class AdImageInline(admin.TabularInline):
    """Inline pour les images d'annonces"""
    model = AdImage
    extra = 0
    fields = ('image', 'caption', 'order', 'is_primary')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.image.url)
        return 'Aucune image'
    image_preview.short_description = 'Aperçu'

class AdVideoInline(admin.TabularInline):
    """Inline pour les vidéos d'annonces"""
    model = AdVideo
    extra = 0
    fields = ('video', 'thumbnail', 'caption', 'duration')

class AdAttributeValueInline(admin.TabularInline):
    """Inline pour les valeurs d'attributs"""
    model = AdAttributeValue
    extra = 0
    fields = ('attribute', 'value')

@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    """Administration des annonces"""
    list_display = (
        'title', 'user', 'category', 'location', 'price', 'status',
        'is_featured', 'is_urgent', 'views_count', 'favorites_count',
        'created_at', 'expires_at'
    )
    list_filter = (
        'status', 'ad_type', 'is_featured', 'is_urgent', 'is_negotiable',
        'category', 'location', 'created_at', 'is_moderated'
    )
    search_fields = ('title', 'description', 'user__username')
    readonly_fields = (
        'id', 'slug', 'views_count', 'favorites_count', 'created_at',
        'updated_at', 'published_at'
    )
    raw_id_fields = ('user', 'moderated_by')
    list_editable = ('is_featured', 'is_urgent')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Informations de base', {
            'fields': (
                'title', 'slug', 'description', 'user', 'category', 'location'
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
        ('Contact', {
            'fields': ('contact_phone', 'contact_email', 'whatsapp_number'),
            'classes': ('collapse',)
        }),
        ('État et visibilité', {
            'fields': (
                'status', 'is_featured', 'is_urgent', 'expires_at'
            )
        }),
        ('Statistiques', {
            'fields': ('views_count', 'favorites_count', 'created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
        ('Modération', {
            'fields': (
                'is_moderated', 'moderated_at', 'moderated_by', 'rejection_reason'
            ),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [AdImageInline, AdVideoInline, AdAttributeValueInline]
    
    actions = ['approve_ads', 'reject_ads', 'feature_ads', 'unfeature_ads']
    
    def approve_ads(self, request, queryset):
        updated = queryset.update(
            status='active',
            is_moderated=True,
            moderated_by=request.user,
            moderated_at=timezone.now()
        )
        self.message_user(request, f'{updated} annonce(s) approuvée(s).')
    approve_ads.short_description = 'Approuver les annonces sélectionnées'
    
    def reject_ads(self, request, queryset):
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

@admin.register(AdVideo)
class AdVideoAdmin(admin.ModelAdmin):
    """Administration des vidéos d'annonces"""
    list_display = ('ad_title', 'video_preview', 'caption', 'duration', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('ad__title', 'caption')
    raw_id_fields = ('ad',)
    
    def ad_title(self, obj):
        return obj.ad.title
    ad_title.short_description = 'Annonce'
    
    def video_preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.thumbnail.url)
        return 'Aucune miniature'
    video_preview.short_description = 'Aperçu'

class AdAttributeChoiceInline(admin.TabularInline):
    """Inline pour les choix d'attributs"""
    model = AdAttributeChoice
    extra = 0
    fields = ('value', 'order')

@admin.register(AdAttribute)
class AdAttributeAdmin(admin.ModelAdmin):
    """Administration des attributs d'annonces"""
    list_display = ('name', 'slug', 'input_type', 'is_required', 'is_filterable', 'order')
    list_filter = ('input_type', 'is_required', 'is_filterable')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('categories',)
    list_editable = ('is_required', 'is_filterable', 'order')
    
    inlines = [AdAttributeChoiceInline]

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