import { Component, OnInit, OnDestroy, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import {Router, RouterLink, RouterLinkActive, RouterOutlet} from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { AuthService, User } from '../service/auth';
import { AnnonceService } from '../service/annonce.service';
import { AdvertisementService } from '../service/advertisement.service';
import { Subscription, forkJoin } from 'rxjs';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    RouterOutlet,
    ButtonModule,
    RouterLinkActive
  ],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css'
})
export class Dashboard implements OnInit, OnDestroy {
  // --- 👤 User & Auth
  currentUser = signal<User | null>(null);
  private userSubscription?: Subscription;

  // --- 📱 État du menu mobile
  isMobileMenuOpen = signal(false);

  // --- 📊 Statistiques utilisateur
  userStats = signal({
    totalAds: 0,
    activeAds: 0,
    totalViews: 0,
    totalAdvertisements: 0,
    activeAdvertisements: 0,
    remainingAds: 0
  });

  loading = signal(true);
  avatarError = false;
  avatarErrorMobile = false;

  constructor(
    private router: Router,
    private authService: AuthService,
    private annonceService: AnnonceService,
    private advertisementService: AdvertisementService
  ) {}

  // --- 🟢 Cycle de vie : initialisation
  ngOnInit() {
    // Abonnement aux changements d'utilisateur
    this.userSubscription = this.authService.currentUser$.subscribe(user => {
      this.currentUser.set(user);
      if (!user) {
        this.router.navigate(['/login']);
      } else {
        // Charger les statistiques quand l'utilisateur est disponible
        this.loadUserStats();
      }

      // DEBUG: Afficher l'avatar dans la console
      if (user) {
        console.log('Dashboard - User avatar:', user.avatar);
        console.log('Dashboard - User avatar_url:', (user as any).avatar_url);
      }
    });

    // Charger le profil si l'utilisateur est déjà connecté
    if (this.authService.isAuthenticated() && !this.currentUser()) {
      this.authService.getProfile().subscribe();
    }
  }

  // --- 🔴 Cycle de vie : destruction
  ngOnDestroy() {
    this.userSubscription?.unsubscribe();
    document.body.classList.remove('menu-open'); // sécurité
  }

  // --- 📊 Charger les statistiques utilisateur
  loadUserStats() {
    this.loading.set(true);

    forkJoin({
      myAds: this.annonceService.getMyAds(),
      myAdvertisements: this.advertisementService.getMyAdvertisements()
    }).subscribe({
      next: (results) => {
        const user = this.currentUser();

        // Calculer le nombre d'annonces actives
        const activeAds = results.myAds.filter((ad: any) => ad.status === 'active').length;

        // Calculer le nombre de publicités actives
        const activeAdvertisements = results.myAdvertisements.filter(
          (ad: any) => ad.is_active && ad.is_running
        ).length;

        // Calculer les vues totales
        const totalViews = results.myAds.reduce((sum: number, ad: any) => sum + (ad.views_count || 0), 0);

        this.userStats.set({
          totalAds: results.myAds.length,
          activeAds: activeAds,
          totalViews: totalViews,
          totalAdvertisements: results.myAdvertisements.length,
          activeAdvertisements: activeAdvertisements,
          remainingAds: user?.remaining_ads || 0
        });

        this.loading.set(false);
      },
      error: (error) => {
        console.error('Erreur lors du chargement des statistiques:', error);
        this.loading.set(false);
      }
    });
  }

  // --- 📱 Ouvrir / fermer le menu mobile
  toggleMobileMenu() {
    const newState = !this.isMobileMenuOpen();
    this.isMobileMenuOpen.set(newState);

    // Empêche le scroll de fond quand le menu est ouvert
    document.body.classList.toggle('menu-open', newState);
  }

  // --- 🔁 Accès simplifié pour le template
  mobileMenuOpen() {
    return this.isMobileMenuOpen();
  }

  // --- 🚪 Déconnexion
  logout() {
    if (confirm('Êtes-vous sûr de vouloir vous déconnecter ?')) {
      this.authService.logout();
      this.isMobileMenuOpen.set(false);
      document.body.classList.remove('menu-open');
    }
  }

  // --- 🧩 Initiales utilisateur
  getUserInitials(): string {
    const user = this.currentUser();
    if (!user) return '';

    const firstInitial = user.first_name?.charAt(0) || '';
    const lastInitial = user.last_name?.charAt(0) || '';
    return (firstInitial + lastInitial).toUpperCase();
  }

  // --- 🖼️ Méthode pour obtenir l'URL de l'avatar
  getUserAvatar(): string | null {
    const user = this.currentUser();
    if (!user) return null;

    // Essayer d'abord avatar_url (URL absolue du backend)
    if ((user as any).avatar_url) {
      return (user as any).avatar_url;
    }

    // Sinon utiliser avatar (peut être relatif)
    if (user.avatar) {
      // Si l'URL commence par http, la retourner telle quelle
      if (user.avatar.startsWith('http')) {
        return user.avatar;
      }
      // Sinon, construire l'URL complète
      return `http://localhost:8000${user.avatar}`;
    }

    return null;
  }

  // --- 📅 Formater la date de fin du premium
  getPremiumEndDate(): string {
    const user = this.currentUser();
    if (!user || !user.premium_end_date) return '';

    const endDate = new Date(user.premium_end_date);
    return endDate.toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }

  // --- 📊 Calculer le pourcentage d'utilisation des annonces
  getAdsUsagePercentage(): number {
    const user = this.currentUser();
    if (!user || user.is_premium_active) return 0;

    const maxAds = 5; // MAX_FREE_ADS
    const usedAds = this.userStats().activeAds;
    return Math.min(100, (usedAds / maxAds) * 100);
  }
}
