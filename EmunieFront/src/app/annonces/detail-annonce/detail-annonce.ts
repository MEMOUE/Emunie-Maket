import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { GalleriaModule } from 'primeng/galleria';
import { AnnonceService } from '../../service/annonce.service';
import { AuthService } from '../../service/auth';

@Component({
  selector: 'app-detail-annonce',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    ButtonModule,
    GalleriaModule
  ],
  templateUrl: './detail-annonce.html',
  styleUrls: ['./detail-annonce.css']
})
export class DetailAnnonce implements OnInit {
  ad: any = null;
  relatedAds: any[] = [];
  loading = true;
  adId: string = '';
  currentImageIndex = 0;
  isOwner = false;
  isAuthenticated = false;

  responsiveOptions = [
    {
      breakpoint: '1024px',
      numVisible: 5
    },
    {
      breakpoint: '768px',
      numVisible: 3
    },
    {
      breakpoint: '560px',
      numVisible: 1
    }
  ];

  constructor(
    private route: ActivatedRoute,
    public router: Router,
    private annonceService: AnnonceService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.isAuthenticated = this.authService.isAuthenticated();

    this.route.params.subscribe(params => {
      this.adId = params['id'];
      if (this.adId) {
        this.loadAdDetails();
      }
    });
  }

  /**
   * Charger les détails de l'annonce
   */
  loadAdDetails(): void {
    this.loading = true;

    this.annonceService.getAdDetail(this.adId).subscribe({
      next: (response) => {
        this.ad = response;
        this.relatedAds = response.related_ads || [];
        this.isOwner = response.is_owner || false;
        this.loading = false;

        // Scroll vers le haut
        window.scrollTo({ top: 0, behavior: 'smooth' });
      },
      error: (error) => {
        console.error('Erreur lors du chargement de l\'annonce:', error);
        this.loading = false;

        // Rediriger si l'annonce n'existe pas
        if (error.status === 404) {
          this.router.navigate(['/annonces']);
        }
      }
    });
  }

  /**
   * ✅ NOUVELLE MÉTHODE: Obtenir le numéro WhatsApp à utiliser
   * Priorité: whatsapp_number de l'annonce > phone_number du user
   */
  getWhatsAppNumber(): string | null {
    // 1. Si l'annonce a un numéro WhatsApp spécifique, l'utiliser
    if (this.ad.whatsapp_number) {
      return this.ad.whatsapp_number;
    }

    // 2. Sinon, utiliser le numéro du propriétaire
    if (this.ad.user?.phone_number) {
      return this.ad.user.phone_number;
    }

    return null;
  }

  /**
   * ✅ NOUVELLE MÉTHODE: Obtenir le numéro de téléphone à utiliser pour appels et SMS
   * Priorité: phone_number du user > whatsapp_number de l'annonce
   */
  getPhoneNumber(): string | null {
    // 1. Si le propriétaire a un numéro de téléphone, l'utiliser
    if (this.ad.user?.phone_number) {
      return this.ad.user.phone_number;
    }

    // 2. Sinon, utiliser le numéro WhatsApp de l'annonce
    if (this.ad.whatsapp_number) {
      return this.ad.whatsapp_number;
    }

    return null;
  }

  /**
   * ✅ MODIFIÉ: Vérifier si on peut contacter via WhatsApp
   */
  hasWhatsApp(): boolean {
    return !!this.getWhatsAppNumber();
  }

