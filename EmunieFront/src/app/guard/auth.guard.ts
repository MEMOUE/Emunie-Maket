import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { AuthService } from '../service/auth';

export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isAuthenticated()) {
    return true;
  }

  // Sauvegarder l'URL demandée pour la redirection après connexion
  sessionStorage.setItem('returnUrl', state.url);
  router.navigate(['/login']);
  return false;
};
