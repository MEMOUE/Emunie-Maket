from rest_framework import serializers
from .models import PremiumPlan, PremiumSubscription


class PremiumPlanSerializer(serializers.ModelSerializer):
    """Serializer pour les plans Premium"""

    class Meta:
        model = PremiumPlan
        fields = (
            'id', 'name', 'plan_type', 'price', 'currency',
            'max_ads', 'duration_days', 'description', 'features'
        )


class PremiumSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer pour les abonnements Premium"""
    plan = PremiumPlanSerializer(read_only=True)
    plan_id = serializers.IntegerField(write_only=True)
    is_active = serializers.ReadOnlyField()
    days_remaining = serializers.ReadOnlyField()

    class Meta:
        model = PremiumSubscription
        fields = (
            'id', 'plan', 'plan_id', 'status', 'start_date', 'end_date',
            'created_at', 'payment_method', 'transaction_reference',
            'amount_paid', 'is_active', 'days_remaining'
        )
        read_only_fields = ('status', 'start_date', 'end_date', 'created_at')


class SubscribeToPremiumSerializer(serializers.Serializer):
    """Serializer pour s'abonner au Premium"""
    plan_id = serializers.IntegerField()
    payment_method = serializers.ChoiceField(
        choices=['wave', 'orange_money'],
        help_text='Méthode de paiement: wave ou orange_money'
    )
    phone_number = serializers.CharField(
        max_length=20,
        help_text='Numéro de téléphone pour le paiement'
    )

    def validate_plan_id(self, value):
        """Valider que le plan existe et est actif"""
        try:
            plan = PremiumPlan.objects.get(id=value, is_active=True)
        except PremiumPlan.DoesNotExist:
            raise serializers.ValidationError("Plan Premium introuvable ou inactif")
        return value

    def validate_phone_number(self, value):
        """Valider le format du numéro de téléphone"""
        # Enlever les espaces et caractères spéciaux
        phone = ''.join(filter(str.isdigit, value))

        if not phone:
            raise serializers.ValidationError("Numéro de téléphone invalide")

        # Vérifier le format ivoirien
        if not (phone.startswith('225') or phone.startswith('07') or phone.startswith('05') or phone.startswith('01')):
            raise serializers.ValidationError(
                "Format invalide. Utilisez un numéro ivoirien (ex: 07XXXXXXXX ou 22507XXXXXXXX)"
            )

        return phone