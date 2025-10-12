import { Component, signal } from '@angular/core';
import {Router, RouterLink, RouterOutlet} from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { Footer } from './footer/footer';

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
export class App {
  protected readonly title = signal('Emunie-Market');
  protected activeTab = signal('accueil');
  protected mobileMenuOpen = signal(false);
  protected searchQuery = signal('');

  constructor(private router: Router) {}

  setActiveTab(tab: string) {
    this.activeTab.set(tab);
    this.mobileMenuOpen.set(false);

    // Navigation vers la route correspondante
    this.router.navigate([tab]);
  }

  toggleMobileMenu() {
    this.mobileMenuOpen.update(value => !value);
  }

  onSearch() {
    console.log('Recherche:', this.searchQuery());
    // Implémenter la logique de recherche
  }
}
