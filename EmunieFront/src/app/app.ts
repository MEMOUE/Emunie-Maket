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
    console.log('Recherche:', this.searchQuery());
    // Implémenter la logique de recherche
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
}
