import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject, throwError } from 'rxjs';
import { tap, catchError } from 'rxjs/operators';
import { Router } from '@angular/router';

export interface RegisterData {
  username: string;
  email: string;
  phone_number?: string;  // Optionnel
  password: string;
  password_confirm: string;
  first_name: string;
  last_name: string;
  avatar?: File;  // Optionnel
}

export interface LoginData {
  username: string;  // Peut être username OU email
  password: string;
}

export interface AuthResponse {
  token: string;
  refresh?: string;
  user: User;
}

export interface User {
  id: number;
  username: string;
  email: string;
  phone_number?: string;
  first_name: string;
  last_name: string;
  full_name: string;
  avatar?: string;
  location?: string;
  bio?: string;
  average_rating: number;
  total_ads: number;
  total_views: number;
  email_verified: boolean;
  phone_verified: boolean;
  is_premium: boolean;
  is_premium_active: boolean;
  premium_end_date?: string;
  can_create_ad: boolean;
  remaining_ads: number;
  created_at: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'http://localhost:8000/api';
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor(
    private http: HttpClient,
    private router: Router
  ) {
    // Charger l'utilisateur depuis le localStorage au démarrage
    this.loadStoredUser();
  }

  /**
   * Charger l'utilisateur stocké au démarrage
   */
  private loadStoredUser(): void {
    const token = this.getToken();
    if (token) {
      const storedUser = localStorage.getItem('currentUser');
      if (storedUser) {
        try {
          const user = JSON.parse(storedUser);
          this.currentUserSubject.next(user);
        } catch (e) {
          console.error('Error parsing stored user', e);
          this.logout();
        }
      } else {
        // Si token existe mais pas l'utilisateur, charger le profil
        this.getProfile().subscribe({
          error: () => this.logout()
        });
      }
    }
  }

  /**
   * Inscription d'un nouvel utilisateur
   */
  register(data: RegisterData): Observable<{message: string, user_id: number}> {
    // Si avatar est fourni, utiliser FormData
    if (data.avatar) {
      const formData = new FormData();
      Object.keys(data).forEach(key => {
        const value = (data as any)[key];
        if (value !== undefined && value !== null) {
          if (key === 'avatar' && value instanceof File) {
            formData.append(key, value, value.name);
          } else {
            formData.append(key, value);
          }
        }
      });
      return this.http.post<{message: string, user_id: number}>(
        `${this.apiUrl}/user/register/`,
        formData
      ).pipe(
        catchError(this.handleError.bind(this))
      );
    }

    // Sinon, utiliser JSON
    return this.http.post<{message: string, user_id: number}>(
      `${this.apiUrl}/user/register/`,
      data
    ).pipe(
      catchError(this.handleError.bind(this))
    );
  }

  /**
   * Connexion utilisateur avec email OU username
   */
  login(credentials: LoginData): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.apiUrl}/auth/login/`, credentials).pipe(
      tap(response => {
        if (response.token) {
          this.setSession(response);
        }
      }),
      catchError(this.handleError.bind(this))
    );
  }

  /**
   * Déconnexion
   */
  logout(): void {
    // Appeler l'API de déconnexion si possible
    const token = this.getToken();
    if (token) {
      this.http.post(`${this.apiUrl}/auth/logout/`, {}).subscribe({
        error: (err) => console.error('Logout API error:', err)
      });
    }

    // Nettoyer le localStorage
    localStorage.removeItem('token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('currentUser');

    // Réinitialiser le subject
    this.currentUserSubject.next(null);

    // Rediriger vers l'accueil
    this.router.navigate(['/accueil']);
  }

  /**
   * Obtenir le profil utilisateur
   */
  getProfile(): Observable<User> {
    return this.http.get<User>(`${this.apiUrl}/user/profile/`).pipe(
      tap(user => {
        localStorage.setItem('currentUser', JSON.stringify(user));
        this.currentUserSubject.next(user);
      }),
      catchError(this.handleError.bind(this))
    );
  }

  /**
   * Mettre à jour le profil utilisateur
   */
  updateProfile(data: Partial<User> | FormData): Observable<User> {
    return this.http.patch<User>(`${this.apiUrl}/user/profile/`, data).pipe(
      tap(user => {
        localStorage.setItem('currentUser', JSON.stringify(user));
        this.currentUserSubject.next(user);
      }),
      catchError(this.handleError.bind(this))
    );
  }

  /**
   * Changer le mot de passe
   */
  changePassword(data: {
    old_password: string;
    new_password: string;
    new_password_confirm: string
  }): Observable<{message: string}> {
    return this.http.post<{message: string}>(
      `${this.apiUrl}/user/password/change/`,
      data
    ).pipe(
      catchError(this.handleError.bind(this))
    );
  }

  /**
   * Vérifier si l'utilisateur est authentifié
   */
  isAuthenticated(): boolean {
    const token = this.getToken();
    if (!token) return false;

    // Vérifier si le token n'est pas expiré (si JWT)
    try {
      const payload = this.decodeToken(token);
      if (payload && payload.exp) {
        const isExpired = payload.exp < Date.now() / 1000;
        if (isExpired) {
          this.logout();
          return false;
        }
        return true;
      }
      return true;
    } catch {
      return !!token;
    }
  }

  /**
   * Obtenir le token
   */
  getToken(): string | null {
    return localStorage.getItem('token');
  }

  /**
   * Obtenir l'utilisateur courant
   */
  getCurrentUser(): User | null {
    return this.currentUserSubject.value;
  }

  /**
   * Observable de l'utilisateur courant
   */
  getCurrentUser$(): Observable<User | null> {
    return this.currentUser$;
  }

  /**
   * Rafraîchir le token
   */
  refreshToken(): Observable<{token: string}> {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      return throwError(() => new Error('No refresh token'));
    }

    return this.http.post<{token: string}>(`${this.apiUrl}/auth/refresh/`, {
      refresh: refreshToken
    }).pipe(
      tap(response => {
        if (response.token) {
          localStorage.setItem('token', response.token);
        }
      }),
      catchError(err => {
        this.logout();
        return throwError(() => err);
      })
    );
  }

  /**
   * Enregistrer la session
   */
  private setSession(authResult: AuthResponse): void {
    localStorage.setItem('token', authResult.token);
    if (authResult.refresh) {
      localStorage.setItem('refresh_token', authResult.refresh);
    }
    if (authResult.user) {
      localStorage.setItem('currentUser', JSON.stringify(authResult.user));
      this.currentUserSubject.next(authResult.user);
    }
  }

  /**
   * Décoder le token JWT
   */
  private decodeToken(token: string): any {
    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
        atob(base64).split('').map(c => {
          return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join('')
      );
      return JSON.parse(jsonPayload);
    } catch {
      return null;
    }
  }

  /**
   * Gestion des erreurs HTTP - retourne l'erreur telle quelle pour que le composant l'affiche
   */
  private handleError(error: any): Observable<never> {
    console.error('HTTP Error:', {
      status: error.status,
      statusText: error.statusText,
      error: error.error,
      message: error.message
    });

    // Retourner l'erreur complète pour que le composant puisse extraire le message
    return throwError(() => error);
  }
}
