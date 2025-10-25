import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule, AbstractControl, ValidationErrors } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { PasswordModule } from 'primeng/password';
import { CheckboxModule } from 'primeng/checkbox';
import { MessageModule } from 'primeng/message';
import { AuthService } from '../../service/auth';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterLink,
    ButtonModule,
    InputTextModule,
    PasswordModule,
    CheckboxModule,
    MessageModule
  ],
  templateUrl: './login.html',
  styleUrl: './login.css'
})
export class Login implements OnInit {
  loginForm: FormGroup;
  loading = false;
  errorMessage = '';
  successMessage = '';

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    // Rediriger si déjà connecté
    if (this.authService.isAuthenticated()) {
      this.router.navigate(['/dashboard']);
    }

    // Initialisation du formulaire avec validation
    this.loginForm = this.fb.group({
      username: ['', [
        Validators.required,
        Validators.minLength(3),
        this.emailOrUsernameValidator.bind(this)
      ]],
      password: ['', [
        Validators.required,
        Validators.minLength(8)
      ]],
      rememberMe: [false]
    });
  }

  ngOnInit(): void {
    // Vérifier si l'utilisateur vient de s'inscrire
    const navigation = this.router.getCurrentNavigation();
    if (navigation?.extras.state?.['registrationSuccess']) {
      this.successMessage = 'Inscription réussie ! Vous pouvez maintenant vous connecter.';
      // Effacer le message après 5 secondes
      setTimeout(() => {
        this.successMessage = '';
      }, 5000);
    }

    // Charger les credentials sauvegardés si "Se souvenir de moi" était activé
    const savedUsername = localStorage.getItem('remembered_username');
    if (savedUsername) {
      this.loginForm.patchValue({
        username: savedUsername,
        rememberMe: true
      });
    }
  }

  /**
   * Validateur personnalisé pour email ou username
   */
  emailOrUsernameValidator(control: AbstractControl): ValidationErrors | null {
    const value = control.value;

    if (!value || value.length < 3) {
      return null; // Laisse le validateur required et minLength gérer cela
    }

    // Pattern pour email
    const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

    // Pattern pour username (lettres, chiffres, underscore, tiret)
    const usernamePattern = /^[a-zA-Z0-9_-]{3,150}$/;

    // Si c'est un email valide OU un username valide, accepter
    if (emailPattern.test(value) || usernamePattern.test(value)) {
      return null;
    }

    return { invalidFormat: true };
  }

  /**
   * Soumission du formulaire de connexion
   */
  onSubmit(): void {
    // Validation du formulaire
    if (this.loginForm.invalid) {
      Object.keys(this.loginForm.controls).forEach(key => {
        this.loginForm.get(key)?.markAsTouched();
      });
      return;
    }

    this.loading = true;
    this.errorMessage = '';
    this.successMessage = '';

    const credentials = {
      username: this.loginForm.value.username.trim(),
      password: this.loginForm.value.password
    };

    this.authService.login(credentials).subscribe({
      next: (response) => {
        this.loading = false;

        // Gérer "Se souvenir de moi"
        if (this.loginForm.value.rememberMe) {
          localStorage.setItem('remembered_username', credentials.username);
        } else {
          localStorage.removeItem('remembered_username');
        }

        // Message de succès
        const userName = response.user.full_name || response.user.username;
        this.successMessage = `Bienvenue ${userName} !`;

        // Redirection vers la page demandée ou le dashboard
        const returnUrl = sessionStorage.getItem('returnUrl') || '/dashboard';
        sessionStorage.removeItem('returnUrl');

        setTimeout(() => {
          this.router.navigate([returnUrl]);
        }, 500);
      },
      error: (error) => {
        this.loading = false;
        console.error('Login error:', error);

        // Extraire le message d'erreur du backend
        this.errorMessage = this.extractErrorMessage(error);

        // Scroll vers le haut pour voir l'erreur
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    });
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

    // 2. Si error.message existe (message de l'intercepteur)
    if (error.message) {
      return error.message;
    }

    // 3. Messages par défaut selon le code HTTP
    switch (error.status) {
      case 0:
        return 'Impossible de se connecter au serveur. Vérifiez votre connexion internet.';
      case 400:
        return 'Données invalides. Veuillez vérifier vos identifiants.';
      case 401:
        return 'Email/nom d\'utilisateur ou mot de passe incorrect.';
      case 403:
        return 'Votre compte est désactivé. Contactez l\'administrateur.';
      case 404:
        return 'Service d\'authentification non trouvé.';
      case 500:
        return 'Erreur serveur. Veuillez réessayer plus tard.';
      case 503:
        return 'Service temporairement indisponible.';
      default:
        return 'Une erreur est survenue lors de la connexion. Veuillez réessayer.';
    }
  }

  /**
   * Obtenir l'erreur d'un champ spécifique
   */
  getFieldError(fieldName: string): string {
    const field = this.loginForm.get(fieldName);

    if (!field?.touched) return '';

    if (field?.hasError('required')) {
      return 'Ce champ est requis';
    }

    if (field?.hasError('minlength')) {
      const minLength = field.errors?.['minlength'].requiredLength;
      return `Minimum ${minLength} caractères`;
    }

    if (field?.hasError('invalidFormat')) {
      return 'Format invalide (email ou nom d\'utilisateur)';
    }

    return '';
  }

  /**
   * Vérifier si un champ est invalide
   */
  isFieldInvalid(fieldName: string): boolean {
    const field = this.loginForm.get(fieldName);
    return !!(field && field.invalid && field.touched);
  }

  /**
   * Connexion avec Google (à implémenter)
   */
  loginWithGoogle(): void {
    console.log('Connexion Google - À implémenter');
    this.errorMessage = 'La connexion avec Google sera bientôt disponible.';
    setTimeout(() => {
      this.errorMessage = '';
    }, 3000);
    // TODO: Implémenter l'authentification Google OAuth
  }

  /**
   * Connexion avec Facebook (à implémenter)
   */
  loginWithFacebook(): void {
    console.log('Connexion Facebook - À implémenter');
    this.errorMessage = 'La connexion avec Facebook sera bientôt disponible.';
    setTimeout(() => {
      this.errorMessage = '';
    }, 3000);
    // TODO: Implémenter l'authentification Facebook OAuth
  }
}
