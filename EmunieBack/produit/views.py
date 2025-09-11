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
            status='active',
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
        
        # Enregistrer la vue
        if request.user.is_authenticated:
            AdView.objects.get_or_create(
                ad=instance,
                user=request.user,
                ip_address=self.get_client_ip(request),
                defaults={'user_agent': request.META.get('HTTP_USER_AGENT', '')}
            )
        else:
            AdView.objects.get_or_create(
                ad=instance,
                ip_address=self.get_client_ip(request),
                defaults={'user_agent': request.META.get('HTTP_USER_AGENT', '')}
            )
        
        # Incrémenter le compteur de vues
        Ad.objects.filter(pk=instance.pk).update(views_count=F('views_count') + 1)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
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
        
        ad = serializer.save(
            user=self.request.user,
            expires_at=expires_at,
            slug=self.generate_unique_slug(serializer.validated_data['title'])
        )
        
        # Mettre à jour le compteur d'annonces de l'utilisateur
        self.request.user.total_ads = F('total_ads') + 1
        self.request.user.save(update_fields=['total_ads'])
    
    def generate_unique_slug(self, title):
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

class MyAdsView(generics.ListAPIView):
    """Mes annonces"""
    serializer_class = AdListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'views_count', 'favorites_count']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Ad.objects.filter(user=self.request.user).select_related('category', 'location')

class CategoryAttributesView(generics.ListAPIView):
    """Attributs d'une catégorie"""
    serializer_class = AdAttributeSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        category_id = self.kwargs.get('category_id')
        category = get_object_or_404(Category, pk=category_id)
        return category.attributes.filter(is_active=True).order_by('order')

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def trending_searches(request):
    """Recherches tendances"""
    # Ici vous pouvez implémenter la logique pour les recherches populaires
    trending = [
        'Appartement Cocody',
        'iPhone Abidjan',
        'Voiture occasion',
        'Villa Riviera',
        'Terrain Bassam'
    ]
    return Response({'trending_searches': trending})

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def home_data(request):
    """Données pour la page d'accueil"""
    featured_ads = Ad.objects.filter(
        status='active',
        is_featured=True,
        expires_at__gt=timezone.now()
    ).select_related('user', 'category', 'location')[:8]
    
    recent_ads = Ad.objects.filter(
        status='active',
        expires_at__gt=timezone.now()
    ).select_related('user', 'category', 'location').order_by('-created_at')[:12]
    
    categories = Category.objects.filter(is_active=True, parent=None)[:8]
    
    return Response({
        'featured_ads': AdListSerializer(featured_ads, many=True, context={'request': request}).data,
        'recent_ads': AdListSerializer(recent_ads, many=True, context={'request': request}).data,
        'categories': CategorySerializer(categories, many=True).data,
        'stats': {
            'total_ads': Ad.objects.filter(status='active').count(),
            'total_users': User.objects.filter(is_active=True).count(),
            'ads_today': Ad.objects.filter(created_at__date=timezone.now().date()).count()
        }
    })