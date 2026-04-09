# Module 03 — Terraform

> **Goal:** Provision real cloud infrastructure by writing code — not clicking buttons in a dashboard.

---

## Why Terraform? (The real problem it solves)

Imagine you set up a server by clicking around the AWS console. Now:

- You need to replicate it for staging — click everything again
- A teammate joins — click everything again and try to remember what you did
- Something goes wrong and you need to rebuild from scratch — click everything again
- You want to review what changed between last week and this week — you can't

**Terraform** solves this with **Infrastructure as Code (IaC):** your entire cloud setup is defined in text files you can version-control, review, reuse, and automate.

Think of it like this:

> As a frontend dev, you use a `package.json` to declare dependencies — everyone on the team runs `npm install` and gets the exact same setup. Terraform is `package.json` for cloud infrastructure. You declare what you want, and Terraform figures out how to make it real.

---

## Key Concepts

### Providers

Terraform speaks to cloud providers via **providers** — plugins that know the API for AWS, GCP, Azure, etc.

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}
```

### Resources

A **resource** is the thing you want to create — an S3 bucket, a VM, a database.

```hcl
resource "aws_s3_bucket" "my_bucket" {
  bucket = "my-unique-bucket-name-2026"
}
```

The format is always: `resource "<provider>_<type>" "<local_name>"`

### Plan → Apply workflow

```
terraform init    # Download providers (like npm install)
terraform plan    # Preview what will change (like a git diff)
terraform apply   # Actually make the changes
terraform destroy # Tear everything down
```

**Always run `terraform plan` before `terraform apply`.** Read it carefully. It shows you exactly what will be created, modified, or destroyed.

### State

Terraform keeps track of what it has created in a **state file** (`terraform.tfstate`). This is how it knows what exists vs what needs to change.

**Never delete or manually edit the state file.** In a team, store it remotely (in an S3 bucket or Terraform Cloud) so everyone shares the same state.

### Variables and outputs

```hcl
# variables.tf — inputs
variable "environment" {
  type    = string
  default = "staging"
}

# main.tf — use variables with var.
resource "aws_s3_bucket" "bucket" {
  bucket = "myapp-${var.environment}-assets"
}

# outputs.tf — expose values after apply
output "bucket_name" {
  value = aws_s3_bucket.bucket.id
}
```

### HCL Syntax cheatsheet

```hcl
# String interpolation
name = "app-${var.environment}"

# Reference another resource's attribute
arn = aws_s3_bucket.bucket.arn

# Lists and maps
availability_zones = ["us-east-1a", "us-east-1b"]
tags = {
  Environment = "staging"
  Team        = "frontend"
}

# Locals (like const inside a module)
locals {
  prefix = "devops-essentials-${var.environment}"
}
```

---

## Setup

Install Terraform:

```bash
brew install terraform   # macOS
terraform -version       # verify
```

For these exercises, **you'll use a free Terraform Cloud workspace as the backend** (so you don't need real AWS/GCP credentials yet). Sign up at https://app.terraform.io/

---

## Exercise 1 — Local state, fake resources

Before touching real cloud, practice with Terraform's built-in **`local_file` resource** — it creates files on your machine.

Create `modules/03-terraform/exercises/01-local/`:

```
Your tasks:
1. Create main.tf with:
   - A local_file resource that creates a file called "output.txt"
   - The file should contain "Hello from Terraform!"
2. Create variables.tf with a variable for the filename (with a default)
3. Create outputs.tf that outputs the filename

Run:
  terraform init
  terraform plan
  terraform apply
  cat output.txt         # should print "Hello from Terraform!"
  terraform destroy
```

**Solution:** `modules/03-terraform/solutions/01-local/`

---

## Exercise 2 — Provision a real S3 bucket on AWS (free tier)

Now use a real provider. An S3 bucket stays well within the AWS free tier.

> You'll need an AWS account and to run `aws configure` with your credentials.
> Free tier: 5GB storage, 20,000 GET requests/month.

Create `modules/03-terraform/exercises/02-s3/`:

```
Your tasks:
1. Configure the AWS provider (region: us-east-1)
2. Create an S3 bucket resource with:
   - A unique name (use your name + random suffix)
   - A tag: Project = "devops-essentials"
3. Output the bucket name and ARN

Run the full terraform init → plan → apply cycle.
Verify the bucket exists in the AWS console.
Then run terraform destroy.
```

**Solution:** `modules/03-terraform/solutions/02-s3/`

---

## Exercise 3 — Modules (reusable infrastructure)

Terraform **modules** are reusable bundles of resources — like React components for infrastructure.

Create a module that provisions a "static site" setup:

- An S3 bucket configured for static website hosting
- (Bonus) A CloudFront distribution in front of it

Use the module from a root `main.tf`:

```hcl
module "static_site" {
  source      = "./modules/static-site"
  bucket_name = "my-devops-static-site"
  environment = "staging"
}
```

**Solution:** `modules/03-terraform/solutions/03-modules/`

---

## Exercise 4 — Remote state with Terraform Cloud

Right now your state file is local. If you lose it, Terraform loses track of everything it created. And you can't collaborate with a team.

Set up **Terraform Cloud** as your state backend:

```hcl
terraform {
  cloud {
    organization = "your-org-name"

    workspaces {
      name = "devops-essentials"
    }
  }
}
```

Then run `terraform login` and `terraform init` to migrate state.

This also unlocks running `terraform plan/apply` in GitHub Actions — which you'll wire up at the end of this exercise.

**Solution:** `modules/03-terraform/solutions/04-remote-state/`

---

## Real-world patterns to know

**1. Don't hardcode regions — use variables:**

```hcl
variable "aws_region" {
  default = "us-east-1"
}
provider "aws" {
  region = var.aws_region
}
```

**2. Separate environments with workspaces:**

```bash
terraform workspace new staging
terraform workspace new production
terraform workspace select staging
terraform apply
```

**3. Lock your provider versions:**

```hcl
required_providers {
  aws = {
    source  = "hashicorp/aws"
    version = "= 5.31.0"   # exact version — no surprises
  }
}
```

**4. Add `.gitignore` entries for Terraform:**

```
.terraform/
*.tfstate
*.tfstate.backup
.terraform.lock.hcl  # commit this one — it's like package-lock.json
```

---

## What to look up

- [Terraform getting started (AWS)](https://developer.hashicorp.com/terraform/tutorials/aws-get-started)
- [Terraform language reference](https://developer.hashicorp.com/terraform/language)
- [AWS provider docs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Terraform Cloud](https://app.terraform.io/)
- [Terraform modules](https://developer.hashicorp.com/terraform/language/modules)

---

## Checkpoint

Before moving to Module 04, verify:

- [ ] `terraform plan` correctly shows what will be created before you apply
- [ ] You've run `terraform apply` against real AWS (even just an S3 bucket)
- [ ] You've run `terraform destroy` and verified the resource is gone
- [ ] You understand what the state file is and why you shouldn't delete it
- [ ] You can explain the difference between a resource and a module

---

## What's next?

In **Module 04**, you'll take the Docker image from Module 01 and deploy it to **Kubernetes** locally — which is exactly how it would run in a cloud cluster provisioned by Terraform.

→ [Module 04 — Kubernetes](../04-kubernetes/README.md)
