# Module 03 — GitHub Actions & CI/CD

> **CI/CD is the heartbeat of DevOps.** Every code change automatically tested, built, and delivered to production — without manual intervention.

---

## Learning Objectives

By the end of this module you will:
- [ ] Understand CI vs CD and why both matter
- [ ] Read and write GitHub Actions YAML workflows
- [ ] Build a CI pipeline that lints, tests, and builds on every pull request
- [ ] Build a CD pipeline that builds a Docker image and pushes to a registry
- [ ] Use GitHub Secrets to store sensitive values
- [ ] Understand environments, approvals, and deployment gates
- [ ] Know when to use Jenkins instead of GitHub Actions

---

## 1. What is CI/CD?

```
Developer               CI Pipeline              CD Pipeline          Production
──────────             ──────────────            ─────────────        ──────────
 push code      →     run tests         →       build image    →      deploy
 open PR        →     lint code         →       push to registry →    health check
                →     security scan     →       update staging  →     notify team
                →     build check       →       wait for approval →   rollback if bad
                       ↑                          ↑
                 Continuous Integration     Continuous Delivery/Deployment
                 (every push)              (every merge to main)
```

**CI (Continuous Integration):** The practice of merging code frequently and automatically verifying that it doesn't break things. Every commit → automated checks.

**CD (Continuous Delivery):** Automating the release process so that code is always in a deployable state. The final push to production may still require human approval.

**Continuous Deployment:** CD, but the final push to production is also automated. Every green build goes to production automatically.

---

## 2. GitHub Actions Concepts

| Concept | What it is |
|---------|-----------|
| **Workflow** | A YAML file that defines an automated process |
| **Event (trigger)** | What starts the workflow (`push`, `pull_request`, `schedule`, etc.) |
| **Job** | A group of steps that run on the same machine |
| **Step** | A single task (run a command, or use an Action) |
| **Action** | A reusable unit of work from the marketplace |
| **Runner** | The machine that executes the job (GitHub-hosted or self-hosted) |
| **Secret** | Encrypted variable stored in GitHub settings |
| **Artifact** | Files that persist after a job ends (test reports, build outputs) |

### Workflow structure:
```yaml
name: My Workflow           # Display name in GitHub UI

on:                         # Triggers
  push:
    branches: [main]
  pull_request:

jobs:
  my-job:                   # Job ID (can have many jobs)
    runs-on: ubuntu-latest  # Runner
    steps:
      - name: Checkout code
        uses: actions/checkout@v4   # An Action from the marketplace

      - name: Run a command
        run: echo "Hello from CI"

      - name: Multi-line command
        run: |
          echo "Line 1"
          echo "Line 2"
          npm install
```

---

## 3. Build a CI Pipeline

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

# Cancel previous runs on the same branch if a new one starts
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  # ─── Job 1: Type checking ───────────────────────────────────────
  typecheck:
    name: TypeScript Check
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: app

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"
          cache-dependency-path: app/package-lock.json

      - name: Install dependencies
        run: npm ci

      - name: Run TypeScript compiler check
        run: npx tsc --noEmit

  # ─── Job 2: Build ───────────────────────────────────────────────
  build:
    name: Build Next.js
    runs-on: ubuntu-latest
    needs: [typecheck]   # Only runs if typecheck passes
    defaults:
      run:
        working-directory: app

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"
          cache-dependency-path: app/package-lock.json

      - name: Install dependencies
        run: npm ci

      - name: Build application
        run: npm run build

      - name: Upload build artifact
        uses: actions/upload-artifact@v4
        with:
          name: nextjs-build
          path: app/.next/
          retention-days: 1
```

### Key things to notice:
- `needs: [typecheck]` — jobs run in parallel by default; `needs` makes them sequential
- `cache: "pnpm"` — caches `node_modules` between runs (speeds up CI by ~2 minutes)
- `working-directory: app` — since our Next.js app is in `app/`, all commands run there
- `concurrency` — stops wasting CI minutes on outdated pushes

---

## 4. Build a Docker Image in CI

Add a new job to `.github/workflows/ci.yml`, or create a separate workflow:

Create `.github/workflows/docker.yml`:

```yaml
name: Build & Push Docker Image

on:
  push:
    branches: [main]     # Only on main (not PRs)
  workflow_dispatch:     # Allow manual trigger from GitHub UI

jobs:
  docker:
    name: Build and push image
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      # Generate image tags based on Git metadata
      - name: Extract metadata for Docker
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ secrets.DOCKERHUB_USERNAME }}/devops-app
          tags: |
            type=sha,prefix=sha-     # sha-abc1234
            type=ref,event=branch    # main
            type=semver,pattern={{version}}  # v1.2.3 (from git tag)

      # Login to Docker Hub using secrets
      - name: Log in to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      # Enable advanced Docker build features (BuildKit)
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      # Build and push the image
      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: ./app
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha        # Use GitHub Actions cache for Docker layers
          cache-to: type=gha,mode=max
```

---

## 5. GitHub Secrets

**Never put passwords, API keys, or tokens directly in YAML files.** GitHub Secrets encrypts them.

### Add Docker Hub secrets:
1. Go to your repo on GitHub
2. **Settings → Secrets and variables → Actions → New repository secret**
3. Add `DOCKERHUB_USERNAME` — your Docker Hub username
4. Add `DOCKERHUB_TOKEN` — get this from Docker Hub: **Account Settings → Security → Access Tokens**

Access in workflows:
```yaml
username: ${{ secrets.DOCKERHUB_USERNAME }}
password: ${{ secrets.DOCKERHUB_TOKEN }}
```

**Secrets are never exposed in logs.** GitHub masks them automatically.

### Environment variables vs Secrets:
```yaml
# Environment variables (not secret, visible in logs — ok for non-sensitive config)
env:
  NODE_ENV: production
  APP_PORT: "3000"

