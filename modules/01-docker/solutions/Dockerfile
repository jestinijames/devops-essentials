# ---- Stage 1: Build ----
FROM node:22-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

# Build the Next.js app in standalone mode
# (requires output: "standalone" in next.config.ts)
RUN npm run build

# ---- Stage 2: Run ----
FROM node:22-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

# Copy only the production output from the builder stage
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD wget -qO- http://localhost:3000/api/health || exit 1

CMD ["node", "server.js"]
