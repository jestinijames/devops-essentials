# Module 01 — Python Basics for DevOps

> **You don't need to become a Python developer. You need to become fluent enough to automate anything.**

DevOps engineers write Python to: automate repetitive tasks, write scripts for CI/CD pipelines, interact with cloud APIs, parse logs, validate configurations, and build internal tooling. You're not building apps — you're building tools.

---

## Learning Objectives

By the end of this module you will:
- [ ] Understand Python syntax well enough to read and write scripts
- [ ] Work with files, directories, and processes from Python
- [ ] Parse JSON and YAML (the languages of DevOps configs)
- [ ] Call HTTP APIs using the `requests` library
- [ ] Write a real DevOps script: a deployment health checker

---

## Setup

```bash
# Verify Python is installed
python --version   # should be 3.11+

# Create a virtual environment for this module
cd modules/01-python-basics
python -m venv .venv

# Activate it (Windows)
.venv\Scripts\activate

# Activate it (Mac/Linux)
source .venv/bin/activate

# Your prompt will change to show (.venv)
```

**Why virtual environments?** Each Python project has its own dependencies. A venv isolates them so they don't conflict. This is the Python equivalent of `node_modules`.

---

## 1. Python Syntax Crash Course

If you know JavaScript, Python syntax will feel familiar with some key differences.

```python
# No semicolons. Indentation defines blocks (use 4 spaces, never tabs)

# Variables (no let/const/var)
name = "DevOps"
count = 42
is_running = True
price = 3.14

# String formatting (like JS template literals)
message = f"Server {name} has {count} containers running"
print(message)

# Comparison
# JS:       ===    !==    &&    ||    !
# Python:   ==     !=     and   or    not

if count > 0 and is_running:
    print("Service is healthy")
elif count == 0:
    print("No containers running")
else:
    print("Service is down")
```

### Lists (like JavaScript arrays)
```python
services = ["nginx", "postgres", "redis", "app"]

# Access
print(services[0])      # "nginx"
print(services[-1])     # "app" (last item)

# Slice
print(services[1:3])    # ["postgres", "redis"]

# Loop
for service in services:
    print(f"Checking {service}...")

# List comprehension (very Pythonic)
running = [s for s in services if s != "postgres"]

# Add/remove
services.append("prometheus")
services.remove("redis")
```

### Dictionaries (like JavaScript objects)
```python
server = {
    "name": "web-01",
    "ip": "10.0.0.1",
    "region": "us-east-1",
    "healthy": True,
    "cpu_percent": 42.5
}

# Access
print(server["name"])
print(server.get("port", 80))   # get with default (safe)

# Update
server["healthy"] = False

# Loop over keys and values
for key, value in server.items():
    print(f"{key}: {value}")

# Check if key exists
if "region" in server:
    print(f"Region: {server['region']}")
```

### Functions
```python
def check_service(name, port=80, retries=3):
    """
    Check if a service is responding.
    Returns True if healthy, False otherwise.
    """
    print(f"Checking {name} on port {port}...")
    # ... logic here
    return True

# Call with positional args
result = check_service("nginx")

# Call with keyword args (order doesn't matter)
result = check_service(port=443, name="app", retries=5)
```

---

## 2. Working with Files

In DevOps you constantly read config files, write log outputs, check if paths exist.

```python
import os
import pathlib

# Check if a file exists
config_path = pathlib.Path("docker-compose.yml")
if config_path.exists():
    print("Config found")

# Read a file
with open("docker-compose.yml", "r") as f:
    content = f.read()
    print(content)

# Write a file
with open("deployment.log", "w") as f:
    f.write("Deployment started at 2026-04-09\n")
    f.write("Image: app:v1.2.0\n")

# Append to a file
with open("deployment.log", "a") as f:
    f.write("Deployment complete.\n")

# List directory contents
for item in pathlib.Path(".").iterdir():
    if item.is_file():
        print(f"File: {item.name}")
    else:
        print(f"Dir:  {item.name}/")

# Get environment variables (critical for DevOps)
api_key = os.environ.get("API_KEY", "not-set")
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    raise ValueError("DATABASE_URL environment variable is required")
```

---

## 3. Running Shell Commands from Python

This is how Python scripts orchestrate other tools.

```python
import subprocess

# Run a command and get output
result = subprocess.run(
    ["docker", "ps", "--format", "{{.Names}}"],
    capture_output=True,
    text=True,
    check=True   # raises exception if command fails
)
print(result.stdout)

# Check return code
if result.returncode == 0:
    print("Command succeeded")

# Run a shell command (simpler but less safe)
result = subprocess.run("git log --oneline -5", shell=True, capture_output=True, text=True)
print(result.stdout)
```

---

## 4. JSON and YAML — The Languages of DevOps

Every config file, every API response, every Kubernetes manifest is JSON or YAML.

### JSON
```python
import json

# Parse JSON string → Python dict
json_string = '{"name": "app", "version": "1.0.0", "healthy": true}'
data = json.loads(json_string)
print(data["name"])  # "app"

# Read JSON file
with open("package.json", "r") as f:
    package = json.load(f)
    print(f"App version: {package['version']}")

# Write a dict as JSON
config = {"replicas": 3, "image": "app:latest", "port": 3000}
print(json.dumps(config, indent=2))

# Write JSON to file
with open("config.json", "w") as f:
    json.dump(config, f, indent=2)
```

### YAML
```bash
# Install the PyYAML library
pip install pyyaml
```

