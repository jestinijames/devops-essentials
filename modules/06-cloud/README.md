# Module 06 — Cloud (GCP, AWS, Azure)

> **Goal:** Deploy everything to a real cloud provider using managed Kubernetes, and understand the free tier options to do it without spending money.

---

## The big picture

By now you have:

- A containerized Next.js app (Module 01)
- A CI/CD pipeline that builds and pushes images (Module 02)
- Infrastructure-as-code with Terraform (Module 03)
- Kubernetes manifests for deploying and scaling (Module 04)
- A microservices architecture (Module 05)

Cloud is where all of this comes together. Instead of running `minikube` on your laptop, your Kubernetes cluster runs on someone else's very large computers — and the rest of the world can reach it.

---

## Free tier reality check

| Cloud     | Managed K8s | Free tier notes                                                                                    |
| --------- | ----------- | -------------------------------------------------------------------------------------------------- |
| **GCP**   | GKE         | **Best for learning** — GKE Autopilot has 1 free zonal cluster. $300 credit for 90 days            |
| **AWS**   | EKS         | EKS control plane costs $0.10/hr (~$72/month). Use EC2 free tier nodes. Not great for K8s learning |
| **Azure** | AKS         | Free control plane. B2s VMs are cheap. $200 credit for 30 days                                     |

**Recommendation:** Start with GCP (GKE) if you want managed K8s for free. For AWS, use ECS Fargate or EC2 directly until you're comfortable paying for EKS.

---

## Module structure

This module covers all three clouds. Pick one to start, then explore the others:

