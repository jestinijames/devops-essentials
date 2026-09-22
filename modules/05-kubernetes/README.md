# Module 05 — Kubernetes

> **Docker runs one container. Kubernetes runs thousands — and heals them, scales them, and routes traffic to them automatically.**

Kubernetes (K8s) is the industry-standard container orchestration platform. When your app needs to run on multiple servers, handle traffic spikes, recover from crashes, and update without downtime — that's Kubernetes.

---

## Learning Objectives

By the end of this module you will:
- [ ] Understand when and why you need Kubernetes
- [ ] Know the core K8s architecture (control plane + nodes)
- [ ] Run a local Kubernetes cluster with `minikube` or `kind`
- [ ] Deploy the Next.js app using Deployments, Services, and Ingress
- [ ] Use ConfigMaps and Secrets
- [ ] Scale an app and perform a rolling update
- [ ] Use Helm — the package manager for Kubernetes
- [ ] Understand namespaces for organizing workloads

---

## 1. When Do You Need Kubernetes?

You don't always need K8s. But you do when you have:

| Scenario | K8s helps |
|----------|-----------|
| Multiple services that need to talk to each other | Service discovery |
| Need to run 10+ replicas of the same container | Deployment management |
| App crashes should auto-recover | Self-healing |
| Traffic spikes need automatic scaling | Horizontal Pod Autoscaler |
| Zero-downtime deployments | Rolling updates |
| Multiple teams deploying to the same cluster | Namespaces + RBAC |

**For a single-server app with predictable traffic:** Docker Compose is enough. K8s adds complexity — only add it when you need what it solves.

---

## 2. Kubernetes Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CONTROL PLANE                         │
│  ┌──────────────┐  ┌──────────┐  ┌───────────────────┐  │
│  │ API Server   │  │  etcd    │  │ Controller Manager │  │
│  │ (kube-apiserver)│ (state DB)│  │ Scheduler          │  │
│  └──────────────┘  └──────────┘  └───────────────────┘  │
└─────────────────────────────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│    NODE 1    │  │    NODE 2    │  │    NODE 3    │
│  ┌────────┐  │  │  ┌────────┐  │  │  ┌────────┐  │
│  │  Pod   │  │  │  │  Pod   │  │  │  │  Pod   │  │
│  │  ┌───┐ │  │  │  │  ┌───┐ │  │  │  │  ┌───┐ │  │
│  │  │app│ │  │  │  │  │db │ │  │  │  │  │app│ │  │
│  │  └───┘ │  │  │  │  └───┘ │  │  │  │  └───┘ │  │
│  └────────┘  │  │  └────────┘  │  │  └────────┘  │
│  kubelet     │  │  kubelet     │  │  kubelet     │
└──────────────┘  └──────────────┘  └──────────────┘
```

### Core Components

| Component | What it does |
|-----------|-------------|
| **Pod** | The smallest unit — one or more containers that share network/storage |
| **Deployment** | Manages a set of identical Pods (desired state, history, rollbacks) |
| **Service** | Stable network endpoint for a set of Pods (load balances across them) |
| **Ingress** | Routes external HTTP/HTTPS traffic to Services |
| **ConfigMap** | Store non-sensitive configuration |
| **Secret** | Store sensitive configuration (base64-encoded, optionally encrypted) |
| **Namespace** | Virtual cluster — isolates groups of resources |
| **Node** | A worker machine (VM or physical) |

---

## 3. Setup: Local Kubernetes Cluster

### Option A: minikube (easiest for beginners)
```bash
# Install minikube
# Windows: choco install minikube
# Mac:     brew install minikube

# Start cluster (uses Docker as the driver)
minikube start --driver=docker

# Enable ingress addon
minikube addons enable ingress

# Check cluster is running
kubectl cluster-info
kubectl get nodes
```

### Option B: kind (Kubernetes in Docker — faster, preferred for CI)
```bash
# Install kind
# Windows: choco install kind
# Mac:     brew install kind

# Create a cluster
kind create cluster --name devops-local

# Verify
kubectl config current-context   # kind-devops-local
kubectl get nodes
```

### Install kubectl (the CLI)
```bash
# Windows: choco install kubernetes-cli
# Mac:     brew install kubectl

kubectl version --client

# Essential aliases (add to your shell profile)
alias k=kubectl
alias kgp="kubectl get pods"
alias kgs="kubectl get services"
alias kgd="kubectl get deployments"
```

---

## 4. Your First Deployment

Create `k8s/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: devops-app
  labels:
    app: devops-app
    version: v0.1.0
