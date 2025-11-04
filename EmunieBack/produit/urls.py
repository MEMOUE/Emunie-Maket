from django.urls import path
from . import views

app_name = 'produit'

urlpatterns = [
    # === DONNÉES DE BASE ===
    # Catégories et villes
    path('categories/', views.get_categories, name='categories'),
    path('cities/', views.get_cities, name='cities'),

    # NOUVEAU: Types et statuts d'annonces
    path('ad-types/', views.get_ad_types, name='ad_types'),
    path('ad-statuses/', views.get_ad_statuses, name='ad_statuses'),

    # === ANNONCES PRINCIPALES ===
    # Liste et création d'annonces
    path('ads/', views.AdListView.as_view(), name='ad_list'),
    path('ads/create/', views.AdCreateView.as_view(), name='ad_create'),
    path('ads/check-limit/', views.check_ad_limit, name='check_ad_limit'),

    # CRUD d'annonces spécifiques
    path('ads/<uuid:pk>/', views.AdDetailView.as_view(), name='ad_detail'),
    path('ads/<uuid:pk>/update/', views.AdUpdateView.as_view(), name='ad_update'),
    path('ads/<uuid:pk>/delete/', views.AdDeleteView.as_view(), name='ad_delete'),
    path('ads/<uuid:pk>/statistics/', views.ad_statistics, name='ad_statistics'),

    # === GESTION UTILISATEUR ===
    # Annonces de l'utilisateur connecté
    path('my-ads/', views.MyAdsView.as_view(), name='my_ads'),

    # === FAVORIS ===
    # Gestion des favoris
    path('favorites/', views.FavoriteListView.as_view(), name='favorite_list'),
    path('favorites/toggle/', views.FavoriteToggleView.as_view(), name='favorite_toggle'),

    # === SIGNALEMENTS ===
    # Signaler une annonce
    path('ads/<uuid:ad_id>/report/', views.AdReportCreateView.as_view(), name='ad_report'),

    # === DONNÉES PUBLIQUES ===
    # Page d'accueil et données générales
    path('home-data/', views.home_data, name='home_data'),
]