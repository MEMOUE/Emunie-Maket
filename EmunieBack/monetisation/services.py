from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

class PaymentService:
    """Service pour gérer les paiements avec différents providers"""
    
    def __init__(self):
        self.base_url = getattr(settings, 'PAYMENT_BASE_URL', 'https://api.payment-provider.com')
        self.api_key = getattr(settings, 'PAYMENT_API_KEY', '')
    
    def initiate_payment(self, transaction):
        """Initier un paiement selon la méthode choisie"""
        # Version simplifiée pour le développement
        return {
            'success': True,
            'reference': transaction.reference,
            'payment_url': f"https://payment-simulator.com/pay/{transaction.reference}",
            'instructions': f"Simulateur: Composez *123*{transaction.total_amount}*{transaction.reference}# pour payer"
        }
    
    def verify_payment(self, reference):
        """Vérifier le statut d'un paiement"""
        # Version simplifiée
        return {
            'success': True,
            'status': 'completed',
            'reference': reference
        }

class NotificationService:
    """Service pour envoyer des notifications"""
    
    @staticmethod
    def send_payment_success(transaction):
        """Envoyer une notification de paiement réussi"""
        try:
            subject = f"Paiement confirmé - {transaction.reference}"
            message = f"""
            Bonjour {transaction.user.first_name or transaction.user.username},
            
            Votre paiement de {transaction.total_amount} {transaction.currency} a été confirmé.
            Référence: {transaction.reference}
            
            Merci d'utiliser notre plateforme !
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[transaction.user.email],
                fail_silently=True
            )
            
        except Exception as e:
            print(f"Erreur envoi notification succès: {e}")
    
    @staticmethod
    def send_payment_failure(transaction):
        """Envoyer une notification d'échec de paiement"""
        try:
            subject = f"Échec de paiement - {transaction.reference}"
            message = f"""
            Bonjour {transaction.user.first_name or transaction.user.username},
            
            Votre paiement de {transaction.total_amount} {transaction.currency} n'a pas pu être traité.
            Référence: {transaction.reference}
            Raison: {transaction.failure_reason}
            
            Veuillez réessayer ou nous contacter.
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[transaction.user.email],
                fail_silently=True
            )
            
        except Exception as e:
            print(f"Erreur envoi notification échec: {e}")
    
    @staticmethod
    def send_subscription_expiry_warning(subscription):
        """Avertir de l'expiration prochaine d'un abonnement"""
        try:
            days_remaining = (subscription.end_date - timezone.now()).days
            
            subject = f"Votre abonnement expire dans {days_remaining} jour(s)"
            message = f"""
            Bonjour {subscription.user.first_name or subscription.user.username},
            
            Votre abonnement {subscription.package.name} expire le {subscription.end_date.strftime('%d/%m/%Y')}.
            
            Renouvelez dès maintenant pour continuer à bénéficier de nos services premium.
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[subscription.user.email],
                fail_silently=True
            )
            
        except Exception as e:
            print(f"Erreur envoi notification expiration: {e}")

class AnalyticsService:
    """Service pour les analyses et statistiques"""
    
    @staticmethod
    def calculate_daily_revenue():
        """Calculer les revenus quotidiens"""
        from django.db.models import Sum
        from .models import Revenue, Transaction
        
        today = timezone.now().date()
        
        # Revenus par type
        transactions_today = Transaction.objects.filter(
            created_at__date=today,
            status='completed'
        )
        
        package_revenue = transactions_today.filter(
            transaction_type='package_purchase'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        boost_revenue = transactions_today.filter(
            transaction_type='ad_boost'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        subscription_revenue = transactions_today.filter(
            transaction_type='subscription'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        total_revenue = package_revenue + boost_revenue + subscription_revenue
        
        # Comptes
        transactions_count = transactions_today.count()
        
        # Créer ou mettre à jour l'enregistrement de revenus
        revenue, created = Revenue.objects.get_or_create(
            date=today,
            defaults={
                'package_revenue': package_revenue,
                'boost_revenue': boost_revenue,
                'subscription_revenue': subscription_revenue,
                'total_revenue': total_revenue,
                'transactions_count': transactions_count,
                'new_subscriptions': 0,
                'ad_boosts': 0
            }
        )
        
        if not created:
            # Mettre à jour si l'enregistrement existe déjà
            revenue.package_revenue = package_revenue
            revenue.boost_revenue = boost_revenue
            revenue.subscription_revenue = subscription_revenue
            revenue.total_revenue = total_revenue
            revenue.transactions_count = transactions_count
            revenue.save()
        
        return revenue