```python
import yaml

# Parse YAML string
yaml_string = """
name: my-app
replicas: 3
image:
  name: app
  tag: latest
ports:
  - 3000
"""
config = yaml.safe_load(yaml_string)
print(config["replicas"])  # 3
print(config["image"]["tag"])  # "latest"

# Read a YAML file (like a Kubernetes manifest)
with open("../../k8s/deployment.yaml", "r") as f:
    manifest = yaml.safe_load(f)

# Write YAML
data = {"apiVersion": "apps/v1", "kind": "Deployment"}
print(yaml.dump(data, default_flow_style=False))
```

---

## 5. Calling HTTP APIs

In DevOps, you frequently call APIs: cloud providers, monitoring tools, Slack webhooks, health endpoints.

```bash
pip install requests
```

```python
import requests

# Simple GET request
response = requests.get("https://httpbin.org/get")
print(response.status_code)  # 200
print(response.json())       # parsed JSON response

# GET with headers (authenticated API)
headers = {
    "Authorization": f"Bearer {os.environ.get('API_TOKEN')}",
    "Content-Type": "application/json"
}
response = requests.get("https://api.github.com/user", headers=headers)

# POST request (like a Slack webhook)
webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
payload = {"text": "Deployment to production complete! :rocket:"}
response = requests.post(webhook_url, json=payload)

# Error handling
try:
    response.raise_for_status()  # raises if status >= 400
    print("Notification sent")
except requests.exceptions.HTTPError as e:
    print(f"Failed to send notification: {e}")
```

---

## 6. Real Exercise: Build a Health Check Script

This script will check if the Next.js app is running and responding correctly. You'll use this concept in CI/CD pipelines later.

Create `scripts/health_check.py`:

```python
#!/usr/bin/env python3
"""
Health check script for the Next.js app.
Usage: python health_check.py [--url http://localhost:3000] [--retries 3]
"""

import sys
import time
import argparse
import requests


def check_health(url: str, timeout: int = 5) -> dict:
    """Check if the app is responding at the given URL."""
    try:
        response = requests.get(url, timeout=timeout)
        return {
            "url": url,
            "status_code": response.status_code,
            "healthy": response.status_code < 400,
            "response_time_ms": round(response.elapsed.total_seconds() * 1000, 2)
        }
    except requests.exceptions.ConnectionError:
        return {"url": url, "healthy": False, "error": "Connection refused"}
    except requests.exceptions.Timeout:
        return {"url": url, "healthy": False, "error": "Timeout"}


def wait_for_health(url: str, retries: int = 5, delay: int = 3) -> bool:
    """Retry health check until the app is healthy or retries are exhausted."""
    for attempt in range(1, retries + 1):
        print(f"Attempt {attempt}/{retries}: Checking {url}")
        result = check_health(url)
        
        if result["healthy"]:
            print(f"✓ App is healthy! (HTTP {result['status_code']}, {result.get('response_time_ms')}ms)")
            return True
        else:
            error = result.get("error") or f"HTTP {result.get('status_code')}"
            print(f"✗ Not healthy: {error}")
        
        if attempt < retries:
            print(f"  Waiting {delay}s before retry...")
            time.sleep(delay)
    
    return False


def main():
    parser = argparse.ArgumentParser(description="Health check for Next.js app")
    parser.add_argument("--url", default="http://localhost:3000", help="URL to check")
    parser.add_argument("--retries", type=int, default=5, help="Number of retries")
    parser.add_argument("--delay", type=int, default=3, help="Seconds between retries")
    args = parser.parse_args()
    
    print(f"Starting health check for {args.url}")
    healthy = wait_for_health(args.url, args.retries, args.delay)
    
    if healthy:
        print("\nHealth check PASSED")
        sys.exit(0)
    else:
        print("\nHealth check FAILED — app did not become healthy in time")
        sys.exit(1)  # Non-zero exit code fails the CI pipeline


if __name__ == "__main__":
    main()
```

### Run it:
```bash
# First, start the Next.js app
cd app && pnpm dev &

# Then run the health check
cd ..
python scripts/health_check.py --url http://localhost:3000 --retries 3
```

**Why `sys.exit(1)` matters:** CI/CD pipelines treat any non-zero exit code as a failure. This script will fail your pipeline if the app didn't start correctly. That's the desired behavior.

---

## 7. Exercise: Write a Deployment Summary Script

Create `scripts/deploy_summary.py` that:
1. Reads `app/package.json` to get the app name and version
2. Gets the current Git branch (`git branch --show-current`)
3. Gets the latest Git commit hash
4. Prints a formatted deployment summary

```python
#!/usr/bin/env python3
import json
import subprocess
from datetime import datetime

def run(cmd):
    """Run a shell command and return its output."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

# Your code here:
# 1. Read package.json
# 2. Get current branch
# 3. Get commit hash
# 4. Print formatted summary

# Expected output:
# ─────────────────────────────────
# DEPLOYMENT SUMMARY
# ─────────────────────────────────
# App:     my-app v0.1.0
# Branch:  main
# Commit:  a3f9b12
# Time:    2026-04-09 14:30:00
# ─────────────────────────────────
```

---

## Checklist

- [ ] I can read and write Python variables, lists, and dicts
- [ ] I can define and call functions with default arguments
- [ ] I can read and write files from Python
- [ ] I can run shell commands using `subprocess`
- [ ] I can parse JSON and YAML
- [ ] I can call an HTTP API with `requests`
- [ ] My health check script exits with code 0 on success, 1 on failure
- [ ] My deploy summary script reads `package.json` and Git metadata

---

## Further Reading

- [Python Official Tutorial](https://docs.python.org/3/tutorial/) — Chapters 3–7
- [Real Python — Automating Tasks](https://realpython.com/automating-tasks-with-python/)
- [requests library docs](https://docs.python-requests.org/)

---

**Next:** [Module 02 — Docker](../02-docker/README.md)
