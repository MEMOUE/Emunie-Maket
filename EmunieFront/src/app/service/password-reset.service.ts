// EmunieFront/src/app/service/password-reset.service.ts

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetConfirm {
  token: string;
  new_password: string;
  new_password_confirm: string;
}

export interface PasswordResetResponse {
  message: string;
  detail: string;
}

export interface TokenVerifyResponse {
  valid: boolean;
  email?: string;
  username?: string;
  error?: string;
}

@Injectable({
  providedIn: 'root'
})
export class PasswordResetService {
  private apiUrl = `${environment.apiUrl}user/password/reset`;

  constructor(private http: HttpClient) {}

  /**
   * Demander un lien de réinitialisation
   */
  requestReset(email: string): Observable<PasswordResetResponse> {
    return this.http.post<PasswordResetResponse>(
      `${this.apiUrl}/request/`,
      { email }
    );
  }

  /**
   * Vérifier la validité d'un token
   */
  verifyToken(token: string): Observable<TokenVerifyResponse> {
    return this.http.post<TokenVerifyResponse>(
      `${this.apiUrl}/verify/`,
      { token }
    );
  }

  /**
   * Confirmer la réinitialisation avec un nouveau mot de passe
   */
  confirmReset(data: PasswordResetConfirm): Observable<PasswordResetResponse> {
    return this.http.post<PasswordResetResponse>(
      `${this.apiUrl}/confirm/`,
      data
    );
  }
}
