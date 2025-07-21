# Stage 1: Build the React app
FROM node:20-alpine AS builder

WORKDIR /app

COPY ../../frontend-react/package.json ../../frontend-react/package-lock.json ./
RUN npm install --frozen-lockfile || npm install
COPY ../../frontend-react ./
RUN npm run build

# Stage 2: Serve the built app with a static server
FROM node:20-alpine
WORKDIR /app
RUN npm install -g serve
COPY --from=builder /app/dist ./dist
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD wget --spider -q http://localhost:8080 || exit 1
CMD ["serve", "-s", "dist", "-l", "8080"] 