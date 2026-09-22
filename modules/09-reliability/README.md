# Module 09 — Observability and Reliability

> **Goal:** Detect problems, explain them with evidence, and improve the system after failure.

A dashboard is not observability by itself. You need useful signals, clear objectives, and a practiced response.

## The three signals

- **Logs:** discrete events with timestamps, severity, request IDs, and useful context
- **Metrics:** numeric time series such as request rate, error rate, latency, saturation, and queue depth
- **Traces:** a request's path across services and its time spent in each dependency

Instrument both the Next.js app and `tasks-api`. Emit structured JSON logs, propagate a request ID, and make health endpoints distinguish liveness from readiness.

## Exercises

### 1. Define service objectives

For each service, write an SLI and SLO:

```text
SLI: percentage of successful GET /api/tasks requests over five minutes
SLO: 99.5% success during the monthly measurement window
Error budget: 0.5% of requests may fail
```

Add latency and availability objectives. Explain which user experience each objective protects.

### 2. Build a local observability stack

Run Prometheus and Grafana with Docker Compose. Export application metrics, scrape them, and create panels for request rate, error rate, p50/p95 latency, container restarts, and CPU/memory saturation. Add an alert with a runbook link.

### 3. Centralize logs and traces

Forward service logs to Loki and instrument a trace from the browser-facing route through `tasks-api`. Use the trace ID to move from a slow request to the relevant logs.

### 4. Write an incident response exercise

Create a game day: make `tasks-api` return errors, fill a disk in a disposable environment, and deploy a deliberately broken image. Practice detection, triage, mitigation, communication, rollback, and recovery. Record a blameless postmortem with timeline, impact, root causes, contributing factors, and actions.

### 5. Backups and recovery

Back up application data, restore it into a clean environment, and measure RPO and RTO:

- **RPO:** how much data can be lost
- **RTO:** how long recovery may take

A backup that has never been restored is an assumption, not a recovery plan.

## Reliability patterns to learn

Retries with bounded backoff, timeouts, circuit breakers, bulkheads, graceful shutdown, idempotency, rate limiting, queue-based load leveling, PodDisruptionBudgets, autoscaling, and capacity planning.

## Checkpoint

You are ready for Module 10 when you can answer what is broken, who is affected, how confident you are, what mitigation is safest, and how you will prevent recurrence.

## What to look up

- [Google SRE book](https://sre.google/sre-book/table-of-contents/)
- [OpenTelemetry](https://opentelemetry.io/docs/)
- [Prometheus](https://prometheus.io/docs/introduction/overview/)
- [Grafana](https://grafana.com/docs/grafana/latest/)

→ [Module 10 — Platform Engineering and Capstone](../10-platform/README.md)
