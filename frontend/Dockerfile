# Build estático (sin dev-server ni watcher): mínimo footprint para dejar
# la app corriendo en segundo plano (~10MB vs ~175MB+CPU del dev server).
FROM node:20-slim AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 5173
