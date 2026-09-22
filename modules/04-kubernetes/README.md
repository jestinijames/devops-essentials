# Module 04 — Kubernetes

> **Goal:** Deploy the containerized Next.js app to a local Kubernetes cluster, scale it, and understand how Kubernetes manages containers at scale.

---

## Why Kubernetes? (The real problem it solves)

Docker runs one container. But in production you need:

- **Multiple copies** of your app for reliability (if one crashes, others keep serving traffic)
- **Automatic restarts** when a container crashes
- **Rolling updates** (deploy new code without downtime)
- **Load balancing** across all the running copies
- **Resource limits** (prevent one app from eating all the CPU)

**Kubernetes (K8s)** is the system that orchestrates all of this. It's a control plane that manages a fleet of containers across one or more machines.

Think of it like this:

> Docker is a single musician. Kubernetes is the **orchestra conductor** — it tells each musician what to play, makes sure they're all playing, brings in replacements when one faints, and adjusts the tempo dynamically.

---

## Key Concepts

### The cluster

A Kubernetes cluster has:

- **Control plane** — the brain (scheduler, API server, etc.) — you don't touch this
- **Nodes** — the worker machines where containers actually run
- **Pods** — the smallest deployable unit (one or more containers)

### Core objects

| Object         | What it is                                        | Analogy                                          |
| -------------- | ------------------------------------------------- | ------------------------------------------------ |
| **Pod**        | One or more containers that run together          | A single instance of your app                    |
| **Deployment** | Declares how many Pod replicas you want           | Like a React state that says "I want 3 of these" |
| **Service**    | A stable network address to reach a set of Pods   | Like a load balancer / DNS entry                 |
| **ConfigMap**  | Non-secret config values (env vars, config files) | `.env` file, but in the cluster                  |
| **Secret**     | Sensitive config values (passwords, API keys)     | `.env.local` delivered through the cluster API   |
| **Namespace**  | A logical partition of the cluster                | Like separate GitHub repos in an org             |
| **Ingress**    | Routes external HTTP traffic to Services          | Like an nginx reverse proxy config               |

### YAML manifests

Everything in Kubernetes is declared in YAML. The structure is always:

```yaml
apiVersion: apps/v1 # Which K8s API version handles this
kind: Deployment # The type of object
metadata:
  name: my-app # Name of this object
  namespace: default # Which namespace
spec: # The desired state — "I want this"
  ...
```

### Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: devops-essentials
spec:
  replicas: 3 # Run 3 copies of the pod
  selector:
    matchLabels:
      app: devops-essentials # Manage pods with this label
  template:
    metadata:
      labels:
        app: devops-essentials # Label the pods
    spec:
      containers:
        - name: app
          image: ghcr.io/yourname/devops-essentials:latest
          ports:
            - containerPort: 3000
          env:
            - name: NODE_ENV
              value: production
```

### Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: devops-essentials-svc
spec:
  selector:
    app: devops-essentials # Route traffic to pods with this label
  ports:
    - port: 80 # Port accessible within the cluster
      targetPort: 3000 # Port the container is listening on
  type: ClusterIP # Only reachable inside the cluster
```

### The reconciliation loop

This is the core of how Kubernetes works:

```
You declare: "I want 3 replicas"
        ↓
Kubernetes checks: "I see 2 running"
        ↓
Kubernetes acts: "Starting 1 more"
        ↓
Kubernetes checks: "Now I see 3 running" ✓
```

If a pod crashes, Kubernetes detects it and starts a replacement — automatically, without you doing anything. This is called **self-healing**.

---

## Setup

Install and start `minikube` (a local single-node Kubernetes cluster):

```bash
# Install
brew install minikube kubectl

# Start the cluster
minikube start

# Verify
kubectl cluster-info
kubectl get nodes
```

---

## Exercise 1 — Run a pod manually

Before using Deployments, understand what a Pod actually is:

```bash
# Run a pod interactively
kubectl run test-pod --image=nginx --port=80

# Check it's running
kubectl get pods

# See detailed info
kubectl describe pod test-pod

# Forward the port to your machine
kubectl port-forward pod/test-pod 8080:80
# Now visit http://localhost:8080

# Clean up
kubectl delete pod test-pod
```

Try this. Notice that if you delete the pod, nothing restarts it. That's why Deployments exist.

---

## Exercise 2 — Write a Deployment manifest

Create `k8s/deployment.yaml`:

```
Your tasks:
1. apiVersion: apps/v1, kind: Deployment
2. name: devops-essentials
3. 2 replicas
4. Container using the image you pushed to GHCR in Module 02
5. containerPort: 3000
6. Set NODE_ENV=production via env
7. Add a liveness probe hitting /api/health (HTTP GET, port 3000)
8. Add a readiness probe hitting /api/health (HTTP GET, port 3000)
   - initialDelaySeconds: 10
   - periodSeconds: 5
```

