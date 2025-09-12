from rest_framework import generics, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg, F
from django.utils import timezone
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from datetime import timedelta
import uuid

User = get_user_model()

from .models import (
    Category, Location, Ad, AdImage, AdVideo, AdAttribute,
    Favorite, AdReport, AdView, AdStatus, AdType
)
from .serializers import (
    CategorySerializer, LocationSerializer, AdListSerializer,
    AdDetailSerializer, AdCreateUpdateSerializer, AdImageSerializer,
    AdVideoSerializer, AdAttributeSerializer, FavoriteSerializer,
    AdReportSerializer
)
from .filters import AdFilter
from .permissions import IsOwnerOrReadOnly

class CategoryListView(generics.ListAPIView):
    """Liste des catégories"""
    queryset = Category.objects.filter(is_active=True, parent=None)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

class CategoryDetailView(generics.RetrieveAPIView):
    """Détail d'une catégorie"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

class LocationListView(generics.ListAPIView):
    """Liste des localisations"""
    queryset = Location.objects.filter(is_active=True)
    serializer_class = LocationSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

class LocationDetailView(generics.RetrieveAPIView):
    """Détail d'une localisation"""
    queryset = Location.objects.filter(is_active=True)
    serializer_class = LocationSerializer
    permission_classes = [permissions.AllowAny]

class AdListView(generics.ListAPIView):
    """Liste des annonces avec filtres"""
    serializer_class = AdListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AdFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'price', 'views_count', 'favorites_count']
    ordering = ['-is_featured', '-is_urgent', '-created_at']
    
    def get_queryset(self):
        return Ad.objects.filter(
            status=AdStatus.ACTIVE,
            expires_at__gt=timezone.now()
        ).select_related('user', 'category', 'location').prefetch_related('images')

class AdDetailView(generics.RetrieveAPIView):
    """Détail d'une annonce"""
    queryset = Ad.objects.select_related('user', 'category', 'location').prefetch_related(
        'images', 'videos', 'attribute_values__attribute'
    )
    serializer_class = AdDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'pk'
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Enregistrer la vue seulement si l'annonce est active
        if instance.status == AdStatus.ACTIVE:
            client_ip = self.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Créer la vue avec get_or_create pour éviter les doublons
            if request.user.is_authenticated:
                view_obj, created = AdView.objects.get_or_create(
                    ad=instance,
                    user=request.user,
                    ip_address=client_ip,
                    defaults={'user_agent': user_agent}
                )
            else:
                view_obj, created = AdView.objects.get_or_create(
                    ad=instance,
                    ip_address=client_ip,
                    user=None,
                    defaults={'user_agent': user_agent}
                )
            
            # Incrémenter le compteur de vues seulement si c'est une nouvelle vue
            if created:
                Ad.objects.filter(pk=instance.pk).update(views_count=F('views_count') + 1)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def get_client_ip(self, request):
        """Obtenir l'adresse IP du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip

class AdCreateView(generics.CreateAPIView):
    """Créer une annonce"""
    serializer_class = AdCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        # Calculer la date d'expiration par défaut (30 jours)
        expires_at = serializer.validated_data.get('expires_at')
        if not expires_at:
            expires_at = timezone.now() + timedelta(days=30)
        
        # Générer un slug unique
        title = serializer.validated_data['title']
        slug = self.generate_unique_slug(title)
        
        ad = serializer.save(
            user=self.request.user,
            expires_at=expires_at,
            slug=slug
        )
        
        # Mettre à jour le compteur d'annonces de l'utilisateur
        User.objects.filter(pk=self.request.user.pk).update(total_ads=F('total_ads') + 1)
    
    def generate_unique_slug(self, title):
        """Générer un slug unique"""
        from django.utils.text import slugify
        base_slug = slugify(title)
        slug = base_slug
        counter = 1
        
        while Ad.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug

class AdUpdateView(generics.UpdateAPIView):
    """Modifier une annonce"""
    serializer_class = AdCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        return Ad.objects.filter(user=self.request.user)

class AdDeleteView(generics.DestroyAPIView):
    """Supprimer une annonce"""
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        return Ad.objects.filter(user=self.request.user)
    
    def perform_destroy(self, instance):
        # Décrémenter le compteur d'annonces de l'utilisateur
        User.objects.filter(pk=self.request.user.pk).update(total_ads=F('total_ads') - 1)
        instance.delete()

class MyAdsView(generics.ListAPIView):
    """Mes annonces"""
    serializer_class = AdListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['created_at', 'views_count', 'favorites_count', 'status']
    ordering = ['-created_at']
    search_fields = ['title', 'description']
    
    def get_queryset(self):
        return Ad.objects.filter(
            user=self.request.user
        ).select_related('category', 'location').prefetch_related('images')

class CategoryAttributesView(generics.ListAPIView):
    """Attributs d'une catégorie"""
    serializer_class = AdAttributeSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        category_id = self.kwargs.get('category_id')
        category = get_object_or_404(Category, pk=category_id, is_active=True)
        return category.attributes.all().order_by('order', 'name')

