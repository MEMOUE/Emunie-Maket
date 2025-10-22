import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
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

    this.loginForm = this.fb.group({
      username: ['', [Validators.required, Validators.minLength(3)]],
      password: ['', [Validators.required, Validators.minLength(8)]],
      rememberMe: [false]
    });
  }

  ngOnInit(): void {
    // Vérifier si l'utilisateur vient de s'inscrire
    const navigation = this.router.getCurrentNavigation();
    if (navigation?.extras.state?.['registrationSuccess']) {
      this.successMessage = 'Inscription réussie ! Vous pouvez maintenant vous connecter.';
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
        this.successMessage = `Bienvenue ${response.user.full_name || response.user.username} !`;

        // Redirection vers la page demandée ou l'accueil
        const returnUrl = sessionStorage.getItem('returnUrl') || '/dashboard';
        sessionStorage.removeItem('returnUrl');

        setTimeout(() => {
          this.router.navigate([returnUrl]);
        }, 500);
      },
      error: (error) => {
        this.loading = false;
        console.error('Login error:', error);

        // Messages d'erreur spécifiques
        if (error.status === 401) {
          this.errorMessage = 'Nom d\'utilisateur ou mot de passe incorrect';
        } else if (error.status === 400) {
          this.errorMessage = 'Veuillez vérifier vos identifiants';
        } else if (error.status === 0) {
          this.errorMessage = 'Impossible de se connecter au serveur. Vérifiez votre connexion.';
        } else {
          this.errorMessage = error.message || 'Une erreur est survenue lors de la connexion';
        }
      }
    });
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
    // TODO: Implémenter l'authentification Google OAuth
  }

  /**
   * Connexion avec Facebook (à implémenter)
   */
  loginWithFacebook(): void {
    console.log('Connexion Facebook - À implémenter');
    // TODO: Implémenter l'authentification Facebook OAuth
  }
}
