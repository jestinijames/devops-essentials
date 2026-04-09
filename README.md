# DevOps Essentials — A Frontend Engineer's Field Guide

> You already know how to build for the browser. Now learn how to **ship, run, and scale it in the real world.**

This repo is your hands-on DevOps curriculum. Every module uses the Next.js app in `/app` as the thing you're deploying and operating. You'll build real artifacts in each module — Dockerfiles, pipelines, Terraform configs, Kubernetes manifests — not fake exercises.

---

## How this works

Each module has:

- **Concept** — plain-English explanation of what and why
- **Mental Model** — an analogy that maps to something you already know as a frontend dev
- **Hands-on exercises** — you write the code/config, not me
- **Solutions** — reference implementations you can check against
- **What to look up** — curated docs so you don't get lost on Google

**Do not skip ahead.** Each module builds on the last.

---

## The App

`/app` is a Next.js app with:

| Route         | What it does                                        |
| ------------- | --------------------------------------------------- |
| `/`           | Dashboard showing your learning checklist           |
| `/api/health` | Health check endpoint (used by Docker & Kubernetes) |
| `/api/tasks`  | Tasks API (split into a microservice later)         |

Run it locally first so you know what you're working with:

```bash
cd app
npm install
npm run dev
```

Visit `http://localhost:3000` and `http://localhost:3000/api/health`.

---

## Modules

| #                                           | Module                     | What you build                                | Key tools              |
| ------------------------------------------- | -------------------------- | --------------------------------------------- | ---------------------- |
| [01](./modules/01-docker/README.md)         | **Docker**                 | Containerize the Next.js app                  | Docker, Docker Compose |
| [02](./modules/02-github-actions/README.md) | **GitHub Actions & CI/CD** | Automated lint → test → build → push pipeline | GitHub Actions         |
| [03](./modules/03-terraform/README.md)      | **Terraform**              | Provision cloud infra with code               | Terraform, HCL         |
| [04](./modules/04-kubernetes/README.md)     | **Kubernetes**             | Deploy & scale containers                     | kubectl, minikube      |
| [05](./modules/05-microservices/README.md)  | **Microservices**          | Break the app into independent services       | Docker Compose, K8s    |
| [06](./modules/06-cloud/README.md)          | **Cloud**                  | Deploy to GCP / AWS / Azure                   | gcloud, aws cli, az    |

---

## Prerequisites

Before you start, make sure you have these installed:

```bash
# Check what you have
docker --version          # Module 01+
git --version             # Module 02+
terraform --version       # Module 03+
kubectl version --client  # Module 04+
minikube version          # Module 04+
```

Install what's missing:

- **Docker Desktop** → https://www.docker.com/products/docker-desktop
- **Terraform** → https://developer.hashicorp.com/terraform/install
- **kubectl** → https://kubernetes.io/docs/tasks/tools/
- **minikube** → https://minikube.sigs.k8s.io/docs/start/

---

## Ground rules

1. **Type everything yourself.** Don't copy-paste solutions until you've tried.
2. **Break things on purpose.** That's how you learn what the error messages mean.
3. **Read the official docs.** Each module links you to the relevant pages.
4. **One module at a time.** Seriously.

---

## What "DevOps" actually means (for a frontend engineer)

As a frontend dev, your mental model is probably:

> "I write code → I push to GitHub → _someone else_ makes it run."

DevOps is about **owning the full path from code to running software**:

```
You write code
    → It gets tested automatically (CI)
    → It gets packaged into a container (Docker)
    → Infrastructure is provisioned (Terraform)
    → The container is deployed (Kubernetes / Cloud)
    → It runs reliably at scale (Kubernetes)
    → The whole thing repeats on every push (CD)
```

You're going to build every step of that pipeline yourself. Let's go.
# devops-esssentials
