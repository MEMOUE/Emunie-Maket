# ========================================
# ÉTAPE 1: BUILD
# ========================================
FROM node:20-alpine as build

WORKDIR /app

# Copier package.json et package-lock.json
COPY package*.json ./

# Installer les dépendances
RUN npm ci --only=production

# Copier le code source
COPY . .

# Build Angular en mode production
RUN npm run build -- --configuration production --output-path=dist

# ========================================
# ÉTAPE 2: NGINX
# ========================================
FROM nginx:alpine

# Copier la configuration Nginx personnalisée
COPY nginx-angular.conf /etc/nginx/conf.d/default.conf

# Copier les fichiers buildés depuis l'étape précédente
COPY --from=build /app/dist /usr/share/nginx/html

# Exposer le port 80
EXPOSE 80

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

# Démarrer Nginx
CMD ["nginx", "-g", "daemon off;"]
