# Multi-stage: stage 1 χτίζει τα static assets (npm run build -> dist/),
# stage 2 τα σερβίρει με nginx. Πριν χρησιμοποιούσαμε "vite preview" (βλ.
# git history) -- άλλαξε γιατί η επίσημη τεκμηρίωση του Vite λέει ρητά ότι
# το preview server δεν προορίζεται για production ("not designed for
# it"), και το επιβεβαιώσαμε στην πράξη με ένα Blocked-request/
# allowedHosts πρόβλημα στο Railway. Το nginx δεν
# έχει τέτοιο host-allowlist μηχανισμό -- σερβίρει static files σε όποιο
# domain φτάσει, καμία allowedHosts ρύθμιση χρειάζεται πια, άρα και το
# CACHEBUST hack από πριν δεν χρειάζεται -- δεν υπάρχει πια config που να
# "κολλάει" σε παλιό cached layer με τρόπο που να μας μπλοκάρει.
# node version ίδιο με το τοπικό (node --version).
FROM node:24-slim AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
# SPA fallback (React Router) + gzip -- βλ. σχόλια μέσα στο nginx.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
