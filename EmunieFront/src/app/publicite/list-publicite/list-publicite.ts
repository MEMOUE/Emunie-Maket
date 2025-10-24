import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MessageService, ConfirmationService } from 'primeng/api';
import { AdvertisementService } from '../../service/advertisement.service';
import { Advertisement } from '../../model/advertisement.model';
import { Toast } from 'primeng/toast';
import { ConfirmDialog } from 'primeng/confirmdialog';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { TagModule } from 'primeng/tag';

@Component({
  selector: 'app-list-publicite',
  templateUrl: './list-publicite.html',
  styleUrls: ['./list-publicite.css'],
  standalone: true,
  imports: [
    CommonModule,
    ButtonModule,
    CardModule,
    TagModule,
    Toast,
    ConfirmDialog
  ],
  providers: [MessageService, ConfirmationService]
})
export class ListPublicite implements OnInit {
  advertisements = signal<Advertisement[]>([]);
  loading = signal(false);

  constructor(
    private advertisementService: AdvertisementService,
    private router: Router,
    private messageService: MessageService,
    private confirmationService: ConfirmationService
  ) {}

  ngOnInit(): void {
    this.loadAdvertisements();
  }

  loadAdvertisements(): void {
    this.loading.set(true);
    this.advertisementService.getMyAdvertisements().subscribe({
      next: (ads) => {
        this.advertisements.set(ads);
        this.loading.set(false);
      },
      error: (error) => {
        this.messageService.add({
          severity: 'error',
          summary: 'Erreur',
          detail: 'Impossible de charger vos publicités'
        });
        this.loading.set(false);
      }
    });
  }

  getStatusSeverity(ad: Advertisement): "success" | "info" | "warn" | "secondary" | "contrast" | "danger" | null {
    switch (ad.status) {
      case 'active':
        return 'success';
      case 'pending':
        return 'info';
      case 'expired':
        return 'warn';
      case 'rejected':
        return 'danger';
      default:
        return null;
    }
  }


  getStatusLabel(ad: Advertisement): string {
    if (ad.is_running) return 'En cours';
    if (ad.is_approved && !ad.is_running) return 'Programmée';
    if (!ad.is_approved) return 'En attente';
    return 'Inactive';
  }

  viewStatistics(ad: Advertisement): void {
    if (!ad.id) return;

    this.advertisementService.getStatistics(ad.id).subscribe({
      next: (stats) => {
        // Afficher les statistiques dans un message
        this.messageService.add({
          severity: 'info',
          summary: `Statistiques - ${ad.title}`,
          detail: `Impressions: ${stats.impressions} | Clics: ${stats.clicks} | CTR: ${stats.ctr.toFixed(2)}%`,
          life: 5000
        });
      },
      error: (error) => {
        this.messageService.add({
          severity: 'error',
          summary: 'Erreur',
          detail: 'Impossible de charger les statistiques'
        });
      }
    });
  }

  deleteAdvertisement(ad: Advertisement): void {
    if (!ad.id) return;

    this.confirmationService.confirm({
      message: `Êtes-vous sûr de vouloir supprimer la publicité "${ad.title}" ?`,
      header: 'Confirmation de suppression',
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Oui, supprimer',
      rejectLabel: 'Annuler',
      acceptButtonStyleClass: 'p-button-danger',
      accept: () => {
        this.advertisementService.delete(ad.id!).subscribe({
          next: () => {
            this.messageService.add({
              severity: 'success',
              summary: 'Suppression réussie',
              detail: 'La publicité a été supprimée avec succès'
            });
            this.loadAdvertisements();
          },
          error: (error) => {
            this.messageService.add({
              severity: 'error',
              summary: 'Erreur',
              detail: 'Impossible de supprimer la publicité'
            });
          }
        });
      }
    });
  }

  createNew(): void {
    this.router.navigate(['/dashboard/buy-pub']);
  }

  getRemainingDays(ad: Advertisement): number {
    if (!ad.end_date) return 0;
    const end = new Date(ad.end_date);
    const now = new Date();
    const diff = end.getTime() - now.getTime();
    return Math.ceil(diff / (1000 * 60 * 60 * 24));
  }

  formatDate(date: string): string {
    return new Date(date).toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  }
}
