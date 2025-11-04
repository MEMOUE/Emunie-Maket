import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { RadioButtonModule } from 'primeng/radiobutton';
import { InputTextModule } from 'primeng/inputtext';
import { MessageModule } from 'primeng/message';
import { DialogModule } from 'primeng/dialog';
import { PremiumService, PremiumPlan, SubscribeResponse } from '../../service/premium.service';
import { AuthService } from '../../service/auth';

@Component({
  selector: 'app-activate-premium',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    ButtonModule,
    RadioButtonModule,
    InputTextModule,
    MessageModule,
    DialogModule
  ],
  templateUrl: './activate-premium.html',
  styleUrl: './activate-premium.css'
})
export class ActivatePremium implements OnInit {
  // ⚠️ CORRECTION : Toujours initialiser comme tableau vide
  plans: PremiumPlan[] = [];
  selectedPlan: PremiumPlan | null = null;
  paymentForm: FormGroup;
  loading = false;
  errorMessage = '';
  successMessage = '';

  // Dialog de confirmation
  showPaymentDialog = false;
  paymentResponse: SubscribeResponse | null = null;

  paymentMethods = [
    { value: 'wave', label: 'Wave', icon: '💳' },
    { value: 'orange_money', label: 'Orange Money', icon: '📱' }
  ];

  constructor(
    private premiumService: PremiumService,
    private authService: AuthService,
    private fb: FormBuilder,
    private router: Router
  ) {
    this.paymentForm = this.fb.group({
      payment_method: ['wave', Validators.required],
      phone_number: ['', [Validators.required, Validators.pattern(/^(225)?[0-9]{10}$/)]]
    });
  }

  ngOnInit(): void {
    this.loadPlans();
  }

  /**
   * Charger les plans Premium
   */
  loadPlans(): void {
    this.loading = true;
    this.errorMessage = '';

    this.premiumService.getPlans().subscribe({
      next: (response) => {
        console.log('Plans reçus:', response);

        // ⚠️ CORRECTION : Vérifier que la réponse est bien un tableau
        if (Array.isArray(response)) {
          this.plans = response;
        } else {
          console.error('La réponse n\'est pas un tableau:', response);
          this.plans = [];
          this.errorMessage = 'Format de réponse invalide';
        }

        this.loading = false;

        // Log pour debug
        console.log('Nombre de plans chargés:', this.plans.length);
      },
      error: (error) => {
        console.error('Erreur lors du chargement des plans:', error);
        this.errorMessage = 'Impossible de charger les plans Premium';
        this.plans = []; // ⚠️ S'assurer que plans reste un tableau
        this.loading = false;
      }
    });
  }

  /**
   * Sélectionner un plan
   */
  selectPlan(plan: PremiumPlan): void {
    this.selectedPlan = plan;
    this.errorMessage = '';
    console.log('Plan sélectionné:', plan);
  }

  /**
   * Vérifier si un plan est sélectionné
   */
  isPlanSelected(plan: PremiumPlan): boolean {
    return this.selectedPlan?.id === plan.id;
  }

  /**
   * Procéder au paiement
   */
  proceedToPayment(): void {
    if (!this.selectedPlan) {
      this.errorMessage = 'Veuillez sélectionner un plan';
      return;
    }

    if (this.paymentForm.invalid) {
      Object.keys(this.paymentForm.controls).forEach(key => {
        this.paymentForm.get(key)?.markAsTouched();
      });
      return;
    }

    this.loading = true;
    this.errorMessage = '';
    this.successMessage = '';

    const subscribeData = {
      plan_id: this.selectedPlan.id,
      payment_method: this.paymentForm.value.payment_method,
      phone_number: this.paymentForm.value.phone_number,
      auto_activate: true // Mode développement - à retirer en production
    };

    console.log('Données d\'abonnement:', subscribeData);

    this.premiumService.subscribe(subscribeData).subscribe({
      next: (response) => {
        this.loading = false;
        this.paymentResponse = response;
        this.showPaymentDialog = true;

        console.log('Abonnement créé:', response);

        // Recharger le profil pour mettre à jour le statut Premium
        this.authService.getProfile().subscribe();
      },
      error: (error) => {
        this.loading = false;
        console.error('Erreur lors de l\'abonnement:', error);

        if (error.error?.error) {
          this.errorMessage = error.error.error;
        } else if (error.error?.detail) {
          this.errorMessage = error.error.detail;
        } else {
          this.errorMessage = 'Erreur lors de l\'abonnement. Veuillez réessayer.';
        }

        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    });
  }

  /**
   * Fermer le dialog et rediriger
   */
  closePaymentDialog(): void {
    this.showPaymentDialog = false;
    this.router.navigate(['/dashboard/overview']);
  }

  /**
   * Obtenir le badge du plan
   */
  getPlanBadge(planType: string): string {
    return planType === 'unlimited' ? '⭐ POPULAIRE' : '';
  }

  /**
   * Obtenir l'erreur d'un champ
   */
  getFieldError(fieldName: string): string {
    const field = this.paymentForm.get(fieldName);
    if (!field?.touched) return '';

    if (field?.hasError('required')) return 'Ce champ est requis';
    if (field?.hasError('pattern')) return 'Format de téléphone invalide (ex: 07XXXXXXXX)';

    return '';
  }

  /**
   * Vérifier si un champ est invalide
   */
  isFieldInvalid(fieldName: string): boolean {
    const field = this.paymentForm.get(fieldName);
    return !!(field && field.invalid && field.touched);
  }

  /**
   * Annuler et retourner au dashboard
   */
  cancel(): void {
    this.router.navigate(['/dashboard/overview']);
  }
}
