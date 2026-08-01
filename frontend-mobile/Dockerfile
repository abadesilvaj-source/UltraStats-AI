FROM node:22-alpine AS build
WORKDIR /web
ENV CI=true
COPY frontend/package.json frontend/pnpm-lock.yaml frontend/pnpm-workspace.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile --shamefully-hoist
COPY frontend ./frontend
COPY frontend-mobile ./frontend-mobile
WORKDIR /web/frontend-mobile
RUN node scripts/prepare-shared.mjs \
    && ../node_modules/.bin/tsc --noEmit \
    && ../node_modules/.bin/vite build

FROM nginx:1.29-alpine
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /web/frontend-mobile/dist /usr/share/nginx/html
EXPOSE 80
HEALTHCHECK --interval=15s --timeout=5s --retries=5 \
  CMD wget -q -O - http://127.0.0.1/healthz || exit 1
