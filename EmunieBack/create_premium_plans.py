"""
Script pour créer les plans Premium par défaut

Exécuter avec: python manage.py shell < create_premium_plans.py
"""

from premium.models import PremiumPlan

# Supprimer les anciens plans (optionnel)
PremiumPlan.objects.all().delete()

# Créer le plan Basic
basic_plan = PremiumPlan.objects.create(
    name='Premium Basic',
    plan_type='basic',
    price=5000,
    currency='XOF',
    max_ads=100,
    duration_days=30,
    description='Idéal pour les vendeurs réguliers',
    features=[
        '100 annonces actives simultanées',
        'Badge Premium ⭐',
        'Visibilité prioritaire dans les recherches',
        'Support prioritaire par email',
        'Statistiques avancées de vos annonces',
        'Pas de publicités sur vos annonces'
    ],
    is_active=True,
    order=1
)

# Créer le plan Unlimited
unlimited_plan = PremiumPlan.objects.create(
    name='Premium Illimité',
    plan_type='unlimited',
    price=10000,
    currency='XOF',
    max_ads=None,  # Illimité
    duration_days=30,
    description='Pour les professionnels et vendeurs intensifs',
    features=[
        'Annonces ILLIMITÉES',
        'Badge Premium ⭐ mis en avant',
        'Visibilité maximale dans toutes les recherches',
        'Support prioritaire par téléphone et email',
        'Statistiques avancées en temps réel',
        'Pas de publicités',
        'Mise en avant automatique de vos annonces',
        'Accès anticipé aux nouvelles fonctionnalités'
    ],
    is_active=True,
    order=2
)

print("✅ Plans Premium créés avec succès!")
print(f"   - {basic_plan.name}: {basic_plan.price} {basic_plan.currency} ({basic_plan.max_ads} annonces)")
print(f"   - {unlimited_plan.name}: {unlimited_plan.price} {unlimited_plan.currency} (Illimité)")