# Module 08 — GitOps

> **GitOps is the practice of using Git as the single source of truth for both application code AND infrastructure state.** If it's not in Git, it doesn't exist.

You asked: "Is GitOps just Terraform?" — not quite. GitOps is a broader philosophy. Terraform is a tool that *fits within* GitOps for infrastructure. But GitOps also covers how Kubernetes *continuously syncs* itself from a Git repo.

---

## Learning Objectives

By the end of this module you will:
- [ ] Understand the four GitOps principles
- [ ] Know the difference between push-based and pull-based CD
- [ ] Install and configure ArgoCD to manage Kubernetes deployments from Git
- [ ] Understand FluxCD as an alternative
- [ ] Implement a full GitOps workflow: push code → CI builds image → ArgoCD deploys

---

## 1. The Four GitOps Principles (OpenGitOps)

1. **Declarative** — The desired system state is expressed declaratively (Kubernetes YAML, Terraform HCL, Helm Charts)
2. **Versioned and Immutable** — All state is stored in Git. History is preserved. Rollback = `git revert`
3. **Pulled Automatically** — Software agents (ArgoCD, Flux) continuously pull the desired state from Git and apply it
4. **Continuously Reconciled** — Agents continuously check if the actual state matches the desired state, and correct drift

---

## 2. Push-Based vs Pull-Based CD

### Push-Based (what we did in Module 03)
```
Developer pushes → CI builds image → CI pipeline deploys to K8s
                                     (pipeline has cloud credentials)
```

Problems:
- CI/CD system needs access to production cluster — a security risk
- Cluster state can drift (someone kubectl applies something manually)
- Hard to audit "what is actually running right now?"

### Pull-Based (GitOps)
```
Developer pushes → CI builds image → CI updates image tag in Git
                                               ↓
                                    ArgoCD/Flux watches Git
                                    → detects change
                                    → pulls new state
                                    → applies to cluster
                                    → reconciles drift
```

Benefits:
- Cluster pulls from Git — no need to give CI access to the cluster
- Any manual changes to the cluster are auto-corrected (drift detection)
- `git log` is a full audit trail of every deployment

---

## 3. Repository Structure for GitOps

GitOps teams often keep app manifests in a **separate repo** from application code:

```
devops-essentials/          ← Application code repo
└── .github/workflows/
    └── docker.yml          ← CI: builds image, then updates manifest repo

devops-essentials-config/   ← GitOps config repo (K8s manifests)
├── apps/
│   └── devops-app/
│       ├── deployment.yaml
│       ├── service.yaml
│       └── kustomization.yaml
└── clusters/
    └── staging/
        └── apps.yaml       ← ArgoCD Application pointing to apps/devops-app/
```

For this module, we'll use a single repo for simplicity.

---

## 4. Kustomize — Manage YAML Variations

Before ArgoCD, learn Kustomize. It's built into `kubectl` and lets you customize YAML without duplicating it.

```
k8s/
├── base/
│   ├── deployment.yaml     ← shared base
│   ├── service.yaml
│   └── kustomization.yaml
└── overlays/
    ├── staging/
    │   ├── kustomization.yaml   ← patch staging-specific values
    │   └── patches/
    │       └── replica-count.yaml
    └── production/
        ├── kustomization.yaml
        └── patches/
            └── replica-count.yaml
```

`k8s/base/kustomization.yaml`:
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - deployment.yaml
  - service.yaml
```

`k8s/overlays/staging/kustomization.yaml`:
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namePrefix: staging-
namespace: staging

resources:
  - ../../base

images:
  - name: YOUR_USERNAME/devops-app
    newTag: sha-abc1234    ← This gets updated by CI automatically!

patches:
  - path: patches/replica-count.yaml
```

`k8s/overlays/staging/patches/replica-count.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: devops-app
spec:
  replicas: 1   # staging uses fewer replicas
```

```bash
# Preview what will be applied
kubectl kustomize k8s/overlays/staging/

# Apply
kubectl apply -k k8s/overlays/staging/

# Production
kubectl apply -k k8s/overlays/production/
```

