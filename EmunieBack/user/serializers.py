from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import UserRating, Conversation, Message

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer pour l'inscription - téléphone et avatar optionnels"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone_number', 'avatar'
        )
        extra_kwargs = {
            'phone_number': {'required': False},
            'avatar': {'required': False}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return attrs

    def validate_avatar(self, value):
        """Valider la taille du logo (max 1Mo)"""
        if value and value.size > 1 * 1024 * 1024:
            raise serializers.ValidationError("La taille du logo ne doit pas dépasser 1Mo.")
        return value

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer pour le profil utilisateur"""
    full_name = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()
    can_create_ad = serializers.ReadOnlyField()
    remaining_ads = serializers.ReadOnlyField()
    is_premium_active = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'phone_number', 'first_name', 'last_name',
            'full_name', 'avatar', 'birth_date', 'location', 'bio', 'average_rating',
            'total_ads', 'total_views', 'email_verified', 'phone_verified',
            'is_premium', 'is_premium_active', 'premium_end_date',
            'can_create_ad', 'remaining_ads', 'created_at'
        )
        read_only_fields = (
            'id', 'username', 'total_ads', 'total_views', 'created_at',
            'email_verified', 'phone_verified', 'is_premium', 'premium_end_date'
        )

    def validate_avatar(self, value):
        """Valider la taille du logo (max 1Mo)"""
        if value and value.size > 1 * 1024 * 1024:
            raise serializers.ValidationError("La taille du logo ne doit pas dépasser 1Mo.")
        return value

class UserListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour la liste des utilisateurs"""
    full_name = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()
    is_premium_active = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'full_name', 'avatar', 'location',
            'average_rating', 'total_ads', 'is_premium_active', 'created_at'
        )

class UserRatingSerializer(serializers.ModelSerializer):
    """Serializer pour les évaluations"""
    rater_name = serializers.CharField(source='rater.full_name', read_only=True)

    class Meta:
        model = UserRating
        fields = ('id', 'rater', 'rater_name', 'rated_user', 'rating', 'comment', 'created_at')
        read_only_fields = ('id', 'rater', 'created_at')

class MessageSerializer(serializers.ModelSerializer):
    """Serializer pour les messages"""
    sender_name = serializers.CharField(source='sender.full_name', read_only=True)
    sender_avatar = serializers.ImageField(source='sender.avatar', read_only=True)

    class Meta:
        model = Message
        fields = ('id', 'sender', 'sender_name', 'sender_avatar', 'content', 'image',
                  'is_read', 'created_at')
        read_only_fields = ('id', 'sender', 'created_at')

class ConversationSerializer(serializers.ModelSerializer):
    """Serializer pour les conversations"""
    participants = UserListSerializer(many=True, read_only=True)
    last_message = MessageSerializer(read_only=True)
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ('id', 'participants', 'last_message', 'unread_count', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0

class PasswordChangeSerializer(serializers.Serializer):
    """Serializer pour changer le mot de passe"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Les nouveaux mots de passe ne correspondent pas.")
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Ancien mot de passe incorrect.")
        return value

class EmailVerificationSerializer(serializers.Serializer):
    """Serializer pour la vérification d'email"""
    email = serializers.EmailField()

class PhoneVerificationSerializer(serializers.Serializer):
    """Serializer pour la vérification de téléphone"""
    phone_number = serializers.CharField()
    code = serializers.CharField(max_length=6, required=False)


# Ajouter ces serializers dans EmunieBack/user/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer pour la demande de réinitialisation"""
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """Vérifier que l'email existe"""
        try:
            User.objects.get(email=value, is_active=True)
        except User.DoesNotExist:
            # Ne pas révéler si l'email existe ou non pour des raisons de sécurité
            # mais retourner une erreur générique
            pass
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer pour confirmer la réinitialisation"""
    token = serializers.CharField(required=True, max_length=100)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        """Vérifier que les mots de passe correspondent"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Les mots de passe ne correspondent pas.'
            })
        return attrs


class PasswordResetVerifyTokenSerializer(serializers.Serializer):
    """Serializer pour vérifier un token"""
    token = serializers.CharField(required=True, max_length=100)