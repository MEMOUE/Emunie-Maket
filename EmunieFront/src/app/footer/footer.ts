import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-footer',
  imports: [CommonModule],
  templateUrl: './footer.html',
  styleUrl: './footer.css'
})
export class Footer {
  currentYear = new Date().getFullYear();

  quickLinks = [
    { label: 'À propos', url: '#' },
    { label: 'Comment ça marche', url: '#' },
    { label: 'Nos services', url: '#' },
    { label: 'Blog', url: '#' },
    { label: 'Carrières', url: '#' }
  ];

  categories = [
    { label: 'Électronique', url: '#' },
    { label: 'Véhicules', url: '#' },
    { label: 'Immobilier', url: '#' },
    { label: 'Mode', url: '#' },
    { label: 'Services', url: '#' }
  ];

  support = [
    { label: 'Centre d\'aide', url: '#' },
    { label: 'Conditions d\'utilisation', url: '#' },
    { label: 'Politique de confidentialité', url: '#' },
    { label: 'Signaler un problème', url: '#' },
    { label: 'Nous contacter', url: '#' }
  ];

  socialLinks = [
    { icon: 'pi-facebook', url: '#', color: 'hover:text-blue-600' },
    { icon: 'pi-twitter', url: '#', color: 'hover:text-sky-500' },
    { icon: 'pi-instagram', url: '#', color: 'hover:text-pink-600' },
    { icon: 'pi-linkedin', url: '#', color: 'hover:text-blue-700' },
    { icon: 'pi-whatsapp', url: '#', color: 'hover:text-green-600' }
  ];

  paymentMethods = [
    { name: 'Orange Money', icon: 'pi-mobile' },
    { name: 'Wave', icon: 'pi-mobile' },
    { name: 'MTN Money', icon: 'pi-mobile' },
    { name: 'Moov Money', icon: 'pi-mobile' },
    { name: 'Visa', icon: 'pi-credit-card' },
    { name: 'MasterCard', icon: 'pi-credit-card' }
  ];
}
