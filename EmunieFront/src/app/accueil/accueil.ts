import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ButtonModule } from 'primeng/button';
import { Router, RouterLink, RouterOutlet } from '@angular/router';
import { Footer } from '../footer/footer';
import { AnnonceService } from '../service/annonce.service';

interface Category {
  icon: string;
  name: string;
  value: string;
  count: number;
  color: string;
  subcategories: string[];
}

@Component({
  selector: 'app-accueil',
  standalone: true,
  imports: [CommonModule, ButtonModule, RouterOutlet, Footer],
  templateUrl: './accueil.html',
  styleUrl: './accueil.css'
})
export class Accueil implements OnInit {
  // Données réelles depuis l'API
  featuredAds: any[] = [];
  recentAds: any[] = [];
  urgentAds: any[] = [];
  categoriesStats: any[] = [];
  stats: any = {};
  loading = true;

  // Catégories avec leurs détails (garder pour l'UI)
  categories: Category[] = [
    {
      icon: 'pi-car',
      name: 'Véhicules',
      value: 'vehicules',
      count: 0,
      color: 'from-red-500 to-red-600',
      subcategories: [
        'Voitures occasion & neuves',
        'Location de véhicules (Auto, Bus)',
        'Motos, Scooters & Tricycles',
        'Équipements, Pneus & Pièces',
        'Camions & Engins lourds',
      ]
    },
    {
      icon: 'pi-briefcase',
      name: "Offres d'emploi & Stages",
      value: 'emploi_stages',
      count: 0,
      color: 'from-yellow-500 to-yellow-600',
      subcategories: [
        'Vente, Commercial & Distribution',
        'Informatique, Web & IT',
        'Comptabilité, Finance & Audit',
        'Hôtellerie, Restauration & Tourisme',
        'BTP (Bâtiment et Travaux Publics) & Industrie',
        'Services à la personne & Emplois domestiques',
        'Marketing & Communication',
      ]
    },
    {
      icon: 'pi-home',
      name: 'Immobilier & Foncier',
      value: 'immobilier',
      count: 0,
      color: 'from-green-500 to-green-600',
      subcategories: [
        'Appartements & Studios à louer',
        'Maisons, Villas & Duplex à louer',
        'Terrains nus à vendre (Foncier)',
        'Vente de biens (Appartements, Maisons)',
        'Bureaux, Commerces & Locaux pro',
      ]
    },
    {
      icon: 'pi-desktop',
      name: 'Électronique & Multimédia',
      value: 'electronique',
      count: 0,
      color: 'from-blue-500 to-blue-600',
      subcategories: [
        'Téléphones Mobiles & Tablettes',
        'Ordinateurs fixes & portables',
        'Accessoires (Chargeurs, Écouteurs, Coques)',
        'TV, Home Cinéma & Sonorisation',
        'Jeux vidéos & Consoles',
      ]
    },
    {
      icon: 'pi-map-marker',
      name: 'Maison & Jardin',
      value: 'maison_jardin',
      count: 0,
      color: 'from-cyan-500 to-cyan-600',
      subcategories: [
        'Mobilier (Salons, Chambres, Bureaux)',
        'Électroménagers (Frigos, Clims, Ventilateurs)',
        'Décoration & Linge de maison',
        'Matériel de Bricolage & Jardinage',
        'Vaisselle & Articles de cuisine',
      ]
    },
    {
      icon: 'pi-shopping-bag',
      name: 'Mode, Vêtements & Beauté',
      value: 'mode_beaute',
      count: 0,
      color: 'from-pink-500 to-pink-600',
      subcategories: [
        'Vêtements Homme & Femme',
        'Chaussures & Sacs',
        'Montres & Bijoux',
        'Produits de Beauté & Cosmétiques',
        'Mode Enfant & Bébé',
      ]
    },
    {
      icon: 'pi-globe',
      name: 'Sport, Loisirs & Culture',
      value: 'sport_loisirs',
      count: 0,
      color: 'from-orange-500 to-orange-600',
      subcategories: [
        'Articles & Matériel de sport',
        'Instruments de musique',
        'Livres, BDs & Supports Culturels',
        'Vélos & Trottinettes',
        'Tourisme, Billets & Activités',
      ]
    },
    {
      icon: 'pi-users',
      name: 'Services & Formation',
      value: 'services',
      count: 0,
      color: 'from-purple-500 to-purple-600',
      subcategories: [
        'Prestations de services (Réparation, Nettoyage, Conseil)',
        'Cours de soutien scolaire & Formations',
        'Événementiel & Mariage (Traiteur, Décoration)',
        'Santé & Bien-être',
      ]
    },
    {
      icon: 'pi-wrench',
      name: 'Matériaux & Équipements Pro',
      value: 'materiaux_pro',
      count: 0,
      color: 'from-teal-500 to-teal-600',
      subcategories: [
        'Matériel de Construction & BTP',
        'Machines & Équipements Industriels',
        'Énergie (Groupes électrogènes, Panneaux Solaires)',
        'Matériel Agricole & de Pêche',
        'Sécurité (Caméras, Alarmes) & Médical',
      ]
    },
    {
      icon: 'pi-th-large',
      name: 'Agroalimentaire & Produits locaux',
      value: 'agroalimentaire',
      count: 0,
      color: 'from-lime-500 to-lime-600',
      subcategories: [
        'Produits agricoles bruts (Vivriers)',
        'Alimentation transformée & Épicerie',
        'Élevage & Pêche (Volailles, Poissons)',
        'Boissons & Jus locaux',
      ]
    },
    {
      icon: 'pi-discord',
      name: 'Animaux & Produits animaliers',
      value: 'animaux_produits_animaliers',
      count: 0,
      color: 'from-yellow-500 to-amber-600',
      subcategories: [
        'Animaux domestiques (Chiens, Chats, Oiseaux...)',
        'Produits et accessoires pour animaux',
        'Alimentation animale',
        'Élevage et reproduction',
        'Services vétérinaires & soins'
      ]
    }
  ];

