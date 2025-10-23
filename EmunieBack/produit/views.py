from rest_framework import generics, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg, F
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta

User = get_user_model()

from .models import (
    Ad, AdImage, Advertisement, Favorite, AdReport, AdView, AdStatus,
    CATEGORY_CHOICES, CITY_CHOICES
)
from .serializers import (
    AdListSerializer, AdDetailSerializer, AdCreateUpdateSerializer,
    AdImageSerializer, FavoriteSerializer, AdReportSerializer,
    AdvertisementSerializer, AdvertisementCreateSerializer,
    CategoryChoiceSerializer, CityChoiceSerializer
)
from .permissions import IsOwnerOrReadOnly

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_categories(request):
    """Récupérer la liste des catégories"""
    categories = [{'value': value, 'label': label} for value, label in CATEGORY_CHOICES]
    return Response({'categories': categories})

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_cities(request):
    """Récupérer la liste des villes"""
    cities = [{'value': value, 'label': label} for value, label in CITY_CHOICES]
    return Response({'cities': cities})

class AdListView(generics.ListAPIView):
    """Liste des annonces avec filtres"""
    serializer_class = AdListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'price', 'views_count', 'favorites_count']
    ordering = ['-is_featured', '-is_urgent', '-created_at']

    def get_queryset(self):
        queryset = Ad.objects.filter(
            status=AdStatus.ACTIVE,
            expires_at__gt=timezone.now()
        ).select_related('user').prefetch_related('images')

        # Filtres personnalisés
        category = self.request.query_params.get('category', None)
        city = self.request.query_params.get('city', None)
        price_min = self.request.query_params.get('price_min', None)
        price_max = self.request.query_params.get('price_max', None)

        if category:
            queryset = queryset.filter(category=category)

        if city:
            queryset = queryset.filter(city=city)

        if price_min:
            queryset = queryset.filter(price__gte=price_min)

        if price_max:
            queryset = queryset.filter(price__lte=price_max)

        return queryset

class AdDetailView(generics.RetrieveAPIView):
    """Détail d'une annonce"""
    queryset = Ad.objects.select_related('user').prefetch_related('images')
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
        ad = serializer.save(user=self.request.user)

        # Mettre à jour le compteur d'annonces de l'utilisateur
        User.objects.filter(pk=self.request.user.pk).update(total_ads=F('total_ads') + 1)

        return ad

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
        ).select_related('user').prefetch_related('images')

