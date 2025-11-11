FROM node:18 as build

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build --configuration production

# Étape de déploiement avec Nginx
FROM nginx:alpine
COPY --from=build /app/dist/mon-projet-angular /usr/share/nginx/html