class FavoriteListView(generics.ListAPIView):
    """Liste des favoris de l'utilisateur"""
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Favorite.objects.filter(
            user=self.request.user
        ).select_related('ad__user', 'ad__category', 'ad__location').order_by('-created_at')

class FavoriteToggleView(APIView):
    """Ajouter/retirer des favoris"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        ad_id = request.data.get('ad_id')
        if not ad_id:
            return Response(
                {'error': 'ad_id requis'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            ad = Ad.objects.get(pk=ad_id, status=AdStatus.ACTIVE)
        except Ad.DoesNotExist:
            return Response(
                {'error': 'Annonce introuvable'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            ad=ad
        )
        
        if created:
            # Ajouté aux favoris
            Ad.objects.filter(pk=ad.pk).update(favorites_count=F('favorites_count') + 1)
            return Response({'favorited': True, 'message': 'Ajouté aux favoris'})
        else:
            # Retiré des favoris
            favorite.delete()
            Ad.objects.filter(pk=ad.pk).update(favorites_count=F('favorites_count') - 1)
            return Response({'favorited': False, 'message': 'Retiré des favoris'})

class AdReportCreateView(generics.CreateAPIView):
    """Signaler une annonce"""
    serializer_class = AdReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        ad_id = self.kwargs.get('ad_id')
        ad = get_object_or_404(Ad, pk=ad_id)
        
        # Vérifier que l'utilisateur ne signale pas sa propre annonce
        if ad.user == self.request.user:
            raise ValidationError("Vous ne pouvez pas signaler votre propre annonce.")
        
        serializer.save(reporter=self.request.user, ad=ad)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def trending_searches(request):
    """Recherches tendances"""
    # Vous pouvez implémenter une logique plus sophistiquée basée sur les données réelles
    trending = [
        'Appartement Cocody',
        'iPhone Abidjan',
        'Voiture occasion',
        'Villa Riviera',
        'Terrain Bassam',
        'Moto Yamaha',
        'Ordinateur portable',
        'Maison Bingerville'
    ]
    return Response({'trending_searches': trending})

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def home_data(request):
    """Données pour la page d'accueil"""
    now = timezone.now()
    
    # Annonces mises en avant
    featured_ads = Ad.objects.filter(
        status=AdStatus.ACTIVE,
        is_featured=True,
        expires_at__gt=now
    ).select_related('user', 'category', 'location').prefetch_related('images')[:8]
    
    # Annonces récentes
    recent_ads = Ad.objects.filter(
        status=AdStatus.ACTIVE,
        expires_at__gt=now
    ).select_related('user', 'category', 'location').prefetch_related('images').order_by('-created_at')[:12]
    
    # Annonces urgentes
    urgent_ads = Ad.objects.filter(
        status=AdStatus.ACTIVE,
        is_urgent=True,
        expires_at__gt=now
    ).select_related('user', 'category', 'location').prefetch_related('images')[:6]
    
    # Catégories principales
    categories = Category.objects.filter(
        is_active=True, 
        parent=None
    ).annotate(
        ads_count=Count('ads', filter=Q(ads__status=AdStatus.ACTIVE))
    ).order_by('order', 'name')[:8]
    
    # Statistiques
    stats = {
        'total_ads': Ad.objects.filter(status=AdStatus.ACTIVE).count(),
        'total_users': User.objects.filter(is_active=True).count(),
        'ads_today': Ad.objects.filter(
            created_at__date=now.date(),
            status=AdStatus.ACTIVE
        ).count(),
        'total_views': Ad.objects.aggregate(
            total=models.Sum('views_count')
        )['total'] or 0,
    }
    
    return Response({
        'featured_ads': AdListSerializer(featured_ads, many=True, context={'request': request}).data,
        'recent_ads': AdListSerializer(recent_ads, many=True, context={'request': request}).data,
        'urgent_ads': AdListSerializer(urgent_ads, many=True, context={'request': request}).data,
        'categories': CategorySerializer(categories, many=True).data,
        'stats': stats
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def ad_statistics(request, pk):
    """Statistiques détaillées d'une annonce (pour le propriétaire)"""
    try:
        ad = Ad.objects.get(pk=pk, user=request.user)
    except Ad.DoesNotExist:
        return Response(
            {'error': 'Annonce introuvable'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Statistiques des vues par jour (7 derniers jours)
    from datetime import date, timedelta
    views_by_day = []
    for i in range(7):
        day = date.today() - timedelta(days=i)
        views_count = ad.views.filter(created_at__date=day).count()
        views_by_day.append({
            'date': day.isoformat(),
            'views': views_count
        })
    
    stats = {
        'total_views': ad.views_count,
        'total_favorites': ad.favorites_count,
        'views_today': ad.views.filter(created_at__date=timezone.now().date()).count(),
        'views_this_week': ad.views.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count(),
        'views_by_day': list(reversed(views_by_day)),
        'unique_visitors': ad.views.values('ip_address').distinct().count(),
        'authenticated_views': ad.views.filter(user__isnull=False).count(),
        'anonymous_views': ad.views.filter(user__isnull=True).count(),
    }
    
    return Response(stats)