# Module 08 — Security and Software Supply Chain

> **Goal:** Make the delivery path difficult to misuse and easy to audit.

DevOps includes security decisions: who may deploy, what enters an image, where secrets live, and whether a build can be traced to source code.

## Core topics

- Least privilege for cloud IAM, Kubernetes RBAC, GitHub permissions, and containers
- Secret management and rotation; base64 is not encryption
- Dependency lockfiles, Dependabot, vulnerability triage, and pinned actions
- Non-root containers, read-only filesystems, dropped Linux capabilities, and resource limits
- SBOMs, image scanning, signing, provenance, and admission policies
- OIDC/workload identity instead of long-lived cloud keys in GitHub secrets

## Exercises

### 1. Harden the image

Update the production image to run as a non-root user, add a `.dockerignore`, and scan it with Trivy:

```bash
docker build -t devops-essentials:secure ./app
trivy image --severity HIGH,CRITICAL devops-essentials:secure
```

Record each finding as accepted, fixed, or false positive. Do not hide a finding by excluding it without a reason.

### 2. Audit the pipeline

Change the workflow so permissions are minimal, actions are pinned to trusted major versions or commit SHAs, and a pull request can never publish a production image. Add a separate protected-environment approval for production deployment.

### 3. Remove static cloud credentials

Configure GitHub OIDC with a cloud provider. The workflow should request a short-lived identity scoped to one repository and environment. Prove that the workflow has no long-lived access key in repository secrets.

### 4. Protect Kubernetes workloads

Add a dedicated namespace, ServiceAccount, RBAC Role, resource requests and limits, a NetworkPolicy, and a Pod Security admission label. Test both an allowed and denied network path.

## Threat-model checkpoint

For the app, list assets, trust boundaries, entry points, threats, mitigations, and residual risk. Include the image registry, CI runner, cluster API, application API, and user data. A secure design is explicit about what it does not protect.

## What to look up

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [SLSA](https://slsa.dev/)
- [GitHub OIDC](https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
- [Kubernetes Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [Trivy](https://aquasecurity.github.io/trivy/)

→ [Module 09 — Observability and Reliability](../09-reliability/README.md)
