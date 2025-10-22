import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { Router } from '@angular/router';
import {NgForOf, NgIf} from '@angular/common';

@Component({
  selector: 'app-new-anonce',
  templateUrl: './new-anonce.html',
  imports: [NgForOf, ReactiveFormsModule, NgIf],
  styleUrls: ['./new-anonce.css']
})
export class NewAnonceComponent implements OnInit {
  form!: FormGroup;
  categories: Array<{ value: string; label: string }> = [];
  cities: Array<{ value: string; label: string }> = [];
  selectedImages: File[] = [];
  imagePreviews: string[] = [];
  loading = false;
  maxImages = 3;

  constructor(
    private fb: FormBuilder,
    private http: HttpClient,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.form = this.fb.group({
      title: ['', Validators.required],
      description: ['', Validators.required],
      price: ['', Validators.required],
      currency: ['FCFA', Validators.required],
      is_negotiable: [true],
      category: ['', Validators.required],
      city: ['', Validators.required],
      address: [''],
      expires_at: ['', Validators.required],
      images: [null]
    });

    this.loadCategories();
    this.loadCities();
  }

  loadCategories() {
    this.http.get<{ categories: any }>(`${environment.apiUrl}produit/categories/`).subscribe({
      next: (res) => (this.categories = res.categories ?? []),
      error: (err) => console.error(err)
    });
  }

  loadCities() {
    this.http.get<{ cities: any }>(`${environment.apiUrl}produit/cities/`).subscribe({
      next: (res) => (this.cities = res.cities ?? []),
      error: (err) => console.error(err)
    });
  }

  today(): string {
    return new Date().toISOString().split('T')[0];
  }

  onImagesSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (!input.files?.length) return;

    const newFiles = Array.from(input.files);
    const total = this.selectedImages.length + newFiles.length;

    if (total > this.maxImages) {
      alert(`Vous pouvez ajouter au maximum ${this.maxImages} images.`);
      input.value = '';
      return;
    }

    for (const file of newFiles) {
      this.selectedImages.push(file);
      const reader = new FileReader();
      reader.onload = (e: any) => this.imagePreviews.push(e.target.result);
      reader.readAsDataURL(file);
    }

    input.value = ''; // reset input
  }

  removeImage(index: number): void {
    this.imagePreviews.splice(index, 1);
    this.selectedImages.splice(index, 1);
  }

  submit(): void {
    if (this.form.invalid) return;
    this.loading = true;

    const formData = new FormData();
    Object.entries(this.form.value).forEach(([key, value]) => {
      if (key !== 'images' && value !== null && value !== undefined) {
        formData.append(key, value as any);
      }
    });

    this.selectedImages.forEach((file) => formData.append('images', file));

    this.http.post(`${environment.apiUrl}produit/ads/create/`, formData).subscribe({
      next: () => {
        this.loading = false;
        this.router.navigate(['/my-ads']);
      },
      error: (err) => {
        this.loading = false;
        console.error('Erreur lors de la création de l’annonce :', err);
      }
    });
  }
}
