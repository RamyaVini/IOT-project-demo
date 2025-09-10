FROM node:22-slim AS base
WORKDIR /app
ENV NODE_ENV=production

# Install dependencies only (cached layer)
FROM base AS deps
WORKDIR /app
ENV NODE_ENV=development
COPY package.json package-lock.json ./
RUN npm ci

# Build the application
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# Production runner image
FROM node:22-slim AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Create non-root user
RUN groupadd -g 1001 nodejs \
    && useradd -r -u 1001 -g nodejs nodejs

# Copy necessary files to run the app
COPY --from=deps /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/next.config.mjs ./next.config.mjs

# Remove devDependencies to slim down the runtime image
RUN npm prune --omit=dev

EXPOSE 3000
# Ensure Next.js binds to all interfaces
ENV HOSTNAME=0.0.0.0

USER nodejs
CMD ["npm", "run", "start"]


