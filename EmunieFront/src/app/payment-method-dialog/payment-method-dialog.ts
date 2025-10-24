import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { DynamicDialogRef, DynamicDialogConfig } from 'primeng/dynamicdialog';
import { MessageService } from 'primeng/api';
import { AdvertisementService } from '../service/advertisement.service';
import { PaymentMethod } from '../model/advertisement.model';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { RadioButtonModule } from 'primeng/radiobutton';

@Component({
  selector: 'app-payment-method-dialog',
  templateUrl: './payment-method-dialog.html',
  styleUrls: ['./payment-method-dialog.css'],
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    ButtonModule,
    InputTextModule,
    RadioButtonModule
  ]
})
export class PaymentMethodDialog implements OnInit {
  paymentForm: FormGroup;
  paymentMethods = signal<PaymentMethod[]>([]);
  loading = signal(false);
  processingPayment = signal(false);
  advertisementId: number;
  totalPrice: number;

  constructor(
    private fb: FormBuilder,
    private ref: DynamicDialogRef,
    private config: DynamicDialogConfig,
    private advertisementService: AdvertisementService,
    private messageService: MessageService
  ) {
    this.advertisementId = this.config.data.advertisementId;
    this.totalPrice = this.config.data.totalPrice;

    this.paymentForm = this.fb.group({
      payment_method: [null, Validators.required],
      phone_number: ['', [Validators.required, Validators.pattern(/^[0-9]{10}$/)]]
    });
  }

  ngOnInit(): void {
    this.loadPaymentMethods();
  }

  loadPaymentMethods(): void {
    this.loading.set(true);
    this.advertisementService.getPaymentMethods().subscribe({
      next: (methods) => {
        // Filtrer pour n'afficher que Wave et Orange Money
        const filteredMethods = methods.filter(m =>
          m.payment_type === 'wave' ||
          m.payment_type === 'orange_money'
        );
        this.paymentMethods.set(filteredMethods);
        this.loading.set(false);
      },
      error: (error) => {
        this.messageService.add({
          severity: 'error',
          summary: 'Erreur',
          detail: 'Impossible de charger les méthodes de paiement'
        });
        this.loading.set(false);
      }
    });
  }

  getMethodIcon(paymentType: string): string {
    switch(paymentType) {
      case 'wave':
        return 'pi pi-wallet';
      case 'orange_money':
        return 'pi pi-mobile';
      default:
        return 'pi pi-credit-card';
    }
  }

  onSubmit(): void {
    if (this.paymentForm.invalid) {
      this.messageService.add({
        severity: 'warn',
        summary: 'Attention',
        detail: 'Veuillez remplir tous les champs requis'
      });
      return;
    }

    this.processingPayment.set(true);

    const paymentData = {
      advertisement_id: this.advertisementId,
      payment_method: this.paymentForm.value.payment_method,
      phone_number: this.paymentForm.value.phone_number
    };

    this.advertisementService.createAdvertisementTransaction(paymentData).subscribe({
      next: (response: any) => {
        this.messageService.add({
          severity: 'success',
          summary: 'Succès',
          detail: 'Transaction initiée avec succès'
        });
        this.ref.close({
          success: true,
          data: response
        });
      },
      error: (error) => {
        this.messageService.add({
          severity: 'error',
          summary: 'Erreur',
          detail: error.error?.detail || 'Erreur lors de l\'initiation du paiement'
        });
        this.processingPayment.set(false);
      }
    });
  }

  cancel(): void {
    this.ref.close({ success: false });
  }
}
