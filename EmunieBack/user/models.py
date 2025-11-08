from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.core.exceptions import ValidationError


def validate_logo_size(file):
    """Valider que la taille du logo ne dépasse pas 1Mo"""
    max_size_mb = 1
    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f'La taille du fichier ne doit pas dépasser {max_size_mb}Mo')


class CustomUser(AbstractUser):
    """Modèle utilisateur personnalisé"""
    # Téléphone optionnel
    phone_number = PhoneNumberField(unique=True, null=True, blank=True)

    # Logo/Avatar optionnel avec validation de taille (max 1Mo)
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        validators=[
            validate_logo_size,
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])
        ],
        help_text='Taille maximale: 1Mo. Formats acceptés: jpg, jpeg, png, gif'
    )

    birth_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)
    bio = models.TextField(max_length=500, blank=True)

    # Réseaux sociaux
    facebook_id = models.CharField(max_length=100, blank=True)
    google_id = models.CharField(max_length=100, blank=True)

    # Paramètres de compte
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    notifications_enabled = models.BooleanField(default=True)
    whatsapp_notifications = models.BooleanField(default=False)

    # Compte premium
    is_premium = models.BooleanField(default=False)
    premium_start_date = models.DateTimeField(null=True, blank=True)
    premium_end_date = models.DateTimeField(null=True, blank=True)

    # Statistiques
    total_ads = models.PositiveIntegerField(default=0)
    total_views = models.PositiveIntegerField(default=0)
    total_messages = models.PositiveIntegerField(default=0)

    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Limite d'annonces
    MAX_FREE_ADS = 5

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username

    @property
    def average_rating(self):
        ratings = self.received_ratings.all()
        if ratings:
            return ratings.aggregate(models.Avg('rating'))['rating__avg']
        return 0

    @property
    def can_create_ad(self):
        """Vérifier si l'utilisateur peut créer une annonce"""
        if self.is_premium:
            return True
        active_ads_count = self.ads.filter(status='active').count()
        return active_ads_count < self.MAX_FREE_ADS

    @property
    def remaining_ads(self):
        """Nombre d'annonces restantes pour les utilisateurs gratuits

        Retourne:
            int: Nombre d'annonces restantes (ou -1 pour illimité si premium)
        """
        if self.is_premium:
            return -1  # -1 signifie illimité pour les utilisateurs premium
        active_ads_count = self.ads.filter(status='active').count()
        return max(0, self.MAX_FREE_ADS - active_ads_count)

    @property
    def is_premium_active(self):
        """Vérifier si le compte premium est actif"""
        from django.utils import timezone
        if not self.is_premium:
            return False
        if self.premium_end_date and self.premium_end_date < timezone.now():
            return False
        return True


class UserRating(models.Model):
    """Système de notation entre utilisateurs"""
    rater = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='given_ratings')
    rated_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_ratings')
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('rater', 'rated_user')

    def __str__(self):
        return f"{self.rater.username} rated {self.rated_user.username}: {self.rating}/5"


class Conversation(models.Model):
    """Conversations entre utilisateurs"""
    participants = models.ManyToManyField(CustomUser, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Conversation {self.id}"

    @property
    def last_message(self):
        return self.messages.order_by('-created_at').first()


class Message(models.Model):
    """Messages dans les conversations"""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    image = models.ImageField(upload_to='messages/', null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message from {self.sender.username} at {self.created_at}"


class EmailVerification(models.Model):
    """Vérification d'email"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)


class PhoneVerification(models.Model):
    """Vérification de téléphone"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)