- [GCP (Google Cloud Platform)](#gcp---google-kubernetes-engine)
- [AWS (Amazon Web Services)](#aws---elastic-container-service--ec2)
- [Azure](#azure---azure-kubernetes-service)

---

## GCP — Google Kubernetes Engine

### Concepts

| GCP Term                 | What it is                                        |
| ------------------------ | ------------------------------------------------- |
| **Project**              | The billing/resource boundary (like a workspace)  |
| **GKE**                  | Google Kubernetes Engine — managed K8s            |
| **Artifact Registry**    | Where you push Docker images (like GHCR, but GCP) |
| **Cloud Load Balancing** | Exposes your K8s Service to the internet          |
| **Cloud Run**            | Simpler: runs a container without Kubernetes      |

### Exercise 1 — Set up the CLI and create a project

```bash
# Install the gcloud CLI
brew install google-cloud-sdk

# Log in
gcloud auth login

# Create a project
gcloud projects create devops-essentials-yourname

# Set it as active
gcloud config set project devops-essentials-yourname

# Enable billing (required even for free tier)
# → https://console.cloud.google.com/billing
```

### Exercise 2 — Push your image to Artifact Registry

```bash
# Enable the Artifact Registry API
gcloud services enable artifactregistry.googleapis.com

# Create a repository
gcloud artifacts repositories create devops-essentials \
  --repository-format=docker \
  --location=us-central1

# Configure Docker to use gcloud credentials
gcloud auth configure-docker us-central1-docker.pkg.dev

# Tag and push your image
docker tag devops-essentials:prod \
  us-central1-docker.pkg.dev/YOUR_PROJECT/devops-essentials/app:latest

docker push us-central1-docker.pkg.dev/YOUR_PROJECT/devops-essentials/app:latest
```

### Exercise 3 — Create a GKE cluster with Terraform

Create `modules/06-cloud/gcp/main.tf`:

```hcl
provider "google" {
  project = var.project_id
  region  = "us-central1"
}

resource "google_container_cluster" "primary" {
  name     = "devops-essentials"
  location = "us-central1"

  # Autopilot manages node pools for you — no node configuration needed
  enable_autopilot = true

  deletion_protection = false
}
```

```bash
terraform init
terraform plan
terraform apply
# This takes ~5 minutes
```

Connect kubectl to it:

```bash
gcloud container clusters get-credentials devops-essentials \
  --region us-central1 \
  --project YOUR_PROJECT
kubectl get nodes
```

### Exercise 4 — Deploy to GKE

Update your `k8s/deployment.yaml` to use the Artifact Registry image URL, then:

```bash
kubectl apply -f k8s/
kubectl get services  # watch for EXTERNAL-IP on the LoadBalancer service
```

Change the Service type to `LoadBalancer` instead of `ClusterIP` to expose it to the internet:

```yaml
type: LoadBalancer
```

Once `EXTERNAL-IP` appears (takes 1-2 min), visit it in your browser.

**Your app is live on the internet.**

### Cleanup (important — don't forget)

```bash
terraform destroy   # tears down the cluster
```

---

## AWS — Elastic Container Service & EC2

### Why not EKS for learning?

EKS charges $0.10/hour for the control plane (~$72/month). Instead, learn AWS fundamentals with:

- **ECS Fargate** — a simpler container runner (no cluster to manage)
- **EC2** — a plain virtual machine (free tier: 750 hours/month of t2.micro)

### Concepts

| AWS Term    | What it is                                                |
| ----------- | --------------------------------------------------------- |
| **ECR**     | Elastic Container Registry — push your Docker images here |
| **ECS**     | Elastic Container Service — runs containers               |
| **Fargate** | Serverless compute for containers (no VMs to manage)      |
| **EC2**     | Virtual machines                                          |
| **VPC**     | Virtual Private Cloud — your private network in AWS       |
| **IAM**     | Identity & Access Management — permissions and roles      |
| **ALB**     | Application Load Balancer — routes HTTP traffic           |

### Exercise 1 — Set up the CLI

```bash
brew install awscli
aws configure   # enter your Access Key ID, Secret, region (us-east-1)
aws sts get-caller-identity   # verify it works
```

### Exercise 2 — Push to ECR

```bash
# Create an ECR repository
aws ecr create-repository --repository-name devops-essentials --region us-east-1

# Log Docker into ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Tag and push
docker tag devops-essentials:prod \
  YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/devops-essentials:latest

docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/devops-essentials:latest
```

### Exercise 3 — Deploy with ECS Fargate using Terraform

Create `modules/06-cloud/aws/main.tf`:

```hcl
provider "aws" {
  region = "us-east-1"
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "devops-essentials"
}

# Task Definition (like a K8s Pod spec)
resource "aws_ecs_task_definition" "app" {
  family                   = "devops-essentials"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 256
  memory                   = 512

  container_definitions = jsonencode([{
    name  = "app"
    image = "YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/devops-essentials:latest"
    portMappings = [{ containerPort = 3000 }]
    environment = [{ name = "NODE_ENV", value = "production" }]
    healthCheck = {
      command = ["CMD-SHELL", "wget -qO- http://localhost:3000/api/health || exit 1"]
    }
  }])
}
```

**Solution:** `modules/06-cloud/aws/`

---

## Azure — Azure Kubernetes Service

### Concepts

| Azure Term         | What it is                                  |
| ------------------ | ------------------------------------------- |
| **Resource Group** | A container for related Azure resources     |
| **ACR**            | Azure Container Registry — push images here |
| **AKS**            | Azure Kubernetes Service — managed K8s      |
| **Azure CLI**      | `az` — the command-line tool                |

### Exercise 1 — Set up the CLI

```bash
brew install azure-cli
az login
az account show   # verify
```

### Exercise 2 — Push to ACR

```bash
# Create a resource group
az group create --name devops-essentials --location eastus

# Create a container registry
az acr create --resource-group devops-essentials \
  --name devopsessentialsyourname \
  --sku Basic

# Log in
az acr login --name devopsessentialsyourname

# Tag and push
docker tag devops-essentials:prod \
  devopsessentialsyourname.azurecr.io/app:latest

docker push devopsessentialsyourname.azurecr.io/app:latest
```

### Exercise 3 — AKS cluster with Terraform

Create `modules/06-cloud/azure/main.tf`:

```hcl
provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = "devops-essentials"
  location = "East US"
}

resource "azurerm_kubernetes_cluster" "aks" {
  name                = "devops-essentials"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  dns_prefix          = "devops-essentials"

  default_node_pool {
    name       = "default"
    node_count = 1
    vm_size    = "Standard_B2s"   # cheapest AKS node
  }

  identity {
    type = "SystemAssigned"
  }
}
```

Connect kubectl:

```bash
az aks get-credentials \
  --resource-group devops-essentials \
  --name devops-essentials
kubectl get nodes
```

---

## Putting it all together — Full CI/CD to Cloud

Now wire GitHub Actions (Module 02) + Terraform (Module 03) + Cloud:

```
Push to main
    → GitHub Actions: lint + build
    → GitHub Actions: docker build + push to ECR/ACR/Artifact Registry
    → GitHub Actions: kubectl apply -f k8s/ (against the cloud cluster)
    → Kubernetes: rolling update, zero downtime
```

The GitHub Actions step to deploy to Kubernetes:

```yaml
- name: Configure kubectl for GKE
  uses: google-github-actions/get-gke-credentials@v2
  with:
    cluster_name: devops-essentials
    location: us-central1
    project_id: ${{ secrets.GCP_PROJECT_ID }}

- name: Deploy to Kubernetes
  run: |
    kubectl set image deployment/devops-essentials \
      app=us-central1-docker.pkg.dev/${{ secrets.GCP_PROJECT_ID }}/devops-essentials/app:${{ github.sha }}
    kubectl rollout status deployment/devops-essentials
```

---

## What to look up

- [GKE quickstart](https://cloud.google.com/kubernetes-engine/docs/quickstarts/create-cluster)
- [GCP free tier](https://cloud.google.com/free/docs/free-cloud-features)
- [AWS ECS getting started](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/getting-started.html)
- [AWS free tier](https://aws.amazon.com/free/)
- [AKS quickstart](https://learn.microsoft.com/en-us/azure/aks/learn/quick-kubernetes-deploy-cli)
- [Azure free tier](https://azure.microsoft.com/en-us/free/)

---

## Checkpoint — You've completed the curriculum

At this point you should be able to:

- [ ] Your app runs in a cloud-managed Kubernetes cluster
- [ ] Pushing to `main` automatically builds, pushes, and deploys a new version
- [ ] You can scale replicas up and down with `kubectl scale`
- [ ] `terraform destroy` tears down all the cloud infrastructure cleanly
- [ ] You understand what you're paying for (and what's free)

---

## Where to go next

- **Monitoring & Observability** — Prometheus + Grafana for metrics, Loki for logs, Jaeger for distributed tracing
- **Service Mesh** — Istio or Linkerd for mTLS, traffic control, advanced observability
- **GitOps** — ArgoCD or Flux: Kubernetes watches a Git repo and self-applies changes (the CD pipeline lives in K8s itself)
- **Helm** — Package manager for Kubernetes manifests (like npm for YAML)
- **Security** — RBAC, network policies, image scanning (Trivy), secrets management (HashiCorp Vault)
- **Cost optimization** — Spot instances, Karpenter, resource requests/limits tuning

You started as a frontend engineer. You now understand the full stack — from `git push` to production.
