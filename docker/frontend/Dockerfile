# Stage 1: Build the React app
FROM node:20-alpine AS builder

WORKDIR /app

COPY ../../frontend-react/package.json ../../frontend-react/package-lock.json ./
RUN npm install --frozen-lockfile || npm install
COPY ../../frontend-react ./
RUN npm run build

# Stage 2: Serve the built app with nginx for proxy support
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY docker/nginx/conf.d/frontend.conf /etc/nginx/conf.d/default.conf
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1
CMD ["nginx", "-g", "daemon off;"] 