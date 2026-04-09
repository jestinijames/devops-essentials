# Module 05 — Microservices

> **Goal:** Break the monolithic Next.js app into independent services that communicate over HTTP — and understand when to split and when not to.

---

## Why Microservices? (The real problem it solves)

Right now, your app is a **monolith** — one Next.js app handles everything: the UI, the tasks API, the health check, everything. That's fine for a small project.

The problems come at scale:

- 10 engineers working in the same codebase → constant merge conflicts
- The API has a memory leak → the frontend goes down too
- You want to rewrite the API in Go for performance → you have to rewrite the whole app
- Tasks API gets 1000 req/s, frontend gets 10 req/s → you have to scale both together

**Microservices** is an architectural pattern where you split the app into **small, independent services** that:

- Each do **one thing well**
- **Deploy independently** (update the API without touching the frontend)
- **Scale independently** (run 10 API pods, 2 frontend pods)
- **Fail independently** (API is down → frontend shows a graceful error, not a blank page)
- **Communicate over HTTP** (or gRPC, or message queues)

Think of it like this:

> As a frontend dev, you already understand component composition — small, focused components that do one thing and take props. Microservices are the **backend equivalent at the infrastructure level**.

---

## The tradeoffs (be honest with yourself)

Microservices add **real complexity**:

- Network calls can fail (you have to handle errors)
- Services need to find each other (service discovery)
- Debugging spans multiple services (distributed tracing)
- More repos, more pipelines, more Docker images to manage

**Rule of thumb:** Start with a monolith. Split into services when a specific pain point demands it. Do not split just because it feels "more proper."

This module teaches you how to split — but also when not to.

---

## What we're building

We'll split the current app into:

| Service     | What it does                        | Port |
| ----------- | ----------------------------------- | ---- |
| `frontend`  | Next.js app (UI only, no API logic) | 3000 |
| `tasks-api` | Express.js REST API for tasks       | 4000 |

The frontend will call the `tasks-api` over HTTP.

---

## Key Concepts

### Service discovery

In a monolith, you call `fetch("/api/tasks")` — same process, no network hop. In microservices, `frontend` needs to know where `tasks-api` lives.

In Docker Compose, services discover each other by **service name**:

```
http://tasks-api:4000/tasks
```

In Kubernetes, a **Service** object provides a stable DNS name:

```
http://tasks-api-svc.default.svc.cluster.local/tasks
```

### API contracts

Once you split, the endpoint shape is a **public contract**. Changing it might break the frontend. This is why teams use:

- **OpenAPI/Swagger** — document the API shape
- **Versioning** — `/api/v1/tasks` so you can change v2 without breaking v1

### Health checks for each service

Every service needs its own `/health` endpoint. Kubernetes needs to know if _each_ service is healthy independently.

---

## Exercise 1 — Build the tasks-api service

Create `microservices/tasks-api/`:

```
Your tasks:
1. Initialize a new Node.js project (npm init)
2. Install express
3. Create index.js with:
   - GET /health → { status: "ok", service: "tasks-api" }
   - GET /tasks  → returns the tasks array
   - POST /tasks → accepts { title: string } and adds a task
4. Create a Dockerfile for this service (use the multi-stage pattern from Module 01)
5. Run it: node index.js — verify GET /tasks works at http://localhost:4000/tasks
```

**Solution:** `microservices/tasks-api/`

---

## Exercise 2 — Update the frontend to call the tasks-api

Update `app/app/api/tasks/route.ts` (the Next.js API route) to proxy requests to the `tasks-api` service:

```ts
// Instead of returning hardcoded data, fetch from the tasks-api:
const res = await fetch(`${process.env.TASKS_API_URL}/tasks`);
```

And update `app/app/page.tsx` so it uses the env variable for the API URL.

The `TASKS_API_URL` will be:

- Local dev: `http://localhost:4000`
- Docker Compose: `http://tasks-api:4000`
- Kubernetes: `http://tasks-api-svc`

---

## Exercise 3 — Wire them together with Docker Compose

Create `docker-compose.microservices.yml` in the project root:

```
Your tasks:
1. Service: tasks-api
   - Build from ./microservices/tasks-api
   - Port: 4000:4000
   - No external dependencies

2. Service: frontend
   - Build from ./app (Dockerfile.dev)
   - Port: 3000:3000
   - depends_on: tasks-api
   - Environment: TASKS_API_URL=http://tasks-api:4000

Both services should share a custom network so they can reach each other by name.
```

Run it:

```bash
docker compose -f docker-compose.microservices.yml up
```

Visit `http://localhost:3000` — the frontend should be fetching tasks from the separate `tasks-api` service.

**Solution:** `modules/05-microservices/solutions/docker-compose.microservices.yml`

---

## Exercise 4 — Deploy both services to Kubernetes

Create Kubernetes manifests for both services in `k8s/`:

```
For tasks-api:
- deployment.yaml: 2 replicas, image, port 4000, liveness probe at /health
- service.yaml: ClusterIP, port 80 → targetPort 4000, name: tasks-api-svc

For frontend:
- Update k8s/deployment.yaml to add:
  env:
    - name: TASKS_API_URL
      value: http://tasks-api-svc   ← uses the K8s Service name
```

Apply everything:

```bash
kubectl apply -f k8s/
kubectl get pods
kubectl get services
kubectl port-forward service/devops-essentials-svc 3000:80
```

**Solution:** `modules/05-microservices/solutions/k8s/`

---

## Exercise 5 — Handle the failure case (resilience)

Kill the `tasks-api` deployment:

```bash
kubectl scale deployment tasks-api --replicas=0
```

What happens to the frontend? If you haven't handled it, you'll get an unhandled error.

Update `app/app/page.tsx` so that when the tasks API is unreachable, the page still renders with a friendly "Tasks unavailable" message instead of crashing.

This is the **fallback pattern** — one of the most important resilience patterns in distributed systems.

---

## Patterns to know

**1. Strangler Fig** — Migrate from monolith to microservices without a big rewrite:

- Route specific endpoints to a new service
- Keep the old monolith running for everything else
- Over time, strangle the monolith route by route

**2. API Gateway** — A single entry point that routes to the right service:

```
browser → API Gateway (/api/tasks → tasks-api, /api/users → users-api)
```

**3. Sidecar** — A helper container running alongside your main container in the same Pod:

- Log collector
- TLS terminator
- Service mesh proxy (Istio, Linkerd)

**4. Event-driven** — Services communicate via a message queue (Kafka, RabbitMQ) instead of direct HTTP calls — looser coupling, better resilience.

---

## What to look up

- [12-Factor App](https://12factor.net/) — principles for building microservices-friendly apps
- [Martin Fowler on Microservices](https://martinfowler.com/articles/microservices.html)
- [Docker Compose networking](https://docs.docker.com/compose/networking/)
- [Kubernetes service DNS](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/)

---

## Checkpoint

Before moving to Module 06, verify:

- [ ] The tasks-api runs independently and returns tasks at `localhost:4000/tasks`
- [ ] The frontend fetches from tasks-api (not hardcoded data) when running via Docker Compose
- [ ] Both services are deployed to minikube as separate Deployments/Services
- [ ] Killing tasks-api doesn't crash the frontend — it shows a graceful fallback
- [ ] You can explain the tradeoff between a monolith and microservices

---

## What's next?

In **Module 06**, you'll take everything you've built and deploy it to a real cloud provider — GCP, AWS, or Azure — using the Terraform configs from Module 03 and the Kubernetes manifests from Module 04.

→ [Module 06 — Cloud](../06-cloud/README.md)
