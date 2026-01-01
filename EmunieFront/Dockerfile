FROM node:20-slim as build
WORKDIR /app

# Installation des outils nécessaires
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Configuration npm
RUN npm config set registry https://registry.npmjs.org/ && \
    npm config set fetch-timeout 120000 && \
    npm config set fetch-retries 5 && \
    npm config set fetch-retry-mintimeout 20000 && \
    npm config set fetch-retry-maxtimeout 120000

# Nettoyer complètement le cache npm
RUN rm -rf /root/.npm /root/.cache && \
    npm cache clean --force && \
    npm cache verify

# Copier package.json
COPY package*.json ./

# Supprimer package-lock.json s'il existe
RUN rm -f package-lock.json

# Installer Angular CLI v20 globalement
RUN npm install -g @angular/cli@^20.0.0

# Installer TOUTES les dépendances en une seule fois (y compris @angular/animations)
RUN npm install --legacy-peer-deps || \
    (rm -rf node_modules /root/.npm && npm cache clean --force && npm install --legacy-peer-deps)

# Copier le code source
COPY . .

# Build de production
RUN ng build --configuration production

# Stage Nginx
FROM nginx:alpine
COPY --from=build /app/dist/EmunieFront/browser /usr/share/nginx/html
COPY nginx-angular.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]