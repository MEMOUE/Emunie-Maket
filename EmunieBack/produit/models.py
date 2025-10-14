from django.db import models
from django.contrib.auth import get_user_model
from mptt.models import MPTTModel, TreeForeignKey
from django.utils import timezone
from django.core.validators import MinValueValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
import uuid

User = get_user_model()

# Choix de catégories prédéfinis
CATEGORY_CHOICES = [
    ('vehicules', 'Véhicules'),
    ('emploi_stages', 'Offres d\'emploi & Stages'),
    ('immobilier', 'Immobilier & Foncier'),
    ('electronique', 'Électronique & Multimédia'),
    ('maison_jardin', 'Maison & Jardin'),
    ('mode_beaute', 'Mode, Vêtements & Beauté'),
    ('sport_loisirs', 'Sport, Loisirs & Culture'),
    ('services', 'Services & Formation'),
    ('materiaux_pro', 'Matériaux & Équipements Pro'),
    ('agroalimentaire', 'Agroalimentaire & Produits locaux'),
    ('autre', 'Autre'),
]

# Grandes villes de Côte d'Ivoire
CITY_CHOICES = [
    ('abidjan', 'Abidjan'),
    ('yamoussoukro', 'Yamoussoukro'),
    ('bouake', 'Bouaké'),
    ('daloa', 'Daloa'),
    ('san_pedro', 'San-Pedro'),
    ('korhogo', 'Korhogo'),
    ('man', 'Man'),
    ('divo', 'Divo'),
    ('gagnoa', 'Gagnoa'),
    ('abengourou', 'Abengourou'),
    ('anyama', 'Anyama'),
    ('agboville', 'Agboville'),
    ('grand_bassam', 'Grand-Bassam'),
    ('dabou', 'Dabou'),
    ('boundiali', 'Boundiali'),
    ('odienne', 'Odienné'),
    ('soubre', 'Soubré'),
    ('bingerville', 'Bingerville'),
    ('sassandra', 'Sassandra'),
    ('issia', 'Issia'),
    ('autre', 'Autre'),
]

class Category(MPTTModel):
    """Catégories hiérarchiques pour les annonces"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class MPTTMeta:
        order_insertion_by = ['order', 'name']

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Location(models.Model):
    """Localisation géographique"""
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class AdStatus(models.TextChoices):
    DRAFT = 'draft', 'Brouillon'
    ACTIVE = 'active', 'Active'
    SOLD = 'sold', 'Vendu'
    EXPIRED = 'expired', 'Expirée'
    SUSPENDED = 'suspended', 'Suspendue'
    REJECTED = 'rejected', 'Rejetée'

class AdType(models.TextChoices):
    SELL = 'sell', 'Vendre'
    BUY = 'buy', 'Acheter'
    RENT = 'rent', 'Louer'
    OFFER_SERVICE = 'offer_service', 'Offrir un service'
    SEEK_SERVICE = 'seek_service', 'Chercher un service'
    JOB_OFFER = 'job_offer', 'Offre d\'emploi'
    JOB_SEEK = 'job_seek', 'Recherche d\'emploi'

class Ad(models.Model):
    """Modèle principal pour les annonces"""
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, verbose_name='Titre')
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(verbose_name='Description')

    # Relations
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ads')

    # Catégorie simplifiée
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        blank=True,
        null=True,
        verbose_name='Catégorie'
    )

    # Ville simplifiée
    city = models.CharField(
        max_length=50,
        choices=CITY_CHOICES,
        blank=True,
        null=True,
        verbose_name='Ville'
    )

    # Détails de l'annonce
    ad_type = models.CharField(max_length=20, choices=AdType.choices, default=AdType.SELL)
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name='Prix'
    )
    currency = models.CharField(max_length=3, default='XOF')
    is_negotiable = models.BooleanField(default=True)

    # Localisation précise (optionnelle)
    address = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # État et gestion
    status = models.CharField(max_length=20, choices=AdStatus.choices, default=AdStatus.DRAFT)
    is_featured = models.BooleanField(default=False)
    is_urgent = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    favorites_count = models.PositiveIntegerField(default=0)

    # Contact
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_email = models.EmailField(blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)

    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    published_at = models.DateTimeField(null=True, blank=True)

    # Modération
    is_moderated = models.BooleanField(default=False)
    moderated_at = models.DateTimeField(null=True, blank=True)
    moderated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderated_ads')
    rejection_reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'category', 'city']),
            models.Index(fields=['created_at', 'is_featured']),
            models.Index(fields=['price', 'category']),
        ]

    def __str__(self):
        return self.title

    @property
    def is_active(self):
        return (self.status == AdStatus.ACTIVE and
                self.expires_at > timezone.now())

    @property
    def is_expired(self):
        return self.expires_at <= timezone.now()

    def save(self, *args, **kwargs):
        if self.status == AdStatus.ACTIVE and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

class AdImage(models.Model):
    """Images des annonces"""
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='ads/images/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"Image for {self.ad.title}"

class AdVideo(models.Model):
    """Vidéos des annonces"""
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to='ads/videos/')
    thumbnail = models.ImageField(upload_to='ads/thumbnails/', null=True, blank=True)
    caption = models.CharField(max_length=200, blank=True)
    duration = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Video for {self.ad.title}"

class AdAttribute(models.Model):
    """Attributs dynamiques pour les annonces"""
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    input_type = models.CharField(max_length=20, choices=[
        ('text', 'Texte'),
        ('number', 'Nombre'),
        ('choice', 'Choix unique'),
        ('multiple_choice', 'Choix multiple'),
        ('boolean', 'Oui/Non'),
        ('date', 'Date'),
    ])
    is_required = models.BooleanField(default=False)
    is_filterable = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    categories = models.ManyToManyField(Category, related_name='attributes')

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

class AdAttributeChoice(models.Model):
    """Choix possibles pour les attributs de type choix"""
    attribute = models.ForeignKey(AdAttribute, on_delete=models.CASCADE, related_name='choices')
    value = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'value']

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"

class AdAttributeValue(models.Model):
    """Valeurs des attributs pour chaque annonce"""
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='attribute_values')
    attribute = models.ForeignKey(AdAttribute, on_delete=models.CASCADE)
    value = models.TextField()

    class Meta:
        unique_together = ('ad', 'attribute')

    def __str__(self):
        return f"{self.ad.title} - {self.attribute.name}: {self.value}"

class Favorite(models.Model):
    """Favoris des utilisateurs"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'ad')

    def __str__(self):
        return f"{self.user.username} - {self.ad.title}"

