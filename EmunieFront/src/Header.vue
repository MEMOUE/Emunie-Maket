<template>
  <header class="header-clean">
    <!-- Header principal épuré -->
    <div class="main-header">
      <div class="container">
        <div class="header-content">
          <!-- Logo simple -->
          <div class="logo-section">
            <div class="logo-wrapper">
              <div class="logo-icon">
                <i class="pi pi-globe"></i>
              </div>
              <div class="logo-text">
                <h1 class="brand-name">Emunie</h1>
                <span class="brand-sub">Côte d'Ivoire</span>
              </div>
            </div>
          </div>

          <!-- Navigation épurée -->
          <nav class="main-nav">
            <Button label="Services" text class="nav-btn" />
            <Button label="Emplois" text class="nav-btn" />
            <Button label="Immobilier" text class="nav-btn" />
            <Button label="Véhicules" text class="nav-btn" />
          </nav>

          <!-- Recherche centrée -->
          <div class="search-section">
            <div class="search-wrapper">
              <i class="pi pi-search search-icon"></i>
              <InputText 
                v-model="search" 
                placeholder="Rechercher à Abidjan..." 
                class="search-input"
              />
              <Button 
                label="Rechercher" 
                class="search-btn"
                @click="onSearch"
              />
            </div>
          </div>

          <!-- Actions simplifiées -->
          <div class="user-actions">
            <Button 
              label="Publier" 
              icon="pi pi-plus"
              class="publish-btn"
            />
            <Button 
              label="Connexion" 
              text 
              class="login-btn"
            />
            <Button 
              label="S'inscrire" 
              class="signup-btn"
            />
          </div>

          <!-- Menu burger -->
          <Button
            icon="pi pi-bars"
            class="mobile-menu-btn"
            @click="toggleMenu"
            text
          />
        </div>
      </div>
    </div>

    <!-- Menu mobile simplifié -->
    <div class="mobile-menu" :class="{ 'mobile-menu-open': menuVisible }">
      <div class="mobile-content">
        <div class="mobile-header">
          <span class="mobile-logo">🇨🇮 Emunie CI</span>
          <Button icon="pi pi-times" text @click="menuVisible = false" />
        </div>
        
        <div class="mobile-search">
          <InputText v-model="search" placeholder="Rechercher..." />
          <Button icon="pi pi-search" @click="onSearch" />
        </div>
        
        <nav class="mobile-nav">
          <a href="#" class="mobile-nav-item">Services</a>
          <a href="#" class="mobile-nav-item">Emplois</a>
          <a href="#" class="mobile-nav-item">Immobilier</a>
          <a href="#" class="mobile-nav-item">Véhicules</a>
        </nav>

        <div class="mobile-actions">
          <Button label="Publier" icon="pi pi-plus" class="publish-mobile" />
          <Button label="Connexion" text />
          <Button label="S'inscrire" class="signup-mobile" />
        </div>
      </div>
    </div>

    <!-- Overlay -->
    <div class="mobile-overlay" v-show="menuVisible" @click="menuVisible = false"></div>
  </header>
</template>

<script setup>
import { ref } from 'vue'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'

const search = ref('')
const menuVisible = ref(false)

function onSearch() {
  console.log(`Recherche : ${search.value}`)
}

function toggleMenu() {
  menuVisible.value = !menuVisible.value
}
</script>

<style scoped>
/* Variables épurées */
:root {
  --orange-ci: #FF7F00;
  --vert-ci: #009639;
  --blanc: #FFFFFF;
  --gris-clair: #F8F9FA;
  --gris-moyen: #6C757D;
  --gris-fonce: #343A40;
  --shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  --radius: 8px;
  --transition: all 0.3s ease;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

/* HEADER ÉPURÉ */
.header-clean {
  background: var(--orange-ci);
  box-shadow: var(--shadow);
  position: sticky;
  top: 0;
  z-index: 100;
}

.main-header {
  padding: 1rem 0;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 2rem;
}

/* LOGO SIMPLIFIÉ */
.logo-wrapper {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  transition: var(--transition);
}

.logo-wrapper:hover {
  opacity: 0.8;
}

.logo-icon {
  width: 2.5rem;
  height: 2.5rem;
  background: linear-gradient(135deg, var(--orange-ci), var(--vert-ci));
  border-radius: var(--radius);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--blanc);
  font-size: 1.2rem;
}

.brand-name {
  font-size: 1.5rem;
  font-weight: 800;
  margin: 0;
  color: var(--gris-fonce);
}

.brand-sub {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--orange-ci);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* NAVIGATION ÉPURÉE */
.main-nav {
  display: flex;
  gap: 0.5rem;
}

.nav-btn {
  color: var(--gris-moyen) !important;
  font-weight: 600 !important;
  padding: 0.75rem 1rem !important;
  border-radius: var(--radius) !important;
  transition: var(--transition) !important;
}

