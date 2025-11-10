from django.urls import path
from . import views, password_reset_views

app_name = 'user'

urlpatterns = [
    # Authentification
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/stats/', views.user_stats, name='user_stats'),
    path('password/change/', views.PasswordChangeView.as_view(), name='password_change'),
    
    # Vérifications
    path('email/send-verification/', views.send_email_verification, name='send_email_verification'),
    path('email/verify/', views.verify_email, name='verify_email'),
    path('phone/send-verification/', views.send_phone_verification, name='send_phone_verification'),
    path('phone/verify/', views.verify_phone, name='verify_phone'),
    
    # Utilisateurs publics
    path('', views.UserListView.as_view(), name='user_list'),
    path('<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    
    # Évaluations
    path('<int:user_id>/ratings/', views.UserRatingListCreateView.as_view(), name='user_ratings'),
    
    # Messagerie
    path('conversations/', views.ConversationListView.as_view(), name='conversation_list'),
    path('conversations/start/', views.StartConversationView.as_view(), name='start_conversation'),
    path('conversations/<int:pk>/', views.ConversationDetailView.as_view(), name='conversation_detail'),
    path('conversations/<int:conversation_id>/messages/', views.MessageListCreateView.as_view(), name='conversation_messages'),


    path('password/reset/request/', password_reset_views.request_password_reset, name='password_reset_request'),
    path('password/reset/verify/', password_reset_views.verify_reset_token, name='password_reset_verify'),
    path('password/reset/confirm/', password_reset_views.confirm_password_reset, name='password_reset_confirm'),
]