spec:
  replicas: 2          # Run 2 identical copies

  selector:
    matchLabels:
      app: devops-app

  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1          # Allow 1 extra Pod during update
      maxUnavailable: 0    # Never go below desired count

  template:              # Pod template
    metadata:
      labels:
        app: devops-app
    spec:
      containers:
        - name: app
          image: YOUR_DOCKERHUB_USERNAME/devops-app:latest
          ports:
            - containerPort: 3000

          # Resource limits (ALWAYS set these in production)
          resources:
            requests:
              memory: "128Mi"
              cpu: "100m"
            limits:
              memory: "256Mi"
              cpu: "500m"

          # Health checks
          livenessProbe:
            httpGet:
              path: /
              port: 3000
            initialDelaySeconds: 10
            periodSeconds: 30

          readinessProbe:
            httpGet:
              path: /
              port: 3000
            initialDelaySeconds: 5
            periodSeconds: 10

          env:
            - name: NODE_ENV
              value: production
            - name: PORT
              value: "3000"
```

```bash
# Apply the deployment
kubectl apply -f k8s/deployment.yaml

# Watch Pods being created
kubectl get pods -w    # -w = watch

# See full details of a Pod
kubectl describe pod devops-app-xxxxx

# See logs
kubectl logs -f deployment/devops-app
```

---

## 5. Services — Making Pods Reachable

Pods are ephemeral — their IPs change. A **Service** gives you a stable IP and load balances across healthy Pods.

Create `k8s/service.yaml`:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: devops-app-service
spec:
  selector:
    app: devops-app     # Targets all Pods with this label

  ports:
    - protocol: TCP
      port: 80          # Port the Service listens on
      targetPort: 3000  # Port the container listens on

  type: ClusterIP       # Internal-only (default)
  # type: LoadBalancer  # Request a cloud load balancer (AWS/GCP/Azure)
  # type: NodePort      # Expose on a port of the node (for testing)
```

```bash
kubectl apply -f k8s/service.yaml

# For testing locally with minikube — get an accessible URL
minikube service devops-app-service --url

# Or port-forward directly
kubectl port-forward service/devops-app-service 8080:80
# Now open http://localhost:8080
```

---

## 6. Ingress — HTTP Routing

Ingress routes external HTTP traffic to multiple services based on hostname or path.

Create `k8s/ingress.yaml`:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: devops-app-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx

  rules:
    - host: devops-app.local    # for local testing with /etc/hosts
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: devops-app-service
                port:
                  number: 80
```

```bash
kubectl apply -f k8s/ingress.yaml

# For minikube — add to your /etc/hosts
minikube ip   # e.g., 192.168.49.2
# Add to C:\Windows\System32\drivers\etc\hosts:
# 192.168.49.2 devops-app.local

# Now open http://devops-app.local
```

---

## 7. ConfigMaps and Secrets

### ConfigMap (non-sensitive config)
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  NODE_ENV: production
  APP_PORT: "3000"
  LOG_LEVEL: info
  FEATURE_FLAG_NEW_UI: "true"
```

### Secret (sensitive config)
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
stringData:       # Kubernetes base64-encodes these automatically
  DATABASE_URL: "postgresql://user:password@db:5432/mydb"
  JWT_SECRET: "super-secret-key-change-me"
```

**Using them in your Deployment:**
```yaml
containers:
  - name: app
    envFrom:
      - configMapRef:
          name: app-config      # All keys become env vars
      - secretRef:
          name: app-secrets     # All keys become env vars
    
    # Or inject individual values:
    env:
      - name: DATABASE_URL
        valueFrom:
          secretKeyRef:
            name: app-secrets
            key: DATABASE_URL
```

> **Security note:** Never commit Secrets YAML files with real values. Use sealed-secrets, external-secrets, or Vault in production.

---

## 8. Scaling and Rolling Updates

```bash
# Scale manually
kubectl scale deployment devops-app --replicas=5
kubectl get pods -w    # Watch 3 new pods appear

# Scale back down
kubectl scale deployment devops-app --replicas=2

# Update the image (triggers a rolling update)
kubectl set image deployment/devops-app app=YOUR_USERNAME/devops-app:v0.2.0

# Watch the rolling update
kubectl rollout status deployment/devops-app

# See rollout history
kubectl rollout history deployment/devops-app

# Rollback to previous version
kubectl rollout undo deployment/devops-app

