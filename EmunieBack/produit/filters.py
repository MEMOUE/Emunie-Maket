import django_filters
from django.db.models import Q
from .models import Ad, Category, Location, AdType, AdStatus

class AdFilter(django_filters.FilterSet):
    """Filtres pour les annonces"""
    
    # Filtres de base
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.filter(is_active=True))
    category_slug = django_filters.CharFilter(field_name='category__slug')
    location = django_filters.ModelChoiceFilter(queryset=Location.objects.filter(is_active=True))
    location_name = django_filters.CharFilter(field_name='location__name', lookup_expr='icontains')
    
    # Filtres de prix
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    price_range = django_filters.RangeFilter(field_name='price')
    is_negotiable = django_filters.BooleanFilter()
    
    # Filtres de type
    ad_type = django_filters.ChoiceFilter(choices=AdType.choices)
    
    # Filtres de statut
    status = django_filters.ChoiceFilter(choices=AdStatus.choices)
    is_featured = django_filters.BooleanFilter()
    is_urgent = django_filters.BooleanFilter()
    
    # Filtres de date
    date_from = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    published_today = django_filters.BooleanFilter(method='filter_published_today')
    published_this_week = django_filters.BooleanFilter(method='filter_published_this_week')
    
    # Filtres par utilisateur
    user = django_filters.NumberFilter(field_name='user__id')
    user_verified = django_filters.BooleanFilter(method='filter_user_verified')
    
    # Filtres par popularité
    min_views = django_filters.NumberFilter(field_name='views_count', lookup_expr='gte')
    min_favorites = django_filters.NumberFilter(field_name='favorites_count', lookup_expr='gte')
    
    # Filtres géographiques
    has_coordinates = django_filters.BooleanFilter(method='filter_has_coordinates')
    
    # Recherche textuelle
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = Ad
        fields = [
            'category', 'category_slug', 'location', 'location_name',
            'price_min', 'price_max', 'price_range', 'is_negotiable',
            'ad_type', 'status', 'is_featured', 'is_urgent',
            'date_from', 'date_to', 'published_today', 'published_this_week',
            'user', 'user_verified', 'min_views', 'min_favorites',
            'has_coordinates', 'search'
        ]
    
    def filter_published_today(self, queryset, name, value):
        if value:
            from django.utils import timezone
            today = timezone.now().date()
            return queryset.filter(created_at__date=today)
        return queryset
    
    def filter_published_this_week(self, queryset, name, value):
        if value:
            from django.utils import timezone
            from datetime import timedelta
            week_ago = timezone.now().date() - timedelta(days=7)
            return queryset.filter(created_at__date__gte=week_ago)
        return queryset
    
    def filter_user_verified(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(user__email_verified=True) | Q(user__phone_verified=True)
            )
        return queryset
    
    def filter_has_coordinates(self, queryset, name, value):
        if value:
            return queryset.filter(
                latitude__isnull=False,
                longitude__isnull=False
            )
        return queryset
    
    def filter_search(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(title__icontains=value) |
                Q(description__icontains=value) |
                Q(category__name__icontains=value) |
                Q(location__name__icontains=value)
            ).distinct()
        return queryset

class CategoryFilter(django_filters.FilterSet):
    """Filtres pour les catégories"""
    parent = django_filters.ModelChoiceFilter(queryset=Category.objects.filter(is_active=True))
    has_children = django_filters.BooleanFilter(method='filter_has_children')
    level = django_filters.NumberFilter(field_name='level')
    
    class Meta:
        model = Category
        fields = ['parent', 'has_children', 'level']
    
    def filter_has_children(self, queryset, name, value):
        if value:
            return queryset.filter(children__isnull=False).distinct()
        else:
            return queryset.filter(children__isnull=True)

class LocationFilter(django_filters.FilterSet):
    """Filtres pour les localisations"""
    parent = django_filters.ModelChoiceFilter(queryset=Location.objects.filter(is_active=True))
    has_coordinates = django_filters.BooleanFilter(method='filter_has_coordinates')
    
    class Meta:
        model = Location
        fields = ['parent', 'has_coordinates']
    
    def filter_has_coordinates(self, queryset, name, value):
        if value:
            return queryset.filter(
                latitude__isnull=False,
                longitude__isnull=False
            )
        return queryset