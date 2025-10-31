// EmunieFront/src/app/service/google-auth.service.ts

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

declare const google: any;

export interface GoogleAuthResponse {
  token: string;
  user: any;
  created: boolean;
  message: string;
}

@Injectable({
  providedIn: 'root'
})
export class GoogleAuthService {
  private apiUrl = environment.apiUrl;
  private googleClientId = environment.googleClientId;
  private googleInitialized = false;

  constructor(private http: HttpClient) {}

  /**
   * Initialiser Google Sign-In
   */
  initializeGoogleSignIn(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.googleInitialized) {
        resolve();
        return;
      }

      // Vérifier si le script est déjà chargé
      if (typeof google !== 'undefined' && google.accounts) {
        this.googleInitialized = true;
        resolve();
        return;
      }

      // Charger le script Google
      const script = document.createElement('script');
      script.src = 'https://accounts.google.com/gsi/client';
      script.async = true;
      script.defer = true;

      script.onload = () => {
        this.googleInitialized = true;
        resolve();
      };

      script.onerror = () => {
        reject(new Error('Failed to load Google Sign-In script'));
      };

      document.head.appendChild(script);
    });
  }

  /**
   * Authentification Google avec popup
   */
  async signInWithGoogle(): Promise<string> {
    await this.initializeGoogleSignIn();

    return new Promise((resolve, reject) => {
      try {
        google.accounts.id.initialize({
          client_id: this.googleClientId,
          callback: (response: any) => {
            if (response.credential) {
              resolve(response.credential);
            } else {
              reject(new Error('No credential received'));
            }
          },
          error_callback: (error: any) => {
            reject(error);
          }
        });

        // Afficher la popup de connexion Google
        google.accounts.id.prompt((notification: any) => {
          if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
            // Fallback: utiliser renderButton si la popup ne s'affiche pas
            console.log('Google prompt not displayed, try again');
          }
        });
      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * Authentification via bouton Google
   */
  async renderGoogleButton(element: HTMLElement): Promise<void> {
    await this.initializeGoogleSignIn();

    return new Promise((resolve, reject) => {
      try {
        google.accounts.id.initialize({
          client_id: this.googleClientId,
          callback: (response: any) => {
            // Ce callback sera géré par le composant
            resolve();
          }
        });

        google.accounts.id.renderButton(
          element,
          {
            theme: 'outline',
            size: 'large',
            type: 'standard',
            text: 'continue_with',
            shape: 'rectangular',
            logo_alignment: 'left',
            width: element.offsetWidth
          }
        );

        resolve();
      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * Envoyer le token Google au backend pour authentification
   */
  authenticateWithBackend(googleToken: string): Observable<GoogleAuthResponse> {
    return this.http.post<GoogleAuthResponse>(
      `${this.apiUrl}auth/google/`,
      { token: googleToken }
    );
  }

  /**
   * Déconnexion Google
   */
  signOut(): void {
    if (typeof google !== 'undefined' && google.accounts) {
      google.accounts.id.disableAutoSelect();
    }
  }
}
