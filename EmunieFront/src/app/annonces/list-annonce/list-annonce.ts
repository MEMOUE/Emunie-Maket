import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { Select } from 'primeng/select';
import { InputTextModule } from 'primeng/inputtext';
import { AnnonceService } from '../../service/annonce.service';

@Component({
  selector: 'app-list-annonce',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ButtonModule,
    InputTextModule,
    Select
  ],
  templateUrl: './list-annonce.html',
  styleUrls: ['./list-annonce.css']
})
export class ListAnnonce implements OnInit {
  ads: any[] = [];
  categories: any[] = [];
  cities: any[] = [];
  loading = true;

  // Filtres
  selectedCategory: string = '';
  selectedCity: string = '';
  searchQuery: string = '';
  minPrice: number | null = null;
  maxPrice: number | null = null;
  sortBy: string = '-created_at';

  // Options de tri
  sortOptions = [
    { label: 'Plus récentes', value: '-created_at' },
    { label: 'Plus anciennes', value: 'created_at' },
    { label: 'Prix croissant', value: 'price' },
    { label: 'Prix décroissant', value: '-price' },
    { label: 'Plus vues', value: '-views_count' },
    { label: 'Plus de favoris', value: '-favorites_count' }
  ];

  constructor(
    private annonceService: AnnonceService,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit(): void {
    // Charger les catégories et villes
    this.loadCategoriesAndCities();

    // Écouter les paramètres de l'URL
    this.route.queryParams.subscribe(params => {
      this.selectedCategory = params['category'] || '';
      this.selectedCity = params['city'] || '';
      this.searchQuery = params['search'] || '';
      this.loadAds();
    });
  }

  /**
   * Charger les catégories et villes
   */
  loadCategoriesAndCities(): void {
    this.annonceService.getCategories().subscribe({
      next: (response) => {
        this.categories = response.categories || [];
      },
      error: (error) => {
        console.error('Erreur lors du chargement des catégories:', error);
      }
    });

    this.annonceService.getCities().subscribe({
      next: (response) => {
        this.cities = response.cities || [];
      },
      error: (error) => {
        console.error('Erreur lors du chargement des villes:', error);
      }
    });
  }

  /**
   * Charger les annonces avec les filtres
   */
  loadAds(): void {
    this.loading = true;

    const params: any = {};

    if (this.selectedCategory) params.category = this.selectedCategory;
    if (this.selectedCity) params.city = this.selectedCity;
    if (this.searchQuery) params.search = this.searchQuery;
    if (this.minPrice) params.price_min = this.minPrice;
    if (this.maxPrice) params.price_max = this.maxPrice;
    if (this.sortBy) params.ordering = this.sortBy;

    this.annonceService.getAds(params).subscribe({
      next: (response) => {
        this.ads = response.results || response;
        this.loading = false;
      },
      error: (error) => {
        console.error('Erreur lors du chargement des annonces:', error);
        this.loading = false;
      }
    });
  }

  /**
   * Appliquer les filtres
   */
  applyFilters(): void {
    const queryParams: any = {};

    if (this.selectedCategory) queryParams.category = this.selectedCategory;
    if (this.selectedCity) queryParams.city = this.selectedCity;
    if (this.searchQuery) queryParams.search = this.searchQuery;

    this.router.navigate([], {
      relativeTo: this.route,
      queryParams,
      queryParamsHandling: 'merge'
    });
  }

  /**
   * Réinitialiser les filtres
   */
  resetFilters(): void {
    this.selectedCategory = '';
    this.selectedCity = '';
    this.searchQuery = '';
    this.minPrice = null;
    this.maxPrice = null;
    this.sortBy = '-created_at';

    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: {}
    });
  }

  /**
   * Naviguer vers les détails
   */
  viewDetails(adId: string): void {
    this.router.navigate(['/annonces', adId]);
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
   * Obtenir le label de la catégorie
   */
  getCategoryLabel(categoryValue: string): string {
    const category = this.categories.find(c => c.value === categoryValue);
    return category ? category.label : categoryValue;
  }
}