---

## 5. ArgoCD

ArgoCD is a Kubernetes controller that watches a Git repo and continuously syncs your cluster to match what's in Git.

### Install ArgoCD:
```bash
# Install ArgoCD into your cluster
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Wait for pods to be ready
kubectl get pods -n argocd -w

# Port-forward the ArgoCD UI
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Get the initial admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# Login via browser: https://localhost:8080
# Username: admin
# Password: <from above>
```

### Install ArgoCD CLI:
```bash
# Mac
brew install argocd

# Login via CLI
argocd login localhost:8080 --insecure --username admin --password <password>
```

### Create an ArgoCD Application:

Create `argocd/apps/devops-app.yaml`:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: devops-app
  namespace: argocd
spec:
  project: default

  source:
    repoURL: https://github.com/YOUR_USERNAME/devops-essentials.git
    targetRevision: main
    path: k8s/overlays/staging    # Path to K8s manifests in repo

  destination:
    server: https://kubernetes.default.svc   # Deploy to the same cluster
    namespace: staging

  syncPolicy:
    automated:
      prune: true      # Delete resources removed from Git
      selfHeal: true   # Auto-fix drift (someone kubectl-applied something)
    syncOptions:
      - CreateNamespace=true
```

```bash
kubectl apply -f argocd/apps/devops-app.yaml

# Check sync status
argocd app get devops-app

# Manually trigger a sync
argocd app sync devops-app
```

---

## 6. The Full GitOps Flow

This is what a complete, automated GitOps pipeline looks like:

```
1. Dev pushes code to feature branch
2. CI (GitHub Actions) runs tests
3. Dev merges PR to main
4. CI builds Docker image: my-app:sha-abc1234
5. CI pushes image to Docker Hub
6. CI updates k8s/overlays/staging/kustomization.yaml:
      images:
        - name: my-app
          newTag: sha-abc1234   ← Updated automatically by CI!
7. CI commits and pushes to Git
8. ArgoCD detects the change in Git
9. ArgoCD syncs: applies new deployment.yaml with new image tag
10. Kubernetes performs rolling update
11. Deployment is live — all traceable in Git history
```

### Automate step 6 in GitHub Actions:
```yaml
- name: Update image tag in manifests
  run: |
    IMAGE_TAG=sha-${{ github.sha::7 }}
    cd k8s/overlays/staging
    
    # Use kustomize to update the image tag
    kustomize edit set image YOUR_USERNAME/devops-app:$IMAGE_TAG
    
    git config user.email "ci@github.com"
    git config user.name "GitHub Actions"
    git add .
    git commit -m "chore(deploy): update staging image to $IMAGE_TAG"
    git push
```

---

## 7. FluxCD — The Alternative

FluxCD is ArgoCD's main competitor. Both implement GitOps but differ in approach:

| | ArgoCD | FluxCD |
|--|--------|--------|
| **UI** | Rich web UI | CLI-focused (no built-in UI) |
| **Config** | Application CRD | More Kubernetes-native CRDs |
| **Multi-tenancy** | Built-in | Built-in |
| **Helm support** | Excellent | Excellent |
| **Best for** | Teams wanting a UI | Teams preferring pure CLI |

Both are CNCF projects. Either is a solid choice.

---

## Checklist

- [ ] I understand the four GitOps principles
- [ ] I can explain the difference between push-based and pull-based CD
- [ ] I've set up Kustomize overlays for staging and production
- [ ] ArgoCD is running in my local cluster
- [ ] I've created an ArgoCD Application that watches my Git repo
- [ ] I understand how drift detection and self-healing work
- [ ] I can trace any deployment back to a specific Git commit

---

## Further Reading

- [OpenGitOps Principles](https://opengitops.dev/)
- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [FluxCD Documentation](https://fluxcd.io/docs/)
- [Kustomize Documentation](https://kustomize.io/)

---

**Next:** [Module 09 — Cloud (AWS)](../09-cloud-aws/README.md)
