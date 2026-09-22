# Module 01 — Docker

> **Goal:** Package the Next.js app into a container so it runs the same way on every machine and in the cloud.

---

## Why Docker? (The real problem it solves)

You've heard "it works on my machine." That's the problem.

When you deploy an app to a server, that server might have:

- A different Node.js version
- Different global packages
- Different OS environment variables
- Different file paths

Docker solves this by **bundling your app + its entire environment** into a single portable unit called a **container**.

Think of it like this:

> As a frontend dev, you use `package.json` to declare exactly which dependencies your project needs. Docker does the same thing for the **entire operating system environment** your app runs in.

---

## Key Concepts

### Image vs Container

| Term          | What it is                                     | Analogy                                       |
| ------------- | ---------------------------------------------- | --------------------------------------------- |
| **Image**     | A blueprint/snapshot of your app + environment | Like a JavaScript `class` definition          |
| **Container** | A running instance of an image                 | Like an instance created with `new MyClass()` |

You can run 10 containers from 1 image, just like you can create 10 instances from 1 class.

### Dockerfile

A `Dockerfile` is a script that describes how to build an image. It's a series of instructions:

```dockerfile
FROM node:22-alpine       # Start from an existing base image (like extending a class)
WORKDIR /app              # Set the working directory inside the container
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile
COPY . .                  # Copy the rest of the source code
RUN pnpm run build        # Build the Next.js app
CMD ["pnpm", "start"]     # Command to run when the container starts
```

### Layer caching (this is important)

Docker builds images in **layers** — one per instruction. Layers are cached. If nothing changed in a layer, Docker reuses the cache for that layer and all previous ones.

This is why we copy `package.json` and `pnpm-lock.yaml` and install dependencies **before** `COPY . .`:

- If you only change a `.tsx` file, Docker reuses the cached dependency-install layer
- Much faster builds

### Multi-stage builds

For production, you don't need the full build toolchain in the final image — that would make it huge and include dev tools that are a security risk. Multi-stage builds let you:

1. **Stage 1 (builder):** Build the app with all the tools
2. **Stage 2 (runner):** Copy only the output into a lean final image

---

## Exercise 1 — Write a basic Dockerfile

Create a file at `app/Dockerfile.dev` (for development):

```
Your tasks:
1. Use node:22-alpine as the base image
2. Set the working directory to /app
3. Copy package.json and pnpm-lock.yaml, then run pnpm install --frozen-lockfile
4. Copy the rest of the source files
5. Expose port 3000
6. Run "pnpm run dev" as the start command
```

Try it **without looking at the solution** first. If you get stuck, look up:

- https://docs.docker.com/reference/dockerfile/

Build and test it:

```bash
cd app
docker build -f Dockerfile.dev -t devops-essentials:dev .
docker run -p 3000:3000 devops-essentials:dev
```

Visit `http://localhost:3000` — your app should be running inside a container.

**Solution:** `modules/01-docker/solutions/Dockerfile.dev`

---

## Exercise 2 — Write a production Dockerfile

Create `app/Dockerfile` using a **multi-stage build**:

```
Stage 1 (builder):
1. Use node:22-alpine
2. Set workdir, copy and install deps, copy source, run pnpm run build

Stage 2 (runner):
1. Use node:22-alpine again (fresh, clean layer)
2. Set NODE_ENV=production
3. Copy ONLY the build output from Stage 1:
   - .next/standalone
   - .next/static
   - public
4. Expose port 3000
5. Run "node server.js" (Next.js standalone output)
```

For the standalone output to work, you need to add this to `app/next.config.ts`:

```ts
output: "standalone";
```

Build and run:

```bash
docker build -t devops-essentials:prod .
docker run -p 3000:3000 devops-essentials:prod
```

Check the image sizes:

```bash
docker images devops-essentials
```

You should see `prod` is much smaller than `dev`.

**Solution:** `modules/01-docker/solutions/Dockerfile`

---

## Exercise 3 — Docker Compose

Running a single container with `docker run` gets tedious with many flags. **Docker Compose** lets you define and run multi-container setups with a single file.

Create `docker-compose.yml` in the project root:

```
Your tasks:
1. Define a service called "app"
2. Build it from ./app using the Dockerfile.dev
3. Map port 3000:3000
4. Mount the ./app directory as a volume so hot-reload works
5. Set NODE_ENV=development as an environment variable
```

Then run:

```bash
docker compose up
docker compose down   # to stop
```

**Solution:** `modules/01-docker/solutions/docker-compose.yml`

---

## Exercise 4 — Use the health check endpoint

Containers need a way to tell the runtime "I'm alive and ready." You built `/api/health` for exactly this.

Add a `HEALTHCHECK` instruction to your production `Dockerfile`:

```
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD wget -qO- http://localhost:3000/api/health || exit 1
```

Rebuild the image and run:

```bash
docker inspect <container-id> | grep -A 10 Health
```

You'll see the health status. This same endpoint will be used by Kubernetes in Module 04.

---

## Key Commands Reference

```bash
docker build -t <name>:<tag> .     # Build an image
docker run -p 3000:3000 <name>     # Run a container
docker ps                           # List running containers
docker ps -a                        # List all containers (including stopped)
docker logs <container-id>          # View container logs
docker exec -it <container-id> sh   # Open a shell inside a running container
docker images                       # List local images
docker rmi <image-id>               # Remove an image
docker stop <container-id>          # Stop a container
docker rm <container-id>            # Remove a stopped container

docker compose up                   # Start all services
docker compose up --build           # Rebuild images before starting
docker compose down                 # Stop and remove containers
docker compose logs -f              # Follow logs for all services
```

---

## What to look up

- [Dockerfile reference](https://docs.docker.com/reference/dockerfile/) — all available instructions
- [Docker multi-stage builds](https://docs.docker.com/build/building/multi-stage/)
- [Next.js standalone output](https://nextjs.org/docs/app/api-reference/next-config-js/output)
- [Docker Compose file reference](https://docs.docker.com/compose/compose-file/)

---

## Checkpoint

Before moving to Module 02, verify:

- [ ] `docker run -p 3000:3000 devops-essentials:prod` works and the app loads
- [ ] `docker images` shows that `prod` image is significantly smaller than `dev`
- [ ] `docker compose up` starts the app from the project root
- [ ] You understand the difference between an image and a container
- [ ] You can explain why we copy `package.json` before the rest of the source

---

## What's next?

In **Module 02**, you'll set up GitHub Actions to automatically build and push this Docker image every time you push code to `main`. No more manual `docker build` commands.

→ [Module 02 — GitHub Actions & CI/CD](../02-github-actions/README.md)
