from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Category, Location, Ad, AdImage, AdVideo, AdAttribute, 
    AdAttributeValue, AdAttributeChoice, Favorite, AdReport
)

User = get_user_model()

class CategorySerializer(serializers.ModelSerializer):
    """Serializer pour les catégories"""
    children = serializers.SerializerMethodField()
    ads_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'icon', 'parent', 'children', 'ads_count', 'order')
    
    def get_children(self, obj):
        if obj.children.exists():
            return CategorySerializer(obj.children.filter(is_active=True), many=True).data
        return []
    
    def get_ads_count(self, obj):
        return obj.ads.filter(status='active').count()

class LocationSerializer(serializers.ModelSerializer):
    """Serializer pour les localisations"""
    ads_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Location
        fields = ('id', 'name', 'parent', 'latitude', 'longitude', 'ads_count')
    
    def get_ads_count(self, obj):
        return obj.ads.filter(status='active').count()

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

class AdAttributeChoiceSerializer(serializers.ModelSerializer):
    """Serializer pour les choix d'attributs"""
    class Meta:
        model = AdAttributeChoice
        fields = ('id', 'value', 'order')

class AdAttributeSerializer(serializers.ModelSerializer):
    """Serializer pour les attributs d'annonces"""
    choices = AdAttributeChoiceSerializer(many=True, read_only=True)
    
    class Meta:
        model = AdAttribute
        fields = ('id', 'name', 'slug', 'input_type', 'is_required', 'is_filterable', 'choices')

class AdAttributeSerializer(serializers.ModelSerializer):
    """Serializer pour les attributs d'annonces"""
    choices = AdAttributeChoiceSerializer(many=True, read_only=True)
    
    class Meta:
        model = AdAttribute
        fields = ('id', 'name', 'slug', 'input_type', 'is_required', 'is_filterable', 'choices')

class AdAttributeValueSerializer(serializers.ModelSerializer):
    """Serializer pour les valeurs d'attributs"""
    attribute_name = serializers.CharField(source='attribute.name', read_only=True)
    attribute_slug = serializers.CharField(source='attribute.slug', read_only=True)
    
    class Meta:
        model = AdAttributeValue
        fields = ('id', 'attribute', 'attribute_name', 'attribute_slug', 'value')

class AdListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des annonces"""
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_avatar = serializers.ImageField(source='user.avatar', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    time_since_published = serializers.SerializerMethodField()
    
    class Meta:
        model = Ad
        fields = (
            'id', 'title', 'slug', 'price', 'currency', 'is_negotiable',
            'user_name', 'user_avatar', 'category_name', 'location_name',
            'primary_image', 'is_favorited', 'is_featured', 'is_urgent',
            'views_count', 'favorites_count', 'status', 'created_at',
            'time_since_published', 'expires_at'
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
    category = CategorySerializer(read_only=True)
    location = LocationSerializer(read_only=True)
    images = AdImageSerializer(many=True, read_only=True)
    videos = AdVideoSerializer(many=True, read_only=True)
    attribute_values = AdAttributeValueSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    related_ads = serializers.SerializerMethodField()
    
    class Meta:
        model = Ad
        fields = (
            'id', 'title', 'slug', 'description', 'price', 'currency', 'is_negotiable',
            'ad_type', 'user', 'category', 'location', 'address', 'latitude', 'longitude',
            'contact_phone', 'contact_email', 'whatsapp_number', 'images', 'videos',
            'attribute_values', 'is_favorited', 'is_owner', 'is_featured', 'is_urgent',
            'views_count', 'favorites_count', 'status', 'created_at', 'updated_at',
            'published_at', 'expires_at', 'related_ads'
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
    attribute_values = serializers.JSONField(required=False, allow_null=True)
    
    class Meta:
        model = Ad
        fields = (
            'title', 'description', 'price', 'currency', 'is_negotiable',
            'ad_type', 'category', 'location', 'address', 'latitude', 'longitude',
            'contact_phone', 'contact_email', 'whatsapp_number', 'is_urgent',
            'expires_at', 'attribute_values'
        )
    
    def create(self, validated_data):
        attribute_values_data = validated_data.pop('attribute_values', {})
        ad = Ad.objects.create(**validated_data)
        
        # Créer les valeurs d'attributs
        self._create_attribute_values(ad, attribute_values_data)
        
        return ad
    
    def update(self, instance, validated_data):
        attribute_values_data = validated_data.pop('attribute_values', {})
        
        # Mettre à jour l'annonce
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Mettre à jour les valeurs d'attributs
        instance.attribute_values.all().delete()
        self._create_attribute_values(instance, attribute_values_data)
        
        return instance
    
    def _create_attribute_values(self, ad, attribute_values_data):
        if not attribute_values_data:
            return
        
        for attribute_id, value in attribute_values_data.items():
            try:
                attribute = AdAttribute.objects.get(id=attribute_id)
                AdAttributeValue.objects.create(
                    ad=ad,
                    attribute=attribute,
                    value=str(value)
                )
            except AdAttribute.DoesNotExist:
                continue

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

class AdStatsSerializer(serializers.Serializer):
    """Serializer pour les statistiques d'une annonce"""
    views_count = serializers.IntegerField()
    favorites_count = serializers.IntegerField()
    contacts_count = serializers.IntegerField()
    views_today = serializers.IntegerField()
    views_this_week = serializers.IntegerField()
    views_this_month = serializers.IntegerField()
    top_referrers = serializers.ListField()
    location_stats = serializers.DictField()
    device_stats = serializers.DictField()