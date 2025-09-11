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
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView  # ✅ Ajout

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Authentication
    path('api/auth/', include([
        path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        path('verify/', TokenVerifyView.as_view(), name='token_verify'),
    ])),
    
    # API v1
    path('api/v1/', include([
        path('users/', include('user.urls')),
        path('ads/', include('produit.urls')),
        path('monetisation/', include('monetisation.urls')),
    ])),
    
    # Documentation API
    path('api/docs/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

# Servir les fichiers media en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
