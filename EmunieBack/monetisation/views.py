from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models import (
    Package, UserSubscription, AdBoost, PaymentMethod,
    Transaction, Coupon, Revenue
)
from .serializers import (
    PackageSerializer, UserSubscriptionSerializer, AdBoostSerializer,
    PaymentMethodSerializer, TransactionSerializer, TransactionCreateSerializer,
    CouponSerializer, CouponValidationSerializer, RevenueSerializer
)
from .services import PaymentService, NotificationService

class PackageListView(generics.ListAPIView):
    """Liste des packages disponibles"""
    queryset = Package.objects.filter(is_active=True).order_by('price')
    serializer_class = PackageSerializer
    permission_classes = [permissions.AllowAny]

class PackageDetailView(generics.RetrieveAPIView):
    """Détail d'un package"""
    queryset = Package.objects.filter(is_active=True)
    serializer_class = PackageSerializer
    permission_classes = [permissions.AllowAny]

class PaymentMethodListView(generics.ListAPIView):
    """Liste des méthodes de paiement"""
    queryset = PaymentMethod.objects.filter(is_active=True).order_by('order')
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.AllowAny]

class UserSubscriptionListView(generics.ListAPIView):
    """Abonnements de l'utilisateur"""
    serializer_class = UserSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserSubscription.objects.filter(user=self.request.user).order_by('-created_at')

class TransactionListView(generics.ListAPIView):
    """Historique des transactions de l'utilisateur"""
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

class TransactionCreateView(generics.CreateAPIView):
    """Créer une nouvelle transaction (achat)"""
    serializer_class = TransactionCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        transaction = serializer.save()
        
        # Initier le paiement avec le service de paiement
        payment_service = PaymentService()
        try:
            payment_result = payment_service.initiate_payment(transaction)
            
            if payment_result['success']:
                transaction.external_reference = payment_result.get('reference')
                transaction.status = 'processing'
                transaction.processed_at = timezone.now()
                transaction.save()
                
                return Response({
                    'transaction_id': transaction.id,
                    'reference': transaction.reference,
                    'payment_url': payment_result.get('payment_url'),
                    'payment_instructions': payment_result.get('instructions'),
                    'status': 'processing'
                }, status=status.HTTP_201_CREATED)
            else:
                transaction.status = 'failed'
                transaction.failure_reason = payment_result.get('error', 'Erreur de paiement')
                transaction.save()
                
                return Response({
                    'error': 'Échec de l\'initiation du paiement',
                    'details': payment_result.get('error')
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            transaction.status = 'failed'
            transaction.failure_reason = str(e)
            transaction.save()
            
            return Response({
                'error': 'Erreur lors du traitement du paiement'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserDashboardView(APIView):
    """Tableau de bord utilisateur pour la monétisation"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Abonnements actifs
        active_subscriptions = UserSubscription.objects.filter(
            user=user,
            status='active',
            end_date__gt=timezone.now()
        )
        
        # Statistiques des dépenses
        total_spent = Transaction.objects.filter(
            user=user,
            status='completed'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Boosts actifs
        active_boosts = AdBoost.objects.filter(
            user=user,
            is_active=True,
            end_date__gt=timezone.now()
        ).count()
        
        # Transactions récentes
        recent_transactions = Transaction.objects.filter(
            user=user
        ).order_by('-created_at')[:5]
        
        return Response({
            'active_subscriptions': UserSubscriptionSerializer(active_subscriptions, many=True).data,
            'statistics': {
                'total_spent': total_spent,
                'active_boosts': active_boosts,
                'total_transactions': Transaction.objects.filter(user=user).count(),
                'successful_transactions': Transaction.objects.filter(user=user, status='completed').count()
            },
            'recent_transactions': TransactionSerializer(recent_transactions, many=True).data,
        })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def pricing_calculator(request):
    """Calculateur de prix avec coupons"""
    package_id = request.query_params.get('package_id')
    coupon_code = request.query_params.get('coupon_code')
    
    if not package_id:
        return Response({'error': 'package_id requis'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        package = Package.objects.get(id=package_id, is_active=True)
    except Package.DoesNotExist:
        return Response({'error': 'Package introuvable'}, status=status.HTTP_404_NOT_FOUND)
    
    base_price = package.price
    discount_amount = Decimal('0')
    final_price = base_price
    coupon_info = None
    
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code, is_active=True)
            if coupon.is_valid:
                # Vérifier l'usage utilisateur
                user_usage = coupon.usages.filter(user=request.user).count()
                if user_usage < coupon.max_uses_per_user:
                    discount_amount = coupon.calculate_discount(base_price)
                    final_price = base_price - discount_amount
                    coupon_info = {
                        'code': coupon.code,
                        'name': coupon.name,
                        'discount_type': coupon.discount_type,
                        'discount_value': coupon.discount_value,
                        'valid': True
                    }
                else:
                    coupon_info = {'valid': False, 'reason': 'Limite d\'utilisation atteinte'}
            else:
                coupon_info = {'valid': False, 'reason': 'Coupon expiré ou invalide'}
        except Coupon.DoesNotExist:
            coupon_info = {'valid': False, 'reason': 'Coupon introuvable'}
    
    # Calculer les frais de traitement pour chaque méthode de paiement
    payment_methods = []
    for method in PaymentMethod.objects.filter(is_active=True):
        processing_fee = final_price * (method.processing_fee / 100)
        total_with_fees = final_price + processing_fee
        
        payment_methods.append({
            'id': method.id,
            'name': method.name,
            'payment_type': method.payment_type,
            'processing_fee': processing_fee,
            'total_amount': total_with_fees
        })
    
    return Response({
        'package': PackageSerializer(package).data,
        'pricing': {
            'base_price': base_price,
            'discount_amount': discount_amount,
            'final_price': final_price,
            'savings_percentage': (discount_amount / base_price * 100) if discount_amount > 0 else 0
        },
        'coupon': coupon_info,
        'payment_methods': payment_methods
    })