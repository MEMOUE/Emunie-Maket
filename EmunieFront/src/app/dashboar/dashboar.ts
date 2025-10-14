import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

// ✅ PrimeNG 20 imports
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { Tabs, Tab } from 'primeng/tabs';
import { TableModule } from 'primeng/table';
import { TagModule } from 'primeng/tag';
import { DialogModule } from 'primeng/dialog';
import { InputTextModule } from 'primeng/inputtext';

import { AuthService, User } from '../service/auth';

interface Ad {
  id: number;
  title: string;
  price: number;
  category: string;
  status: 'active' | 'pending' | 'expired' | 'rejected';
  views: number;
  favorites: number;
  created_at: string;
  is_promoted: boolean;
  promotion_end?: string;
}

interface PremiumPlan {
  id: string;
  name: string;
  price: number;
  duration: string;
  features: string[];
  popular?: boolean;
  ads_limit: number;
  promotion_bonus: number;
}

@Component({
  selector: 'app-dashboar',
  standalone: true,
  imports: [
    CommonModule,
    ButtonModule,
    CardModule,
    TableModule,
    TagModule,
    DialogModule,
    InputTextModule,
    Tab
  ],
  templateUrl: './dashboar.html',
  styleUrl: './dashboar.css'
})
export class Dashboar implements OnInit {
  currentUser = signal<User | null>(null);
  activeTab = signal(0);

  stats = signal({
    totalAds: 0,
    activeAds: 0,
    totalViews: 0,
    totalFavorites: 0,
    pendingAds: 0
  });

  myAds = signal<Ad[]>([]);

  premiumPlans: PremiumPlan[] = [
    {
      id: 'starter',
      name: 'Starter',
      price: 5000,
      duration: '1 mois',
      ads_limit: 20,
      promotion_bonus: 2,
      features: [
        '20 annonces par mois',
        '2 promotions gratuites',
        'Badge Premium',
        'Support prioritaire',
        'Statistiques détaillées'
      ]
    },
    {
      id: 'pro',
      name: 'Professionnel',
      price: 12000,
      duration: '3 mois',
      ads_limit: 75,
      promotion_bonus: 10,
      popular: true,
      features: [
        '75 annonces (25/mois)',
        '10 promotions gratuites',
        'Badge Premium Gold',
        'Support prioritaire 24/7',
        'Statistiques avancées',
        'Mise en avant homepage',
        'Réduction 20% sur publicités'
      ]
    },
    {
      id: 'business',
      name: 'Business',
      price: 20000,
      duration: '6 mois',
      ads_limit: 200,
      promotion_bonus: 30,
      features: [
        '200 annonces illimitées',
        '30 promotions gratuites',
        'Badge Premium Platinum',
        'Support dédié 24/7',
        'Statistiques complètes + export',
        'Mise en avant permanente',
        'Réduction 40% sur publicités',
        'API accès pour intégration'
      ]
    }
  ];

  promotions = [
    { id: 'boost_1d', name: 'Boost 24h', price: 1000, duration: '24 heures', description: 'Mettez votre annonce en avant pendant 24h', icon: 'pi-bolt', color: 'orange' },
    { id: 'boost_3d', name: 'Boost 3 jours', price: 2500, duration: '3 jours', description: 'Visibilité maximale pendant 3 jours', icon: 'pi-star', color: 'yellow', popular: true },
    { id: 'boost_7d', name: 'Boost 7 jours', price: 5000, duration: '7 jours', description: 'Top position pendant une semaine complète', icon: 'pi-crown', color: 'purple' },
    { id: 'featured', name: 'À la Une', price: 3500, duration: '7 jours', description: 'Apparaît dans la section "À la Une" de la homepage', icon: 'pi-trophy', color: 'gold' }
  ];

  showPremiumDialog = signal(false);
  showPromotionDialog = signal(false);
  selectedAd = signal<Ad | null>(null);
  selectedPlan = signal<PremiumPlan | null>(null);

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit() {
    this.authService.currentUser$.subscribe(user => {
      this.currentUser.set(user);
      if (user) this.loadUserData();
      else this.router.navigate(['/login']);
    });
  }

  loadUserData() {
    this.loadStats();
    this.loadMyAds();
  }

  loadStats() {
    const user = this.currentUser();
    if (user) {
      this.stats.set({
        totalAds: user.total_ads || 0,
        activeAds: Math.floor((user.total_ads || 0) * 0.8),
        totalViews: user.total_views || 0,
        totalFavorites: Math.floor((user.total_views || 0) * 0.1),
        pendingAds: Math.floor((user.total_ads || 0) * 0.2)
      });
    }
  }

  loadMyAds() {
    this.myAds.set([
      {
        id: 1,
        title: 'iPhone 15 Pro Max 256GB',
        price: 850000,
        category: 'Électronique',
        status: 'active',
        views: 456,
        favorites: 23,
        created_at: '2025-10-10',
        is_promoted: true,
        promotion_end: '2025-10-17'
      },
      {
        id: 2,
        title: 'MacBook Pro M3 2024',
        price: 1200000,
        category: 'Électronique',
        status: 'active',
        views: 789,
        favorites: 45,
        created_at: '2025-10-08',
        is_promoted: false
      },
      {
        id: 3,
        title: 'Appartement F3 Cocody',
        price: 250000,
        category: 'Immobilier',
        status: 'pending',
        views: 0,
        favorites: 0,
        created_at: '2025-10-14',
        is_promoted: false
      }
    ]);
  }

  getStatusSeverity(status: string): 'success' | 'warning' | 'danger' | 'info' {
    const map = { active: 'success', pending: 'warning', expired: 'danger', rejected: 'danger' } as const;
    return map[status] || 'info';
  }

  getStatusLabel(status: string): string {
    const map = { active: 'Active', pending: 'En attente', expired: 'Expirée', rejected: 'Rejetée' };
    return map[status] || status;
  }

  formatPrice(price: number): string {
    return price.toLocaleString('fr-FR') + ' FCFA';
  }

  formatDate(date: string): string {
    return new Date(date).toLocaleDateString('fr-FR');
  }

  openPremiumDialog(plan?: PremiumPlan) {
    if (plan) this.selectedPlan.set(plan);
    this.showPremiumDialog.set(true);
  }

  openPromotionDialog(ad: Ad) {
    this.selectedAd.set(ad);
    this.showPromotionDialog.set(true);
  }

  subscribeToPremium(plan: PremiumPlan) {
    alert(`Redirection vers le paiement de ${this.formatPrice(plan.price)} pour le plan ${plan.name}`);
  }

  promoteAd(ad: Ad, promotion: any) {
    alert(`Promotion de "${ad.title}" avec ${promotion.name} - ${this.formatPrice(promotion.price)}`);
    this.showPromotionDialog.set(false);
  }

  editAd(ad: Ad) {
    console.log('Éditer annonce:', ad);
  }

  deleteAd(ad: Ad) {
    if (confirm(`Supprimer "${ad.title}" ?`)) {
      console.log('Suppression', ad);
    }
  }

  createNewAd() {
    this.router.navigate(['/create-ad']);
  }
}
