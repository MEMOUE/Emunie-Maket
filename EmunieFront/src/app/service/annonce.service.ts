import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Ad, City, Category } from '../model/annonce.model';

@Injectable({
  providedIn: 'root'
})
export class AnnonceService {
  private apiUrl = environment.apiUrl; // ex: http://localhost:8000/api/produit

  constructor(private http: HttpClient) {}

  // === CATÉGORIES ET VILLES ===
  getCategories(): Observable<any> {
    return this.http.get(`${this.apiUrl}produit/categories/`);
  }

  getCities(): Observable<any> {
    return this.http.get(`${this.apiUrl}produit/cities/`);
  }

  // === ANNONCES ===
  getAds(params?: any): Observable<any> {
    return this.http.get(`${this.apiUrl}produit/ads/`, { params });
  }

  getMyAds(): Observable<any> {
    return this.http.get(`${this.apiUrl}produit/my-ads/`);
  }

  getAdDetail(adId: string): Observable<any> {
    return this.http.get(`${this.apiUrl}produit/ads/${adId}/`);
  }

  createAd(data: FormData): Observable<any> {
    return this.http.post(`${this.apiUrl}produit/ads/create/`, data);
  }

  updateAd(adId: string, data: FormData | any): Observable<any> {
    return this.http.put(`${this.apiUrl}produit/ads/${adId}/update/`, data);
  }

  deleteAd(adId: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}produit/ads/${adId}/delete/`);
  }

  checkAdLimit(): Observable<any> {
    return this.http.get(`${this.apiUrl}produitproduit/ads/check-limit/`);
  }

  // === FAVORIS ===
  getFavorites(): Observable<any> {
    return this.http.get(`${this.apiUrl}produit/favorites/`);
  }

  toggleFavorite(adId: string): Observable<any> {
    return this.http.post(`${this.apiUrl}produit/favorites/toggle/`, { ad_id: adId });
  }

  // === SIGNALEMENT ===
  reportAd(adId: string, reason: string, description?: string): Observable<any> {
    return this.http.post(`${this.apiUrl}produit/ads/${adId}/report/`, { reason, description });
  }

  // === PUBLICITÉS PAYANTES ===
  getAdvertisements(): Observable<any> {
    return this.http.get(`${this.apiUrl}produit/advertisements/`);
  }

  getMyAdvertisements(): Observable<any> {
    return this.http.get(`${this.apiUrl}produit/advertisements/my/`);
  }

  createAdvertisement(data: FormData): Observable<any> {
    return this.http.post(`${this.apiUrl}produit/advertisements/create/`, data);
  }

  getAdvertisementDetail(adId: number): Observable<any> {
    return this.http.get(`${this.apiUrl}produit/advertisements/${adId}/`);
  }

  trackAdImpression(adId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}produit/advertisements/${adId}/impression/`, {});
  }

  trackAdClick(adId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}produit/advertisements/${adId}/click/`, {});
  }

  getAdvertisementStatistics(adId: number): Observable<any> {
    return this.http.get(`${this.apiUrl}produit/advertisements/${adId}/statistics/`);
  }
}