# Secrets (encrypted, never shown in logs)
env:
  DATABASE_PASSWORD: ${{ secrets.DATABASE_PASSWORD }}
```

---

## 6. Workflow Triggers — The Full Picture

```yaml
on:
  # Run on push to specific branches
  push:
    branches: [main, "release/*"]
    paths: ["app/**", "docker-compose.yml"]  # Only if these files changed

  # Run on pull requests targeting main
  pull_request:
    branches: [main]
    types: [opened, synchronize, reopened]

  # Run on a schedule (cron syntax)
  schedule:
    - cron: "0 9 * * 1"   # Every Monday at 9am UTC

  # Run manually from GitHub UI
  workflow_dispatch:
    inputs:
      environment:
        description: "Deploy to which environment?"
        required: true
        default: "staging"
        type: choice
        options: [staging, production]

  # Run when another workflow finishes
  workflow_run:
    workflows: ["CI"]
    types: [completed]
```

---

## 7. Environments and Deployment Gates

GitHub Environments let you add **manual approval requirements** for production deployments.

1. Go to **Settings → Environments → New environment**
2. Create `staging` and `production`
3. For `production`, add a **Required reviewer** (yourself)

```yaml
jobs:
  deploy-staging:
    environment: staging   # No approval needed
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying to staging..."

  deploy-production:
    environment: production  # Requires approval from reviewers
    needs: [deploy-staging]
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying to production..."
```

Now every time the workflow tries to deploy to production, it **pauses and waits for a human to approve** in the GitHub Actions UI. This is your deployment gate.

---

## 8. Job Matrix — Run the Same Job for Multiple Configs

```yaml
jobs:
  test:
    strategy:
      matrix:
        node-version: [18, 20, 22]
        os: [ubuntu-latest, windows-latest]
    
    runs-on: ${{ matrix.os }}
    
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with:
          version: latest
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: "pnpm"
      - run: pnpm install --frozen-lockfile
      - run: pnpm test
```

This creates 6 parallel jobs (3 Node versions × 2 OSes) automatically.

---

## 9. Jenkins vs GitHub Actions

| | GitHub Actions | Jenkins |
|--|---------------|---------|
| **Hosting** | GitHub-managed | Self-hosted (your server) |
| **Config** | YAML in your repo | Jenkinsfile (Groovy) |
| **Cost** | Free for public repos, 2000 min/month for private | Free (but you pay for the server) |
| **Setup** | Zero — built into GitHub | Heavy — need to install and maintain Jenkins |
| **Plugins** | Actions marketplace | 1800+ plugins |
| **Best for** | Most teams, especially GitHub-native | Large enterprises, complex pipelines, air-gapped environments |

**For this curriculum, we use GitHub Actions.** Jenkins would add unnecessary complexity at this stage. If you want to explore Jenkins, see the `extras/jenkins/` folder.

---

## 10. Full CI/CD Flow We're Building Toward

```
Developer pushes code
         │
         ▼
CI Workflow (on every push/PR)
  ├── TypeScript check
  ├── Build Next.js
  └── Security scan (future: trivy, snyk)
         │ (all pass)
         ▼
Docker Workflow (on merge to main)
  ├── Build production Docker image
  ├── Run health check script (from Module 01!)
  └── Push to Docker Hub / GitHub Container Registry
         │
         ▼
CD Workflow (after image is pushed)
  ├── Deploy to staging
  ├── Run smoke tests
  └── [Manual approval] → Deploy to production
         │
         ▼
Kubernetes updates the deployment (Module 05 + Module 08 GitOps)
```

---

## 11. Exercises

### Exercise 1: Push the CI Workflow
1. Create `.github/workflows/ci.yml` with the content from Section 3
2. Push to your GitHub repo
3. Go to the **Actions** tab and watch your first workflow run
4. Intentionally break TypeScript (`const x: number = "oops"`) and see the CI fail
5. Fix it, push again, and see it pass

### Exercise 2: Add Docker Secrets and Push a Docker Image
1. Create a Docker Hub access token
2. Add `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` to your repo secrets
3. Create `.github/workflows/docker.yml` from Section 4
4. Push to `main` and watch the Docker image get built and pushed to Docker Hub

### Exercise 3: Add a Health Check Step
Update the docker workflow to run your Python health check after building:
```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: "3.11"

- name: Install health check dependencies
  run: pip install requests

- name: Verify image starts correctly
  run: |
    docker run -d -p 3000:3000 --name test-app ${{ secrets.DOCKERHUB_USERNAME }}/devops-app:latest
    python scripts/health_check.py --url http://localhost:3000 --retries 10 --delay 2
    docker stop test-app
```

---

## Checklist

- [ ] I understand the difference between CI and CD
- [ ] I can read a GitHub Actions YAML workflow and explain every line
- [ ] My CI workflow runs on every pull request and checks the build
- [ ] My Docker workflow builds and pushes an image to Docker Hub
- [ ] Secrets are stored in GitHub Settings, not in YAML files
- [ ] I understand `needs`, `concurrency`, and `working-directory`
- [ ] I've watched at least one workflow fail and fixed it

---

## Further Reading

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Actions Marketplace](https://github.com/marketplace?type=actions)
- [GitHub Actions: Caching Dependencies](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows)

---

**Next:** [Module 04 — Terraform](../04-terraform/README.md)
