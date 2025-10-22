import { Routes } from '@angular/router';
import { Accueil } from './accueil/accueil';
import { Login } from './auth/login/login';
import { Register } from './auth/register/register';

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

  {
    path: 'acheter',
    loadComponent: () => import('./accueil/accueil').then(m => m.Accueil) // Temporaire
  },
  {
    path: 'vendre',
    loadComponent: () => import('./accueil/accueil').then(m => m.Accueil) // Temporaire
  },
  {
    path: 'categories',
    loadComponent: () => import('./accueil/accueil').then(m => m.Accueil) // Temporaire
  },
  {
    path: 'contact',
    loadComponent: () => import('./accueil/accueil').then(m => m.Accueil) // Temporaire
  },
  {
    path: 'dashboard',
    loadComponent: () => import('./dashboard/dashboard').then(m => m.Dashboard) // Temporaire
  },
  {
    path: 'dashboard/buy-pub',
    loadComponent: () => import('./publicite/new-publicite/new-publicite').then(m => m.NewPublicite) // Temporaire
  },
  {
    path: 'dashboard/my-ads',
    loadComponent: () => import('./annonces/list-annonce/list-annonce').then(m => m.ListAnnonce) // Temporaire
  },
  {
    path: 'dashboard/new-ad',
    loadComponent: () => import('./annonces/new-anonce/new-anonce').then(m => m.NewAnonceComponent) // Temporaire
  },
  {
    path: 'dashboard/overview',
    loadComponent: () => import('./dashboard/dashboard').then(m => m.Dashboard) // Temporaire
  },
  {
    path: '**',
    redirectTo: 'accueil'
  }
];
