# Module 02 — Docker

> **"It works on my machine."** Docker kills that sentence forever.

Docker packages your application and all its dependencies into a single portable unit called a **container**. The container runs identically on your laptop, your colleague's machine, your CI server, and in production. That's the whole point.

---

## Learning Objectives

By the end of this module you will:
- [ ] Understand the difference between containers and virtual machines
- [ ] Write a Dockerfile for the Next.js app
- [ ] Build, run, stop, and inspect Docker containers
- [ ] Use multi-stage builds to create optimized production images
- [ ] Run multi-container setups with Docker Compose
- [ ] Push an image to Docker Hub (your first "registry")
- [ ] Understand Docker networking and volumes

---

## 1. Containers vs Virtual Machines

This is the most important conceptual distinction in containerization.

```
VIRTUAL MACHINE                    CONTAINER
────────────────                   ─────────────────────────
┌──────────────┐                   ┌────────┐ ┌────────┐ ┌────────┐
│  Your App    │                   │ App A  │ │ App B  │ │ App C  │
├──────────────┤                   ├────────┴─┴────────┴─┴────────┤
│  Guest OS    │  ← heavy          │     Container Runtime         │
│  (full OS!)  │                   │     (Docker Engine)           │
├──────────────┤                   ├──────────────────────────────┤
│  Hypervisor  │                   │     HOST OPERATING SYSTEM     │
├──────────────┤                   ├──────────────────────────────┤
│  Host OS     │                   │     HARDWARE                  │
└──────────────┘                   └──────────────────────────────┘

Boots in: minutes                  Boots in: milliseconds
Size: GBs                          Size: MBs
Isolation: complete                Isolation: process-level
```

**Containers share the host OS kernel.** They're just isolated processes. That's why they start in milliseconds and are so lightweight.

---

## 2. Core Docker Concepts

| Concept | What it is | Analogy |
|---------|-----------|---------|
| **Image** | A read-only snapshot of your app + all dependencies | A blueprint / class |
| **Container** | A running instance of an image | An instance / object |
| **Dockerfile** | Instructions to build an image | A recipe |
| **Registry** | A place to store and share images | npm registry, but for images |
| **Docker Hub** | The default public registry | GitHub, but for images |
| **Volume** | Persistent storage that survives container restarts | External hard drive for containers |
| **Network** | Virtual network between containers | LAN between containers |

---

## 3. Essential Docker Commands

```bash
# ─── Images ───────────────────────────────────────

# Build an image from a Dockerfile in current directory
docker build -t my-app:latest .

# Build with a specific Dockerfile
docker build -f Dockerfile.prod -t my-app:v1.0 .

# List local images
docker images

# Pull an image from Docker Hub
docker pull node:20-alpine

# Remove an image
docker rmi my-app:latest

# ─── Containers ────────────────────────────────────

# Run a container (detached mode, with port mapping)
docker run -d -p 3000:3000 --name my-app my-app:latest

# Run interactively (good for debugging)
docker run -it --rm node:20-alpine sh

# List running containers
docker ps

# List ALL containers (including stopped)
docker ps -a

# View logs
docker logs my-app
docker logs -f my-app   # follow (like tail -f)

# Execute a command inside a running container
docker exec -it my-app sh

# Stop / start / remove a container
docker stop my-app
docker start my-app
docker rm my-app

# ─── Cleanup ────────────────────────────────────────

# Remove all stopped containers
docker container prune

# Remove unused images
docker image prune

# Nuclear option (removes everything)
docker system prune -a
```

---

## 4. Writing a Dockerfile for the Next.js App

A Dockerfile is a set of instructions that Docker executes top-to-bottom to build an image.

### Simple Dockerfile (development)

Create `app/Dockerfile.dev`:

```dockerfile
# Start from the official Node.js image (Alpine Linux = tiny)
FROM node:20-alpine

# Set the working directory inside the container
WORKDIR /app

# Enable pnpm via corepack (built into Node.js 16.13+)
RUN corepack enable && corepack prepare pnpm@latest --activate

# Copy dependency files first (layer caching optimization)
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install

# Copy the rest of the application
COPY . .

# Expose the port the app runs on
EXPOSE 3000

# Command to start the app
CMD ["pnpm", "dev"]
```

### Build and run it:
```bash
cd app
docker build -f Dockerfile.dev -t my-app:dev .
docker run -p 3000:3000 my-app:dev
```
Open http://localhost:3000 — your app is running inside Docker.

---

## 5. Multi-Stage Build (Production Dockerfile)

The development image is bloated — it has dev dependencies, source files, etc. For production we use **multi-stage builds**:

Create `app/Dockerfile`:
```dockerfile
# ──────────────────────────── Stage 1: Dependencies ────
FROM node:20-alpine AS deps
WORKDIR /app
RUN corepack enable && corepack prepare pnpm@latest --activate
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile --prod

# ──────────────────────────── Stage 2: Builder ──────────
FROM node:20-alpine AS builder
WORKDIR /app
RUN corepack enable && corepack prepare pnpm@latest --activate
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .
RUN pnpm build

# ──────────────────────────── Stage 3: Runner ───────────
# This is the FINAL image — only what's needed to run
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production

# Create a non-root user (security best practice)
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy only what we need from the builder stage
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
```

