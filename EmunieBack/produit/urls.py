from django.urls import path
from . import views

app_name = 'produit'

urlpatterns = [
    # === DONNÉES DE BASE ===
    # Catégories et villes
    path('categories/', views.get_categories, name='categories'),
    path('cities/', views.get_cities, name='cities'),

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

    # === PUBLICITÉS PAYANTES ===
    # Liste et création de publicités
    # path('publicite/', views.AdvertisementListView.as_view(), name='advertisement_list'),
    # path('publicite/create/', views.AdvertisementCreateView.as_view(), name='advertisement_create'),
    # path('publicite/my/', views.MypubliciteView.as_view(), name='my_publicite'),
    # path('publicite/<int:pk>/', views.AdvertisementDetailView.as_view(), name='advertisement_detail'),
    # path('publicite/<int:pk>/statistics/', views.advertisement_statistics, name='advertisement_statistics'),
    #
    # # Tracking des publicités
    # path('publicite/<int:pk>/impression/', views.track_ad_impression, name='track_ad_impression'),
    # path('publicite/<int:pk>/click/', views.track_ad_click, name='track_ad_click'),

    # === DONNÉES PUBLIQUES ===
    # Page d'accueil et données générales
    path('home-data/', views.home_data, name='home_data'),
]