import { Component, OnInit, OnDestroy, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink, RouterOutlet } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { AuthService, User } from '../service/auth';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    RouterOutlet,
    ButtonModule
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

  constructor(
    private router: Router,
    private authService: AuthService
  ) {}

  // --- 🟢 Cycle de vie : initialisation
  ngOnInit() {
    // Abonnement aux changements d’utilisateur
    this.userSubscription = this.authService.currentUser$.subscribe(user => {
      this.currentUser.set(user);
      if (!user) {
        this.router.navigate(['/login']);
      }
    });

    // Charger le profil si l’utilisateur est déjà connecté
    if (this.authService.isAuthenticated() && !this.currentUser()) {
      this.authService.getProfile().subscribe();
    }
  }

  // --- 🔴 Cycle de vie : destruction
  ngOnDestroy() {
    this.userSubscription?.unsubscribe();
    document.body.classList.remove('menu-open'); // sécurité
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
}