# Rollback to a specific version
kubectl rollout undo deployment/devops-app --to-revision=2
```

This is how **zero-downtime deployments** work. Kubernetes:
1. Creates 1 new Pod with the new image (`maxSurge: 1`)
2. Waits for it to pass readiness checks
3. Kills 1 old Pod
4. Repeats until all Pods are updated

---

## 9. Namespaces

Namespaces partition a cluster. Use them to separate environments or teams.

```bash
# Create namespaces
kubectl create namespace staging
kubectl create namespace production

# Deploy to a specific namespace
kubectl apply -f k8s/deployment.yaml -n staging

# View resources in a namespace
kubectl get pods -n staging

# View resources across all namespaces
kubectl get pods --all-namespaces   # or -A

# Set default namespace for your session
kubectl config set-context --current --namespace=staging
```

---

## 10. Helm — Package Manager for Kubernetes

Helm is to Kubernetes what npm is to Node.js. Instead of managing 10 separate YAML files, you use a **Chart** (a packaged set of templates).

```bash
# Install Helm
# Windows: choco install kubernetes-helm
# Mac:     brew install helm

# Add the repo for a chart
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Install PostgreSQL with one command
helm install my-postgres bitnami/postgresql \
  --set auth.postgresPassword=secretpassword \
  --set primary.persistence.size=1Gi

# See what's installed
helm list

# Upgrade a release
helm upgrade my-postgres bitnami/postgresql --set auth.postgresPassword=newpassword

# Uninstall
helm uninstall my-postgres
```

### Create a Helm Chart for our app:
```bash
helm create devops-app
```

This generates:
```
devops-app/
├── Chart.yaml         ← metadata
├── values.yaml        ← default values
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    └── ingress.yaml
```

Customise `values.yaml`:
```yaml
replicaCount: 2
image:
  repository: YOUR_DOCKERHUB_USERNAME/devops-app
  tag: latest
service:
  type: ClusterIP
  port: 80
```

```bash
# Install our chart
helm install devops-release ./devops-app

# Install with custom values
helm install devops-release ./devops-app --set replicaCount=3

# Upgrade
helm upgrade devops-release ./devops-app --set image.tag=v0.2.0
```

---

## 11. Exercises

### Exercise 1: Deploy to Local Cluster
```bash
# Start minikube
minikube start --driver=docker

# Apply all your manifests
kubectl apply -f k8s/

# Watch Pods start
kubectl get pods -w

# Port-forward and verify the app is running
kubectl port-forward service/devops-app-service 8080:80
# http://localhost:8080
```

### Exercise 2: Trigger a Rolling Update
1. Push a change to the Next.js homepage
2. Build and push a new Docker image tagged `v0.2.0`
3. `kubectl set image deployment/devops-app app=YOUR_USERNAME/devops-app:v0.2.0`
4. Watch `kubectl rollout status deployment/devops-app`
5. Verify the new version is live

### Exercise 3: Kill a Pod and Watch Self-Healing
```bash
kubectl get pods  # note a pod name
kubectl delete pod devops-app-xxxxx   # delete one
kubectl get pods -w  # watch K8s immediately create a replacement
```

### Exercise 4: Create Your Helm Chart
```bash
helm create devops-app-chart
# Modify values.yaml with your image details
helm install devops --dry-run --debug ./devops-app-chart  # preview
helm install devops ./devops-app-chart
```

---

## Checklist

- [ ] I have a local Kubernetes cluster running (minikube or kind)
- [ ] My Deployment YAML is applying correctly
- [ ] I understand the difference between Pod, Deployment, and Service
- [ ] I've successfully port-forwarded to access the app
- [ ] I've scaled the deployment up and down manually
- [ ] I've performed a rolling update with zero downtime
- [ ] I've rolled back to a previous version
- [ ] I can create and use ConfigMaps and Secrets
- [ ] I understand what Helm is and have created a basic chart

---

## Further Reading

- [Kubernetes Official Docs](https://kubernetes.io/docs/home/)
- [Kubernetes The Hard Way](https://github.com/kelseyhightower/kubernetes-the-hard-way) — learn by building from scratch
- [Lens Desktop](https://k8slens.dev/) — GUI for Kubernetes clusters
- [k9s](https://k9scli.io/) — terminal UI for K8s (highly recommended)
- [Helm Docs](https://helm.sh/docs/)

---

**Next:** [Module 06 — Microservices](../06-microservices/README.md)
