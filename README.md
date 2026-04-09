# DevOps Essentials — From Frontend Dev to DevOps Engineer

> You already know how to build things. Now you'll learn how to **ship, scale, and operate** them.

This repo is your hands-on DevOps curriculum. Every concept you learn gets applied to one real project: a **Next.js web app** that lives in the `app/` folder. You'll containerize it, automate its deployment, provision its infrastructure, orchestrate it at scale, and monitor it in production — piece by piece, module by module.

---

## The Philosophy

DevOps is not a tool. It's a **culture and a set of practices** that bridges the gap between writing code and running it reliably in production. You'll hear this called:

- **DevOps** — Dev + Ops working together
- **SRE (Site Reliability Engineering)** — Google's take on DevOps
- **Platform Engineering** — building internal developer platforms

All of them share the same DNA: **automate everything, version control everything, measure everything**.

As a frontend developer, you already have a massive advantage: you understand the product, you can read and write code, you know how web apps work. The DevOps layer is just the infrastructure that wraps around that knowledge.

---

## The App We're Building With

```
app/         ← Next.js 15 (TypeScript + Tailwind CSS)
```

It's a simple web app, but it will grow with you. By the end of this curriculum:
- It runs in a **Docker container**
- It's deployed via a **GitHub Actions CI/CD pipeline**
- Its infrastructure is provisioned with **Terraform**
- It scales on **Kubernetes**
- It's monitored with **Prometheus + Grafana**

---

## Prerequisites (Install These First)

