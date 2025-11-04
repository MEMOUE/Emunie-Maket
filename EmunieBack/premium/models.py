from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class PremiumPlan(models.Model):
    """Plans d'abonnement Premium"""
    PLAN_TYPES = [
        ('basic', 'Premium Basic - 100 annonces'),
        ('unlimited', 'Premium Illimité')
    ]

    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='XOF')
    max_ads = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Nombre maximum d\'annonces (null = illimité)'
    )
    duration_days = models.PositiveIntegerField(default=30)
    description = models.TextField(blank=True)
    features = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'price']
        verbose_name = 'Plan Premium'
        verbose_name_plural = 'Plans Premium'

    def __str__(self):
        return f"{self.name} - {self.price} {self.currency}"


class PremiumSubscription(models.Model):
    """Abonnements Premium des utilisateurs"""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('active', 'Actif'),
        ('expired', 'Expiré'),
        ('cancelled', 'Annulé')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='premium_subscriptions')
    plan = models.ForeignKey(PremiumPlan, on_delete=models.PROTECT, related_name='subscriptions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Dates
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Paiement
    payment_method = models.CharField(max_length=50, blank=True)
    transaction_reference = models.CharField(max_length=100, blank=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Abonnement Premium'
        verbose_name_plural = 'Abonnements Premium'

    def __str__(self):
        return f"{self.user.username} - {self.plan.name} ({self.status})"

    def activate(self):
        """Activer l'abonnement"""
        self.status = 'active'
        self.start_date = timezone.now()
        self.end_date = self.start_date + timedelta(days=self.plan.duration_days)

        # Mettre à jour l'utilisateur
        self.user.is_premium = True
        self.user.premium_start_date = self.start_date
        self.user.premium_end_date = self.end_date
        self.user.save()

        self.save()

    @property
    def is_active(self):
        """Vérifier si l'abonnement est actif"""
        return (
                self.status == 'active' and
                self.end_date and
                self.end_date > timezone.now()
        )

    @property
    def days_remaining(self):
        """Jours restants avant expiration"""
        if self.end_date:
            delta = self.end_date - timezone.now()
            return max(0, delta.days)
        return 0