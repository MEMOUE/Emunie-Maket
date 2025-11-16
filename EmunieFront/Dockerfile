FROM node:20-slim as build

WORKDIR /app

RUN npm cache verify && npm cache clean --force

COPY package*.json ./
RUN npm install --legacy-peer-deps --no-audit --no-fund --prefer-online

COPY . .

RUN npm install -g @angular/cli
RUN npm install @angular/animations @angular/core @angular/common --save

# Build Angular en production sans bloquer pour le budget
RUN ng build EmunieFront --configuration production

FROM nginx:alpine
COPY --from=build /app/dist/EmunieFront /usr/share/nginx/html
