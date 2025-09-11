from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Package, UserSubscription, AdBoost, PaymentMethod, 
    Transaction, Coupon, CouponUsage, Revenue
)

User = get_user_model()

class PackageSerializer(serializers.ModelSerializer):
    """Serializer pour les packages"""
    is_popular = serializers.SerializerMethodField()
    savings_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Package
        fields = (
            'id', 'name', 'package_type', 'description', 'price', 'currency',
            'duration_days', 'boost_multiplier', 'max_ads', 'priority_support',
            'featured_placement', 'unlimited_photos', 'video_upload',
            'is_popular', 'savings_percentage', 'is_active'
        )
    
    def get_is_popular(self, obj):
        # Marquer comme populaire les packages les plus achetés
        return obj.package_type in ['boost', 'featured']
    
    def get_savings_percentage(self, obj):
        # Calculer les économies par rapport au prix unitaire
        if obj.duration_days > 30:
            daily_rate = obj.price / obj.duration_days
            standard_daily_rate = 1000  # Prix de référence
            if daily_rate < standard_daily_rate:
                return round(((standard_daily_rate - daily_rate) / standard_daily_rate) * 100)
        return 0

class UserSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer pour les abonnements utilisateur"""
    package_name = serializers.CharField(source='package.name', read_only=True)
    package_type = serializers.CharField(source='package.package_type', read_only=True)
    days_remaining = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    usage_stats = serializers.SerializerMethodField()
    
    class Meta:
        model = UserSubscription
        fields = (
            'id', 'package', 'package_name', 'package_type', 'status',
            'start_date', 'end_date', 'auto_renew', 'days_remaining',
            'is_active', 'ads_boosted', 'ads_featured', 'usage_stats',
            'created_at'
        )
        read_only_fields = ('id', 'created_at', 'ads_boosted', 'ads_featured')
    
    def get_usage_stats(self, obj):
        return {
            'ads_boosted': obj.ads_boosted,
            'ads_featured': obj.ads_featured,
            'max_ads_allowed': obj.package.max_ads,
            'boost_multiplier': obj.package.boost_multiplier,
        }

class AdBoostSerializer(serializers.ModelSerializer):
    """Serializer pour les boosts d'annonces"""
    ad_title = serializers.CharField(source='ad.title', read_only=True)
    package_name = serializers.CharField(source='package.name', read_only=True)
    is_expired = serializers.ReadOnlyField()
    effectiveness = serializers.SerializerMethodField()
    
    class Meta:
        model = AdBoost
        fields = (
            'id', 'ad', 'ad_title', 'boost_type', 'package', 'package_name',
            'price_paid', 'currency', 'start_date', 'end_date', 'is_active',
            'is_expired', 'views_before', 'views_after', 'contacts_before',
            'contacts_after', 'effectiveness', 'created_at'
        )
        read_only_fields = ('id', 'user', 'created_at')
    
    def get_effectiveness(self, obj):
        views_increase = obj.views_after - obj.views_before
        contacts_increase = obj.contacts_after - obj.contacts_before
        return {
            'views_increase': views_increase,
            'contacts_increase': contacts_increase,
            'views_increase_percentage': (views_increase / max(obj.views_before, 1)) * 100,
            'contacts_increase_percentage': (contacts_increase / max(obj.contacts_before, 1)) * 100,
        }

class PaymentMethodSerializer(serializers.ModelSerializer):
    """Serializer pour les méthodes de paiement"""
    class Meta:
        model = PaymentMethod
        fields = (
            'id', 'name', 'payment_type', 'provider', 'logo',
            'is_active', 'processing_fee', 'order'
        )

