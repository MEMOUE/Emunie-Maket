import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ButtonModule } from 'primeng/button';
import {RouterOutlet} from '@angular/router';
import {Footer} from '../footer/footer';

@Component({
  selector: 'app-accueil',
  imports: [CommonModule, ButtonModule, RouterOutlet, Footer],
  templateUrl: './accueil.html',
  styleUrl: './accueil.css'
})
export class Accueil {
  categories = [
    {
      icon: 'pi-car',
      name: 'Véhicules',
      count: 5765,
      color: 'from-red-500 to-red-600',
      subcategories: [
        'Voitures occasion & neuves', // Précision sur l'état
        'Location de véhicules (Auto, Bus)', // Inclut les bus/minibus (Gbaka)
        'Motos, Scooters & Tricycles', // Très important pour la mobilité urbaine
        'Équipements, Pneus & Pièces',
        'Camions & Engins lourds', // Pertinent pour le secteur BTP et transport

      ]
    },
    {
      icon: 'pi-briefcase',
      name: "Offres d'emploi & Stages", // Ajout de "Stages"
      count: 277,
      color: 'from-yellow-500 to-yellow-600',
      subcategories: [
        'Vente, Commercial & Distribution',
        'Informatique, Web & IT', // Secteur en croissance (e.g., Développeur, IT Support)
        'Comptabilité, Finance & Audit',
        'Hôtellerie, Restauration & Tourisme',
        'BTP (Bâtiment et Travaux Publics) & Industrie',
        'Services à la personne & Emplois domestiques',
        'Marketing & Communication',

      ]
    },
    {
      icon: 'pi-home',
      name: 'Immobilier & Foncier', // Ajout de Foncier (Terrains)
      count: 4471,
      color: 'from-green-500 to-green-600',
      subcategories: [
        'Appartements & Studios à louer', // Le "Studio" est très courant
        'Maisons, Villas & Duplex à louer',
        'Terrains nus à vendre (Foncier)', // Catégorie clé
        'Vente de biens (Appartements, Maisons)',
        'Bureaux, Commerces & Locaux pro',

      ]
    },
    {
      icon: 'pi-desktop',
      name: 'Électronique & Multimédia',
      count: 10155,
      color: 'from-blue-500 to-blue-600',
      subcategories: [
        'Téléphones Mobiles & Tablettes', // La catégorie principale
        'Ordinateurs fixes & portables',
        'Accessoires (Chargeurs, Écouteurs, Coques)',
        'TV, Home Cinéma & Sonorisation',
        'Jeux vidéos & Consoles',

      ]
    },
    {
      icon: 'pi-couch',
      name: 'Maison & Jardin',
      count: 11587,
      color: 'from-cyan-500 to-cyan-600',
      subcategories: [
        'Mobilier (Salons, Chambres, Bureaux)',
        'Électroménagers (Frigos, Clims, Ventilateurs)', // Clim/Ventilateurs essentiels
        'Décoration & Linge de maison',
        'Matériel de Bricolage & Jardinage',
        'Vaisselle & Articles de cuisine',

      ]
    },
    {
      icon: 'pi-shopping-bag',
      name: 'Mode, Vêtements & Beauté',
      count: 1108,
      color: 'from-pink-500 to-pink-600',
      subcategories: [
        'Vêtements Homme & Femme',
        'Chaussures & Sacs',
        'Montres & Bijoux',
        'Produits de Beauté & Cosmétiques', // Inclut coiffure/cheveux
        'Mode Enfant & Bébé',

      ]
    },
    {
      icon: 'pi-globe',
      name: 'Sport, Loisirs & Culture', // Ajout de Culture
      count: 685,
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
      count: 427,
      color: 'from-purple-500 to-purple-600',
      subcategories: [
        'Prestations de services (Réparation, Nettoyage, Conseil)',
        'Cours de soutien scolaire & Formations',
        'Événementiel & Mariage (Traiteur, Décoration)',
        'Santé & Bien-être',

      ]
    },
    {
      icon: 'pi-user-plus',
      name: 'Demandes d’emploi (Candidatures)', // Précision que ce sont des candidatures
      count: 619,
      color: 'from-indigo-500 to-indigo-600',
      subcategories: [
        'Autres demandes d’emploi',
        'Emplois de Maison (Nounou, Nettoyage)', // Terminologie locale
        'Chauffeur, Coursier & Conducteur',
        'Restauration & Cuisine',
        'Sécurité & Gardiennage',

      ]
    },
    {
      icon: 'pi-wrench',
      name: 'Matériaux & Équipements Pro',
      count: 1489,
      color: 'from-teal-500 to-teal-600',
      subcategories: [
        'Matériel de Construction & BTP',
        'Machines & Équipements Industriels',
        'Énergie (Groupes électrogènes, Panneaux Solaires)', // Essentiel
        'Matériel Agricole & de Pêche',
        'Sécurité (Caméras, Alarmes) & Médical',

      ]
    },
    {
      icon: 'pi-th-large',
      name: 'Agroalimentaire & Produits locaux', // Accent sur le local
      count: 187,
      color: 'from-lime-500 to-lime-600',
      subcategories: [
        'Produits agricoles bruts (Vivriers)', // Terminologie clé
        'Alimentation transformée & Épicerie',
        'Élevage & Pêche (Volailles, Poissons)',
        'Boissons & Jus locaux',

      ]
    },
    {
      icon: 'pi-paw',
      name: 'Animaux & Élevage', // Élevage pour le côté commercial
      count: 0,
      color: 'from-brown-500 to-brown-600',
      subcategories: [
        'Chiens & Chiots',
        'Chats & Chatons',
        'Volailles (Poulets, Pintades...)', // Très important
        'Bovins & Petits ruminants (Moutons, Chèvres)',
        'Accessoires & Aliments pour animaux',
        'Autres animaux (Exotiques, Aquatiques)',

      ]
    }
  ];
  featuredProducts = [
    {
      id: 1,
      image: 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400',
      title: 'iPhone 15 Pro Max',
      price: 850000,
      location: 'Abidjan, Cocody',
      featured: true
    },
    {
      id: 2,
      image: 'https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=400',
      title: 'MacBook Pro M3',
      price: 1200000,
      location: 'Abidjan, Plateau',
      featured: true
    },
    {
      id: 3,
      image: 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400',
      title: 'Nike Air Jordan',
      price: 45000,
      location: 'Abidjan, Marcory',
      featured: false
    },
    {
      id: 4,
      image: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400',
      title: 'Montre connectée',
      price: 85000,
      location: 'Abidjan, Yopougon',
      featured: false
    },
    {
      id: 5,
      image: 'https://images.unsplash.com/photo-1585386959984-a4155224a1ad?w=400',
      title: 'Caméra Sony A7',
      price: 650000,
      location: 'Abidjan, Cocody',
      featured: true
    },
    {
      id: 6,
      image: 'https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=400',
      title: 'Lunettes de soleil',
      price: 25000,
      location: 'Abidjan, Treichville',
      featured: false
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

  formatPrice(price: number): string {
    return price.toLocaleString('fr-FR') + ' FCFA';
  }
}
