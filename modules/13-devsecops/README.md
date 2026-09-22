# Module 13 — DevSecOps

> **Shift security left.** Instead of checking security at the end, you bake it into every step of the pipeline.

**Status:** This module unlocks after you complete Module 03 (GitHub Actions).

---

## What You'll Learn

- [ ] What "shift left" means and why security belongs in CI, not at the end
- [ ] Static Application Security Testing (SAST) with Semgrep
- [ ] Software Composition Analysis (SCA) — scanning your dependencies for CVEs
- [ ] Container image scanning with **Trivy**
- [ ] Secret scanning — prevent credentials from being committed to Git
- [ ] OWASP Top 10 — the industry's list of the most critical web security risks
- [ ] Signing Docker images with **cosign** (supply chain security)

---

## Key Tools

| Tool | Type | What it does |
|------|------|-------------|
| **Trivy** | Image/IaC/code scanner | Scans images, repos, configs for CVEs and misconfigs |
| **Semgrep** | SAST | Finds security bugs in source code using rules |
| **Snyk** | SCA | Scans dependencies for known vulnerabilities |
| **gitleaks** | Secret scanning | Prevents committing API keys, passwords, tokens |
| **cosign** | Image signing | Signs and verifies container images (supply chain trust) |
| **OWASP ZAP** | DAST | Dynamic testing — scans a running app for vulnerabilities |

---

## Preview: Trivy in GitHub Actions

```yaml
- name: Scan Docker image for vulnerabilities
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: '${{ secrets.DOCKERHUB_USERNAME }}/devops-app:latest'
    format: 'sarif'
    output: 'trivy-results.sarif'
    severity: 'CRITICAL,HIGH'
    exit-code: '1'   # Fail the build if critical vulnerabilities found

- name: Upload Trivy results to GitHub Security tab
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: 'trivy-results.sarif'
```

---

*Module content coming when you're ready. Complete through Module 08 first.*