| Tool | Version | Why |
|------|---------|-----|
| [Node.js](https://nodejs.org) | 20+ | Run the Next.js app |
| [pnpm](https://pnpm.io/installation) | 9+ | Package manager (faster than npm, used throughout this repo) |
| [Git](https://git-scm.com) | 2.40+ | Version control everything |
| [Docker Desktop](https://www.docker.com/products/docker-desktop) | Latest | Containers (Module 02) |
| [VS Code](https://code.visualstudio.com) | Latest | Your editor |
| [Python](https://www.python.org/downloads/) | 3.11+ | Scripts & tooling (Module 01) |

> Install these before starting. Everything else (kubectl, terraform, etc.) is installed as part of its module.

### Verify your setup

Run this to confirm what you have installed before starting:

```bash
# Phase 1 — needed from day 1
node --version          # should be v20+
pnpm --version          # should be 9+
git --version           # should be 2.40+
python --version        # should be 3.11+

# Phase 2 — install Docker Desktop first
docker --version
docker compose version

# Phase 4 — installed during Module 04
terraform --version

# Phase 5 — installed during Module 05
kubectl version --client
minikube version        # or: kind version
helm version

# Phase 6 — installed during Module 07
ansible --version

# Phase 7 — installed during Module 08
argocd version

# Cloud CLIs — installed during Modules 09/10/10b
aws --version
gcloud --version
az --version
```

Don't worry if most of these say "not found" — that's expected. Each module tells you exactly when and how to install the tool it needs.

---

## Learning Roadmap

### Phase 1 — Foundations (Weeks 1–2)
| Module | Topic | What You'll Do |
|--------|-------|----------------|
| [00 — Git Foundations](./modules/00-git-foundations/README.md) | Branching, PRs, Hooks | Set up a proper Git workflow for the app |
| [01 — Python Basics](./modules/01-python-basics/README.md) | Python for DevOps | Write scripts to automate tasks |

### Phase 2 — Containerization (Weeks 3–4)
| Module | Topic | What You'll Do |
|--------|-------|----------------|
| [02 — Docker](./modules/02-docker/README.md) | Containers | Package the Next.js app into a Docker image |

### Phase 3 — CI/CD (Weeks 5–6)
| Module | Topic | What You'll Do |
|--------|-------|----------------|
| [03 — GitHub Actions](./modules/03-github-actions/README.md) | Pipelines | Auto-build & push images on every push |

### Phase 4 — Infrastructure as Code (Weeks 7–9)
| Module | Topic | What You'll Do |
|--------|-------|----------------|
| [04 — Terraform](./modules/04-terraform/README.md) | IaC | Provision servers and networking with code |
| [11 — Vagrant](./modules/11-vagrant/README.md) | Local VMs | Spin up local Linux VMs for practice |

### Phase 5 — Orchestration (Weeks 10–13)
| Module | Topic | What You'll Do |
|--------|-------|----------------|
| [05 — Kubernetes](./modules/05-kubernetes/README.md) | K8s | Deploy and scale the app in a cluster |

### Phase 6 — Architecture (Weeks 14–15)
| Module | Topic | What You'll Do |
|--------|-------|----------------|
| [06 — Microservices](./modules/06-microservices/README.md) | Service Design | Split the app into independent services |
| [07 — Ansible](./modules/07-ansible/README.md) | Config Management | Configure servers automatically |

### Phase 7 — GitOps & Cloud (Weeks 16–20)
| Module | Topic | What You'll Do |
|--------|-------|----------------|
| [08 — GitOps](./modules/08-gitops/README.md) | ArgoCD / FluxCD | Git as the source of truth for deployments |
| [09 — Cloud — AWS](./modules/09-cloud-aws/README.md) | AWS Free Tier | Deploy to EC2, S3, ECS |
| [10 — Cloud — GCP](./modules/10-cloud-gcp/README.md) | GCP Free Tier | Deploy to GKE, GCS, Cloud Run |
| [10b — Cloud — Azure](./modules/10b-cloud-azure/README.md) | Azure Free Tier | Deploy to AKS, Azure Container Apps |

### Phase 8 — Observability (Weeks 21–22)
| Module | Topic | What You'll Do |
|--------|-------|----------------|
| [12 — Monitoring](./modules/12-monitoring/README.md) | Prometheus + Grafana | See what your app is doing in real time |

### Phase 9 — Advanced (Unlocks after Phase 8)
> These modules go deeper. Work through them after you're comfortable with the foundations.

| Module | Topic | What You'll Do |
|--------|-------|----------------|
| [13 — DevSecOps](./modules/13-devsecops/README.md) | Security in the pipeline | Trivy, Semgrep, secret scanning, image signing |
| [14 — Advanced Kubernetes](./modules/14-advanced-kubernetes/README.md) | K8s at scale | RBAC, NetworkPolicies, Operators, HPA/VPA |
| [15 — Service Mesh](./modules/15-service-mesh/README.md) | Istio | mTLS, canary traffic, mesh observability |
| [16 — Chaos Engineering](./modules/16-chaos-engineering/README.md) | LitmusChaos | Break things on purpose, build resilience |
| [17 — Platform Engineering](./modules/17-platform-engineering/README.md) | Backstage + Crossplane | Build an internal developer platform |

---

## Keyword Decoder

DevOps comes with a lot of jargon. Here's a plain-English reference for every term you'll encounter in this curriculum:

| Keyword | What it is | Where you'll learn it |
|---------|-----------|----------------------|
| **Docker** | Packages your app into a portable container | Module 02 |
| **Kubernetes (K8s)** | Manages and scales containers across many machines | Module 05 |
| **GitHub Actions** | Automates build/test/deploy workflows in GitHub | Module 03 |
| **CI/CD** | _Continuous Integration / Continuous Delivery_ — the practice of shipping code automatically | Module 03 |
| **Terraform** | Write code to provision cloud infrastructure | Module 04 |
| **GitOps** | Using Git as the single source of truth for infrastructure AND deployments | Module 08 |
| **Ansible** | Automates configuring servers (install packages, set up files, etc.) | Module 07 |
| **Jenkins** | Alternative to GitHub Actions — a self-hosted CI/CD server | Covered in Module 03 as an alternative |
| **Vagrant** | Creates local Linux virtual machines for safe practice | Module 11 |
| **Microservices** | Architecture pattern — split one big app into small independent services | Module 06 |
| **Containerization** | Running apps in isolated containers (Docker) | Module 02 |
| **IaC** | _Infrastructure as Code_ — Terraform, Pulumi, CloudFormation | Module 04 |
| **SRE** | Site Reliability Engineering — applying software engineering to operations | Woven throughout |

---

## How to Use This Repo

1. **Work through modules in order** — each one builds on the last
2. **Apply every concept to the `app/`** — hands-on beats reading every time
3. **Commit your work** — treat this as a real project on your GitHub profile
4. **Break things on purpose** — that's how DevOps is learned
5. **Don't skip the exercises** — the checkboxes in each module README are your progress tracker

---

## Folder Structure

```
devops-essentials/
├── README.md                    ← You are here
├── app/                         ← Next.js application (pnpm)
│   ├── Dockerfile               ← Added in Module 02
│   └── ...
├── docker-compose.yml           ← Added in Module 02
├── .github/
│   └── workflows/
│       ├── ci.yml               ← Added in Module 03
│       └── docker.yml           ← Added in Module 03
├── terraform/                   ← Added in Module 04
├── k8s/                         ← Added in Module 05
├── ansible/                     ← Added in Module 07
├── scripts/
│   ├── health_check.py          ← Module 01 exercise
│   └── deploy_summary.py        ← Module 01 exercise
└── modules/
    ├── 00-git-foundations/      ← Phase 1
    ├── 01-python-basics/
    ├── 02-docker/               ← Phase 2
    ├── 03-github-actions/       ← Phase 3
    ├── 04-terraform/            ← Phase 4
    ├── 05-kubernetes/           ← Phase 5
    ├── 06-microservices/        ← Phase 6
    ├── 07-ansible/
    ├── 08-gitops/               ← Phase 7
    ├── 09-cloud-aws/
    ├── 10-cloud-gcp/
    ├── 10b-cloud-azure/
    ├── 11-vagrant/
    ├── 12-monitoring/           ← Phase 8
    ├── 13-devsecops/            ← Phase 9 (Advanced)
    ├── 14-advanced-kubernetes/
    ├── 15-service-mesh/
    ├── 16-chaos-engineering/
    └── 17-platform-engineering/
```

---

## Start Here

```bash
# 1. Run the app locally to confirm it works
cd app
pnpm install
pnpm dev
# Open http://localhost:3000
```

Then open [Module 00 — Git Foundations](./modules/00-git-foundations/README.md) and begin.

---

## Quick Reference Cheat Sheet

Commands you'll use constantly across all modules.

### Git
```bash
git status
git log --oneline --graph --all     # visual branch history
git checkout -b feat/my-feature
git add . && git commit -m "feat(app): my change"
git push origin HEAD
git stash / git stash pop
```

### pnpm
```bash
pnpm install             # install dependencies
pnpm dev                 # start dev server
pnpm build               # production build
pnpm add <package>       # add a dependency
pnpm add -D <package>    # add a dev dependency
pnpm remove <package>
```

### Docker
```bash
docker build -t my-app:latest .      # build image
docker run -d -p 3000:3000 my-app    # run container
docker ps                            # list running containers
docker ps -a                         # all containers including stopped
docker logs -f <container>          # follow logs
docker exec -it <container> sh      # shell inside container
docker stop <container>
docker rm <container>
docker images
docker rmi <image>
docker system prune -a               # clean up everything

docker compose up -d
docker compose down
docker compose logs -f
docker compose ps
```

### Kubernetes
```bash
kubectl get pods                     # list pods
kubectl get pods -w                  # watch pods
kubectl get deployments
kubectl get services
kubectl get all                      # everything
kubectl apply -f k8s/               # apply all manifests in folder
kubectl delete -f k8s/
kubectl logs -f deployment/my-app
kubectl exec -it <pod> -- sh
kubectl describe pod <pod>           # debug a failing pod
kubectl port-forward svc/my-svc 8080:80
kubectl scale deployment my-app --replicas=3
kubectl rollout status deployment/my-app
kubectl rollout undo deployment/my-app
kubectl rollout history deployment/my-app

# Helm
helm install <release> <chart>
helm upgrade <release> <chart>
helm uninstall <release>
helm list
```

### Terraform
```bash
terraform init           # download providers
terraform plan           # preview changes (safe, read-only)
terraform apply          # make changes
terraform apply -auto-approve   # skip confirmation (CI only)
terraform destroy        # tear everything down
terraform fmt            # format .tf files
terraform validate       # check config syntax
terraform output         # show output values
terraform state list     # list tracked resources
```

### Ansible
```bash
ansible all -i inventory/ -m ping                   # test connectivity
ansible-playbook -i inventory/ playbook.yml         # run a playbook
ansible-playbook -i inventory/ playbook.yml --check # dry run
ansible-playbook -i inventory/ playbook.yml -v      # verbose
ansible-vault create secrets.yml
ansible-vault edit secrets.yml
```

### Python (DevOps scripts)
```bash
python -m venv .venv          # create virtual environment
.venv\Scripts\activate        # activate (Windows)
source .venv/bin/activate     # activate (Mac/Linux)
pip install requests pyyaml   # install packages
python script.py --help
python script.py              # exit 0 = success, exit 1 = failure in CI
```
