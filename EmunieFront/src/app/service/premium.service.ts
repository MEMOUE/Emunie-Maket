import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface PremiumPlan {
  id: number;
  name: string;
  plan_type: 'basic' | 'unlimited';
  price: number;
  currency: string;
  max_ads: number | null;
  duration_days: number;
  description: string;
  features: string[];
}

export interface PremiumSubscription {
  id: number;
  plan: PremiumPlan;
  status: 'pending' | 'active' | 'expired' | 'cancelled';
  start_date: string | null;
  end_date: string | null;
  created_at: string;
  payment_method: string;
  transaction_reference: string;
  amount_paid: number;
  is_active: boolean;
  days_remaining: number;
}

export interface SubscribeRequest {
  plan_id: number;
  payment_method: 'wave' | 'orange_money';
  phone_number: string;
  auto_activate?: boolean; // Pour le mode développement
}

export interface SubscribeResponse {
  message: string;
  subscription: PremiumSubscription;
  payment_info: {
    method: string;
    phone: string;
    amount: number;
    reference: string;
    instructions: {
      provider: string;
      instructions: string[];
    };
  };
}

export interface PremiumStatus {
  is_premium: boolean;
  can_create_ad: boolean;
  remaining_ads: number;
  max_free_ads: number;
  active_subscription: PremiumSubscription | null;
}

@Injectable({
  providedIn: 'root'
})
export class PremiumService {
  private apiUrl = `${environment.apiUrl}premium/`;

  constructor(private http: HttpClient) {}

  /**
   * Récupérer les plans Premium disponibles
   */
  getPlans(): Observable<PremiumPlan[]> {
    return this.http.get<PremiumPlan[]>(`${this.apiUrl}plans/`);
  }

  /**
   * S'abonner à un plan Premium
   */
  subscribe(data: SubscribeRequest): Observable<SubscribeResponse> {
    return this.http.post<SubscribeResponse>(`${this.apiUrl}subscribe/`, data);
  }

  /**
   * Récupérer mes abonnements
   */
  getMySubscriptions(): Observable<PremiumSubscription[]> {
    return this.http.get<PremiumSubscription[]>(`${this.apiUrl}my-subscriptions/`);
  }

  /**
   * Annuler un abonnement
   */
  cancelSubscription(subscriptionId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}subscriptions/${subscriptionId}/cancel/`, {});
  }

  /**
   * Vérifier le statut Premium
   */
  checkStatus(): Observable<PremiumStatus> {
    return this.http.get<PremiumStatus>(`${this.apiUrl}check-status/`);
  }
}
