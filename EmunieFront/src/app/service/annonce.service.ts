import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AnnonceService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getCategories(): Observable<any> {
    return this.http.get(`${this.apiUrl}produit/categories/`);
  }

  getCities(): Observable<any> {
    return this.http.get(`${this.apiUrl}produit/cities/`);
  }

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
    return this.http.get(`${this.apiUrl}produit/ads/check-limit/`);
  }

  // Nouvelle méthode pour récupérer les données de la page d'accueil
  getHomeData(): Observable<any> {
    return this.http.get(`${this.apiUrl}produit/home-data/`);
  }
}