  /**
   * ✅ MODIFIÉ: Vérifier si on peut appeler ou envoyer un SMS
   */
  hasPhone(): boolean {
    return !!this.getPhoneNumber();
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
  getImageUrl(image: any): string {
    return image?.image_url || image || 'https://via.placeholder.com/800x600?text=Aucune+image';
  }

  /**
   * ✅ MODIFIÉ: Contacter via WhatsApp avec le bon numéro
   */
  /**
   * ✅ MODIFIÉ: Contacter via WhatsApp avec message automatique
   */
  contactViaWhatsApp(): void {
    // if (!this.isAuthenticated) {
    //   sessionStorage.setItem('returnUrl', this.router.url);
    //   this.router.navigate(['/login']);
    //   return;
    // }

    const phone = this.getWhatsAppNumber();
    if (!phone) {
      alert('Aucun numéro WhatsApp disponible');
      return;
    }

    // Nettoyer le numéro de téléphone
    const cleanPhone = phone.replace(/\D/g, '');

    // Ajouter l'indicatif international si nécessaire
    const internationalPhone = cleanPhone.startsWith('225') ? cleanPhone : '225' + cleanPhone;

    // ✅ Message prédéfini qui sera envoyé automatiquement
    const message = `Bonjour,

Je suis intéressé(e) par votre annonce "${this.ad.title}".

Prix affiché: ${this.formatPrice(this.ad.price)}
Catégorie: ${this.ad.category_display}
Localisation: ${this.ad.city_display}

Pouvez-vous me donner plus d'informations ?

Vu sur emunie-market.com
Lien: ${window.location.href}`;

    // Encoder le message pour l'URL
    const encodedMessage = encodeURIComponent(message);

    // ✅ Ouvrir WhatsApp avec le message pré-rempli
    // L'utilisateur devra juste cliquer sur "Envoyer" dans WhatsApp
    window.open(`https://wa.me/${internationalPhone}?text=${encodedMessage}`, '_blank');
  }

  /**
   * ✅ MODIFIÉ: Appeler le vendeur avec le bon numéro
   */
  callSeller(): void {
    const phone = this.getPhoneNumber();
    if (!phone) {
      alert('Aucun numéro de téléphone disponible');
      return;
    }
    window.location.href = `tel:${phone}`;
  }

  /**
   * ✅ MODIFIÉ: Envoyer un SMS avec le bon numéro
   */
  sendSMS(): void {
    if (!this.isAuthenticated) {
      sessionStorage.setItem('returnUrl', this.router.url);
      this.router.navigate(['/login']);
      return;
    }

    const phone = this.getPhoneNumber();
    if (!phone) {
      alert('Aucun numéro de téléphone disponible');
      return;
    }

    const message = encodeURIComponent(`Bonjour, je suis intéressé(e) par votre annonce: ${this.ad.title}`);
    window.location.href = `sms:${phone}?body=${message}`;
  }

  /**
   * Ajouter aux favoris
   */
  toggleFavorite(): void {
    if (!this.isAuthenticated) {
      sessionStorage.setItem('returnUrl', this.router.url);
      this.router.navigate(['/login']);
      return;
    }

    // TODO: Implémenter l'ajout aux favoris
    console.log('Toggle favorite');
  }

  /**
   * Partager l'annonce
   */
  shareAd(): void {
    const url = window.location.href;
    if (navigator.share) {
      navigator.share({
        title: this.ad.title,
        text: this.ad.description,
        url: url
      });
    } else {
      // Copier le lien
      navigator.clipboard.writeText(url);
      alert('Lien copié dans le presse-papier !');
    }
  }

  /**
   * Signaler l'annonce
   */
  reportAd(): void {
    if (!this.isAuthenticated) {
      sessionStorage.setItem('returnUrl', this.router.url);
      this.router.navigate(['/login']);
      return;
    }

    // TODO: Ouvrir un dialog de signalement
    console.log('Report ad');
  }

  /**
   * Modifier l'annonce
   */
  editAd(): void {
    this.router.navigate(['/dashboard/edit-ad', this.adId]);
  }

  /**
   * Supprimer l'annonce
   */
  deleteAd(): void {
    if (confirm('Êtes-vous sûr de vouloir supprimer cette annonce ?')) {
      this.annonceService.deleteAd(this.adId).subscribe({
        next: () => {
          alert('Annonce supprimée avec succès');
          this.router.navigate(['/dashboard/my-ads']);
        },
        error: (error) => {
          console.error('Erreur lors de la suppression:', error);
          alert('Erreur lors de la suppression de l\'annonce');
        }
      });
    }
  }

  /**
   * Voir les autres annonces du vendeur
   */
  viewSellerAds(): void {
    this.router.navigate(['/annonces'], {
      queryParams: { user: this.ad.user.id }
    });
  }

  /**
   * Voir une annonce similaire
   */
  viewRelatedAd(adId: string): void {
    this.router.navigate(['/annonces', adId]);
  }

  /**
   * Formater la date
   */
  formatDate(dateString: string): string {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  }
}
