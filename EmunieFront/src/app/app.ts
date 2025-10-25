import { Component, signal, OnInit, OnDestroy } from '@angular/core';
import { Router, RouterLink, RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { AuthService, User } from './service/auth';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-root',
  imports: [
    RouterOutlet,
    CommonModule,
    FormsModule,
    ButtonModule,
    InputTextModule,
    RouterLink,
  ],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App implements OnInit, OnDestroy {
  protected readonly title = signal('Emunie-Market');
  protected activeTab = signal('accueil');
  protected mobileMenuOpen = signal(false);
  protected searchQuery = signal('');
  protected currentUser = signal<User | null>(null);
  protected isAuthenticated = signal(false);

  private userSubscription?: Subscription;

  constructor(
    private router: Router,
    private authService: AuthService
  ) {}

  ngOnInit() {
    // S'abonner aux changements d'utilisateur
    this.userSubscription = this.authService.currentUser$.subscribe(user => {
      this.currentUser.set(user);
      this.isAuthenticated.set(!!user);

      // DEBUG: Afficher l'avatar dans la console
      if (user) {
        console.log('User avatar:', user.avatar);
        console.log('User avatar_url:', (user as any).avatar_url);
      }
    });

    // Vérifier l'authentification au démarrage
    if (this.authService.isAuthenticated() && !this.currentUser()) {
      this.authService.getProfile().subscribe();
    }
  }

  ngOnDestroy() {
    this.userSubscription?.unsubscribe();
  }

  setActiveTab(tab: string) {
    this.activeTab.set(tab);
    this.mobileMenuOpen.set(false);
    this.router.navigate([tab]);
  }

  toggleMobileMenu() {
    this.mobileMenuOpen.update(value => !value);
  }

  onSearch() {
    const query = this.searchQuery().trim();
    if (query) {
      // Naviguer vers la page de recherche avec le paramètre de requête
      this.router.navigate(['/search'], {
        queryParams: { q: query }
      });
      // Réinitialiser le champ de recherche après navigation
      this.searchQuery.set('');
    }
  }

  logout() {
    this.authService.logout();
    this.mobileMenuOpen.set(false);
  }

  getUserInitials(): string {
    const user = this.currentUser();
    if (!user) return '';

    const firstInitial = user.first_name?.charAt(0) || '';
    const lastInitial = user.last_name?.charAt(0) || '';
    return (firstInitial + lastInitial).toUpperCase();
  }

  // CORRECTION : Méthode pour obtenir l'URL de l'avatar
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

  avatarError = false;
  avatarErrorMobile = false;


}
