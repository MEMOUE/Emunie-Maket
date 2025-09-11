from django.urls import path
from .views import (
    PackageListView, PackageDetailView, PaymentMethodListView,
    UserSubscriptionListView, TransactionListView, TransactionCreateView,
    pricing_calculator, UserDashboardView
)

app_name = 'monetisation'

urlpatterns = [
    # Packages
    path('packages/', PackageListView.as_view(), name='package_list'),
    path('packages/<int:pk>/', PackageDetailView.as_view(), name='package_detail'),
    
    # Méthodes de paiement
    path('payment-methods/', PaymentMethodListView.as_view(), name='payment_method_list'),
    
    # Abonnements
    path('subscriptions/', UserSubscriptionListView.as_view(), name='subscription_list'),
    
    # Transactions
    path('transactions/', TransactionListView.as_view(), name='transaction_list'),
    path('transactions/create/', TransactionCreateView.as_view(), name='transaction_create'),
    
    # Utilitaires
    path('pricing-calculator/', pricing_calculator, name='pricing_calculator'),
    path('dashboard/', UserDashboardView.as_view(), name='user_dashboard'),
]
