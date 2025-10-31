// EmunieFront/src/app/auth/register/register.ts
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { PasswordModule } from 'primeng/password';
import { MessageModule } from 'primeng/message';
import { FileUploadModule } from 'primeng/fileupload';
import { AuthService } from '../../service/auth';
import { GoogleAuthService } from '../../service/google-auth.service';

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
export class Register implements OnInit {
  registerForm: FormGroup;
  loading = false;
  googleLoading = false;
  errorMessage = '';
  successMessage = '';
  selectedAvatar: File | null = null;
  avatarPreview: string | null = null;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private googleAuthService: GoogleAuthService,
    private router: Router
  ) {
    // Rediriger si déjà connecté
    if (this.authService.isAuthenticated()) {
      this.router.navigate(['/accueil']);
    }

    // Initialisation du formulaire
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

  ngOnInit(): void {
    // Initialiser Google Sign-In
    this.googleAuthService.initializeGoogleSignIn().catch(error => {
      console.error('Failed to initialize Google Sign-In:', error);
    });
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
   * Soumission du formulaire d'inscription classique
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

        this.errorMessage = this.extractErrorMessage(error);

        // Scroll vers le haut pour voir l'erreur
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    });
  }

  /**
   * Inscription/Connexion avec Google
   */
  async registerWithGoogle(): Promise<void> {
    this.googleLoading = true;
    this.errorMessage = '';
    this.successMessage = '';

    try {
      // Obtenir le token Google
      const googleToken = await this.googleAuthService.signInWithGoogle();

      // Envoyer le token au backend
      this.googleAuthService.authenticateWithBackend(googleToken).subscribe({
        next: (response) => {
          this.googleLoading = false;

          // Sauvegarder la session
          localStorage.setItem('token', response.token);
          localStorage.setItem('currentUser', JSON.stringify(response.user));

          const userName = response.user.full_name || response.user.username;

          if (response.created) {
            this.successMessage = `Compte créé avec succès ! Bienvenue ${userName} !`;
          } else {
            this.successMessage = `Ce compte existe déjà. Bienvenue ${userName} !`;
          }

          // Redirection vers dashboard après 1.5 secondes
          setTimeout(() => {
            this.router.navigate(['/dashboard']);
          }, 1500);
        },
        error: (error) => {
          this.googleLoading = false;
          console.error('Google authentication error:', error);

          this.errorMessage = this.extractErrorMessage(error) ||
            'Erreur lors de l\'inscription avec Google. Veuillez réessayer.';

          window.scrollTo({ top: 0, behavior: 'smooth' });
        }
      });
    } catch (error) {
      this.googleLoading = false;
      console.error('Google Sign-In error:', error);
      this.errorMessage = 'Erreur lors de l\'initialisation de Google Sign-In. Veuillez réessayer.';
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }

  /**
   * Extraire le message d'erreur de la réponse du backend
   */
  private extractErrorMessage(error: any): string {
    // 1. Vérifier si error.error existe et contient un message
    if (error.error) {
      // 1.1 Si error.error est une string
      if (typeof error.error === 'string') {
        return error.error;
      }

      // 1.2 Si error.error.detail existe (format Django REST Framework)
      if (error.error.detail) {
        return error.error.detail;
      }

      // 1.3 Si error.error.message existe
      if (error.error.message) {
        return error.error.message;
      }

      // 1.4 Si error.error contient des erreurs de champs
      if (typeof error.error === 'object') {
        const fieldErrors: string[] = [];

        // Parcourir tous les champs d'erreur
        Object.keys(error.error).forEach(key => {
          const value = error.error[key];

          if (Array.isArray(value)) {
            // Si c'est un tableau d'erreurs
            fieldErrors.push(...value);
          } else if (typeof value === 'string') {
            // Si c'est une string
            fieldErrors.push(value);
          }
        });

        if (fieldErrors.length > 0) {
          return fieldErrors.join('. ');
        }
      }
    }

    // 2. Si error.message existe
    if (error.message) {
      return error.message;
    }

    // 3. Messages par défaut selon le code HTTP
    switch (error.status) {
      case 0:
        return 'Impossible de se connecter au serveur. Vérifiez votre connexion internet.';
      case 400:
        return 'Données invalides. Veuillez vérifier les informations saisies.';
      case 401:
        return 'Erreur d\'authentification Google.';
      case 403:
        return 'Accès refusé.';
      case 409:
        return 'Ce nom d\'utilisateur ou cet email existe déjà.';
      case 500:
        return 'Erreur serveur. Veuillez réessayer plus tard.';
      case 503:
        return 'Service temporairement indisponible.';
      default:
        return 'Une erreur est survenue lors de l\'inscription. Veuillez réessayer.';
    }
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
