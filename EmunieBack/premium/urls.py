from django.urls import path
from . import views

app_name = 'premium'

urlpatterns = [
    # Plans Premium
    path('plans/', views.PremiumPlanListView.as_view(), name='plans'),

    # Abonnements
    path('subscribe/', views.SubscribeToPremiumView.as_view(), name='subscribe'),
    path('my-subscriptions/', views.MyPremiumSubscriptionsView.as_view(), name='my_subscriptions'),
    path('subscriptions/<int:subscription_id>/cancel/', views.cancel_subscription, name='cancel_subscription'),

    # Statut
    path('check-status/', views.check_premium_status, name='check_status'),
]