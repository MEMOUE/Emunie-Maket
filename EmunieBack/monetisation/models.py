from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal

User = get_user_model()

class Package(models.Model):
    """Packages de services premium"""
    PACKAGE_TYPES = [
        ('boost', 'Boost d\'annonce'),
        ('featured', 'Mise en avant'),
        ('premium', 'Compte premium'),
        ('urgent', 'Marquage urgent'),
        ('refresh', 'Actualisation'),
        ('highlight', 'Surbrillance'),
    ]
    
    name = models.CharField(max_length=100)
    package_type = models.CharField(max_length=20, choices=PACKAGE_TYPES)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='XOF')
    duration_days = models.PositiveIntegerField()  # Durée en jours
    
    # Avantages du package
    boost_multiplier = models.DecimalField(max_digits=3, decimal_places=1, default=1.0)  # Multiplicateur de visibilité
    max_ads = models.PositiveIntegerField(null=True, blank=True)  # Nombre max d'annonces
    priority_support = models.BooleanField(default=False)
    featured_placement = models.BooleanField(default=False)
    unlimited_photos = models.BooleanField(default=False)
    video_upload = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['price']
    
    def __str__(self):
        return f"{self.name} - {self.price} {self.currency}"

class UserSubscription(models.Model):
    """Abonnements des utilisateurs"""
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('expired', 'Expiré'),
        ('cancelled', 'Annulé'),
        ('pending', 'En attente'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    auto_renew = models.BooleanField(default=False)
    
    # Compteurs d'utilisation
    ads_boosted = models.PositiveIntegerField(default=0)
    ads_featured = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.package.name}"
    
    @property
    def is_active(self):
        return (self.status == 'active' and 
                self.end_date > timezone.now())
    
    @property
    def days_remaining(self):
        if self.is_active:
            return (self.end_date - timezone.now()).days
        return 0

class AdBoost(models.Model):
    """Boost d'annonces individuelles"""
    BOOST_TYPES = [
        ('basic', 'Boost basique'),
        ('premium', 'Boost premium'),
        ('urgent', 'Mise en urgent'),
        ('featured', 'Mise en avant'),
        ('top', 'Haut de liste'),
    ]
    
    ad = models.ForeignKey('produit.Ad', on_delete=models.CASCADE, related_name='boosts')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ad_boosts')
    boost_type = models.CharField(max_length=20, choices=BOOST_TYPES)
    package = models.ForeignKey(Package, on_delete=models.CASCADE, null=True, blank=True)
    
    price_paid = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='XOF')
    
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    # Statistiques du boost
    views_before = models.PositiveIntegerField(default=0)
    views_after = models.PositiveIntegerField(default=0)
    contacts_before = models.PositiveIntegerField(default=0)
    contacts_after = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Boost {self.boost_type} for {self.ad.title}"
    
    @property
    def is_expired(self):
        return timezone.now() > self.end_date

class PaymentMethod(models.Model):
    """Méthodes de paiement disponibles"""
    PAYMENT_TYPES = [
        ('mobile_money', 'Mobile Money'),
        ('orange_money', 'Orange Money'),
        ('mtn_money', 'MTN Money'),
        ('moov_money', 'Moov Money'),
        ('wave', 'Wave'),
        ('bank_transfer', 'Virement bancaire'),
        ('cash', 'Espèces'),
        ('card', 'Carte bancaire'),
    ]
    
    name = models.CharField(max_length=50)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    provider = models.CharField(max_length=50, blank=True)
    logo = models.ImageField(upload_to='payment_methods/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    processing_fee = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Frais en %
    
    # Configuration API
    api_key = models.CharField(max_length=255, blank=True)
    secret_key = models.CharField(max_length=255, blank=True)
    webhook_url = models.URLField(blank=True)
    
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name

class Transaction(models.Model):
    """Transactions financières"""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En cours'),
        ('completed', 'Complétée'),
        ('failed', 'Échouée'),
        ('cancelled', 'Annulée'),
        ('refunded', 'Remboursée'),
    ]
    
    TRANSACTION_TYPES = [
        ('package_purchase', 'Achat de package'),
        ('ad_boost', 'Boost d\'annonce'),
        ('subscription', 'Abonnement'),
        ('refund', 'Remboursement'),
    ]
    
    # Identification
    reference = models.CharField(max_length=100, unique=True)
    external_reference = models.CharField(max_length=100, blank=True)  # Référence du provider
    
    # Relations
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    package = models.ForeignKey(Package, on_delete=models.CASCADE, null=True, blank=True)
    subscription = models.ForeignKey(UserSubscription, on_delete=models.CASCADE, null=True, blank=True)
    ad_boost = models.ForeignKey(AdBoost, on_delete=models.CASCADE, null=True, blank=True)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    
    # Détails financiers
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='XOF')
    processing_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # État et type
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    
    # Métadonnées
    description = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    failure_reason = models.TextField(blank=True)
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['reference']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Transaction {self.reference} - {self.amount} {self.currency}"
    
    def save(self, *args, **kwargs):
        if not self.total_amount:
            self.total_amount = self.amount + self.processing_fee
        super().save(*args, **kwargs)

class Coupon(models.Model):
    """Codes de réduction"""
    DISCOUNT_TYPES = [
        ('percentage', 'Pourcentage'),
        ('fixed', 'Montant fixe'),
    ]
    
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Conditions d'utilisation
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_uses = models.PositiveIntegerField(null=True, blank=True)
    max_uses_per_user = models.PositiveIntegerField(default=1)
    current_uses = models.PositiveIntegerField(default=0)
    
    # Validité
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    # Restrictions
    applicable_packages = models.ManyToManyField(Package, blank=True)
    new_users_only = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_coupons')
    
    def __str__(self):
        return f"{self.code} - {self.discount_value}{'%' if self.discount_type == 'percentage' else ' XOF'}"
    
    @property
    def is_valid(self):
        now = timezone.now()
        return (self.is_active and 
                self.valid_from <= now <= self.valid_until and
                (not self.max_uses or self.current_uses < self.max_uses))
    
    def calculate_discount(self, amount):
        if not self.is_valid:
            return Decimal('0')
        
        if self.discount_type == 'percentage':
            discount = amount * (self.discount_value / 100)
            if self.max_discount:
                discount = min(discount, self.max_discount)
        else:
            discount = self.discount_value
        
        return min(discount, amount)

class CouponUsage(models.Model):
    """Utilisation des coupons"""
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coupon_usages')
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='coupon_usage')
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    used_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('coupon', 'transaction')
    
    def __str__(self):
        return f"{self.user.username} used {self.coupon.code}"

class Revenue(models.Model):
    """Suivi des revenus"""
    date = models.DateField()
    package_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    boost_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    subscription_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    transactions_count = models.PositiveIntegerField(default=0)
    new_subscriptions = models.PositiveIntegerField(default=0)
    ad_boosts = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('date',)
        ordering = ['-date']
    
    def __str__(self):
        return f"Revenue {self.date}: {self.total_revenue} XOF"