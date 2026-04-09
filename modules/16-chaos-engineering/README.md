# Module 16 — Chaos Engineering

> **Break things on purpose before production breaks them for you.**

**Status:** This module unlocks after you complete Module 05 (Kubernetes) + Module 12 (Monitoring).

---

## What You'll Learn

- [ ] The principles of chaos engineering (Netflix's Chaos Monkey origin story)
- [ ] **LitmusChaos** — the CNCF chaos engineering platform for Kubernetes
- [ ] Designing chaos experiments with a hypothesis
- [ ] Steady-state hypothesis — define "healthy" before you break things
- [ ] Common chaos experiments: pod kill, CPU stress, network latency injection, node drain
- [ ] Game Days — running planned chaos exercises with your team
- [ ] **Gremlin** — the commercial chaos engineering SaaS

---

## Preview: Pod Kill Chaos Experiment

```yaml
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: pod-delete-chaos
  namespace: staging
spec:
  appinfo:
    appns: staging
    applabel: "app=devops-app"
  chaosServiceAccount: litmus-admin
  experiments:
    - name: pod-delete
      spec:
        components:
          env:
            - name: FORCE
              value: "false"
            - name: TOTAL_CHAOS_DURATION
              value: "30"    # Kill pods for 30 seconds
            - name: CHAOS_INTERVAL
              value: "10"    # Kill one every 10 seconds
```

Watch your Grafana dashboard while the experiment runs — do error rates spike? Does the app self-heal within your SLO?

---

*Module content coming when you're ready. Complete through Module 12 first.*
