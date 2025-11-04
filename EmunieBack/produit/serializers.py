from rest_framework import serializers
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.contrib.auth import get_user_model
from .models import (
    Ad, AdImage, Advertisement, Favorite, AdReport,
    CATEGORY_CHOICES, CITY_CHOICES
)

User = get_user_model()

class AdImageSerializer(serializers.ModelSerializer):
    """Serializer pour les images d'annonces"""
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = AdImage
        fields = ('id', 'image', 'image_url', 'caption', 'order', 'is_primary', 'created_at')
        read_only_fields = ('id', 'created_at')

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

    def validate_image(self, value):
        """Valider la taille de l'image"""
        if value.size > 5 * 1024 * 1024:  # 5Mo
            raise DRFValidationError("La taille de l'image ne doit pas dépasser 5Mo.")

        # Vérifier l'extension
        allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
        ext = value.name.split('.')[-1].lower()
        if ext not in allowed_extensions:
            raise DRFValidationError(
                f"Format non supporté. Utilisez: {', '.join(allowed_extensions)}"
            )

        return value


class AdListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des annonces"""
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_avatar = serializers.ImageField(source='user.avatar', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    city_display = serializers.CharField(source='get_city_display', read_only=True)
    primary_image = serializers.SerializerMethodField()
    images = AdImageSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    time_since_published = serializers.SerializerMethodField()
    images_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Ad
        fields = (
            'id', 'title', 'slug', 'price', 'currency', 'is_negotiable',
            'user_name', 'user_avatar', 'category', 'category_display',
            'city', 'city_display', 'primary_image', 'images', 'images_count',
            'is_favorited', 'is_featured', 'is_urgent', 'views_count',
            'favorites_count', 'status', 'created_at', 'time_since_published',
            'expires_at'
        )

    def get_primary_image(self, obj):
        """Obtenir l'URL de l'image primaire"""
        request = self.context.get('request')
        primary_image = obj.images.filter(is_primary=True).first()

        if primary_image and primary_image.image:
            if request:
                return request.build_absolute_uri(primary_image.image.url)
            return primary_image.image.url

        # Sinon prendre la première image
        first_image = obj.images.first()
        if first_image and first_image.image:
            if request:
                return request.build_absolute_uri(first_image.image.url)
            return first_image.image.url

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
    is_favorited = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    related_ads = serializers.SerializerMethodField()
    images_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Ad
        fields = (
            'id', 'title', 'slug', 'description', 'price', 'currency', 'is_negotiable',
            'ad_type', 'user', 'category', 'category_display', 'city', 'city_display',
            'address', 'latitude', 'longitude', 'contact_email',
            'whatsapp_number', 'images', 'images_count', 'is_favorited', 'is_owner',
            'is_featured', 'is_urgent', 'views_count', 'favorites_count', 'status',
            'created_at', 'updated_at', 'published_at', 'expires_at', 'related_ads'
        )

    def get_user(self, obj):
        request = self.context.get('request')
        avatar_url = None
        if obj.user.avatar and hasattr(obj.user.avatar, 'url'):
            if request:
                avatar_url = request.build_absolute_uri(obj.user.avatar.url)
            else:
                avatar_url = obj.user.avatar.url

        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'full_name': obj.user.full_name,
            'avatar': avatar_url,
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
    images = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        write_only=True,
        max_length=3,
        min_length=1
    )

    class Meta:
        model = Ad
        fields = (
            'title', 'description', 'price', 'currency', 'is_negotiable',
            'ad_type', 'status', 'category', 'city', 'address', 'latitude',
            'longitude', 'contact_email', 'whatsapp_number', 'is_urgent',
            'expires_at', 'images'
        )
        # ✅ Ajout du champ 'status'

        # Champs optionnels avec valeurs par défaut
        extra_kwargs = {
            'status': {'required': False},  # Optionnel en création
            'ad_type': {'required': False, 'default': 'sell'},
        }

    def validate_images(self, value):
        """Valider les images"""
        if len(value) < 1:
            raise DRFValidationError("Vous devez ajouter au moins 1 image.")
        if len(value) > 3:
            raise DRFValidationError("Vous ne pouvez ajouter que 3 images maximum.")

        # Vérifier la taille de chaque image
        for image in value:
            if image.size > 5 * 1024 * 1024:  # 5Mo
                raise DRFValidationError(
                    f"L'image {image.name} dépasse la taille maximale de 5Mo."
                )

        return value

    def validate(self, attrs):
        request = self.context.get('request')

        # Vérifier si l'utilisateur peut créer une annonce (création uniquement)
        if self.instance is None and request:
            if not request.user.can_create_ad:
                raise DRFValidationError(
                    f"Limite d'annonces atteinte. Vous avez déjà {request.user.ads.filter(status='active').count()} annonces actives. "
                    f"Passez au compte premium pour publier des annonces illimitées."
                )

        return attrs

    def create(self, validated_data):
        from django.utils import timezone
        from django.utils.text import slugify
        from datetime import timedelta

        # Extraire les images
        images_data = validated_data.pop('images', [])

        # Calculer la date d'expiration (30 jours par défaut)
        if 'expires_at' not in validated_data or not validated_data['expires_at']:
            validated_data['expires_at'] = timezone.now() + timedelta(days=30)

        # Générer un slug unique
        title = validated_data['title']
        slug = slugify(title)
        counter = 1
        while Ad.objects.filter(slug=slug).exists():
            slug = f"{slugify(title)}-{counter}"
            counter += 1

        validated_data['slug'] = slug

        # ✅ Définir le statut par défaut en création si non fourni
        if 'status' not in validated_data:
            validated_data['status'] = 'active'

        # Créer l'annonce
        ad = Ad.objects.create(**validated_data)

        # Créer les images
        for index, image_file in enumerate(images_data):
            AdImage.objects.create(
                ad=ad,
                image=image_file,
                order=index,
                is_primary=(index == 0)  # La première image est primaire
            )

        return ad

    def update(self, instance, validated_data):
        """
        Mise à jour de l'annonce avec gestion sécurisée des images
        """
        from django.db import transaction

        # Extraire les images si présentes
        images_data = validated_data.pop('images', None)

        # ✅ Mettre à jour TOUS les champs, y compris le statut
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # Gérer les images si fournies
        if images_data is not None and len(images_data) > 0:
            try:
                with transaction.atomic():
                    # 1. Supprimer d'abord TOUTES les anciennes images
                    old_images = list(instance.images.all())

                    # Supprimer les fichiers physiques
                    for old_img in old_images:
                        try:
                            if old_img.image:
                                old_img.image.delete(save=False)
                        except Exception as e:
                            print(f"Avertissement: impossible de supprimer le fichier: {e}")

                    # Supprimer tous les enregistrements via queryset
                    AdImage.objects.filter(ad=instance).delete()

                    # 2. Créer les nouvelles images
                    for index, image_file in enumerate(images_data):
                        AdImage.objects.create(
                            ad=instance,
                            image=image_file,
                            order=index,
                            is_primary=(index == 0)
                        )

            except Exception as e:
                raise DRFValidationError({
                    'images': f"Erreur lors de la mise à jour des images: {str(e)}"
                })

        return instance


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
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Advertisement
        fields = (
            'id', 'user', 'user_name', 'title', 'link', 'image', 'image_url',
            'duration_hours', 'duration_days', 'price_per_day', 'total_price',
            'start_date', 'end_date', 'is_active', 'is_approved',
            'impressions', 'clicks', 'ctr', 'is_running', 'created_at'
        )
        read_only_fields = ('id', 'user', 'total_price', 'impressions', 'clicks', 'created_at')

    def get_duration_days(self, obj):
        return obj.duration_hours / 24

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

    def validate_image(self, value):
        """Valider la taille de l'affiche (max 2Mo)"""
        if value and value.size > 2 * 1024 * 1024:
            raise DRFValidationError("La taille de l'affiche ne doit pas dépasser 2Mo.")
        return value

    def validate_duration_hours(self, value):
        """S'assurer que la durée est un multiple de 24h"""
        if value % 24 != 0:
            raise DRFValidationError("La durée doit être un multiple de 24 heures (1 jour, 2 jours, etc.)")
        return value


class AdvertisementCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer une publicité"""

    class Meta:
        model = Advertisement
        fields = ('title', 'link', 'image', 'duration_hours', 'start_date')

    def validate_image(self, value):
        """Valider la taille de l'affiche (max 2Mo)"""
        if value and value.size > 2 * 1024 * 1024:
            raise DRFValidationError("La taille de l'affiche ne doit pas dépasser 2Mo.")
        return value

    def validate_duration_hours(self, value):
        """S'assurer que la durée est un multiple de 24h"""
        if value % 24 != 0:
            raise DRFValidationError("La durée doit être un multiple de 24 heures.")
        if value < 24:
            raise DRFValidationError("La durée minimale est de 24 heures.")
        return value

    def create(self, validated_data):
        from django.utils import timezone
        from datetime import timedelta

        # Calculer la date de fin
        start_date = validated_data['start_date']
        duration_hours = validated_data.get('duration_hours')
        if duration_hours is None:
            raise DRFValidationError("Le champ 'duration_hours' est requis.")

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