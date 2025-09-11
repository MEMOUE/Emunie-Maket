from django.urls import path
from . import views

app_name = 'produit'

urlpatterns = [
    # === ANNONCES PRINCIPALES ===
    # Liste et création d'annonces
    path('', views.AdListView.as_view(), name='ad_list'),
    path('create/', views.AdCreateView.as_view(), name='ad_create'),
    
    # CRUD d'annonces spécifiques
    path('<uuid:pk>/', views.AdDetailView.as_view(), name='ad_detail'),
    path('<uuid:pk>/update/', views.AdUpdateView.as_view(), name='ad_update'),
    path('<uuid:pk>/delete/', views.AdDeleteView.as_view(), name='ad_delete'),
    
    # === GESTION UTILISATEUR ===
    # Annonces de l'utilisateur connecté
    path('my-ads/', views.MyAdsView.as_view(), name='my_ads'),
    
    # === CATÉGORIES ===
    # CRUD catégories
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category_detail'),
    
    # Attributs de catégories
    path('categories/<int:category_id>/attributes/', views.CategoryAttributesView.as_view(), name='category_attributes'),
    
    # === LOCALISATIONS ===
    # CRUD localisations
    path('locations/', views.LocationListView.as_view(), name='location_list'),
    path('locations/<int:pk>/', views.LocationDetailView.as_view(), name='location_detail'),
    
    # === RECHERCHE ET NAVIGATION ===
    # Recherche
    path('search/trending/', views.trending_searches, name='trending_searches'),
    
    # === DONNÉES PUBLIQUES ===
    # Page d'accueil et données générales
    path('home-data/', views.home_data, name='home_data'),
]