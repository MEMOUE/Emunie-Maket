from django.shortcuts import render

# Create your views here.
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import PremiumPlan, PremiumSubscription
from .serializers import (
    PremiumPlanSerializer,
    PremiumSubscriptionSerializer,
    SubscribeToPremiumSerializer
)


class PremiumPlanListView(generics.ListAPIView):
    """Liste des plans Premium disponibles"""
    serializer_class = PremiumPlanSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None  # ✅ CORRECTION : Désactiver la pagination pour retourner un tableau simple

    def get_queryset(self):
        return PremiumPlan.objects.filter(is_active=True)


class MyPremiumSubscriptionsView(generics.ListAPIView):
    """Mes abonnements Premium"""
    serializer_class = PremiumSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PremiumSubscription.objects.filter(user=self.request.user)


class SubscribeToPremiumView(APIView):
    """Souscrire à un plan Premium"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = SubscribeToPremiumSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        plan_id = serializer.validated_data['plan_id']
        payment_method = serializer.validated_data['payment_method']
        phone_number = serializer.validated_data['phone_number']

        # Récupérer le plan
        plan = get_object_or_404(PremiumPlan, id=plan_id, is_active=True)

        # Vérifier si l'utilisateur a déjà un abonnement actif
        active_subscription = PremiumSubscription.objects.filter(
            user=request.user,
            status='active'
        ).first()

        if active_subscription and active_subscription.is_active:
            return Response(
                {
                    'error': 'Vous avez déjà un abonnement Premium actif',
                    'current_subscription': PremiumSubscriptionSerializer(active_subscription).data
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                # Créer l'abonnement
                subscription = PremiumSubscription.objects.create(
                    user=request.user,
                    plan=plan,
                    status='pending',
                    payment_method=payment_method,
                    amount_paid=plan.price
                )

                # Ici, vous devrez intégrer l'API de paiement (Wave ou Orange Money)
                # Pour l'instant, on simule une transaction réussie

                # Simuler la génération d'une référence de transaction
                import uuid
                transaction_ref = f"PREMIUM-{uuid.uuid4().hex[:12].upper()}"
                subscription.transaction_reference = transaction_ref
                subscription.save()

                # Dans un environnement réel, vous devriez:
                # 1. Appeler l'API Wave ou Orange Money
                # 2. Obtenir une URL de paiement ou un code de transaction
                # 3. Retourner cette information au frontend
                # 4. Attendre la confirmation du paiement via webhook
                # 5. Activer l'abonnement une fois le paiement confirmé

                # Pour le développement, on active directement
                if request.data.get('auto_activate'):  # Mode développement
                    subscription.activate()

                return Response({
                    'message': 'Abonnement créé avec succès',
                    'subscription': PremiumSubscriptionSerializer(subscription).data,
                    'payment_info': {
                        'method': payment_method,
                        'phone': phone_number,
                        'amount': float(plan.price),
                        'reference': transaction_ref,
                        'instructions': self._get_payment_instructions(payment_method, phone_number, plan.price)
                    }
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la création de l\'abonnement: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _get_payment_instructions(self, method, phone, amount):
        """Générer les instructions de paiement selon la méthode"""
        if method == 'wave':
            return {
                'provider': 'Wave',
                'instructions': [
                    '1. Ouvrez votre application Wave',
                    f'2. Envoyez {amount} FCFA au numéro suivant',
                    '3. Confirmez le paiement',
                    '4. Votre abonnement sera activé automatiquement'
                ]
            }
        elif method == 'orange_money':
            return {
                'provider': 'Orange Money',
                'instructions': [
                    '1. Composez #144# sur votre téléphone',
                    '2. Sélectionnez "Transfert d\'argent"',
                    f'3. Envoyez {amount} FCFA au numéro indiqué',
                    '4. Confirmez avec votre code PIN',
                    '5. Votre abonnement sera activé automatiquement'
                ]
            }
        return {}


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_subscription(request, subscription_id):
    """Annuler un abonnement Premium"""
    subscription = get_object_or_404(
        PremiumSubscription,
        id=subscription_id,
        user=request.user
    )

    if subscription.status == 'cancelled':
        return Response(
            {'error': 'Cet abonnement est déjà annulé'},
            status=status.HTTP_400_BAD_REQUEST
        )

    subscription.status = 'cancelled'
    subscription.save()

    return Response({
        'message': 'Abonnement annulé avec succès',
        'subscription': PremiumSubscriptionSerializer(subscription).data
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def check_premium_status(request):
    """Vérifier le statut Premium de l'utilisateur"""
    user = request.user

    active_subscription = PremiumSubscription.objects.filter(
        user=user,
        status='active'
    ).first()

    data = {
        'is_premium': user.is_premium_active,
        'can_create_ad': user.can_create_ad,
        'remaining_ads': user.remaining_ads,
        'max_free_ads': user.MAX_FREE_ADS,
        'active_subscription': None
    }

    if active_subscription and active_subscription.is_active:
        data['active_subscription'] = PremiumSubscriptionSerializer(active_subscription).data

    return Response(data)