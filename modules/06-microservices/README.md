# Module 06 — Microservices

> **A microservice is a small, independently deployable service that does one thing well.** Monoliths are easier to start with. Microservices are easier to scale.

---

## Learning Objectives

By the end of this module you will:
- [ ] Understand the trade-offs between monoliths and microservices
- [ ] Know the core patterns: API Gateway, Service Discovery, Circuit Breaker
- [ ] Split the Next.js app into a frontend service and an API service
- [ ] Understand how services communicate (REST, gRPC, message queues)
- [ ] Deploy multiple services to Kubernetes

---

## 1. Monolith vs Microservices

```
MONOLITH                          MICROSERVICES
────────────────────              ──────────────────────────────────────
┌──────────────────┐              ┌─────────┐  ┌─────────┐  ┌────────┐
│   One big app    │              │ Frontend│  │  Users  │  │ Orders │
│  ┌────────────┐  │              │ Service │  │ Service │  │Service │
│  │ Frontend   │  │              └────┬────┘  └────┬────┘  └───┬────┘
│  ├────────────┤  │                   │             │           │
│  │ Users API  │  │              ┌────▼─────────────▼───────────▼────┐
│  ├────────────┤  │              │           API Gateway              │
│  │ Orders API │  │              └───────────────────────────────────┘
│  ├────────────┤  │
│  │ Database   │  │
│  └────────────┘  │
└──────────────────┘
```

### When to use each:

| Monolith | Microservices |
|----------|--------------|
| Early stage / MVP | Product is proven and growing |
| Small team (1-5 devs) | Multiple teams per service |
| Simple domain | Complex domain with distinct bounded contexts |
| Fast iteration needed | Independent scaling needed |

**Don't start with microservices.** The complexity is real. Start with a monolith, extract services when a specific boundary becomes painful.

---

## 2. Core Microservices Patterns

### API Gateway
The single entry point for all external traffic. It routes requests to the right service.

```
Client → API Gateway → /users  → Users Service
                     → /orders → Orders Service
                     → /       → Frontend Service
```

Tools: **Kong**, **nginx**, **AWS API Gateway**, **Traefik** (used as K8s Ingress)

### Service Discovery
Services need to find each other. In Kubernetes, this is built-in via DNS:

```
Frontend calls: http://users-service:80/api/users
               ↑ K8s resolves "users-service" to the Service's ClusterIP
```

### Circuit Breaker
If Service B is down, Service A shouldn't keep sending requests and timing out:

```
Normal:     A → B → success
Degraded:   A → B → timeout → A waits...
Circuit open: A  → immediately return fallback (don't even try B)
              → after timeout → try B again → if healthy, close circuit
```

### Sidecar Pattern
A helper container runs alongside the main container in the same Pod:
```
Pod:
├── App container (your Next.js service)
└── Sidecar container (Envoy proxy, logging agent, metrics collector)
```
This is how service meshes like **Istio** and **Linkerd** work.

---

## 3. Service Communication

### Synchronous (REST / gRPC)
```
Request → Service A → waits → Response from Service B
```

**REST (HTTP/JSON)** — simple, universal
```typescript
// users-service calls orders-service
const response = await fetch('http://orders-service/orders?userId=123')
const orders = await response.json()
```

**gRPC** — faster, strongly typed, binary protocol (better for internal services)
- Uses Protocol Buffers to define the API contract
- Generates client/server code in any language

### Asynchronous (Message Queues)
```
Service A → publishes event → Message Queue → Service B consumes event
                                            → Service C consumes event
```

Services don't wait for each other. This improves resilience and decoupling.

Tools: **RabbitMQ**, **Apache Kafka**, **AWS SQS**, **Google Pub/Sub**

```
User places order → OrderService publishes "order.created" event
                  → EmailService receives event → sends confirmation email
                  → InventoryService receives event → decrements stock
                  → AnalyticsService receives event → records sale
```

---

## 4. Splitting Our App

Our Next.js app is currently a monolith. Here's how we'd split it into microservices:

```
devops-essentials/
├── services/
│   ├── frontend/          ← Next.js (UI only, calls API service)
│   │   ├── Dockerfile
│   │   └── ...
│   └── api/               ← Standalone API (Node.js / Express / FastAPI)
│       ├── Dockerfile
│       ├── src/
│       │   ├── routes/
│       │   └── index.ts
│       └── package.json
├── k8s/
│   ├── frontend-deployment.yaml
│   ├── api-deployment.yaml
│   └── ingress.yaml         ← Routes / to frontend, /api to api service
└── docker-compose.yml       ← Run all services locally
```

### Example: Create a simple API service

Create `services/api/src/index.ts`:
```typescript
import express from 'express'

const app = express()
const PORT = process.env.PORT || 4000

app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'api', timestamp: new Date() })
})

app.get('/api/info', (req, res) => {
  res.json({
    version: '0.1.0',
    environment: process.env.NODE_ENV,
    uptime: process.uptime()
  })
})

app.listen(PORT, () => {
  console.log(`API service running on port ${PORT}`)
})
```

### Ingress to route between services:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
spec:
  rules:
    - host: devops-app.local
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: api-service
                port:
                  number: 80
          - path: /
            pathType: Prefix
            backend:
              service:
                name: frontend-service
                port:
                  number: 80
```

---

## 5. Docker Compose for Local Multi-Service Development

```yaml
version: "3.9"

services:
  frontend:
    build: ./services/frontend
    ports:
      - "3000:3000"
    environment:
      - API_URL=http://api:4000
    depends_on:
      - api

  api:
    build: ./services/api
    ports:
      - "4000:4000"
    environment:
      - DATABASE_URL=postgresql://devops:password@db:5432/devops_db
    depends_on:
      - db

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: devops
      POSTGRES_PASSWORD: password
      POSTGRES_DB: devops_db

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - frontend
      - api
```

---

## 6. Exercise: Add a Health Endpoint

Update `app/app/api/health/route.ts`:

```typescript
import { NextResponse } from 'next/server'

export async function GET() {
  return NextResponse.json({
    status: 'healthy',
    version: process.env.APP_VERSION || '0.1.0',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  })
}
```

This is a standard pattern in microservices — every service exposes `/health` and `/ready` endpoints. Kubernetes uses them for liveness and readiness probes.

---

## Checklist

- [ ] I can explain the trade-offs between monoliths and microservices
- [ ] I understand what an API Gateway does
- [ ] I've added a `/health` endpoint to the Next.js app
- [ ] I understand the difference between REST and gRPC communication
- [ ] I understand what message queues solve (async communication)
- [ ] I can describe the sidecar pattern
- [ ] My Docker Compose file runs the frontend and API as separate services

---

**Next:** [Module 07 — Ansible](../07-ansible/README.md)
