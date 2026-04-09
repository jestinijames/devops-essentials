# Module 10b — Cloud: Azure (Free Tier)

> **Azure** is Microsoft's cloud. It's dominant in enterprise environments, especially companies already using Microsoft 365, Active Directory, and .NET. Azure Container Apps and AKS (Azure Kubernetes Service) are excellent.

---

## Learning Objectives

- [ ] Set up an Azure account and configure the Azure CLI
- [ ] Understand core Azure services
- [ ] Deploy a Docker container to Azure Container Apps (free tier)
- [ ] Use ACR (Azure Container Registry) to store images
- [ ] Provision Azure resources with Terraform

---

## 1. Azure Free Tier

| Service | Free Tier |
|---------|-----------|
| **Azure Container Apps** | 180,000 vCPU-seconds/month + 360,000 GB-seconds/month |
| **Azure Container Registry** | Not free, but ~$5/month on Basic tier |
| **AKS** | Free cluster management (pay for VMs) |
| **Azure Blob Storage** | 5 GB LRS storage/month (12 months) |
| **App Service** | 1 F1 (free) app service plan |

> **Sign up:** https://azure.microsoft.com/free/ — $200 credit for 30 days + always-free services.

---

## 2. Setup

```bash
# Install Azure CLI
# Windows: winget install Microsoft.AzureCLI
# Mac: brew install azure-cli

az --version

# Login
az login    # Opens browser for auth

# Set subscription (if you have multiple)
az account list --output table
az account set --subscription "YOUR_SUBSCRIPTION_ID"

# Verify
az account show
```

---

## 3. Core Azure Services

| Azure | AWS | GCP | What it does |
|-------|-----|-----|-------------|
| **Azure VM** | EC2 | Compute Engine | Virtual machines |
| **AKS** | EKS | GKE | Managed Kubernetes |
| **Container Apps** | App Runner | Cloud Run | Serverless containers |
| **Azure Blob Storage** | S3 | GCS | Object storage |
| **ACR** | ECR | Artifact Registry | Container registry |
| **Azure SQL / PostgreSQL** | RDS | Cloud SQL | Managed databases |
| **Azure DevOps** | GitHub Actions + CodePipeline | Cloud Build | CI/CD + project management |
| **Service Bus** | SQS | Pub/Sub | Message queues |
| **Azure Functions** | Lambda | Cloud Functions | Serverless functions |

---

## 4. Deploy to Azure Container Apps

Container Apps is Azure's serverless container platform — similar to GCP Cloud Run.

```bash
# Install Container Apps extension
az extension add --name containerapp

# Create a resource group (logical container for your resources)
az group create --name devops-rg --location eastus

# Create a Container Apps environment
az containerapp env create \
  --name devops-env \
  --resource-group devops-rg \
  --location eastus

# Deploy directly from Docker Hub
az containerapp create \
  --name devops-app \
  --resource-group devops-rg \
  --environment devops-env \
  --image YOUR_DOCKERHUB_USERNAME/devops-app:latest \
  --target-port 3000 \
  --ingress external \   # Publicly accessible
  --min-replicas 0 \     # Scale to zero (cost-saving)
  --max-replicas 3

# Get public URL
az containerapp show \
  --name devops-app \
  --resource-group devops-rg \
  --query "properties.configuration.ingress.fqdn" \
  --output tsv

# Update the container image
az containerapp update \
  --name devops-app \
  --resource-group devops-rg \
  --image YOUR_DOCKERHUB_USERNAME/devops-app:v0.2.0

# Clean up (delete everything in the resource group)
az group delete --name devops-rg --yes
```

---

## 5. Azure Container Registry (ACR)

```bash
# Create registry
az acr create \
  --resource-group devops-rg \
  --name devopsacr$(date +%s) \    # must be globally unique
  --sku Basic

ACR_NAME=$(az acr list --resource-group devops-rg --query "[0].name" --output tsv)

# Login to ACR
az acr login --name $ACR_NAME

# Get the login server
ACR_SERVER=$(az acr show --name $ACR_NAME --query loginServer --output tsv)
# something like devopsacr1234.azurecr.io

# Build and push
docker build -t $ACR_SERVER/devops-app:latest ./app
docker push $ACR_SERVER/devops-app:latest

# Or use ACR to build (no Docker needed locally)
az acr build --registry $ACR_NAME --image devops-app:latest ./app
```

---

## 6. Terraform with Azure

```hcl
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

variable "location" {
  default = "East US"
}

resource "azurerm_resource_group" "main" {
  name     = "devops-essentials-rg"
  location = var.location
}

resource "azurerm_container_app_environment" "main" {
  name                = "devops-env"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
}

resource "azurerm_container_app" "app" {
  name                         = "devops-app"
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = azurerm_resource_group.main.name
  revision_mode                = "Single"

  template {
    container {
      name   = "devops-app"
      image  = "YOUR_USERNAME/devops-app:latest"
      cpu    = 0.25
      memory = "0.5Gi"
    }
  }

  ingress {
    external_enabled = true
    target_port      = 3000
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }
}

output "app_url" {
  value = "https://${azurerm_container_app.app.latest_revision_fqdn}"
}
```

---

## 7. Azure DevOps (Alternative to GitHub Actions)

Azure DevOps is Microsoft's all-in-one DevOps platform:
- **Azure Boards** — issue tracking (like Jira)
- **Azure Repos** — Git repositories (like GitHub)
- **Azure Pipelines** — CI/CD (like GitHub Actions)
- **Azure Artifacts** — package registry
- **Azure Test Plans** — test management

Pipeline YAML for Azure Pipelines:
```yaml
trigger:
  - main

pool:
  vmImage: ubuntu-latest

stages:
  - stage: Build
    jobs:
      - job: BuildAndPush
        steps:
          - task: Docker@2
            inputs:
              command: buildAndPush
              repository: devops-app
              dockerfile: app/Dockerfile
              containerRegistry: 'ACR Service Connection'
              tags: $(Build.BuildId)

  - stage: Deploy
    dependsOn: Build
    jobs:
      - deployment: DeployToContainerApps
        environment: production
        strategy:
          runOnce:
            deploy:
              steps:
                - task: AzureContainerApps@1
                  inputs:
                    appSourcePath: '$(Pipeline.Workspace)'
                    containerAppName: devops-app
                    resourceGroup: devops-rg
                    imageToDeploy: devopsacr.azurecr.io/devops-app:$(Build.BuildId)
```

---

## Checklist

- [ ] Azure account set up, `az` CLI configured
- [ ] I understand resource groups as an organizational unit
- [ ] My app is deployed to Container Apps with a public URL
- [ ] I've pushed a Docker image to ACR
- [ ] I've provisioned Azure resources with Terraform
- [ ] All resources deleted after practice (prevent charges)

---

**Next:** [Module 11 — Vagrant](../11-vagrant/README.md)
