#!/usr/bin/env python3
"""
Prints a deployment summary: app name, version, branch, commit, and timestamp.
Usage: python deploy_summary.py
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path


def run(cmd: str) -> str:
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()


def main():
    # Read app metadata from package.json
    package_path = Path(__file__).parent.parent / "app" / "package.json"
    with open(package_path) as f:
        package = json.load(f)

    app_name = package.get("name", "unknown")
    version = package.get("version", "0.0.0")

    # Get Git metadata
    branch = run("git branch --show-current")
    commit = run("git rev-parse --short HEAD")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Print summary
    separator = "─" * 40
    print(separator)
    print("DEPLOYMENT SUMMARY")
    print(separator)
    print(f"App:     {app_name} v{version}")
    print(f"Branch:  {branch}")
    print(f"Commit:  {commit}")
    print(f"Time:    {timestamp}")
    print(separator)


if __name__ == "__main__":
    main()
