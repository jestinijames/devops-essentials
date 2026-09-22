# Module 07 — Foundations: Linux, Networking, and Git

> **Goal:** Build the operating-system and networking intuition that makes every later DevOps tool easier to understand.

The earlier modules are practical, but they move quickly over the substrate underneath them. DevOps work becomes much less mysterious when you can inspect a process, trace a request, read a log, and explain what DNS and TLS are doing.

## Learning path

### 1. Linux and processes

Practice these commands in a disposable directory or virtual machine:

```bash
pwd
find . -maxdepth 2 -type f
ls -la
id
ps aux
lsof -i :3000
curl -i http://localhost:3000/api/health
kill <pid>
chmod 600 .env.example
```

Understand users and groups, file permissions, environment variables, standard input/output/error, exit codes, signals, processes, services, and logs. Then run the app and answer:

- Which process owns port 3000?
- What happens to its child processes when you stop it?
- Which exit code does a failed command return?

### 2. Networking

Draw the path for `curl https://example.com`:

```text
application -> DNS -> TCP -> TLS -> HTTP -> reverse proxy -> application
```

Learn ports, sockets, IPv4/IPv6, DNS records, HTTP methods and status codes, TLS certificates, proxies, load balancers, and NAT. Use `dig`, `nslookup`, `curl -v`, and `traceroute` to inspect real traffic.

Exercise: run the app, use `curl -v http://localhost:3000/api/health`, then place a reverse proxy in front of it and explain each changed header.

### 3. Git as an operations tool

Practice feature branches, pull requests, rebasing, tags, revert, bisect, and release notes. Create a release tag for the app, then use `git bisect` to find an intentionally introduced health-check regression.

A useful release sequence is:

```bash
git switch -c feat/health-improvement
git diff
 git log --oneline --decorate --graph -20
git tag -a v0.1.0 -m "First runnable release"
```

### 4. Configuration and validation

Separate code, configuration, and secrets. Validate YAML, JSON, HCL, Dockerfiles, and Kubernetes manifests before applying them. Never rely on a successful local shell command as proof that a deployment is safe.

## Checkpoint

You are ready for Module 08 when you can explain a request from browser to process, find a listening process, inspect its logs, diagnose a DNS or HTTP failure, and safely revert a bad change.

## What to look up

- [Linux command line](https://ubuntu.com/tutorials/command-line-for-beginners)
- [HTTP Semantics](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods)
- [DNS concepts](https://www.cloudflare.com/learning/dns/what-is-dns/)
- [Pro Git](https://git-scm.com/book/en/v2)

→ [Module 08 — Security and Supply Chain](../08-security/README.md)
