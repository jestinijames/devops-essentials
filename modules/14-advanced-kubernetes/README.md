# Module 14 — Advanced Kubernetes

> **You know how to deploy. Now learn how to operate K8s at scale and harden it.**

**Status:** This module unlocks after you complete Module 05 (Kubernetes).

---

## What You'll Learn

- [ ] **RBAC** — Role-Based Access Control: who can do what in your cluster
- [ ] **Network Policies** — firewall rules between Pods
- [ ] **StatefulSets** — running stateful apps (databases) in K8s
- [ ] **Custom Resource Definitions (CRDs)** — extend K8s with your own object types
- [ ] **Operators** — controllers that automate complex stateful apps (the Postgres Operator, etc.)
- [ ] **HPA / VPA** — Horizontal and Vertical Pod Autoscalers
- [ ] **PodDisruptionBudgets** — guarantee uptime during node maintenance
- [ ] **Resource Quotas and LimitRanges** — prevent runaway workloads from starving others
- [ ] **kubeconfig** — managing multiple cluster contexts (dev, staging, prod)

---

## Preview: RBAC

```yaml
# Create a role that can only read pods
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: staging
rules:
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list", "watch"]

---
# Bind the role to a service account
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: staging
subjects:
  - kind: ServiceAccount
    name: ci-runner
    namespace: staging
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

---

*Module content coming when you're ready. Complete through Module 08 first.*
