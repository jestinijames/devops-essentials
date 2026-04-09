# Module 12 — Monitoring & Observability

> **You can't fix what you can't see.** Monitoring tells you when something is wrong. Observability tells you *why*.

---

## Learning Objectives

- [ ] Understand the three pillars of observability: Metrics, Logs, Traces
- [ ] Run Prometheus + Grafana locally with Docker Compose
- [ ] Expose metrics from the Next.js app
- [ ] Build a Grafana dashboard for the app
- [ ] Set up alerting (get notified when things break)
- [ ] Understand centralized logging with the ELK stack

---

## 1. The Three Pillars of Observability

```
METRICS          LOGS              TRACES
────────         ─────             ────────────────────────────────
CPU: 82%         2026-04-09       Request ID: abc-123
Memory: 1.2GB    14:32:01 ERROR   ├── API Gateway (12ms)
Requests: 1200/s App crashed:     ├── Auth Service (8ms)
Error rate: 0.1% out of memory    ├── Database query (45ms)  ← slow!
                                  └── Response sent (67ms total)

"What happened?"  "What exactly   "Where in the chain
                   happened?"      did it slow down?"
Prometheus        ELK Stack        Jaeger / Zipkin / OpenTelemetry
```

---

## 2. Prometheus + Grafana Setup

Add to `docker-compose.yml`:

```yaml
services:
  # ... existing services ...

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.retention.time=15d'
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
    depends_on:
      - prometheus
    restart: unless-stopped

volumes:
  prometheus_data:
  grafana_data:
```

Create `monitoring/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s      # Collect metrics every 15 seconds
  evaluation_interval: 15s

scrape_configs:
  # Monitor Prometheus itself
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # Monitor our Next.js app
  - job_name: 'devops-app'
    static_configs:
      - targets: ['app:3000']
    metrics_path: '/api/metrics'   # We'll create this endpoint

  # Monitor the host machine (with node_exporter)
  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
```

```bash
docker compose up -d prometheus grafana

# Prometheus UI: http://localhost:9090
# Grafana UI:    http://localhost:3001
#   Login: admin / admin
```

---

## 3. Expose Metrics from Next.js

Install the Prometheus client:

```bash
cd app
pnpm add prom-client
```

Create `app/app/api/metrics/route.ts`:

```typescript
import { NextResponse } from 'next/server'
import { collectDefaultMetrics, register } from 'prom-client'

// Collect default Node.js metrics (memory, CPU, GC, etc.)
collectDefaultMetrics({ prefix: 'nextjs_' })

export async function GET() {
  const metrics = await register.metrics()
  
  return new NextResponse(metrics, {
    headers: {
      'Content-Type': register.contentType,
    },
  })
}
```

Now visit http://localhost:3000/api/metrics — you'll see raw Prometheus metrics.

### Add custom business metrics:

```typescript
// app/lib/metrics.ts
import { Counter, Histogram, register } from 'prom-client'

export const pageViews = new Counter({
  name: 'nextjs_page_views_total',
  help: 'Total number of page views',
  labelNames: ['path'],
})

export const requestDuration = new Histogram({
  name: 'nextjs_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'path', 'status'],
  buckets: [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5],
})
```

Use in a middleware or route handler:
```typescript
import { pageViews } from '@/lib/metrics'

// Track page views
pageViews.inc({ path: '/dashboard' })
```

---

## 4. Grafana Dashboard

After Prometheus is scraping metrics:

1. Open Grafana at http://localhost:3001
2. **Configuration → Data Sources → Add data source → Prometheus**
   - URL: `http://prometheus:9090`
3. **Dashboards → Import** — enter `1860` (Node Exporter Full — community dashboard)
4. Create a custom panel:
   - **+ Add panel → Time series**
   - Query: `rate(nextjs_page_views_total[5m])` — page views per second
   - Query: `nextjs_request_duration_seconds_p99` — 99th percentile latency

**Key metrics to track:**
```promql
# Request rate (per second)
rate(http_requests_total[5m])

# Error rate (% of requests that are 5xx)
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) * 100

# 99th percentile latency
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))

# Memory usage
process_resident_memory_bytes / 1024 / 1024

# CPU usage
rate(process_cpu_seconds_total[5m]) * 100
```

---

## 5. Alerting

Configure alerts in `monitoring/prometheus-rules.yml`:

```yaml
groups:
  - name: devops-app-alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }} for the last 2 minutes"

      - alert: AppDown
        expr: up{job="devops-app"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "App is DOWN"
          description: "devops-app has been unreachable for 1 minute"

      - alert: HighMemoryUsage
        expr: process_resident_memory_bytes / 1024 / 1024 > 500
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "App is using {{ $value }}MB of memory"
```

In Grafana, add an **Alert rule** that sends to Slack/email:
- **Alerting → Contact points → Add Slack webhook**
- **Alert rules → Link to contact point**

---

## 6. Centralized Logging (ELK Stack)

ELK = **Elasticsearch** (search engine) + **Logstash** (log processor) + **Kibana** (UI).

Add to `docker-compose.yml`:

```yaml
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.12.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  kibana:
    image: docker.elastic.co/kibana/kibana:8.12.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch

volumes:
  elasticsearch_data:
```

**Kibana** at http://localhost:5601 lets you search logs with the same query language used across Elastic's products.

---

## 7. The SRE Golden Signals

The four metrics Google SRE recommends monitoring for any service:

| Signal | What to measure | Example |
|--------|----------------|---------|
| **Latency** | How long requests take | p99 < 500ms |
| **Traffic** | How much demand | requests/second |
| **Errors** | Rate of failed requests | error rate < 0.1% |
| **Saturation** | How "full" the service is | CPU < 80%, memory < 70% |

These four things tell you almost everything you need to know about service health.

---

## Checklist

- [ ] Prometheus and Grafana are running locally via Docker Compose
- [ ] The Next.js app exposes `/api/metrics`
- [ ] Prometheus is scraping the app metrics
- [ ] I've built a Grafana dashboard showing request rate, latency, and errors
- [ ] I've set up at least one alert rule
- [ ] I can explain the four SRE Golden Signals
- [ ] I understand the difference between metrics, logs, and traces

---

## Further Reading

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Google SRE Book (free)](https://sre.google/sre-book/table-of-contents/) — Chapters 6, 10 (monitoring)
- [OpenTelemetry](https://opentelemetry.io/) — the future of distributed tracing

---

**Congratulations — you've completed the DevOps Essentials curriculum!**

You now have hands-on experience with:
Docker → CI/CD → IaC → Kubernetes → GitOps → Cloud → Monitoring

Your `devops-essentials` repo is a portfolio of real work. Push it public.
