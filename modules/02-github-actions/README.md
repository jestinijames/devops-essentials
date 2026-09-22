# Module 02 — GitHub Actions & CI/CD

> **Goal:** Every time you push code, automatically run linting, build the Docker image, and push it to a container registry. No manual steps.

---

## Why CI/CD? (The real problem it solves)

Right now your workflow is:

1. Write code
2. Manually run `pnpm run build` to check it compiles
3. Manually run `docker build` to make the image
4. Manually push it somewhere
5. Manually deploy it

That's error-prone, slow, and doesn't scale when a team is involved. **CI/CD automates the boring, repeatable stuff so you can focus on shipping.**

**CI (Continuous Integration):** Every time someone pushes code, automatically verify it's correct — lint it, test it, build it.

**CD (Continuous Delivery/Deployment):** Automatically ship it — package it, push it to a registry, deploy it.

Think of it like this:

> As a frontend dev, you know ESLint runs automatically in your editor. CI/CD is ESLint (and tests, and builds, and deployments) running automatically in the cloud on every push.

---

## Key Concepts

### GitHub Actions vocabulary

| Term              | What it means                                                               |
| ----------------- | --------------------------------------------------------------------------- |
| **Workflow**      | A YAML file that defines automated work                                     |
| **Trigger (on:)** | What starts the workflow (push, PR, schedule, etc.)                         |
| **Job**           | A group of steps that run on the same machine                               |
| **Step**          | A single command or action within a job                                     |
| **Action**        | A reusable unit of work (like an npm package, but for CI)                   |
| **Runner**        | The virtual machine that runs your job                                      |
| **Secret**        | An encrypted environment variable (for API keys, passwords)                 |
| **Artifact**      | A file produced by a workflow that can be downloaded or passed between jobs |

### Workflow file anatomy

```yaml
name: CI # Display name in GitHub UI

on: # What triggers this workflow
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build: # Job name (you choose this)
    runs-on: ubuntu-latest # The runner environment

    steps:
      - uses: actions/checkout@v4 # Check out the repo code

      - uses: actions/setup-node@v4 # Set up Node.js
        with:
          node-version: "22"

      - name: Install dependencies
        run: pnpm install --frozen-lockfile # Single-line shell command

      - name: Lint
        run: pnpm run lint
```

### Job dependencies

By default, jobs run in parallel. Use `needs:` to create a dependency:

```yaml
jobs:
  lint:
    ...
  build:
    needs: lint   # Only run this if "lint" passes
    ...
  deploy:
    needs: build  # Only run this if "build" passes
    ...
```

### Secrets

Never put passwords, tokens, or API keys in your YAML. Store them in:
`GitHub → Repository → Settings → Secrets and variables → Actions`

Then reference them in YAML as `${{ secrets.MY_SECRET }}`.

---

## Exercise 1 — Your first workflow (lint + build check)

Create `.github/workflows/ci.yml`:

```
Your tasks:
1. Trigger on push to main AND on pull requests to main
2. Job called "lint-and-build" running on ubuntu-latest
3. Steps:
   a. Check out the code
   b. Set up Node.js 22
   c. Cache node_modules (use actions/cache@v4 with the npm cache key)
  d. Run: cd app && pnpm install --frozen-lockfile
  e. Run: cd app && pnpm run lint
  f. Run: cd app && pnpm run build
```

Push your branch and open a PR to `main`. Watch the Actions tab in GitHub.

**Solution:** `modules/02-github-actions/solutions/ci.yml`

---

## Exercise 2 — Build and push a Docker image

When a push lands on `main`, we want to:

1. Build the Docker image
2. Push it to **GitHub Container Registry (GHCR)** — it's free and built into GitHub

Create `.github/workflows/docker.yml`:

```
Your tasks:
1. Trigger ONLY on push to main
2. Job called "build-and-push" with permissions: packages: write, contents: read
3. Steps:
   a. Checkout the code
   b. Log in to GHCR using:
      - registry: ghcr.io
      - username: ${{ github.actor }}
      - password: ${{ secrets.GITHUB_TOKEN }}   ← this one is automatic, no setup needed
   c. Build and push the image using docker/build-push-action@v5
      - context: ./app
      - push: true
      - tags: ghcr.io/<your-github-username>/devops-essentials:latest
```

Look up:

- `docker/login-action` — https://github.com/docker/login-action
- `docker/build-push-action` — https://github.com/docker/build-push-action

**Solution:** `modules/02-github-actions/solutions/docker.yml`

---

## Exercise 3 — Add image tagging by git SHA

Using `:latest` as a tag is fine for learning but bad in production — you lose track of which exact code is running.

A better pattern: tag every image with the git commit SHA so you can always trace a running container back to exact code.

Modify your docker workflow to tag the image as **both** `latest` AND the commit SHA:

```
ghcr.io/your-username/devops-essentials:latest
ghcr.io/your-username/devops-essentials:abc1234   ← git SHA (first 7 chars)
```

Hint: `${{ github.sha }}` gives you the full SHA. Use `docker/metadata-action` to generate tags automatically:

- https://github.com/docker/metadata-action

**Solution:** `modules/02-github-actions/solutions/docker-with-sha.yml`

---

## Exercise 4 — Branch protection via status checks

Now that your CI runs on every PR, enforce it:

1. Go to GitHub → Repository → Settings → Branches
2. Add a branch protection rule for `main`
3. Enable "Require status checks to pass before merging"
4. Select your `lint-and-build` job as a required check

Now no one (including you) can merge broken code to `main`.

This isn't a code exercise — it's a GitHub configuration exercise. But it's important to know.

---

## Key GitHub Actions reference

```yaml
# Common triggers
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: "0 9 * * 1"   # Every Monday at 9am UTC

# Useful built-in context variables
${{ github.sha }}          # Full commit SHA
${{ github.ref }}          # Branch name (refs/heads/main)
${{ github.actor }}        # Username of whoever triggered the run
${{ github.repository }}   # owner/repo
${{ secrets.MY_SECRET }}   # Access a secret

# Conditionals
if: github.ref == 'refs/heads/main'   # Only run on main branch
if: failure()                          # Only run if previous step failed (for notifications)
```

---

## What to look up

- [GitHub Actions quickstart](https://docs.github.com/en/actions/quickstart)
- [Workflow syntax reference](https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions)
- [GitHub Actions marketplace](https://github.com/marketplace?type=actions)
- [GHCR docs](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Caching dependencies](https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/caching-dependencies-to-speed-up-workflows)

---

## Checkpoint

Before moving to Module 03, verify:

- [ ] Pushing to a branch triggers the CI workflow and you can see it in the Actions tab
- [ ] A lint failure (try introducing one intentionally) makes the CI workflow fail
- [ ] Merging to `main` triggers the Docker build and the image appears in your GitHub Packages
- [ ] You understand the difference between a Job and a Step
- [ ] You know how to store and use a Secret

---

## What's next?

In **Module 03**, you'll use Terraform to write code that provisions the cloud infrastructure where this Docker image will eventually run — instead of clicking around GCP/AWS/Azure dashboards.

→ [Module 03 — Terraform](../03-terraform/README.md)