.nav-btn:hover {
  color: var(--orange-ci) !important;
  background: rgba(202, 113, 24, 0.1) !important;
}

/* RECHERCHE ÉPURÉE */
.search-section {
  flex: 1;
  max-width: 500px;
}

.search-wrapper {
  display: flex;
  align-items: center;
  background: var(--gris-clair);
  border-radius: 25px;
  padding: 0.25rem;
  gap: 0.5rem;
}

.search-icon {
  color: var(--gris-moyen);
  margin-left: 1rem;
}

.search-input {
  flex: 1;
  border: none !important;
  background: transparent !important;
  padding: 0.75rem 0.5rem !important;
  font-size: 0.9rem !important;
  color: var(--gris-fonce) !important;
}

.search-input:focus {
  box-shadow: none !important;
  outline: none !important;
}

.search-btn {
  background: var(--orange-ci) !important;
  border: none !important;
  color: var(--blanc) !important;
  border-radius: 20px !important;
  padding: 0.75rem 1.5rem !important;
  font-weight: 600 !important;
  font-size: 0.9rem !important;
  transition: var(--transition) !important;
}

.search-btn:hover {
  background: var(--vert-ci) !important;
  transform: translateY(-1px);
}

/* ACTIONS ÉPURÉES */
.user-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.publish-btn {
  background: var(--vert-ci) !important;
  border: none !important;
  color: var(--blanc) !important;
  border-radius: var(--radius) !important;
  font-weight: 600 !important;
  padding: 0.75rem 1.25rem !important;
  transition: var(--transition) !important;
}

.publish-btn:hover {
  background: var(--orange-ci) !important;
  transform: translateY(-1px);
}

.login-btn {
  color: var(--gris-moyen) !important;
  font-weight: 600 !important;
  padding: 0.75rem 1rem !important;
}

.login-btn:hover {
  color: var(--orange-ci) !important;
}

.signup-btn {
  background: transparent !important;
  border: 2px solid var(--orange-ci) !important;
  color: var(--orange-ci) !important;
  border-radius: var(--radius) !important;
  font-weight: 600 !important;
  padding: 0.5rem 1.25rem !important;
  transition: var(--transition) !important;
}

.signup-btn:hover {
  background: var(--orange-ci) !important;
  color: var(--blanc) !important;
}

/* MOBILE ÉPURÉ */
.mobile-menu-btn {
  display: none;
  color: var(--gris-fonce) !important;
  font-size: 1.5rem !important;
}

.mobile-menu {
  position: fixed;
  top: 0;
  right: -100%;
  width: 280px;
  height: 100vh;
  background: var(--blanc);
  z-index: 200;
  transition: var(--transition);
  box-shadow: -5px 0 15px rgba(0, 0, 0, 0.1);
}

.mobile-menu-open {
  right: 0;
}

.mobile-content {
  padding: 1.5rem;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.mobile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--gris-clair);
}

.mobile-logo {
  font-weight: 800;
  font-size: 1.1rem;
  color: var(--gris-fonce);
}

.mobile-search {
  display: flex;
  gap: 0.5rem;
}

.mobile-search InputText {
  flex: 1;
  border: 1px solid var(--gris-clair) !important;
  border-radius: var(--radius) !important;
  padding: 0.75rem !important;
}

.mobile-search Button {
  background: var(--orange-ci) !important;
  border: none !important;
  color: var(--blanc) !important;
  border-radius: var(--radius) !important;
  padding: 0.75rem !important;
}

.mobile-nav {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.mobile-nav-item {
  padding: 1rem;
  text-decoration: none;
  color: var(--gris-fonce);
  font-weight: 600;
  border-radius: var(--radius);
  transition: var(--transition);
}

.mobile-nav-item:hover {
  background: rgba(255, 127, 0, 0.1);
  color: var(--orange-ci);
}

.mobile-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: auto;
}

.publish-mobile {
  background: var(--vert-ci) !important;
  border: none !important;
  color: var(--blanc) !important;
  border-radius: var(--radius) !important;
  font-weight: 600 !important;
  padding: 0.875rem !important;
}

.signup-mobile {
  background: var(--orange-ci) !important;
  border: none !important;
  color: var(--blanc) !important;
  border-radius: var(--radius) !important;
  font-weight: 600 !important;
  padding: 0.875rem !important;
}

.mobile-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.3);
  z-index: 150;
}

/* RESPONSIVE */
@media (max-width: 768px) {
  .main-nav,
  .search-section,
  .user-actions {
    display: none;
  }
  
  .mobile-menu-btn {
    display: flex !important;
  }
  
  .header-content {
    justify-content: space-between;
  }
}

@media (max-width: 480px) {
  .brand-name {
    font-size: 1.3rem;
  }
  
  .brand-sub {
    font-size: 0.7rem;
  }
  
  .logo-icon {
    width: 2.2rem;
    height: 2.2rem;
    font-size: 1.1rem;
  }
}
</style>