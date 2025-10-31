from django.urls import path
from . import auth_views
from .google_auth_views import GoogleAuthView, GoogleAuthCallbackView

app_name = 'auth'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Google OAuth
    path('google/', GoogleAuthView.as_view(), name='google_auth'),
    path('google/callback/', GoogleAuthCallbackView.as_view(), name='google_callback'),
]