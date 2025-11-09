import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { Select } from 'primeng/select';
import { TagModule } from 'primeng/tag';
import { InputTextModule } from 'primeng/inputtext';
import { ConfirmDialogModule } from 'primeng/confirmdialog';
import { ToastModule } from 'primeng/toast';
import { ConfirmationService, MessageService } from 'primeng/api';
import { AnnonceService } from '../../service/annonce.service';

@Component({
  selector: 'app-my-annonce',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    FormsModule,
    ButtonModule,
    Select,
    TagModule,
    InputTextModule,
    ConfirmDialogModule,
    ToastModule
  ],
  providers: [ConfirmationService, MessageService],
  templateUrl: './my-annonce.html',
  styleUrl: './my-annonce.css'
})
export class MyAnnonce implements OnInit {
  ads: any[] = [];
  filteredAds: any[] = [];
  loading = true;

  // Filtres
  searchQuery: string = '';
  selectedStatus: string = '';
  sortBy: string = '-created_at';

  // Options de statut
  statusOptions = [
    { label: 'Tous les statuts', value: '' },
    { label: 'Active', value: 'active' },
    { label: 'Brouillon', value: 'draft' },
    { label: 'Vendu', value: 'sold' },
    { label: 'Expirée', value: 'expired' },
    { label: 'Suspendue', value: 'suspended' },
    { label: 'Rejetée', value: 'rejected' }
  ];

  // Options de tri
  sortOptions = [
    { label: 'Plus récentes', value: '-created_at' },
    { label: 'Plus anciennes', value: 'created_at' },
    { label: 'Plus vues', value: '-views_count' },
    { label: 'Plus de favoris', value: '-favorites_count' },
    { label: 'Prix croissant', value: 'price' },
    { label: 'Prix décroissant', value: '-price' }
  ];

  constructor(
    private annonceService: AnnonceService,
    private router: Router,
    private confirmationService: ConfirmationService,
    private messageService: MessageService
  ) {}

  ngOnInit(): void {
    this.loadMyAds();
  }

  /**
   * Charger mes annonces
   */
  loadMyAds(): void {
    this.loading = true;

    this.annonceService.getMyAds().subscribe({
      next: (response) => {
        this.ads = response;
        this.applyFilters();
        this.loading = false;
      },
      error: (error) => {
        console.error('Erreur lors du chargement des annonces:', error);
        this.messageService.add({
          severity: 'error',
          summary: 'Erreur',
          detail: 'Impossible de charger vos annonces'
        });
        this.loading = false;
      }
    });
  }

  /**
   * Appliquer les filtres
   */
  applyFilters(): void {
    let filtered = [...this.ads];

    // Filtre par statut
    if (this.selectedStatus) {
      filtered = filtered.filter(ad => ad.status === this.selectedStatus);
    }

    // Filtre par recherche
    if (this.searchQuery.trim()) {
      const query = this.searchQuery.toLowerCase().trim();
      filtered = filtered.filter(ad =>
        ad.title.toLowerCase().includes(query) ||
        ad.description?.toLowerCase().includes(query) ||
        ad.category_display?.toLowerCase().includes(query)
      );
    }

    // Tri
    filtered = this.sortAds(filtered, this.sortBy);

    this.filteredAds = filtered;
  }

  /**
   * Trier les annonces
   */
  sortAds(ads: any[], sortBy: string): any[] {
    const sorted = [...ads];
    const isDesc = sortBy.startsWith('-');
    const field = isDesc ? sortBy.substring(1) : sortBy;

    sorted.sort((a, b) => {
      let aValue = a[field];
      let bValue = b[field];

      // Gérer les dates
      if (field.includes('_at')) {
        aValue = new Date(aValue).getTime();
        bValue = new Date(bValue).getTime();
      }

      // Gérer les nombres
      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return isDesc ? bValue - aValue : aValue - bValue;
      }

      // Gérer les strings
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return isDesc
          ? bValue.localeCompare(aValue)
          : aValue.localeCompare(bValue);
      }

      return 0;
    });

    return sorted;
  }

  /**
   * Réinitialiser les filtres
   */
  resetFilters(): void {
    this.searchQuery = '';
    this.selectedStatus = '';
    this.sortBy = '-created_at';
    this.applyFilters();
  }

  /**
   * Modifier une annonce
   */
  editAd(adId: string): void {
    this.router.navigate(['/dashboard/edit-ad', adId]);
  }

  /**
   * Supprimer une annonce
   */
  deleteAd(ad: any): void {
    this.confirmationService.confirm({
      message: `Êtes-vous sûr de vouloir supprimer l'annonce "${ad.title}" ?`,
      header: 'Confirmation de suppression',
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Oui, supprimer',
      rejectLabel: 'Annuler',
      acceptButtonStyleClass: 'p-button-danger',
      accept: () => {
        this.annonceService.deleteAd(ad.id).subscribe({
          next: () => {
            this.messageService.add({
              severity: 'success',
              summary: 'Succès',
              detail: 'Annonce supprimée avec succès'
            });
            this.loadMyAds();
          },
          error: (error) => {
            console.error('Erreur lors de la suppression:', error);
            this.messageService.add({
              severity: 'error',
              summary: 'Erreur',
              detail: 'Impossible de supprimer l\'annonce'
            });
          }
        });
      }
    });
  }

  /**
   * Voir les détails d'une annonce
   */
  viewDetails(adId: string): void {
    this.router.navigate(['/annonces', adId]);
  }

  /**
   * Obtenir la sévérité du badge de statut
   */
  getStatusSeverity(status: string): 'success' | 'info' | 'warn' | 'danger' | 'secondary' {
    const severityMap: Record<string, 'success' | 'info' | 'warn' | 'danger' | 'secondary'> = {
      'active': 'success',
      'draft': 'info',
      'sold': 'secondary',
      'expired': 'warn',
      'suspended': 'danger',
      'rejected': 'danger'
    };
    return severityMap[status] || 'info';
  }

  /**
   * Obtenir le label du statut
   */
  getStatusLabel(status: string): string {
    const labelMap: Record<string, string> = {
      'active': 'Active',
      'draft': 'Brouillon',
      'sold': 'Vendu',
      'expired': 'Expirée',
      'suspended': 'Suspendue',
      'rejected': 'Rejetée'
    };
    return labelMap[status] || status;
  }

  /**
   * Formater le prix
   */
  formatPrice(price: number): string {
    if (!price) return '0 FCFA';
    return price.toLocaleString('fr-FR') + ' FCFA';
  }

  /**
   * Obtenir l'URL de l'image
   */
  getImageUrl(ad: any): string {
    return ad.primary_image || 'https://via.placeholder.com/400x300?text=Aucune+image';
  }

  /**
   * Formater la date
   */
  formatDate(dateString: string): string {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  /**
   * Vérifier si une annonce est expirée
   */
  isExpired(ad: any): boolean {
    if (!ad.expires_at) return false;
    return new Date(ad.expires_at) <= new Date();
  }
}
