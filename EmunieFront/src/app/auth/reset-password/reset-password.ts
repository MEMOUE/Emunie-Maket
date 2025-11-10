// EmunieFront/src/app/auth/reset-password/reset-password.ts

import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { PasswordModule } from 'primeng/password';
import { MessageModule } from 'primeng/message';
import { PasswordResetService, TokenVerifyResponse } from '../../service/password-reset.service';

@Component({
  selector: 'app-reset-password',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    ButtonModule,
    PasswordModule,
    MessageModule
  ],
  templateUrl: './reset-password.html',
  styleUrl: './reset-password.css'
})
export class ResetPasswordComponent implements OnInit {
  resetPasswordForm: FormGroup;
  loading = false;
  verifying = true;
  errorMessage = '';
  successMessage = '';
  token: string = '';
  tokenValid = false;
  userEmail = '';
  passwordReset = false;

  constructor(
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private router: Router,
    private passwordResetService: PasswordResetService
  ) {
    this.resetPasswordForm = this.fb.group({
      new_password: ['', [Validators.required, Validators.minLength(8)]],
      new_password_confirm: ['', Validators.required]
    }, { validators: this.passwordMatchValidator });
  }

  ngOnInit(): void {
    // Récupérer le token depuis l'URL
    this.route.queryParams.subscribe(params => {
      this.token = params['token'];

      if (!this.token) {
        this.verifying = false;
        this.errorMessage = 'Aucun token de réinitialisation fourni.';
        return;
      }

      // Vérifier la validité du token
      this.verifyToken();
    });
  }

  /**
   * Vérifier la validité du token
   */
  verifyToken(): void {
    this.verifying = true;
    this.errorMessage = '';

    this.passwordResetService.verifyToken(this.token).subscribe({
      next: (response: TokenVerifyResponse) => {
        this.verifying = false;

        if (response.valid) {
          this.tokenValid = true;
          this.userEmail = response.email || '';
        } else {
          this.tokenValid = false;
          this.errorMessage = response.error || 'Token invalide.';
        }
      },
      error: (error) => {
        this.verifying = false;
        this.tokenValid = false;

        if (error.error && error.error.error) {
          this.errorMessage = error.error.error;
        } else {
          this.errorMessage = 'Impossible de vérifier le token.';
        }
      }
    });
  }

  /**
   * Validateur personnalisé pour vérifier que les mots de passe correspondent
   */
  passwordMatchValidator(group: FormGroup) {
    const password = group.get('new_password')?.value;
    const confirmPassword = group.get('new_password_confirm')?.value;
    return password === confirmPassword ? null : { passwordMismatch: true };
  }

  /**
   * Soumettre le nouveau mot de passe
   */
  onSubmit(): void {
    if (this.resetPasswordForm.invalid) {
      this.resetPasswordForm.markAllAsTouched();
      return;
    }

    this.loading = true;
    this.errorMessage = '';
    this.successMessage = '';

    const data = {
      token: this.token,
      new_password: this.resetPasswordForm.value.new_password,
      new_password_confirm: this.resetPasswordForm.value.new_password_confirm
    };

    this.passwordResetService.confirmReset(data).subscribe({
      next: (response) => {
        this.loading = false;
        this.passwordReset = true;
        this.successMessage = response.message;

        // Rediriger vers la page de connexion après 3 secondes
        setTimeout(() => {
          this.router.navigate(['/login'], {
            state: { passwordResetSuccess: true }
          });
        }, 3000);
      },
      error: (error) => {
        this.loading = false;
        console.error('Password reset error:', error);

        if (error.error && typeof error.error === 'object') {
          // Erreurs de validation
          if (error.error.new_password) {
            this.errorMessage = Array.isArray(error.error.new_password)
              ? error.error.new_password.join(', ')
              : error.error.new_password;
          } else if (error.error.new_password_confirm) {
            this.errorMessage = Array.isArray(error.error.new_password_confirm)
              ? error.error.new_password_confirm.join(', ')
              : error.error.new_password_confirm;
          } else if (error.error.error) {
            this.errorMessage = error.error.error;
          } else {
            this.errorMessage = 'Une erreur est survenue lors de la réinitialisation.';
          }
        } else {
          this.errorMessage = error.message || 'Une erreur est survenue.';
        }

        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    });
  }

  getFieldError(fieldName: string): string {
    const field = this.resetPasswordForm.get(fieldName);
    if (!field?.touched) return '';

    if (field?.hasError('required')) {
      return 'Ce champ est requis';
    }
    if (field?.hasError('minlength')) {
      const minLength = field.errors?.['minlength'].requiredLength;
      return `Minimum ${minLength} caractères requis`;
    }

    if (fieldName === 'new_password_confirm' && this.resetPasswordForm.hasError('passwordMismatch')) {
      return 'Les mots de passe ne correspondent pas';
    }

    return '';
  }

  isFieldInvalid(fieldName: string): boolean {
    const field = this.resetPasswordForm.get(fieldName);
    return !!(field && field.invalid && field.touched);
  }
}
