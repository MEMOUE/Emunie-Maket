from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Ad, AdImage, AdVideo, Advertisement, Favorite, AdReport,
    CATEGORY_CHOICES, CITY_CHOICES
)

User = get_user_model()

class AdImageSerializer(serializers.ModelSerializer):
    """Serializer pour les images d'annonces"""
    class Meta:
        model = AdImage
        fields = ('id', 'image', 'caption', 'order', 'is_primary', 'created_at')
        read_only_fields = ('id', 'created_at')

class AdVideoSerializer(serializers.ModelSerializer):
    """Serializer pour les vidéos d'annonces"""
    class Meta:
        model = AdVideo
        fields = ('id', 'video', 'thumbnail', 'caption', 'duration', 'created_at')
        read_only_fields = ('id', 'created_at')

class AdListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des annonces"""
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_avatar = serializers.ImageField(source='user.avatar', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    city_display = serializers.CharField(source='get_city_display', read_only=True)
    primary_image = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    time_since_published = serializers.SerializerMethodField()

    class Meta:
        model = Ad
        fields = (
            'id', 'title', 'slug', 'price', 'currency', 'is_negotiable',
            'user_name', 'user_avatar', 'category', 'category_display',
            'city', 'city_display', 'primary_image', 'is_favorited',
            'is_featured', 'is_urgent', 'views_count', 'favorites_count',
            'status', 'created_at', 'time_since_published', 'expires_at'
        )

    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return self.context['request'].build_absolute_uri(primary_image.image.url)
        first_image = obj.images.first()
        if first_image:
            return self.context['request'].build_absolute_uri(first_image.image.url)
        return None

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorited_by.filter(user=request.user).exists()
        return False

    def get_time_since_published(self, obj):
        if obj.published_at:
            from django.utils import timezone
            from django.utils.timesince import timesince
            return timesince(obj.published_at, timezone.now())
        return None

class AdDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour une annonce"""
    user = serializers.SerializerMethodField()
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    city_display = serializers.CharField(source='get_city_display', read_only=True)
    images = AdImageSerializer(many=True, read_only=True)
    videos = AdVideoSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    related_ads = serializers.SerializerMethodField()

    class Meta:
        model = Ad
        fields = (
            'id', 'title', 'slug', 'description', 'price', 'currency', 'is_negotiable',
            'ad_type', 'user', 'category', 'category_display', 'city', 'city_display',
            'address', 'latitude', 'longitude', 'contact_phone', 'contact_email',
            'whatsapp_number', 'images', 'videos', 'is_favorited', 'is_owner',
            'is_featured', 'is_urgent', 'views_count', 'favorites_count', 'status',
            'created_at', 'updated_at', 'published_at', 'expires_at', 'related_ads'
        )

    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'full_name': obj.user.full_name,
            'avatar': self.context['request'].build_absolute_uri(obj.user.avatar.url) if obj.user.avatar else None,
            'average_rating': obj.user.average_rating,
            'total_ads': obj.user.total_ads,
            'location': obj.user.location,
            'is_premium': obj.user.is_premium_active,
            'created_at': obj.user.created_at
        }

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorited_by.filter(user=request.user).exists()
        return False

    def get_is_owner(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.user == request.user
        return False

    def get_related_ads(self, obj):
        related = Ad.objects.filter(
            category=obj.category,
            status='active'
        ).exclude(id=obj.id)[:4]

        return AdListSerializer(related, many=True, context=self.context).data

class AdCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour créer/modifier une annonce"""

    class Meta:
        model = Ad
        fields = (
            'title', 'description', 'price', 'currency', 'is_negotiable',
            'ad_type', 'category', 'city', 'address', 'latitude', 'longitude',
            'contact_phone', 'contact_email', 'whatsapp_number', 'is_urgent',
            'expires_at'
        )

    def validate(self, attrs):
        request = self.context.get('request')

        # Vérifier si l'utilisateur peut créer une annonce
        if self.instance is None:  # Création uniquement
            if not request.user.can_create_ad:
                raise serializers.ValidationError(
                    f"Limite d'annonces atteinte. Vous avez déjà {request.user.ads.filter(status='active').count()} annonces actives. "
                    f"Passez au compte premium pour publier des annonces illimitées."
                )

        return attrs

    def create(self, validated_data):
        from django.utils import timezone
        from datetime import timedelta

        # Calculer la date d'expiration (30 jours par défaut)
        if 'expires_at' not in validated_data or not validated_data['expires_at']:
            validated_data['expires_at'] = timezone.now() + timedelta(days=30)

        # Générer un slug unique
        from django.utils.text import slugify
        title = validated_data['title']
        slug = slugify(title)
        counter = 1
        while Ad.objects.filter(slug=slug).exists():
            slug = f"{slugify(title)}-{counter}"
            counter += 1

        validated_data['slug'] = slug
        ad = Ad.objects.create(**validated_data)

        return ad

class FavoriteSerializer(serializers.ModelSerializer):
    """Serializer pour les favoris"""
    ad = AdListSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ('id', 'ad', 'created_at')
        read_only_fields = ('id', 'created_at')

class AdReportSerializer(serializers.ModelSerializer):
    """Serializer pour signaler une annonce"""
    reporter_name = serializers.CharField(source='reporter.full_name', read_only=True)

    class Meta:
        model = AdReport
        fields = ('id', 'reason', 'description', 'reporter_name', 'created_at', 'is_resolved')
        read_only_fields = ('id', 'reporter_name', 'created_at', 'is_resolved')

class AdvertisementSerializer(serializers.ModelSerializer):
    """Serializer pour les publicités payantes"""
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    duration_days = serializers.SerializerMethodField()
    is_running = serializers.ReadOnlyField()
    ctr = serializers.ReadOnlyField()

    class Meta:
        model = Advertisement
        fields = (
            'id', 'user', 'user_name', 'title', 'link', 'image',
            'duration_hours', 'duration_days', 'price_per_day', 'total_price',
            'start_date', 'end_date', 'is_active', 'is_approved',
            'impressions', 'clicks', 'ctr', 'is_running', 'created_at'
        )
        read_only_fields = ('id', 'user', 'total_price', 'impressions', 'clicks', 'created_at')

    def get_duration_days(self, obj):
        return obj.duration_hours / 24

    def validate_image(self, value):
        """Valider la taille de l'affiche (max 2Mo)"""
        if value and value.size > 2 * 1024 * 1024:
            raise serializers.ValidationError("La taille de l'affiche ne doit pas dépasser 2Mo.")
        return value

    def validate_duration_hours(self, value):
        """S'assurer que la durée est un multiple de 24h"""
        if value % 24 != 0:
            raise serializers.ValidationError("La durée doit être un multiple de 24 heures (1 jour, 2 jours, etc.)")
        return value

class AdvertisementCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer une publicité"""

    class Meta:
        model = Advertisement
        fields = ('title', 'link', 'image', 'duration_hours', 'start_date')

    def validate_image(self, value):
        """Valider la taille de l'affiche (max 2Mo)"""
        if value and value.size > 2 * 1024 * 1024:
            raise serializers.ValidationError("La taille de l'affiche ne doit pas dépasser 2Mo.")
        return value

    def validate_duration_hours(self, value):
        """S'assurer que la durée est un multiple de 24h"""
        if value % 24 != 0:
            raise serializers.ValidationError("La durée doit être un multiple de 24 heures.")
        if value < 24:
            raise serializers.ValidationError("La durée minimale est de 24 heures.")
        return value

    def create(self, validated_data):
        from django.utils import timezone
        from datetime import timedelta

        # Calculer la date de fin
        start_date = validated_data['start_date']
        duration_hours = validated_data['duration_hours']
        validated_data['end_date'] = start_date + timedelta(hours=duration_hours)

        # Le prix sera calculé automatiquement dans le modèle
        advertisement = Advertisement.objects.create(**validated_data)

        return advertisement

class CategoryChoiceSerializer(serializers.Serializer):
    """Serializer pour les choix de catégories"""
    value = serializers.CharField()
    label = serializers.CharField()

class CityChoiceSerializer(serializers.Serializer):
    """Serializer pour les choix de villes"""
    value = serializers.CharField()
    label = serializers.CharField()