# ---- Stage 1: Install ----
FROM node:22-alpine AS builder
WORKDIR /app
COPY package.json ./
RUN npm install

# ---- Stage 2: Run ----
FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/node_modules ./node_modules
COPY . .
EXPOSE 4000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD wget -qO- http://localhost:4000/health || exit 1
CMD ["node", "index.js"]
