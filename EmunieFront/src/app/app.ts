import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';

@Component({
  selector: 'app-root',
  imports: [
    RouterOutlet,
    CommonModule,
    ButtonModule,
    InputTextModule
  ],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected readonly title = signal('Emunie-Market');
  protected activeTab = signal('accueil');
  protected mobileMenuOpen = signal(false);

  setActiveTab(tab: string) {
    this.activeTab.set(tab);
    this.mobileMenuOpen.set(false);
  }

  toggleMobileMenu() {
    this.mobileMenuOpen.update(value => !value);
  }
}
