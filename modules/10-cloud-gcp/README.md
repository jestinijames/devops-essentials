# Module 10 — Cloud: GCP (Free Tier)

> **GCP (Google Cloud Platform)** is Google's cloud. Kubernetes originated at Google (it's based on their internal system Borg), so GCP's Kubernetes offering (GKE) is considered best-in-class. Cloud Run is also a standout — deploy containers without managing K8s.

---

## Learning Objectives

- [ ] Set up a GCP account and configure the `gcloud` CLI
- [ ] Understand core GCP services
- [ ] Deploy a Docker container to Cloud Run (free tier, zero-config scale-to-zero)
- [ ] Use GKE (Google Kubernetes Engine) — the managed K8s service
- [ ] Store images in Artifact Registry (GCP's image registry)
- [ ] Use GCS (Google Cloud Storage) — GCP's equivalent of S3

---

## 1. GCP Free Tier

| Service | Free Tier |
|---------|-----------|
| **Compute Engine** | 1 e2-micro instance/month (us-central1/us-west1/us-east1 only) |
| **Cloud Storage (GCS)** | 5 GB regional storage/month |
| **Cloud Run** | 2M requests/month, 360K GB-seconds compute/month |
| **Artifact Registry** | 0.5 GB storage/month |
| **Cloud Build** | 120 build-minutes/day |

> **Sign up:** https://cloud.google.com/free — $300 credit for 90 days + always-free tier.

---

## 2. Setup

```bash
# Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Initialize
gcloud init
# Follow prompts: select account, create/select project

# Set default project
gcloud config set project YOUR_PROJECT_ID

# Verify
gcloud auth list
gcloud config list
```

---

## 3. Core GCP Services

| GCP | AWS Equivalent | What it does |
|-----|---------------|-------------|
| **Compute Engine** | EC2 | Virtual machines |
| **GKE** | EKS | Managed Kubernetes |
| **Cloud Run** | App Runner / Fargate | Serverless containers |
| **Cloud Storage (GCS)** | S3 | Object storage |
| **Artifact Registry** | ECR | Container image registry |
| **Cloud SQL** | RDS | Managed databases |
| **Cloud Build** | CodeBuild | CI/CD service |
| **Cloud Pub/Sub** | SQS/SNS | Message queues |
| **Cloud Functions** | Lambda | Serverless functions |

---

## 4. Deploy to Cloud Run (Easiest Path)

Cloud Run is the fastest way to run containers on GCP. You push an image — it handles scaling, load balancing, TLS, a free domain.

```bash
# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# Create a container registry
gcloud artifacts repositories create devops-repo \
  --repository-format=docker \
  --location=us-central1

# Configure Docker to push to Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev

# Build and push the image
PROJECT_ID=$(gcloud config get-value project)
IMAGE=us-central1-docker.pkg.dev/$PROJECT_ID/devops-repo/devops-app

docker build -t $IMAGE:latest ./app
docker push $IMAGE:latest

# Deploy to Cloud Run
gcloud run deploy devops-app \
  --image $IMAGE:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \   # public access
  --port 3000 \
  --memory 256Mi

# Get the URL
gcloud run services describe devops-app --region us-central1 --format='value(status.url)'
# https://devops-app-xxxxx-uc.a.run.app  ← your live app!

# Update (just push new image and re-deploy)
docker build -t $IMAGE:v0.2.0 ./app
docker push $IMAGE:v0.2.0
gcloud run deploy devops-app --image $IMAGE:v0.2.0 --region us-central1

# Delete when done
gcloud run services delete devops-app --region us-central1
```

**Cloud Run in GitHub Actions:**
```yaml
- name: Deploy to Cloud Run
  uses: google-github-actions/deploy-cloudrun@v2
  with:
    service: devops-app
    region: us-central1
    image: us-central1-docker.pkg.dev/${{ env.PROJECT_ID }}/devops-repo/devops-app:${{ github.sha }}
```

---

## 5. GKE — Managed Kubernetes

```bash
# Enable GKE API
gcloud services enable container.googleapis.com

# Create an Autopilot cluster (fully managed, pay per Pod, not per node)
gcloud container clusters create-auto devops-cluster \
  --region us-central1

# Get credentials (updates ~/.kube/config)
gcloud container clusters get-credentials devops-cluster --region us-central1

# Verify
kubectl get nodes

# Deploy (same K8s commands from Module 05!)
kubectl apply -f k8s/

# Delete cluster when done (to avoid charges)
gcloud container clusters delete devops-cluster --region us-central1
```

---

## 6. GCS (Google Cloud Storage)

```bash
# Create a bucket
gsutil mb -p $PROJECT_ID -l us-central1 gs://devops-essentials-YOUR_NAME/

# Upload files
gsutil cp app/public/favicon.ico gs://devops-essentials-YOUR_NAME/

# Sync directory
gsutil -m rsync -r app/public/ gs://devops-essentials-YOUR_NAME/public/

# Make a file public
gsutil acl ch -u AllUsers:R gs://devops-essentials-YOUR_NAME/public/favicon.ico

# List bucket contents
gsutil ls gs://devops-essentials-YOUR_NAME/

# Delete bucket
gsutil rm -r gs://devops-essentials-YOUR_NAME/
```

---

## 7. Terraform with GCP

```hcl
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = "us-central1"
}

variable "project_id" {}

# GCS bucket for storing static assets
resource "google_storage_bucket" "app_assets" {
  name     = "${var.project_id}-devops-assets"
  location = "US"

  uniform_bucket_level_access = true

  lifecycle_rule {
    condition { age = 30 }
    action    { type = "Delete" }
  }
}

# Cloud Run service
resource "google_cloud_run_v2_service" "app" {
  name     = "devops-app"
  location = "us-central1"

  template {
    containers {
      image = "us-central1-docker.pkg.dev/${var.project_id}/devops-repo/devops-app:latest"

      resources {
        limits = {
          cpu    = "1"
          memory = "256Mi"
        }
      }
    }
  }
}

# Make Cloud Run service publicly accessible
resource "google_cloud_run_service_iam_member" "public" {
  service  = google_cloud_run_v2_service.app.name
  location = google_cloud_run_v2_service.app.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}
```

---

## Checklist

- [ ] GCP account set up, `gcloud` CLI configured
- [ ] I know the GCP equivalents of core AWS services
- [ ] My app is deployed to Cloud Run and accessible via a public URL
- [ ] I've pushed an image to Artifact Registry
- [ ] I've used GCS to store files
- [ ] I've provisioned GCP resources with Terraform
- [ ] I've cleaned up all resources when done

---

**Next:** [Module 10b — Cloud (Azure)](../10b-cloud-azure/README.md)