class AdView(models.Model):
    """Vues des annonces pour statistiques"""
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('ad', 'ip_address', 'user')

    def __str__(self):
        return f"View for {self.ad.title}"

class AdReport(models.Model):
    """Signalements d'annonces"""
    REPORT_REASONS = [
        ('spam', 'Spam'),
        ('fraud', 'Fraude'),
        ('inappropriate', 'Contenu inapproprié'),
        ('wrong_category', 'Mauvaise catégorie'),
        ('duplicate', 'Doublon'),
        ('other', 'Autre'),
    ]

    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    reason = models.CharField(max_length=20, choices=REPORT_REASONS)
    description = models.TextField(blank=True)
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports_resolved')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('ad', 'reporter')

    def __str__(self):
        return f"Report for {self.ad.title} by {self.reporter.username}"


def validate_ad_image_size(file):
    """Valider la taille de l'affiche publicitaire (max 2Mo)"""
    max_size_mb = 2
    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f'La taille du fichier ne doit pas dépasser {max_size_mb}Mo')


class Advertisement(models.Model):
    """Publicités payantes (bannières publicitaires)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='advertisements')
    title = models.CharField(max_length=200, verbose_name='Titre de la publicité')
    link = models.URLField(verbose_name='Lien de destination')

    # Affiche publicitaire avec validation de taille
    image = models.ImageField(
        upload_to='advertisements/',
        validators=[
            validate_ad_image_size,
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])
        ],
        verbose_name='Affiche publicitaire',
        help_text='Taille maximale: 2Mo. Formats acceptés: jpg, jpeg, png, gif'
    )

    # Durée et tarification (1000 FCFA / 24h)
    duration_hours = models.PositiveIntegerField(
        default=24,
        validators=[MinValueValidator(24)],
        help_text='Durée en heures (minimum 24h)'
    )
    price_per_day = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1000,
        verbose_name='Prix par jour (FCFA)'
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Prix total'
    )

    # Dates
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    # Statut
    is_active = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)

    # Statistiques
    impressions = models.PositiveIntegerField(default=0, verbose_name='Nombre d\'affichages')
    clicks = models.PositiveIntegerField(default=0, verbose_name='Nombre de clics')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Publicité'
        verbose_name_plural = 'Publicités'

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    def save(self, *args, **kwargs):
        # Calculer le prix total
        days = self.duration_hours / 24
        self.total_price = days * self.price_per_day
        super().save(*args, **kwargs)

    @property
    def is_running(self):
        """Vérifier si la publicité est en cours"""
        now = timezone.now()
        return self.is_active and self.is_approved and self.start_date <= now <= self.end_date

    @property
    def ctr(self):
        """Calcul du taux de clic (Click Through Rate)"""
        if self.impressions == 0:
            return 0
        return (self.clicks / self.impressions) * 100