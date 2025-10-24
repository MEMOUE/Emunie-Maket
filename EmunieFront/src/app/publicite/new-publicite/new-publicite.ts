import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { MessageService } from 'primeng/api';
import { DialogService, DynamicDialogRef } from 'primeng/dynamicdialog';
import { AdvertisementService } from '../../service/advertisement.service';
import { PaymentMethodDialog } from '../../payment-method-dialog/payment-method-dialog'
import { Toast } from 'primeng/toast';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { InputNumberModule } from 'primeng/inputnumber';

@Component({
  selector: 'app-new-publicite',
  templateUrl: './new-publicite.html',
  styleUrls: ['./new-publicite.css'],
  providers: [MessageService, DialogService],
  imports: [
    CommonModule,
    ReactiveFormsModule,
    Toast,
    ButtonModule,
    InputTextModule,
    InputNumberModule
  ],
  standalone: true
})
export class NewPublicite implements OnInit {
  form: FormGroup;
  isSubmitting = signal(false);
  selectedFile: File | null = null;
  imagePreview: string | null = null;
  pricePerDay = 1000;
  today: string = new Date().toISOString().split('T')[0];
  ref: DynamicDialogRef<any> | null | undefined;
  createdAdvertisementId: number | null = null;

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private messageService: MessageService,
    private dialogService: DialogService,
    private advertisementService: AdvertisementService
  ) {
    this.form = this.fb.group({
      title: ['', [Validators.required, Validators.minLength(5)]],
      link: ['', [Validators.required, Validators.pattern(/^https?:\/\/.+/)]],
      start_date: [this.today, Validators.required],
      duration_days: [1, [Validators.required, Validators.min(1)]],
      image: [null, Validators.required]
    });
  }

  ngOnInit(): void {
    // Calculer la durée en heures quand les jours changent
    this.form.get('duration_days')?.valueChanges.subscribe(days => {
      if (days && days > 0) {
        // La durée en heures sera calculée lors de la soumission
      }
    });
  }

  get totalPrice(): number {
    const days = this.form.get('duration_days')?.value || 0;
    return days * this.pricePerDay;
  }

  get durationHours(): number {
    const days = this.form.get('duration_days')?.value || 0;
    return days * 24;
  }

  onFileSelect(event: any) {
    const file = event.target.files?.[0];
    if (file) {
      // Vérifier la taille du fichier (max 2MB)
      if (file.size > 2 * 1024 * 1024) {
        this.messageService.add({
          severity: 'error',
          summary: 'Fichier trop volumineux',
          detail: 'La taille de l\'image ne doit pas dépasser 2 Mo'
        });
        return;
      }

      // Vérifier le type de fichier
      const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
      if (!validTypes.includes(file.type)) {
        this.messageService.add({
          severity: 'error',
          summary: 'Format invalide',
          detail: 'Formats acceptés : JPG, PNG, GIF'
        });
        return;
      }

      this.selectedFile = file;
      this.form.patchValue({ image: file });

      // Créer un aperçu de l'image
      const reader = new FileReader();
      reader.onload = (e: any) => {
        this.imagePreview = e.target.result;
      };
      reader.readAsDataURL(file);
    }
  }

  removeImage() {
    this.selectedFile = null;
    this.imagePreview = null;
    this.form.patchValue({ image: null });
  }

  onSubmit() {
    if (this.form.invalid) {
      this.messageService.add({
        severity: 'warn',
        summary: 'Formulaire incomplet',
        detail: 'Veuillez remplir tous les champs obligatoires.'
      });

      // Marquer tous les champs comme touchés pour afficher les erreurs
      Object.keys(this.form.controls).forEach(key => {
        this.form.get(key)?.markAsTouched();
      });
      return;
    }

    this.isSubmitting.set(true);

    const formData = new FormData();
    const formValue = this.form.getRawValue();

    // Ajouter les données au FormData
    formData.append('title', formValue.title);
    formData.append('link', formValue.link);
    formData.append('start_date', formValue.start_date);
    formData.append('duration_hours', this.durationHours.toString());

    if (this.selectedFile) {
      formData.append('image', this.selectedFile, this.selectedFile.name);
    }

    // Créer d'abord la publicité
    this.advertisementService.create(formData).subscribe({
      next: (response) => {
        this.createdAdvertisementId = response.id!;

        this.messageService.add({
          severity: 'success',
          summary: 'Publicité créée',
          detail: 'Votre publicité a été créée avec succès. Veuillez procéder au paiement.'
        });

        // Ouvrir le dialogue de paiement
        setTimeout(() => {
          this.openPaymentDialog();
        }, 1000);

        this.isSubmitting.set(false);
      },
      error: (error) => {
        console.error('Error creating advertisement:', error);

        let errorMessage = 'Une erreur est survenue lors de la création de la publicité.';

        if (error.error) {
          if (typeof error.error === 'string') {
            errorMessage = error.error;
          } else if (error.error.detail) {
            errorMessage = error.error.detail;
          } else {
            // Extraire les erreurs des champs
            const fieldErrors = Object.entries(error.error)
              .map(([key, value]) => `${key}: ${value}`)
              .join(', ');
            if (fieldErrors) {
              errorMessage = fieldErrors;
            }
          }
        }

        this.messageService.add({
          severity: 'error',
          summary: 'Erreur',
          detail: errorMessage
        });

        this.isSubmitting.set(false);
      }
    });
  }

  openPaymentDialog() {
    if (!this.createdAdvertisementId) {
      this.messageService.add({
        severity: 'error',
        summary: 'Erreur',
        detail: 'Impossible d\'ouvrir le dialogue de paiement'
      });
      return;
    }

    this.ref = this.dialogService.open(PaymentMethodDialog, {
      header: 'Paiement de la publicité',
      width: '600px',
      modal: true,
      dismissableMask: false,
      data: {
        advertisementId: this.createdAdvertisementId,
        totalPrice: this.totalPrice
      }
    });

    this.ref!.onClose.subscribe((result: any) => {
      if (result && result.success) {
        // Paiement réussi
        this.messageService.add({
          severity: 'success',
          summary: 'Paiement initié',
          detail: result.data.payment_instructions || 'Votre paiement a été initié avec succès'
        });

        // Afficher les instructions de paiement si disponibles
        if (result.data.payment_instructions) {
          setTimeout(() => {
            this.messageService.add({
              severity: 'info',
              summary: 'Instructions',
              detail: result.data.payment_instructions,
              life: 10000
            });
          }, 1500);
        }

        // Rediriger vers la liste des publicités après quelques secondes
        setTimeout(() => {
          this.router.navigate(['/publicite/my']);
        }, 3000);
      } else {
        // Paiement annulé ou échoué
        this.messageService.add({
          severity: 'warn',
          summary: 'Paiement non effectué',
          detail: 'Vous pourrez effectuer le paiement plus tard depuis votre liste de publicités'
        });
      }
    });
  }

  cancel() {
    if (confirm('Êtes-vous sûr de vouloir annuler ? Les données saisies seront perdues.')) {
      this.router.navigate(['/publicite']);
    }
  }

  ngOnDestroy() {
    if (this.ref) {
      this.ref.close();
    }
  }
}
