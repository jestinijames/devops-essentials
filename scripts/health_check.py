#!/usr/bin/env python3
"""
Health check script for the Next.js app.
Returns exit code 0 on success, 1 on failure.
Usage: python health_check.py [--url http://localhost:3000] [--retries 5] [--delay 3]
"""

import sys
import time
import argparse
import requests


def check_health(url: str, timeout: int = 5) -> dict:
    try:
        response = requests.get(url, timeout=timeout)
        return {
            "url": url,
            "status_code": response.status_code,
            "healthy": response.status_code < 400,
            "response_time_ms": round(response.elapsed.total_seconds() * 1000, 2),
        }
    except requests.exceptions.ConnectionError:
        return {"url": url, "healthy": False, "error": "Connection refused"}
    except requests.exceptions.Timeout:
        return {"url": url, "healthy": False, "error": "Timeout"}


def wait_for_health(url: str, retries: int = 5, delay: int = 3) -> bool:
    for attempt in range(1, retries + 1):
        print(f"Attempt {attempt}/{retries}: checking {url}")
        result = check_health(url)

        if result["healthy"]:
            print(f"  ✓ Healthy (HTTP {result['status_code']}, {result.get('response_time_ms')}ms)")
            return True

        error = result.get("error") or f"HTTP {result.get('status_code')}"
        print(f"  ✗ Not healthy: {error}")

        if attempt < retries:
            print(f"  Waiting {delay}s before retry...")
            time.sleep(delay)

    return False


def main():
    parser = argparse.ArgumentParser(description="Health check for Next.js app")
    parser.add_argument("--url", default="http://localhost:3000")
    parser.add_argument("--retries", type=int, default=5)
    parser.add_argument("--delay", type=int, default=3)
    args = parser.parse_args()

    print(f"Health check: {args.url}")
    healthy = wait_for_health(args.url, args.retries, args.delay)

    if healthy:
        print("\nHealth check PASSED")
        sys.exit(0)
    else:
        print("\nHealth check FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
