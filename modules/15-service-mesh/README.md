# Module 15 — Service Mesh (Istio)

> **When you have dozens of microservices, managing traffic, security, and observability between them becomes a full-time job. A service mesh handles it automatically.**

**Status:** This module unlocks after you complete Module 06 (Microservices) + Module 05 (Kubernetes).

---

## What You'll Learn

- [ ] What a service mesh is and when you actually need one
- [ ] **Istio** — the most widely used service mesh
- [ ] **mTLS** — automatic mutual TLS between every service (zero-trust networking)
- [ ] Traffic management — canary releases, A/B testing, circuit breaking at the mesh level
- [ ] **Kiali** — visualise your service mesh topology
- [ ] **Envoy** — the proxy that powers Istio
- [ ] **Linkerd** — the lightweight alternative to Istio

---

## Preview: Canary Deployment with Istio

```yaml
# Route 90% of traffic to v1, 10% to v2 (canary)
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: devops-app
spec:
  hosts:
    - devops-app
  http:
    - route:
        - destination:
            host: devops-app
            subset: v1
          weight: 90
        - destination:
            host: devops-app
            subset: v2
          weight: 10   # 10% of users get the new version
```

---

*Module content coming when you're ready. Complete through Module 12 first.*