Apply it:

```bash
kubectl apply -f k8s/deployment.yaml
kubectl get pods    # watch 2 pods come up
kubectl get pods -w # -w means "watch" for changes
```

**What are liveness/readiness probes?**

- **Liveness:** "Is this container still alive? If not, restart it."
- **Readiness:** "Is this container ready to receive traffic? If not, remove it from the load balancer."

Your `/api/health` endpoint powers both.

**Solution:** `modules/04-kubernetes/solutions/deployment.yaml`

---

## Exercise 3 — Write a Service manifest

Your pods are running but unreachable. Create `k8s/service.yaml`:

```
Your tasks:
1. kind: Service
2. name: devops-essentials-svc
3. selector: app: devops-essentials (must match your Deployment's pod labels)
4. Port 80 → targetPort 3000
5. type: ClusterIP
```

Apply and test with port-forward:

```bash
kubectl apply -f k8s/service.yaml
kubectl get services
kubectl port-forward service/devops-essentials-svc 8080:80
# Visit http://localhost:8080
```

**Solution:** `modules/04-kubernetes/solutions/service.yaml`

---

## Exercise 4 — Scale and watch self-healing

```bash
# Scale up to 5 replicas
kubectl scale deployment devops-essentials --replicas=5
kubectl get pods -w    # watch 3 more pods spin up

# Kill one pod manually
kubectl delete pod <one-of-the-pod-names>
kubectl get pods -w    # watch Kubernetes immediately start a replacement

# Scale down
kubectl scale deployment devops-essentials --replicas=2
kubectl get pods -w    # watch 3 pods terminate
```

This is self-healing. You didn't write any restart logic. Kubernetes just does it.

---

## Exercise 5 — Rolling update (zero-downtime deploy)

Change the `APP_VERSION` env var in your deployment to simulate a new release:

```bash
kubectl set env deployment/devops-essentials APP_VERSION=2.0.0
kubectl rollout status deployment/devops-essentials  # watch the rollout
kubectl get pods -w                                   # watch old pods terminate, new ones start
```

Visit `http://localhost:8080/api/health` while the rollout happens — you should get responses the whole time. No downtime.

Roll back if something goes wrong:

```bash
kubectl rollout undo deployment/devops-essentials
kubectl rollout history deployment/devops-essentials
```

---

## Exercise 6 — ConfigMap and Secret

Create `k8s/configmap.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  APP_VERSION: "3.0.0"
  LOG_LEVEL: "info"
```

Create `k8s/secret.yaml` (base64 is encoding, not encryption; do not commit real secrets):

```bash
echo -n "my-secret-api-key" | base64
```

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
data:
  API_KEY: <base64-encoded-value>
```

Update your Deployment to use them:

```yaml
envFrom:
  - configMapRef:
      name: app-config
  - secretRef:
      name: app-secrets
```

**Solution:** `modules/04-kubernetes/solutions/`

---

## Key Commands Reference

```bash
kubectl get pods                              # List pods
kubectl get pods -w                           # Watch for changes
kubectl get deployments                       # List deployments
kubectl get services                          # List services
kubectl describe pod <name>                   # Detailed pod info + events
kubectl logs <pod-name>                       # Container logs
kubectl logs -f <pod-name>                    # Follow logs
kubectl exec -it <pod-name> -- sh             # Shell into a container
kubectl apply -f <file>.yaml                  # Apply a manifest
kubectl delete -f <file>.yaml                 # Delete resources defined in a manifest
kubectl port-forward service/<name> 8080:80  # Forward local port to a service
kubectl scale deployment <name> --replicas=N  # Scale a deployment
kubectl rollout status deployment/<name>      # Watch a rollout
kubectl rollout undo deployment/<name>        # Roll back
```

---

## What to look up

- [Kubernetes concepts](https://kubernetes.io/docs/concepts/)
- [kubectl cheatsheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Services](https://kubernetes.io/docs/concepts/services-networking/service/)
- [Liveness and readiness probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [minikube docs](https://minikube.sigs.k8s.io/docs/)

---

## Checkpoint

Before moving to Module 05, verify:

- [ ] `kubectl get pods` shows your app running with 2+ replicas
- [ ] `kubectl port-forward` lets you access the app at localhost
- [ ] You killed a pod manually and watched Kubernetes restart it
- [ ] You performed a rolling update with zero downtime
- [ ] You can explain what a liveness probe vs readiness probe does

---

## What's next?

In **Module 05**, you'll break the monolithic Next.js app into multiple independent services — a separate API service, a separate frontend — and connect them together using both Docker Compose (local) and Kubernetes (production style).

→ [Module 05 — Microservices](../05-microservices/README.md)
