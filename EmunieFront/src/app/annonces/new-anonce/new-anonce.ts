import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { Router, ActivatedRoute } from '@angular/router';
import { NgForOf, NgIf } from '@angular/common';
import { AnnonceService } from '../../service/annonce.service';

interface ImagePreview {
  file?: File;
  url: string;
  order: number;
  existing?: boolean;
  id?: string;
}

@Component({
  selector: 'app-new-anonce',
  templateUrl: './new-anonce.html',
  imports: [NgForOf, ReactiveFormsModule],
  styleUrls: ['./new-anonce.css']
})
export class NewAnonceComponent implements OnInit {
  form!: FormGroup;
  categories: Array<{ value: string; label: string }> = [];
  cities: Array<{ value: string; label: string }> = [];
  adTypes: Array<{ value: string; label: string }> = [];      // NOUVEAU
  adStatuses: Array<{ value: string; label: string }> = [];   // NOUVEAU
  imagePreviews: ImagePreview[] = [];
  loading = false;
  errorMessage = '';
  successMessage = '';

  // Mode édition
  isEditMode = false;
  adId: string = '';
  hasNewImages = false;

  readonly MIN_IMAGES = 1;
  readonly MAX_IMAGES = 3;
  readonly MAX_IMAGE_SIZE = 5 * 1024 * 1024; // 5Mo
  readonly ALLOWED_FORMATS = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];

  constructor(
    private fb: FormBuilder,
    private http: HttpClient,
    private router: Router,
    private route: ActivatedRoute,
    private annonceService: AnnonceService
  ) {}

  ngOnInit(): void {
    this.form = this.fb.group({
      title: ['', [Validators.required, Validators.minLength(5), Validators.maxLength(200)]],
      description: [null],
      price: ['', [Validators.required, Validators.min(0)]],
      currency: ['XOF'],
      is_negotiable: [true],
      ad_type: ['sell', Validators.required],        // NOUVEAU avec valeur par défaut
      status: ['active'],                            // NOUVEAU avec valeur par défaut
      category: ['', Validators.required],
      city: ['', Validators.required],
      address: [''],
      latitude: [null],
      longitude: [null],
      contact_email: ['', Validators.email],
      whatsapp_number: [''],
      is_urgent: [false],
      expires_at: ['', Validators.required]
    });

    this.loadCategories();
    this.loadCities();
    this.loadAdTypes();      // NOUVEAU
    this.loadAdStatuses();   // NOUVEAU

    // Vérifier si on est en mode édition
    this.route.params.subscribe(params => {
      if (params['id']) {
        this.isEditMode = true;
        this.adId = params['id'];
        this.loadAdData();
      }
    });
  }

  /**
   * NOUVEAU: Charger les types d'annonces
   */
  loadAdTypes(): void {
    this.annonceService.getAdTypes().subscribe({
      next: (res) => (this.adTypes = res.ad_types ?? []),
      error: (err) => console.error('Erreur lors du chargement des types d\'annonces:', err)
    });
  }

  /**
   * NOUVEAU: Charger les statuts d'annonces
   */
  loadAdStatuses(): void {
    this.annonceService.getAdStatuses().subscribe({
      next: (res) => (this.adStatuses = res.ad_statuses ?? []),
      error: (err) => console.error('Erreur lors du chargement des statuts:', err)
    });
  }

  /**
   * Charger les données de l'annonce à modifier
   */
  loadAdData(): void {
    this.loading = true;

    this.annonceService.getAdDetail(this.adId).subscribe({
      next: (ad) => {
        // Remplir le formulaire avec les données existantes
        this.form.patchValue({
          title: ad.title,
          description: ad.description,
          price: ad.price,
          currency: ad.currency || 'XOF',
          is_negotiable: ad.is_negotiable,
          ad_type: ad.ad_type || 'sell',          // NOUVEAU
          status: ad.status || 'active',           // NOUVEAU
          category: ad.category,
          city: ad.city,
          address: ad.address || '',
          latitude: ad.latitude,
          longitude: ad.longitude,
          contact_phone: ad.contact_phone || '',
          contact_email: ad.contact_email || '',
          whatsapp_number: ad.whatsapp_number || '',
          is_urgent: ad.is_urgent,
          expires_at: ad.expires_at ? this.formatDateForInput(ad.expires_at) : ''
        });

        // Charger les images existantes
        if (ad.images && ad.images.length > 0) {
          this.imagePreviews = ad.images.map((img: any, index: number) => ({
            url: img.image_url || img.image,
            order: index,
            existing: true,
            id: img.id
          }));
        }

        this.loading = false;
      },
      error: (error) => {
        console.error('Erreur lors du chargement de l\'annonce:', error);
        this.errorMessage = 'Impossible de charger les données de l\'annonce';
        this.loading = false;

        // Rediriger après 2 secondes
        setTimeout(() => {
          this.router.navigate(['/my-ads']);
        }, 2000);
      }
    });
  }

  /**
   * Formater la date pour l'input date
   */
  formatDateForInput(dateString: string): string {
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  loadCategories(): void {
    this.http.get<{ categories: any }>(`${environment.apiUrl}produit/categories/`).subscribe({
      next: (res) => (this.categories = res.categories ?? []),
      error: (err) => console.error('Erreur lors du chargement des catégories:', err)
    });
  }

  loadCities(): void {
    this.http.get<{ cities: any }>(`${environment.apiUrl}produit/cities/`).subscribe({
      next: (res) => (this.cities = res.cities ?? []),
      error: (err) => console.error('Erreur lors du chargement des villes:', err)
    });
  }

  today(): string {
    return new Date().toISOString().split('T')[0];
  }

  /**
   * Gestion de la sélection d'images
   */
  onImagesSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (!input.files?.length) return;

    const newFiles = Array.from(input.files);

    // En mode édition, si on ajoute de nouvelles images, on remplace toutes les anciennes
    if (this.isEditMode && !this.hasNewImages) {
      this.imagePreviews = [];
      this.hasNewImages = true;
    }

    // Vérifier le nombre total d'images
    if (this.imagePreviews.length + newFiles.length > this.MAX_IMAGES) {
      this.errorMessage = `Vous pouvez ajouter au maximum ${this.MAX_IMAGES} images.`;
      input.value = '';
      return;
    }

    // Traiter chaque fichier
    for (const file of newFiles) {
      // Vérifier le format
      if (!this.ALLOWED_FORMATS.includes(file.type)) {
        this.errorMessage = `Format non supporté: ${file.name}. Utilisez: JPG, PNG, GIF ou WEBP`;
        continue;
      }

      // Vérifier la taille
      if (file.size > this.MAX_IMAGE_SIZE) {
        this.errorMessage = `Image trop volumineuse: ${file.name}. Taille max: 5Mo`;
        continue;
      }

      // Créer l'aperçu
      const reader = new FileReader();
      reader.onload = (e: any) => {
        this.imagePreviews.push({
          file: file,
          url: e.target.result,
          order: this.imagePreviews.length,
          existing: false
        });

        // Réinitialiser le message d'erreur si tout est OK
        if (this.imagePreviews.length >= this.MIN_IMAGES) {
          this.errorMessage = '';
        }
      };
      reader.readAsDataURL(file);
    }

    input.value = ''; // Reset input
  }

  /**
   * Supprimer une image
   */
  removeImage(index: number): void {
    if (this.imagePreviews.length <= this.MIN_IMAGES) {
      this.errorMessage = `Vous devez avoir au moins ${this.MIN_IMAGES} image.`;
      return;
    }

    const removedImage = this.imagePreviews[index];

    // Si on supprime une image existante en mode édition
    if (this.isEditMode && removedImage.existing && !this.hasNewImages) {
      this.errorMessage = "Pour modifier les images, ajoutez d'abord de nouvelles images.";
      return;
    }

    this.imagePreviews.splice(index, 1);

    // Réorganiser les ordres
    this.imagePreviews.forEach((img, idx) => {
      img.order = idx;
    });

    this.errorMessage = '';
  }

  /**
   * Définir une image comme primaire
   */
  setPrimaryImage(index: number): void {
    const [image] = this.imagePreviews.splice(index, 1);
    this.imagePreviews.unshift(image);

    // Réorganiser les ordres
    this.imagePreviews.forEach((img, idx) => {
      img.order = idx;
    });
  }

  /**
   * Valider les images
   */
  validateImages(): boolean {
    if (this.imagePreviews.length < this.MIN_IMAGES) {
      this.errorMessage = `Vous devez ajouter au moins ${this.MIN_IMAGES} image.`;
      return false;
    }

    if (this.imagePreviews.length > this.MAX_IMAGES) {
      this.errorMessage = `Vous ne pouvez pas ajouter plus de ${this.MAX_IMAGES} images.`;
      return false;
    }

    return true;
  }

  /**
   * Soumettre le formulaire
   */
  submit(): void {
    // Valider le formulaire
    if (this.form.invalid) {
      Object.keys(this.form.controls).forEach(key => {
        this.form.get(key)?.markAsTouched();
      });
      this.errorMessage = 'Veuillez remplir tous les champs obligatoires.';
      return;
    }

    // Valider les images
    if (!this.validateImages()) {
      return;
    }

    this.loading = true;
    this.errorMessage = '';
    this.successMessage = '';

    // Préparer FormData
    const formData = new FormData();

    // Ajouter les champs du formulaire
    Object.entries(this.form.value).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        formData.append(key, value as any);
      }
    });

    // Ajouter les images selon le mode
    if (this.isEditMode) {
      // En mode édition, n'envoyer les images que si de nouvelles images ont été ajoutées
      if (this.hasNewImages) {
        const newImages = this.imagePreviews
          .filter(preview => preview.file)
          .sort((a, b) => a.order - b.order);

        newImages.forEach((preview) => {
          if (preview.file) {
            formData.append('images', preview.file);
          }
        });
      }
    } else {
      // En mode création, toujours inclure les images
      this.imagePreviews
        .sort((a, b) => a.order - b.order)
        .forEach((preview) => {
          if (preview.file) {
            formData.append('images', preview.file);
          }
        });
    }

    // Envoyer la requête appropriée selon le mode
    const request = this.isEditMode
      ? this.annonceService.updateAd(this.adId, formData)
      : this.http.post(`${environment.apiUrl}produit/ads/create/`, formData);

    request.subscribe({
      next: (response: any) => {
        this.loading = false;
        this.successMessage = this.isEditMode
          ? 'Annonce modifiée avec succès !'
          : 'Annonce créée avec succès !';

        // Rediriger après 2 secondes
        setTimeout(() => {
          this.router.navigate(['/my-ads']);
        }, 2000);
      },
      error: (err) => {
        this.loading = false;
        console.error('Erreur lors de la sauvegarde de l\'annonce:', err);

        if (err.error) {
          if (typeof err.error === 'string') {
            this.errorMessage = err.error;
          } else if (err.error.detail) {
            this.errorMessage = err.error.detail;
          } else if (err.error.images) {
            this.errorMessage = err.error.images.join(' ');
          } else {
            // Extraire les messages d'erreur des champs
            const errors = Object.values(err.error).flat();
            this.errorMessage = errors.join(' ');
          }
        } else {
          this.errorMessage = this.isEditMode
            ? 'Une erreur est survenue lors de la modification de l\'annonce.'
            : 'Une erreur est survenue lors de la création de l\'annonce.';
        }

        // Scroll vers le haut pour voir l'erreur
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    });
  }

  /**
   * Obtenir l'erreur d'un champ
   */
  getFieldError(fieldName: string): string {
    const field = this.form.get(fieldName);

    if (!field?.touched) return '';

    if (field?.hasError('required')) return 'Ce champ est requis';
    if (field?.hasError('minlength')) {
      const minLength = field.errors?.['minlength'].requiredLength;
      return `Minimum ${minLength} caractères`;
    }
    if (field?.hasError('maxlength')) {
      const maxLength = field.errors?.['maxlength'].requiredLength;
      return `Maximum ${maxLength} caractères`;
    }
    if (field?.hasError('email')) return 'Email invalide';
    if (field?.hasError('min')) return 'Valeur minimale: 0';

    return '';
  }

  /**
   * Vérifier si un champ est invalide
   */
  isFieldInvalid(fieldName: string): boolean {
    const field = this.form.get(fieldName);
    return !!(field && field.invalid && field.touched);
  }

  /**
   * Obtenir le nombre d'images restantes
   */
  getRemainingImagesCount(): number {
    return this.MAX_IMAGES - this.imagePreviews.length;
  }

  /**
   * Vérifier si on peut ajouter des images
   */
  canAddImages(): boolean {
    return this.imagePreviews.length < this.MAX_IMAGES;
  }
}
