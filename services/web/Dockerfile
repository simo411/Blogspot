# ---- build stage: produce the static React bundle ----
FROM node:22-alpine AS build
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund

COPY public ./public
COPY src ./src
RUN npm run build

# ---- runtime stage: nginx serves the bundle and proxies /api ----
# nginx-unprivileged runs as a non-root user and listens on 8080.
FROM nginxinc/nginx-unprivileged:stable-alpine

# Where /api/* is forwarded. Same name works in compose and Kubernetes
# because both expose the API as a service called "blog-api".
ENV API_UPSTREAM=blog-api:8000

COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/build /usr/share/nginx/html

EXPOSE 8080
HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
  CMD ["wget", "-q", "-O", "/dev/null", "http://127.0.0.1:8080/nginx-health"]
