"""
URL configuration for EmunieBack project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from drf_spectacular.views import (
    SpectacularAPIView, 
    SpectacularSwaggerView, 
    SpectacularRedocView  # ✅ Ajout de ReDoc
)

urlpatterns = [
    # ==========================================
    # ADMINISTRATION
    # ==========================================
    path('admin/', admin.site.urls),
    
    # ==========================================
    # AUTHENTIFICATION JWT
    # ==========================================
    path('api/auth/', include([
        path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        path('verify/', TokenVerifyView.as_view(), name='token_verify'),
    ])),
    
    # ==========================================
    # API ENDPOINTS
    # ==========================================
    path('api/v1/', include([
        path('users/', include('user.urls')),
    ])),

    path('api/v2/', include([
        path('ads/', include('produit.urls')),
    ])),
    path('api/v3/', include([
        path('monetisation/', include('monetisation.urls')),
    ])),
    
    # ==========================================
    # DOCUMENTATION API
    # ==========================================
    # Schéma OpenAPI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # Interface Swagger UI
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # Interface ReDoc (alternative à Swagger)
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # ==========================================
    # REDIRECTIONS POUR LA RACINE
    # ==========================================
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='api-root'),
]

# ==========================================
# GESTION DES FICHIERS STATIQUES ET MEDIA
# ==========================================
if settings.DEBUG:
    # Servir les fichiers media en développement
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Servir les fichiers statiques en développement
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Optionnel: Django Debug Toolbar (à décommenter si installé)
    # import debug_toolbar
    # urlpatterns = [
    #     path('__debug__/', include(debug_toolbar.urls)),
    # ] + urlpatterns

# ==========================================
# GESTION DES ERREURS (PRODUCTION)
# ==========================================
handler404 = 'django.views.defaults.page_not_found'
handler500 = 'django.views.defaults.server_error'
handler403 = 'django.views.defaults.permission_denied'
handler400 = 'django.views.defaults.bad_request'