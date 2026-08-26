# Multi-stage: stage 1 χτίζει τα static assets (npm run build -> dist/),
# stage 2 τα σερβίρει. Χρησιμοποιούμε "vite preview" αντί για nginx --
# χρειάζεται μηδέν extra config, ΚΑΙ κάνει σωστά SPA fallback (κάθε
# deep-link route όπως /actors ή /events/1 σερβίρει το index.html, όχι
# 404 -- ίδιο πρόβλημα με το SPA fallback που ήδη λύσαμε στο Vite dev
# server, βλ. routing skeleton). node version ίδιο με το τοπικό (node --version).
FROM node:24-slim AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
# Cache-busting: μερικά build platforms (π.χ. Railway) καίνε cached layers
# ακόμα και όταν το source άλλαξε -- το COPY . . παρακάτω δείχνει "cached"
# στα logs αντί να ξαναδιαβάσει τα αρχεία. Το ARG είναι ένα no-op instruction
# του οποίου η default τιμή αλλάζει χειροκίνητα (νέα τιμή = νέο layer hash),
# σπάει το cache από αυτό το σημείο και μετά. Άλλαξε την τιμή σε νέο
# timestamp/τυχαίο string κάθε φορά που χρειάζεσαι πραγματικό, guaranteed
# fresh rebuild.
ARG CACHEBUST=2026-08-26T200802Z
COPY . .
RUN npm run build

FROM node:24-slim
WORKDIR /app
# Copy node_modules ολόκληρο (όχι npm ci --omit=dev) -- το "vite preview"
# χρειάζεται το ίδιο το vite, που είναι devDependency, όχι production.
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
COPY --from=build /app/package.json ./
COPY --from=build /app/vite.config.ts ./

EXPOSE 3000

CMD ["npx", "vite", "preview", "--host", "0.0.0.0", "--port", "3000"]