To enable the `standalone` output mode, update `app/next.config.ts`:

```typescript
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
};

export default nextConfig;
```

Build and run the production image:
```bash
cd app
docker build -t my-app:prod .
docker run -p 3000:3000 my-app:prod
```

**Compare the sizes:**
```bash
docker images my-app
# dev image: ~1.2GB
# prod image: ~150MB
```

---

## 6. Docker Compose

Running one container is easy. Running an app with a database, cache, and reverse proxy? That's where Docker Compose comes in.

Create `docker-compose.yml` at the **root** of the repo:

```yaml
version: "3.9"

services:
  # Our Next.js application
  app:
    build:
      context: ./app
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://devops:password@db:5432/devops_db
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

  # PostgreSQL database (you'll use this in microservices module)
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: devops
      POSTGRES_PASSWORD: password
      POSTGRES_DB: devops_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U devops -d devops_db"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # Redis cache
  redis:
    image: redis:7-alpine
    restart: unless-stopped

volumes:
  postgres_data:   # Named volume — data persists across restarts
```

```bash
# Start all services
docker compose up -d

# View logs for all services
docker compose logs -f

# View logs for one service
docker compose logs -f app

# Stop all services
docker compose down

# Stop and remove volumes (wipes the database)
docker compose down -v
```

---

## 7. Docker Networking

When containers are in the same Compose network, they talk to each other using **service names** as hostnames:

```
app → db            uses hostname "db"       (not localhost!)
app → redis         uses hostname "redis"    (not localhost!)
```

That's why `DATABASE_URL` in the Compose file uses `@db:5432` instead of `@localhost:5432`.

Docker creates three network types:
| Network | Description |
|---------|-------------|
| `bridge` | Default. Containers on the same bridge can talk to each other. |
| `host` | Container shares the host's network (no isolation). |
| `none` | No networking. Complete isolation. |

---

## 8. Docker Volumes

Containers are **ephemeral** — when they stop, all data inside is lost. Volumes solve this.

```bash
# Create a named volume
docker volume create my_data

# Mount a host directory into a container (bind mount — for development)
docker run -v $(pwd)/app:/app my-app:dev

# Mount a named volume (for persistence — databases, etc.)
docker run -v postgres_data:/var/lib/postgresql/data postgres:16-alpine

# List volumes
docker volume ls

# Inspect a volume (see where data is stored)
docker volume inspect postgres_data

# In docker-compose.yml, volumes are defined at the bottom:
# volumes:
#   postgres_data:
```

---

## 9. Push to Docker Hub

```bash
# Create a free account at hub.docker.com
# Then login
docker login

# Tag your image with your Docker Hub username
docker tag my-app:prod YOUR_DOCKERHUB_USERNAME/devops-app:v0.1.0
docker tag my-app:prod YOUR_DOCKERHUB_USERNAME/devops-app:latest

# Push to the registry
docker push YOUR_DOCKERHUB_USERNAME/devops-app:v0.1.0
docker push YOUR_DOCKERHUB_USERNAME/devops-app:latest

# Now anyone (and any CI pipeline) can pull it
docker pull YOUR_DOCKERHUB_USERNAME/devops-app:latest
```

---

## 10. Exercises

### Exercise 1: Build and Run
```bash
# Build the dev image
cd app
docker build -f Dockerfile.dev -t my-app:dev .

# Run it
docker run -d -p 3000:3000 --name my-app-dev my-app:dev

# Open http://localhost:3000
# View the logs
docker logs my-app-dev

# Get a shell inside the container
docker exec -it my-app-dev sh
ls -la

# Clean up
docker stop my-app-dev && docker rm my-app-dev
```

### Exercise 2: Multi-Stage Build
1. Add `output: "standalone"` to `next.config.ts`
2. Create the production `Dockerfile` from Section 5
3. Build and run the production image
4. Compare image sizes with `docker images`

### Exercise 3: Docker Compose
1. Create the `docker-compose.yml` from Section 6
2. Run `docker compose up -d`
3. Verify all services are running: `docker compose ps`
4. Check that the app can be reached at http://localhost:3000
5. Run `docker compose down`

### Exercise 4: Inspect the Network
```bash
docker compose up -d

# See the network Docker Compose created
docker network ls
docker network inspect devops-essentials_default

# See connected containers
```

---

## Checklist

- [ ] I can explain the difference between an image and a container
- [ ] I can write a Dockerfile from scratch
- [ ] I understand multi-stage builds and why they matter
- [ ] I have a working production Dockerfile for the Next.js app
- [ ] I can use Docker Compose to run multiple services
- [ ] I understand how containers communicate over Docker networks
- [ ] I have pushed an image to Docker Hub
- [ ] I know how to view logs and exec into containers for debugging

---

## Further Reading

- [Docker Official Get Started](https://docs.docker.com/get-started/)
- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [Play with Docker (free online playground)](https://labs.play-with-docker.com/)

---

**Next:** [Module 03 — GitHub Actions](../03-github-actions/README.md)
