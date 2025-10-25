import { Routes } from '@angular/router';
import { Accueil } from './accueil/accueil';
import { Login } from './auth/login/login';
import { Register } from './auth/register/register';
import { authGuard } from './guard/auth.guard';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'accueil',
    pathMatch: 'full'
  },
  {
    path: 'accueil',
    component: Accueil
  },
  {
    path: 'login',
    component: Login
  },
  {
    path: 'register',
    component: Register
  },

  // Routes pour les annonces
  {
    path: 'annonces',
    loadComponent: () => import('./annonces/list-annonce/list-annonce').then(m => m.ListAnnonce)
  },
  {
    path: 'annonces/:id',
    loadComponent: () => import('./annonces/detail-annonce/detail-annonce').then(m => m.DetailAnnonce)
  },

  // Routes temporaires
  {
    path: 'acheter',
    redirectTo: 'annonces',
    pathMatch: 'full'
  },
  {
    path: 'vendre',
    redirectTo: 'dashboard/new-ad',
    pathMatch: 'full'
  },
  {
    path: 'categories',
    redirectTo: 'annonces',
    pathMatch: 'full'
  },
  {
    path: 'contact',
    loadComponent: () => import('./accueil/accueil').then(m => m.Accueil) // Temporaire
  },

  // Dashboard (protégé par authGuard)
  {
    path: 'dashboard',
    canActivate: [authGuard],
    loadComponent: () => import('./dashboard/dashboard').then(m => m.Dashboard)
  },
  {
    path: 'dashboard/buy-pub',
    canActivate: [authGuard],
    loadComponent: () => import('./publicite/new-publicite/new-publicite').then(m => m.NewPublicite)
  },
  {
    path: 'dashboard/list-pub',
    canActivate: [authGuard],
    loadComponent: () => import('./publicite/list-publicite/list-publicite').then(m => m.ListPublicite)
  },
  {
    path: 'dashboard/my-ads',
    canActivate: [authGuard],
    loadComponent: () => import('./annonces/list-annonce/list-annonce').then(m => m.ListAnnonce)
  },
  {
    path: 'dashboard/new-ad',
    canActivate: [authGuard],
    loadComponent: () => import('./annonces/new-anonce/new-anonce').then(m => m.NewAnonceComponent)
  },
  {
    path: 'dashboard/edit-ad/:id',
    canActivate: [authGuard],
    loadComponent: () => import('./annonces/new-anonce/new-anonce').then(m => m.NewAnonceComponent)
  },
  {
    path: 'dashboard/overview',
    canActivate: [authGuard],
    loadComponent: () => import('./dashboard/dashboard').then(m => m.Dashboard)
  },
  {
    path: 'search',
    loadComponent: () => import('./research-coponent/research-coponent').then(m => m.ResearchCoponent)
  },

  // Route 404
  {
    path: '**',
    redirectTo: 'accueil'
  }
];
