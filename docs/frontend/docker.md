# Docker & Deployment

The frontend ships via Docker Compose alongside the FastAPI backend.

---

## 1. Local Development

We leverage Vite’s HMR in a standalone container that mounts source code:

```yaml title="docker-compose.override.yml"
services:
  frontend:
    build:
      context: frontend
      target: dev
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "5173:5173"
    environment:
      - VITE_API_URL=http://localhost:8000
    depends_on:
      - backend
```

The `dev` stage in `frontend/Dockerfile` uses `pnpm dev`.

## 2. Production Build

```yaml title="docker-compose.yml"
services:
  frontend:
    build:
      context: frontend
      target: prod
    image: convosphere/frontend:latest
    environment:
      - VITE_API_URL=/api
    ports:
      - "80:80"
```

### Dockerfile Multi-stage

```Dockerfile
# Stage 1 – builder
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile
COPY . .
RUN pnpm build

# Stage 2 – nginx
FROM nginx:1.25-alpine AS prod
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

## 3. CI/CD

1. **Build** – GitHub Actions builds image, pushes to GHCR.
2. **Deploy** – Production server pulls latest tag; Compose recreates frontend service.

## 4. Environment Variables

| Name | Default | Description |
|------|---------|-------------|
| `VITE_API_URL` | `/api` | Base URL for Axios/RTK Query |
| `VITE_AUTH_AUDIENCE` | – | (optional) OAuth audience |

## 5. Nginx Config Highlights

```nginx
location /api/ {
    proxy_pass http://backend:8000/;
}

location / {
    try_files $uri /index.html;
}
```

---
This setup ensures parity between local dev and production while keeping services loosely coupled.
