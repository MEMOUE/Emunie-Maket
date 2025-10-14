import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { PasswordModule } from 'primeng/password';
import { MessageModule } from 'primeng/message';
import { FileUploadModule } from 'primeng/fileupload';
import { AuthService } from '../../service/auth';

@Component({
  selector: 'app-register',
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
  templateUrl: './register.html',
  styleUrl: './register.css'
})
export class Register {
  registerForm: FormGroup;
  loading = false;
  errorMessage = '';
  successMessage = '';
  selectedAvatar: File | null = null;
  avatarPreview: string | null = null;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    // Rediriger si déjà connecté
    if (this.authService.isAuthenticated()) {
      this.router.navigate(['/accueil']);
    }

    this.registerForm = this.fb.group({
      username: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(150)]],
      email: ['', [Validators.required, Validators.email]],
      phone_number: [''], // Optionnel
      first_name: ['', [Validators.required, Validators.minLength(2)]],
      last_name: ['', [Validators.required, Validators.minLength(2)]],
      password: ['', [Validators.required, Validators.minLength(8)]],
      password_confirm: ['', Validators.required]
    }, { validators: this.passwordMatchValidator });
  }

  /**
   * Validateur personnalisé pour vérifier que les mots de passe correspondent
   */
  passwordMatchValidator(group: FormGroup) {
    const password = group.get('password')?.value;
    const confirmPassword = group.get('password_confirm')?.value;
    return password === confirmPassword ? null : { passwordMismatch: true };
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
        this.avatarPreview = null;
        return;
      }

      // Vérifier le type
      const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
      if (!allowedTypes.includes(file.type)) {
        this.errorMessage = 'Format d\'image non supporté. Utilisez: jpg, jpeg, png, gif';
        this.selectedAvatar = null;
        this.avatarPreview = null;
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
    if (this.registerForm.invalid) {
      Object.keys(this.registerForm.controls).forEach(key => {
        this.registerForm.get(key)?.markAsTouched();
      });
      return;
    }

    this.loading = true;
    this.errorMessage = '';
    this.successMessage = '';

    // Préparer les données
    const formData: any = {
      ...this.registerForm.value
    };

    // Ajouter l'avatar si sélectionné
    if (this.selectedAvatar) {
      formData.avatar = this.selectedAvatar;
    }

    // Retirer phone_number s'il est vide
    if (!formData.phone_number || formData.phone_number.trim() === '') {
      delete formData.phone_number;
    }

    // Appel au service
    this.authService.register(formData).subscribe({
      next: (response) => {
        this.successMessage = response.message || 'Compte créé avec succès !';
        this.loading = false;

        // Redirection vers login après 2 secondes
        setTimeout(() => {
          this.router.navigate(['/login'], {
            state: { registrationSuccess: true }
          });
        }, 2000);
      },
      error: (error) => {
        this.loading = false;
        console.error('Registration error:', error);

        this.errorMessage = error.message || 'Une erreur est survenue lors de l\'inscription';

        // Scroll vers le haut pour voir l'erreur
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    });
  }

  /**
   * Obtenir l'erreur d'un champ spécifique
   */
  getFieldError(fieldName: string): string {
    const field = this.registerForm.get(fieldName);

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
    if (field?.hasError('pattern')) {
      if (fieldName === 'phone_number') {
        return 'Format de téléphone invalide (ex: +225XXXXXXXXXX)';
      }
      return 'Format invalide';
    }

    if (fieldName === 'password_confirm' && this.registerForm.hasError('passwordMismatch')) {
      return 'Les mots de passe ne correspondent pas';
    }

    return '';
  }

  /**
   * Vérifier si un champ est invalide
   */
  isFieldInvalid(fieldName: string): boolean {
    const field = this.registerForm.get(fieldName);
    return !!(field && field.invalid && field.touched);
  }
}