  features = [
    {
      icon: 'pi-shield',
      title: 'Transactions Sécurisées',
      description: 'Vos achats et ventes sont protégés'
    },
    {
      icon: 'pi-bolt',
      title: 'Rapide et Simple',
      description: 'Publiez en quelques clics'
    },
    {
      icon: 'pi-users',
      title: 'Communauté Active',
      description: 'Des milliers d\'utilisateurs quotidiens'
    },
    {
      icon: 'pi-star-fill',
      title: 'Produits Vérifiés',
      description: 'Annonces contrôlées par nos équipes'
    }
  ];

  constructor(
    private annonceService: AnnonceService,
    public router: Router
  ) {}

  ngOnInit(): void {
    this.loadHomeData();
  }

  /**
   * Charger les données de la page d'accueil
   */
  loadHomeData(): void {
    this.loading = true;

    this.annonceService.getHomeData().subscribe({
      next: (response) => {
        console.log('Home data:', response);

        // Annonces en vedette
        this.featuredAds = response.featured_ads || [];

        // Annonces récentes
        this.recentAds = response.recent_ads || [];

        // Annonces urgentes
        this.urgentAds = response.urgent_ads || [];

        // Statistiques par catégorie
        this.categoriesStats = response.categories || [];

        // Mettre à jour les compteurs de catégories
        this.updateCategoryCounts();

        // Statistiques globales
        this.stats = response.stats || {};

        this.loading = false;
      },
      error: (error) => {
        console.error('Erreur lors du chargement des données:', error);
        this.loading = false;
      }
    });
  }

  /**
   * Mettre à jour les compteurs des catégories avec les stats de l'API
   */
  updateCategoryCounts(): void {
    this.categoriesStats.forEach(stat => {
      const category = this.categories.find(c => c.value === stat.value);
      if (category) {
        category.count = stat.count;
      }
    });
  }

  /**
   * Naviguer vers les détails d'une annonce
   */
  viewAdDetails(adId: string): void {
    this.router.navigate(['/annonces', adId]);
  }

  /**
   * Naviguer vers la liste d'une catégorie
   */
  viewCategoryAds(categoryValue: string): void {
    this.router.navigate(['/annonces'], {
      queryParams: { category: categoryValue }
    });
  }

  /**
   * Naviguer vers toutes les annonces
   */
  viewAllAds(): void {
    this.router.navigate(['/annonces']);
  }

  /**
   * Naviguer vers la création d'annonce
   */
  createAd(): void {
    this.router.navigate(['/dashboard/new-ad']);
  }

  /**
   * Contacter via WhatsApp
   */
  contactViaWhatsApp(phoneNumber: string, adTitle: string): void {
    // Nettoyer le numéro de téléphone
    const cleanPhone = phoneNumber.replace(/\D/g, '');

    // Ajouter l'indicatif international si nécessaire
    const internationalPhone = cleanPhone.startsWith('225') ? cleanPhone : '225' + cleanPhone;

    // Créer le message
    const message = encodeURIComponent(`Bonjour, je suis intéressé(e) par votre annonce: ${adTitle}`);

    // Ouvrir WhatsApp
    window.open(`https://wa.me/${internationalPhone}?text=${message}`, '_blank');
  }

  /**
   * Appeler le vendeur
   */
  callSeller(phoneNumber: string): void {
    window.location.href = `tel:${phoneNumber}`;
  }

  /**
   * Envoyer un SMS au vendeur
   */
  sendSMS(phoneNumber: string, adTitle: string): void {
    const message = encodeURIComponent(`Bonjour, je suis intéressé(e) par votre annonce: ${adTitle}`);
    window.location.href = `sms:${phoneNumber}?body=${message}`;
  }

  /**
   * Formater le prix
   */
  formatPrice(price: number): string {
    if (!price) return '0 FCFA';
    return price.toLocaleString('fr-FR') + ' FCFA';
  }

  /**
   * Obtenir l'image placeholder si pas d'image
   */
  getImageUrl(ad: any): string {
    return ad.primary_image || 'https://via.placeholder.com/400x300?text=Aucune+image';
  }
}
