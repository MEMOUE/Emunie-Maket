import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { PasswordModule } from 'primeng/password';
import { MessageModule } from 'primeng/message';
import { FileUploadModule } from 'primeng/fileupload';
import { AuthService, User } from '../../service/auth';

@Component({
  selector: 'app-profile-edit',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterLink,
    ButtonModule,
    InputTextModule,
    PasswordModule,
    MessageModule,
    FileUploadModule
  ],
  templateUrl: './profile-edit.html',
  styleUrl: './profile-edit.css'
})
export class ProfileEditComponent implements OnInit {
  profileForm: FormGroup;
  loading = false;
  errorMessage = '';
  successMessage = '';
  selectedAvatar: File | null = null;
  avatarPreview: string | null = null;
  currentUser: User | null = null;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.profileForm = this.fb.group({
      username: [{value: '', disabled: true}], // Username non modifiable
      email: ['', [Validators.required, Validators.email]],
      phone_number: [''], // Optionnel
      first_name: ['', [Validators.required, Validators.minLength(2)]],
      last_name: ['', [Validators.required, Validators.minLength(2)]],
      location: [''],
      bio: ['', Validators.maxLength(500)]
    });
  }

  ngOnInit(): void {
    // Charger les données utilisateur actuelles
    this.authService.getCurrentUser$().subscribe(user => {
      if (user) {
        this.currentUser = user;
        this.loadUserData(user);
      }
    });

    // Si pas d'utilisateur en mémoire, charger depuis l'API
    if (!this.currentUser) {
      this.authService.getProfile().subscribe({
        next: (user) => {
          this.currentUser = user;
          this.loadUserData(user);
        },
        error: () => {
          this.router.navigate(['/login']);
        }
      });
    }
  }

  /**
   * Charger les données utilisateur dans le formulaire
   */
  private loadUserData(user: User): void {
    this.profileForm.patchValue({
      username: user.username,
      email: user.email,
      phone_number: user.phone_number || '',
      first_name: user.first_name,
      last_name: user.last_name,
      location: user.location || '',
      bio: user.bio || ''
    });

    // Charger l'avatar existant
    if (user.avatar) {
      // Construire l'URL complète de l'avatar
      const avatarUrl = user.avatar.startsWith('http')
        ? user.avatar
        : `http://localhost:8000${user.avatar}`;
      this.avatarPreview = avatarUrl;
    }
  }

  /**
   * Gestion de la sélection d'avatar
   */
  onAvatarSelect(event: any): void {
    const file = event.files?.[0] || event.target.files?.[0];

    if (file) {
      // Vérifier la taille (max 1Mo)
      if (file.size > 1024 * 1024) {
        this.errorMessage = 'La taille de l\'avatar ne doit pas dépasser 1Mo';
        this.selectedAvatar = null;
        return;
      }

      // Vérifier le type
      const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
      if (!allowedTypes.includes(file.type)) {
        this.errorMessage = 'Format d\'image non supporté. Utilisez: jpg, jpeg, png, gif';
        this.selectedAvatar = null;
        return;
      }

      this.selectedAvatar = file;
      this.errorMessage = '';

      // Créer un aperçu
      const reader = new FileReader();
      reader.onload = (e: any) => {
        this.avatarPreview = e.target.result;
      };
      reader.readAsDataURL(file);
    }
  }

  /**
   * Retirer l'avatar sélectionné
   */
  removeAvatar(): void {
    this.selectedAvatar = null;
    this.avatarPreview = null;
  }

  /**
   * Soumission du formulaire
   */
  onSubmit(): void {
    // Marquer tous les champs comme touchés
    if (this.profileForm.invalid) {
      Object.keys(this.profileForm.controls).forEach(key => {
        this.profileForm.get(key)?.markAsTouched();
      });
      return;
    }

    this.loading = true;
    this.errorMessage = '';
    this.successMessage = '';

    // Préparer les données avec FormData si un avatar est sélectionné
    let updateData: FormData | any;

    if (this.selectedAvatar) {
      updateData = new FormData();
      const formValues = this.profileForm.getRawValue();

      Object.keys(formValues).forEach(key => {
        if (key !== 'username' && formValues[key]) {
          updateData.append(key, formValues[key]);
        }
      });

      updateData.append('avatar', this.selectedAvatar, this.selectedAvatar.name);
    } else {
      // Utiliser JSON si pas d'avatar
      updateData = { ...this.profileForm.value };

      // Retirer phone_number s'il est vide
      if (!updateData.phone_number || updateData.phone_number.trim() === '') {
        delete updateData.phone_number;
      }
    }

    // Appel au service
    this.authService.updateProfile(updateData).subscribe({
      next: (response) => {
        this.successMessage = 'Profil mis à jour avec succès !';
        this.loading = false;
        this.selectedAvatar = null;

        // Redirection vers le dashboard après 2 secondes
        setTimeout(() => {
          this.router.navigate(['/dashboard/overview']);
        }, 2000);
      },
      error: (error) => {
        this.loading = false;
        console.error('Update error:', error);

        // Extraire le message d'erreur
        if (error.error && typeof error.error === 'object') {
          const errors = Object.values(error.error).flat();
          this.errorMessage = errors.join(', ');
        } else {
          this.errorMessage = error.message || 'Une erreur est survenue lors de la mise à jour';
        }

        // Scroll vers le haut pour voir l'erreur
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    });
  }

  /**
   * Obtenir l'erreur d'un champ spécifique
   */
  getFieldError(fieldName: string): string {
    const field = this.profileForm.get(fieldName);

    if (!field?.touched) return '';

    if (field?.hasError('required')) {
      return 'Ce champ est requis';
    }
    if (field?.hasError('email')) {
      return 'Adresse email invalide';
    }
    if (field?.hasError('minlength')) {
      const minLength = field.errors?.['minlength'].requiredLength;
      return `Minimum ${minLength} caractères requis`;
    }
    if (field?.hasError('maxlength')) {
      const maxLength = field.errors?.['maxlength'].requiredLength;
      return `Maximum ${maxLength} caractères autorisés`;
    }

    return '';
  }

  /**
   * Vérifier si un champ est invalide
   */
  isFieldInvalid(fieldName: string): boolean {
    const field = this.profileForm.get(fieldName);
    return !!(field && field.invalid && field.touched);
  }

  /**
   * Annuler et retourner au dashboard
   */
  cancel(): void {
    this.router.navigate(['/dashboard/overview']);
  }
}
