from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, UserRating, Conversation, Message, EmailVerification, PhoneVerification

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Administration des utilisateurs personnalisés"""
    list_display = (
        'username', 'email', 'phone_number', 'full_name', 'location',
        'email_verified', 'phone_verified', 'total_ads', 'average_rating_display',
        'is_active', 'date_joined'
    )
    list_filter = (
        'is_active', 'is_staff', 'email_verified', 'phone_verified',
        'two_factor_enabled', 'date_joined', 'location'
    )
    search_fields = ('username', 'email', 'phone_number', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'last_login', 'total_ads', 'total_views', 'total_messages')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informations supplémentaires', {
            'fields': (
                'phone_number', 'avatar', 'birth_date', 'location', 'bio',
                'facebook_id', 'google_id'
            )
        }),
        ('Vérifications', {
            'fields': (
                'email_verified', 'phone_verified', 'two_factor_enabled',
                'notifications_enabled', 'whatsapp_notifications'
            )
        }),
        ('Statistiques', {
            'fields': ('total_ads', 'total_views', 'total_messages'),
            'classes': ('collapse',)
        }),
    )
    
    def full_name(self, obj):
        return obj.full_name or '-'
    full_name.short_description = 'Nom complet'
    
    def average_rating_display(self, obj):
        rating = obj.average_rating
        if rating:
            stars = '⭐' * int(rating)
            return f"{stars} ({rating:.1f})"
        return 'Aucune note'
    average_rating_display.short_description = 'Note moyenne'

@admin.register(UserRating)
class UserRatingAdmin(admin.ModelAdmin):
    """Administration des évaluations utilisateur"""
    list_display = ('rater', 'rated_user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('rater__username', 'rated_user__username')
    raw_id_fields = ('rater', 'rated_user')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('rater', 'rated_user')

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """Administration des conversations"""
    list_display = ('id', 'participants_display', 'created_at', 'updated_at', 'message_count')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('participants__username',)
    filter_horizontal = ('participants',)
    
    def participants_display(self, obj):
        return ', '.join([p.username for p in obj.participants.all()])
    participants_display.short_description = 'Participants'
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Nb messages'

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Administration des messages"""
    list_display = ('id', 'conversation', 'sender', 'content_preview', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__username', 'content')
    raw_id_fields = ('conversation', 'sender')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Aperçu du contenu'

@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    """Administration des vérifications d'email"""
    list_display = ('user', 'token', 'created_at', 'expires_at', 'is_used')
    list_filter = ('is_used', 'created_at', 'expires_at')
    search_fields = ('user__username', 'user__email')
    raw_id_fields = ('user',)

@admin.register(PhoneVerification)
class PhoneVerificationAdmin(admin.ModelAdmin):
    """Administration des vérifications de téléphone"""
    list_display = ('user', 'code', 'created_at', 'expires_at', 'is_used')
    list_filter = ('is_used', 'created_at', 'expires_at')
    search_fields = ('user__username', 'user__phone_number')
    raw_id_fields = ('user',)