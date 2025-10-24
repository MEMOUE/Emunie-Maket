import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Advertisement, PaymentMethod, PaymentResponse } from '../model/advertisement.model';

@Injectable({
  providedIn: 'root'
})
export class AdvertisementService {
  private baseUrl = 'http://localhost:8000/api/publicite/';
  private monetisationUrl = 'http://localhost:8000/api/monetisation/';

  constructor(private http: HttpClient) {}

  // Gestion des publicités
  create(ad: FormData): Observable<Advertisement> {
    return this.http.post<Advertisement>(`${this.baseUrl}create/`, ad);
  }

  getAll(): Observable<Advertisement[]> {
    return this.http.get<Advertisement[]>(this.baseUrl);
  }

  getMyAdvertisements(): Observable<Advertisement[]> {
    return this.http.get<Advertisement[]>(`${this.baseUrl}my/`);
  }

  getById(id: number): Observable<Advertisement> {
    return this.http.get<Advertisement>(`${this.baseUrl}${id}/`);
  }

  getStatistics(id: number): Observable<any> {
    return this.http.get(`${this.baseUrl}${id}/statistics/`);
  }

  delete(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}${id}/`);
  }

  // Tracking
  trackImpression(id: number): Observable<any> {
    return this.http.post(`${this.baseUrl}${id}/impression/`, {});
  }

  trackClick(id: number): Observable<any> {
    return this.http.post(`${this.baseUrl}${id}/click/`, {});
  }

  // Méthodes de paiement
  getPaymentMethods(): Observable<PaymentMethod[]> {
    return this.http.get<PaymentMethod[]>(`${this.monetisationUrl}payment-methods/`);
  }

  // Créer une transaction pour la publicité
  createAdvertisementTransaction(data: {
    advertisement_id: number;
    payment_method: number;
    phone_number?: string;
  }): Observable<PaymentResponse> {
    return this.http.post<PaymentResponse>(
      `${this.monetisationUrl}transactions/create/`,
      data
    );
  }

  // Vérifier le statut d'une transaction
  getTransactionStatus(transactionId: number): Observable<any> {
    return this.http.get(`${this.monetisationUrl}transactions/${transactionId}/`);
  }
}
