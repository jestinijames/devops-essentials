# Module 00 — Git Foundations

> **You already use Git. Now you'll use it like a DevOps engineer.**

Most developers know `git add`, `git commit`, `git push`. DevOps engineers go deeper: branching strategies, protected branches, conventional commits, Git hooks, and using Git as a control plane for infrastructure.

---

## Learning Objectives

By the end of this module you will:
- [ ] Understand branching strategies (GitFlow vs Trunk-Based)
- [ ] Write commits that follow the Conventional Commits standard
- [ ] Protect your `main` branch and require PRs
- [ ] Use Git hooks to run checks before committing
- [ ] Understand `.gitignore` for DevOps files (secrets, state files)
- [ ] Tag releases using semantic versioning

---

## 1. Branching Strategies

There are two dominant models in DevOps:

### GitFlow
```
main          ──────────────────────────── (always production-ready)
develop       ───────────────────────────
feature/x      ───┘          (feature branches merge into develop)
release/1.0          ─────┘  (release branches merge into main + develop)
hotfix/y                   ──┘ (emergency fix goes straight to main)
```
**Good for:** teams with scheduled releases, complex projects.  
**Downside:** can slow down delivery.

### Trunk-Based Development (preferred in modern DevOps)
```
main     ──────────────────────────────── (everyone commits here frequently)
feat/x   ──┘  (short-lived branches, < 1 day)
```
**Good for:** CI/CD heavy teams, fast-moving projects.  
**Rule:** branches live for hours, not weeks.

**For this repo, we'll use trunk-based development.**

---

## 2. Conventional Commits

This is a standard for writing commit messages that is machine-readable. CI/CD pipelines use it to auto-generate changelogs and determine version bumps.

```
<type>(<scope>): <short description>

[optional body]

[optional footer]
```

**Types:**
| Type | When to use |
|------|------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `chore` | Maintenance (deps, config) |
| `docs` | Documentation changes |
| `ci` | CI/CD configuration changes |
| `refactor` | Code restructure, no feature change |
| `test` | Adding or fixing tests |
| `perf` | Performance improvement |

**Examples:**
```bash
git commit -m "feat(app): add homepage hero section"
git commit -m "ci: add GitHub Actions workflow"
git commit -m "fix(docker): correct port in Dockerfile"
git commit -m "chore: update pnpm dependencies"
```

**Why it matters:** Tools like `semantic-release` read these commits and automatically publish versioned releases (1.0.0 → 1.1.0 → 2.0.0).

---

## 3. Semantic Versioning (SemVer)

Every release should be tagged: `MAJOR.MINOR.PATCH`

| Version Part | When it increments |
|-------------|-------------------|
| `MAJOR` (2.x.x) | Breaking change — existing users must update |
| `MINOR` (x.1.x) | New feature that is backwards-compatible |
| `PATCH` (x.x.1) | Bug fix |

```bash
# Tag a release
git tag -a v1.0.0 -m "Initial release"
git push origin v1.0.0
```

```bash
# List all tags
git tag -l

# Checkout a specific version
git checkout v1.0.0
```

---

## 4. The .gitignore for DevOps Work

As you progress through this curriculum, many tools generate files that should **never** be committed:

```gitignore
# Terraform state (contains sensitive infrastructure data)
*.tfstate
*.tfstate.backup
.terraform/
.terraform.lock.hcl

# Ansible
*.retry

# Environment variables (NEVER commit secrets)
.env
.env.local
.env.production

# Docker-generated
.docker/

# Kubernetes secrets
*-secret.yaml
*-secret.yml

# Python
__pycache__/
*.pyc
.venv/
venv/

# OS
.DS_Store
Thumbs.db
```

---

## 5. Git Hooks

Git hooks are scripts that run automatically at specific points in the Git workflow. They live in `.git/hooks/` but you can manage them with a tool called **Husky**.

### Why hooks matter for DevOps:
- Run linting before every commit (`pre-commit`)
- Enforce commit message format (`commit-msg`)
- Run tests before pushing (`pre-push`)

### Set up Husky in the app:

```bash
cd app
pnpm add -D husky
pnpx husky init
```

This creates a `.husky/` folder. Now create a pre-commit hook:

```bash
# .husky/pre-commit
pnpm run build --if-present
```

And a commit-msg hook to enforce conventional commits:

```bash
pnpm add -D @commitlint/cli @commitlint/config-conventional
```

Create `commitlint.config.js` in `app/`:
```js
module.exports = { extends: ['@commitlint/config-conventional'] }
```

```bash
# .husky/commit-msg
pnpx --no -- commitlint --edit $1
```

Now any commit with a bad message format will be rejected locally.

---

## 6. Protecting Main Branch on GitHub

Once you push this repo to GitHub:

1. Go to **Settings → Branches**
2. Add a branch protection rule for `main`
3. Enable:
   - ✅ Require pull request before merging
   - ✅ Require at least 1 approving review
   - ✅ Require status checks to pass (you'll add these in Module 03)
   - ✅ Do not allow bypassing the above settings

This ensures `main` is always deployable.

---

## 7. Exercises

### Exercise 1: Set Up Your Repo
```bash
# Make sure you're in the devops-essentials folder
git log --oneline  # See existing commits from create-next-app

# Create a new branch for your first feature
git checkout -b feat/update-homepage

# Make a change to app/app/page.tsx (update the title or hero text)
# Then commit with conventional commit format
git add .
git commit -m "feat(app): update homepage title"
git checkout main
git merge feat/update-homepage
```

### Exercise 2: Tag Your First Version

```bash
git tag -a v0.1.0 -m "feat: initial Next.js application"
git log --oneline --decorate
```

### Exercise 3: Create a .gitignore

Update the root `.gitignore` to include the DevOps patterns from Section 4. (The Next.js app already has its own `.gitignore` inside `app/`.)

```bash
# Create root .gitignore
touch .gitignore
# Add the DevOps-specific patterns
```

### Exercise 4: Explore Git Internals
```bash
# See what Git is actually storing
cat .git/HEAD
ls .git/refs/heads/
git cat-file -p HEAD   # Read the actual commit object
```

---

## Checklist

Before moving to the next module, verify:

- [ ] I understand the difference between GitFlow and trunk-based development
- [ ] My commits follow the Conventional Commits format
- [ ] I have a root `.gitignore` with DevOps-specific patterns
- [ ] I can create and push Git tags
- [ ] I understand what Git hooks are and when they run

---

## Further Reading

- [Conventional Commits Spec](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [Trunk Based Development](https://trunkbaseddevelopment.com/)
- [Pro Git Book (free)](https://git-scm.com/book/en/v2) — Chapters 3, 7, 8

---

**Next:** [Module 01 — Python Basics](../01-python-basics/README.md)