class FavoriteListView(generics.ListAPIView):
    """Liste des favoris de l'utilisateur"""
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(
            user=self.request.user
        ).select_related('ad__user').order_by('-created_at')

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
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Vous ne pouvez pas signaler votre propre annonce.")

        serializer.save(reporter=self.request.user, ad=ad)

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
    ).select_related('user').prefetch_related('images')[:8]

    # Annonces récentes
    recent_ads = Ad.objects.filter(
        status=AdStatus.ACTIVE,
        expires_at__gt=now
    ).select_related('user').prefetch_related('images').order_by('-created_at')[:12]

    # Annonces urgentes
    urgent_ads = Ad.objects.filter(
        status=AdStatus.ACTIVE,
        is_urgent=True,
        expires_at__gt=now
    ).select_related('user').prefetch_related('images')[:6]

    # Statistiques par catégorie
    categories_stats = []
    for value, label in CATEGORY_CHOICES:
        count = Ad.objects.filter(status=AdStatus.ACTIVE, category=value).count()
        if count > 0:
            categories_stats.append({
                'value': value,
                'label': label,
                'count': count
            })

    # Statistiques globales
    stats = {
        'total_ads': Ad.objects.filter(status=AdStatus.ACTIVE).count(),
        'total_users': User.objects.filter(is_active=True).count(),
        'ads_today': Ad.objects.filter(
            created_at__date=now.date(),
            status=AdStatus.ACTIVE
        ).count(),
    }

    return Response({
        'featured_ads': AdListSerializer(featured_ads, many=True, context={'request': request}).data,
        'recent_ads': AdListSerializer(recent_ads, many=True, context={'request': request}).data,
        'urgent_ads': AdListSerializer(urgent_ads, many=True, context={'request': request}).data,
        'categories': categories_stats,
        'cities': [{'value': v, 'label': l} for v, l in CITY_CHOICES[:10]],  # Top 10 villes
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
    from datetime import date
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
        'total_images': ad.images.count(),
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

# ===== VUES POUR LES PUBLICITÉS =====

class AdvertisementListView(generics.ListAPIView):
    """Liste des publicités actives"""
    serializer_class = AdvertisementSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        now = timezone.now()
        return Advertisement.objects.filter(
            is_active=True,
            is_approved=True,
            start_date__lte=now,
            end_date__gte=now
        ).order_by('?')  # Ordre aléatoire

class MyAdvertisementsView(generics.ListAPIView):
    """Mes publicités"""
    serializer_class = AdvertisementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Advertisement.objects.filter(user=self.request.user).order_by('-created_at')

class AdvertisementCreateView(generics.CreateAPIView):
    """Créer une publicité"""
    serializer_class = AdvertisementCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        advertisement = serializer.save(user=self.request.user)
        return advertisement

class AdvertisementDetailView(generics.RetrieveAPIView):
    """Détail d'une publicité"""
    serializer_class = AdvertisementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Advertisement.objects.filter(user=self.request.user)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def track_ad_impression(request, pk):
    """Enregistrer une impression de publicité"""
    try:
        ad = Advertisement.objects.get(pk=pk, is_active=True, is_approved=True)
        ad.impressions += 1
        ad.save(update_fields=['impressions'])
        return Response({'success': True})
    except Advertisement.DoesNotExist:
        return Response({'error': 'Publicité introuvable'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def track_ad_click(request, pk):
    """Enregistrer un clic sur une publicité"""
    try:
        ad = Advertisement.objects.get(pk=pk, is_active=True, is_approved=True)
        ad.clicks += 1
        ad.save(update_fields=['clicks'])
        return Response({'success': True, 'redirect_url': ad.link})
    except Advertisement.DoesNotExist:
        return Response({'error': 'Publicité introuvable'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def advertisement_statistics(request, pk):
    """Statistiques d'une publicité (pour le propriétaire)"""
    try:
        ad = Advertisement.objects.get(pk=pk, user=request.user)
    except Advertisement.DoesNotExist:
        return Response(
            {'error': 'Publicité introuvable'},
            status=status.HTTP_404_NOT_FOUND
        )

    stats = {
        'impressions': ad.impressions,
        'clicks': ad.clicks,
        'ctr': ad.ctr,
        'is_running': ad.is_running,
        'days_remaining': (ad.end_date - timezone.now()).days if ad.end_date > timezone.now() else 0,
        'total_spent': float(ad.total_price),
        'cost_per_click': float(ad.total_price / ad.clicks) if ad.clicks > 0 else 0,
    }

    return Response(stats)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def check_ad_limit(request):
    """Vérifier si l'utilisateur peut créer une annonce"""
    user = request.user
    can_create = user.can_create_ad
    remaining = user.remaining_ads

    return Response({
        'can_create_ad': can_create,
        'remaining_ads': remaining,
        'is_premium': user.is_premium_active,
        'active_ads_count': user.ads.filter(status='active').count(),
        'max_free_ads': User.MAX_FREE_ADS,
        'message': 'Vous pouvez créer une annonce' if can_create else
        'Limite atteinte. Passez au premium pour publier plus d\'annonces.'
    })

class MypubliciteView(APIView):
    def get(self, request):
        # Exemple : retourner les publicités de l’utilisateur connecté
        publicites = Advertisement.objects.filter(user=request.user)
        serializer = AdvertisementSerializer(publicites, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
