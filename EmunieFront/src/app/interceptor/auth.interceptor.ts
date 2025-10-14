import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const router = inject(Router);
  const token = localStorage.getItem('token');

  // Cloner la requête et ajouter le token si disponible
  let clonedReq = req;

  if (token) {
    clonedReq = req.clone({
      setHeaders: {
        'Authorization': `Token ${token}`  // Utiliser 'Token' pour Django REST Framework
      }
    });
  }

  // Gérer les erreurs
  return next(clonedReq).pipe(
    catchError((error: HttpErrorResponse) => {
      // Si erreur 401 (non autorisé), déconnecter l'utilisateur
      if (error.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('currentUser');

        // Sauvegarder l'URL pour redirection après connexion
        const currentUrl = router.url;
        if (currentUrl !== '/login' && currentUrl !== '/register') {
          sessionStorage.setItem('returnUrl', currentUrl);
        }

        router.navigate(['/login']);
      }

      // Si erreur 403 (interdit)
      if (error.status === 403) {
        console.error('Accès interdit:', error.message);
      }

      // Si erreur 500 (serveur)
      if (error.status === 500) {
        console.error('Erreur serveur:', error.message);
      }

      // Si erreur de connexion
      if (error.status === 0) {
        console.error('Impossible de se connecter au serveur');
      }

      return throwError(() => error);
    })
  );
};
