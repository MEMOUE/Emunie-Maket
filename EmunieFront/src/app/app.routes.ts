import { Routes } from '@angular/router';
import { Accueil } from './accueil/accueil';

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
    path: '**',
    redirectTo: 'accueil'
  }
];
