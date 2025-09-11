from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import MinValueValidator, MaxValueValidator

class CustomUser(AbstractUser):
    """Modèle utilisateur personnalisé"""
    phone_number = PhoneNumberField(unique=True, null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
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
    
    # Statistiques
    total_ads = models.PositiveIntegerField(default=0)
    total_views = models.PositiveIntegerField(default=0)
    total_messages = models.PositiveIntegerField(default=0)
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.username

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def average_rating(self):
        ratings = self.received_ratings.all()
        if ratings:
            return ratings.aggregate(models.Avg('rating'))['rating__avg']
        return 0

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