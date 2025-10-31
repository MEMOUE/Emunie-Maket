// EmunieFront/src/app/auth/login/login.ts - Modifications à apporter

import { Component, OnInit, AfterViewInit, ElementRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule, AbstractControl, ValidationErrors } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { PasswordModule } from 'primeng/password';
import { CheckboxModule } from 'primeng/checkbox';
import { MessageModule } from 'primeng/message';
import { AuthService } from '../../service/auth';
import { GoogleAuthService } from '../../service/google-auth.service';

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
export class Login implements OnInit, AfterViewInit {
  @ViewChild('googleButton', { static: false }) googleButton!: ElementRef;

  loginForm: FormGroup;
  loading = false;
  errorMessage = '';
  successMessage = '';
  googleLoading = false;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private googleAuthService: GoogleAuthService,
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

    // Initialiser Google Sign-In
    this.googleAuthService.initializeGoogleSignIn().catch(error => {
      console.error('Failed to initialize Google Sign-In:', error);
    });
  }

  ngAfterViewInit(): void {
    // Le bouton Google sera géré via la méthode loginWithGoogle()
  }

  /**
   * Validateur personnalisé pour email ou username
   */
  emailOrUsernameValidator(control: AbstractControl): ValidationErrors | null {
    const value = control.value;

    if (!value || value.length < 3) {
      return null;
    }

    const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    const usernamePattern = /^[a-zA-Z0-9_-]{3,150}$/;

    if (emailPattern.test(value) || usernamePattern.test(value)) {
      return null;
    }

    return { invalidFormat: true };
  }

  /**
   * Soumission du formulaire de connexion
   */
  onSubmit(): void {
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

        if (this.loginForm.value.rememberMe) {
          localStorage.setItem('remembered_username', credentials.username);
        } else {
          localStorage.removeItem('remembered_username');
        }

        const userName = response.user.full_name || response.user.username;
        this.successMessage = `Bienvenue ${userName} !`;

        const returnUrl = sessionStorage.getItem('returnUrl') || '/dashboard';
        sessionStorage.removeItem('returnUrl');

        setTimeout(() => {
          this.router.navigate([returnUrl]);
        }, 500);
      },
      error: (error) => {
        this.loading = false;
        console.error('Login error:', error);
        this.errorMessage = this.extractErrorMessage(error);
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    });
  }

  /**
   * Connexion avec Google
   */
  async loginWithGoogle(): Promise<void> {
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
          this.successMessage = response.created
            ? `Compte créé avec succès ! Bienvenue ${userName} !`
            : `Bienvenue ${userName} !`;

          const returnUrl = sessionStorage.getItem('returnUrl') || '/dashboard';
          sessionStorage.removeItem('returnUrl');

          setTimeout(() => {
            this.router.navigate([returnUrl]);
          }, 1000);
        },
        error: (error) => {
          this.googleLoading = false;
          console.error('Google authentication error:', error);
          this.errorMessage = this.extractErrorMessage(error) ||
            'Erreur lors de la connexion avec Google. Veuillez réessayer.';
          window.scrollTo({ top: 0, behavior: 'smooth' });
        }
      });
    } catch (error) {
      this.googleLoading = false;
      console.error('Google Sign-In error:', error);
      this.errorMessage = 'Erreur lors de l\'initialisation de la connexion Google. Veuillez réessayer.';
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }

  /**
   * Extraire le message d'erreur de la réponse du backend
   */
  private extractErrorMessage(error: any): string {
    if (error.error) {
      if (typeof error.error === 'string') {
        return error.error;
      }
      if (error.error.detail) {
        return error.error.detail;
      }
      if (error.error.message) {
        return error.error.message;
      }
      if (typeof error.error === 'object') {
        const fieldErrors: string[] = [];
        Object.keys(error.error).forEach(key => {
          const value = error.error[key];
          if (Array.isArray(value)) {
            fieldErrors.push(...value);
          } else if (typeof value === 'string') {
            fieldErrors.push(value);
          }
        });
        if (fieldErrors.length > 0) {
          return fieldErrors.join('. ');
        }
      }
    }

    if (error.message) {
      return error.message;
    }

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

  getFieldError(fieldName: string): string {
    const field = this.loginForm.get(fieldName);
    if (!field?.touched) return '';
    if (field?.hasError('required')) return 'Ce champ est requis';
    if (field?.hasError('minlength')) {
      const minLength = field.errors?.['minlength'].requiredLength;
      return `Minimum ${minLength} caractères`;
    }
    if (field?.hasError('invalidFormat')) {
      return 'Format invalide (email ou nom d\'utilisateur)';
    }
    return '';
  }

  isFieldInvalid(fieldName: string): boolean {
    const field = this.loginForm.get(fieldName);
    return !!(field && field.invalid && field.touched);
  }

  loginWithFacebook(): void {
    console.log('Connexion Facebook - À implémenter');
    this.errorMessage = 'La connexion avec Facebook sera bientôt disponible.';
    setTimeout(() => {
      this.errorMessage = '';
    }, 3000);
  }
}
