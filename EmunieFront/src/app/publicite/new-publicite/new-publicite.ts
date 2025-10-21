import { Component, OnInit, signal } from '@angular/core';
import {FormBuilder, FormGroup, ReactiveFormsModule, Validators} from '@angular/forms';
import { Router } from '@angular/router';
import { MessageService } from 'primeng/api';
import { AdvertisementService } from '../../service/advertisement.service';
import {Toast} from 'primeng/toast';

@Component({
  selector: 'app-new-publicite',
  templateUrl: './new-publicite.html',
  styleUrls: ['./new-publicite.css'],
  providers: [MessageService],
  imports: [
    ReactiveFormsModule,
    Toast
  ],
  standalone: true
})
export class NewPublicite implements OnInit {
  form: FormGroup;
  isSubmitting = signal(false);
  selectedFile: File | null = null;
  pricePerDay = 1000;
  today: string = new Date().toISOString().split('T')[0];


  constructor(
    private fb: FormBuilder,
    private router: Router,
    private messageService: MessageService,
    private advertisementService: AdvertisementService
  ) {
    this.form = this.fb.group({
      title: ['', Validators.required],
      link: ['', Validators.required],
      start_date: [null, Validators.required],
      duration_days: [1, [Validators.required, Validators.min(1)]],
      image: [null, Validators.required]
    });
  }

  ngOnInit(): void {}

  get totalPrice(): number {
    const days = this.form.get('duration_days')?.value || 0;
    return days * this.pricePerDay;
  }

  onFileSelect(event: any) {
    const file = event.target.files?.[0];
    if (file) {
      this.selectedFile = file;
      this.form.patchValue({ image: file });
    }
  }

  onSubmit() {
    if (this.form.invalid) {
      this.messageService.add({
        severity: 'warn',
        summary: 'Champs manquants',
        detail: 'Veuillez remplir tous les champs obligatoires.'
      });
      return;
    }

    this.isSubmitting.set(true);

    const formData = new FormData();
    Object.entries(this.form.getRawValue()).forEach(([key, value]) => {
      if (value) formData.append(key, value as any);
    });

    formData.append('total_price', this.totalPrice.toString());

    this.advertisementService.create(formData).subscribe({
      next: () => {
        this.messageService.add({
          severity: 'success',
          summary: 'Succès',
          detail: 'Publicité créée avec succès !'
        });
        this.isSubmitting.set(false);
        this.router.navigate(['/dashboard']);
      },
      error: () => {
        this.messageService.add({
          severity: 'error',
          summary: 'Erreur',
          detail: 'Une erreur est survenue lors de la création.'
        });
        this.isSubmitting.set(false);
      }
    });
  }
}