class TransactionSerializer(serializers.ModelSerializer):
    """Serializer pour les transactions"""
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    package_name = serializers.CharField(source='package.name', read_only=True)
    payment_method_name = serializers.CharField(source='payment_method.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Transaction
        fields = (
            'id', 'reference', 'external_reference', 'user', 'user_name',
            'package', 'package_name', 'payment_method', 'payment_method_name',
            'amount', 'currency', 'processing_fee', 'total_amount',
            'status', 'status_display', 'transaction_type', 'description',
            'phone_number', 'failure_reason', 'created_at', 'processed_at',
            'completed_at'
        )
        read_only_fields = (
            'id', 'reference', 'external_reference', 'user', 'total_amount',
            'created_at', 'processed_at', 'completed_at'
        )

class TransactionCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer une transaction"""
    coupon_code = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = Transaction
        fields = (
            'package', 'payment_method', 'phone_number', 'coupon_code'
        )
    
    def validate(self, attrs):
        # Valider le package
        package = attrs.get('package')
        if not package or not package.is_active:
            raise serializers.ValidationError("Package invalide ou inactif")
        
        # Valider la méthode de paiement
        payment_method = attrs.get('payment_method')
        if not payment_method or not payment_method.is_active:
            raise serializers.ValidationError("Méthode de paiement invalide ou inactive")
        
        # Valider le numéro de téléphone pour Mobile Money
        if payment_method.payment_type in ['mobile_money', 'orange_money', 'mtn_money', 'moov_money']:
            phone_number = attrs.get('phone_number')
            if not phone_number:
                raise serializers.ValidationError("Numéro de téléphone requis pour Mobile Money")
        
        return attrs
    
    def create(self, validated_data):
        coupon_code = validated_data.pop('coupon_code', None)
        user = self.context['request'].user
        package = validated_data['package']
        payment_method = validated_data['payment_method']
        
        # Calculer les montants
        amount = package.price
        processing_fee = amount * (payment_method.processing_fee / 100)
        discount_amount = 0
        
        # Appliquer le coupon si fourni
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code, is_active=True)
                if coupon.is_valid:
                    discount_amount = coupon.calculate_discount(amount)
                    amount -= discount_amount
            except Coupon.DoesNotExist:
                raise serializers.ValidationError("Code de réduction invalide")
        
        total_amount = amount + processing_fee
        
        # Générer une référence unique
        import uuid
        reference = f"EMU-{uuid.uuid4().hex[:8].upper()}"
        
        # Créer la transaction
        transaction = Transaction.objects.create(
            reference=reference,
            user=user,
            amount=amount,
            processing_fee=processing_fee,
            total_amount=total_amount,
            transaction_type='package_purchase',
            **validated_data
        )
        
        # Enregistrer l'utilisation du coupon
        if coupon_code and discount_amount > 0:
            CouponUsage.objects.create(
                coupon=coupon,
                user=user,
                transaction=transaction,
                discount_amount=discount_amount
            )
            coupon.current_uses += 1
            coupon.save()
        
        return transaction

class CouponSerializer(serializers.ModelSerializer):
    """Serializer pour les coupons"""
    is_valid = serializers.ReadOnlyField()
    uses_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = Coupon
        fields = (
            'id', 'code', 'name', 'description', 'discount_type',
            'discount_value', 'max_discount', 'min_amount', 'max_uses',
            'max_uses_per_user', 'current_uses', 'uses_remaining',
            'valid_from', 'valid_until', 'is_valid', 'new_users_only'
        )
    
    def get_uses_remaining(self, obj):
        if obj.max_uses:
            return obj.max_uses - obj.current_uses
        return None

class CouponValidationSerializer(serializers.Serializer):
    """Serializer pour valider un coupon"""
    code = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    def validate(self, attrs):
        code = attrs['code']
        amount = attrs['amount']
        
        try:
            coupon = Coupon.objects.get(code=code, is_active=True)
        except Coupon.DoesNotExist:
            raise serializers.ValidationError("Code de réduction invalide")
        
        if not coupon.is_valid:
            raise serializers.ValidationError("Code de réduction expiré ou invalide")
        
        if coupon.min_amount and amount < coupon.min_amount:
            raise serializers.ValidationError(f"Montant minimum requis: {coupon.min_amount} {coupon.currency}")
        
        user = self.context['request'].user
        user_usage = coupon.usages.filter(user=user).count()
        if user_usage >= coupon.max_uses_per_user:
            raise serializers.ValidationError("Limite d'utilisation atteinte pour ce coupon")
        
        attrs['coupon'] = coupon
        attrs['discount_amount'] = coupon.calculate_discount(amount)
        
        return attrs

class RevenueSerializer(serializers.ModelSerializer):
    """Serializer pour les revenus"""
    growth_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = Revenue
        fields = (
            'date', 'package_revenue', 'boost_revenue', 'subscription_revenue',
            'total_revenue', 'transactions_count', 'new_subscriptions',
            'ad_boosts', 'growth_rate'
        )
    
    def get_growth_rate(self, obj):
        # Calculer le taux de croissance par rapport au jour précédent
        try:
            from datetime import timedelta
            previous_day = Revenue.objects.get(date=obj.date - timedelta(days=1))
            if previous_day.total_revenue > 0:
                return ((obj.total_revenue - previous_day.total_revenue) / previous_day.total_revenue) * 100
        except Revenue.DoesNotExist:
            pass
        return 0

class PaymentCallbackSerializer(serializers.Serializer):
    """Serializer pour les callbacks de paiement"""
    reference = serializers.CharField()
    external_reference = serializers.CharField(required=False)
    status = serializers.ChoiceField(choices=['completed', 'failed', 'cancelled'])
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    currency = serializers.CharField(default='XOF')
    failure_reason = serializers.CharField(required=False, allow_blank=True)
    
    def validate_reference(self, value):
        try:
            Transaction.objects.get(reference=value)
        except Transaction.DoesNotExist:
            raise serializers.ValidationError("Référence de transaction introuvable")
        return value