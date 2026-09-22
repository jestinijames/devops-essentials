# Module 10 — Platform Engineering and Capstone

> **Goal:** Turn repeated operational work into a paved road that teams can use safely.

Mastery is not memorizing every cloud command. It is designing systems and interfaces that make the reliable path the easiest path.

## Advanced topics

### GitOps

Use Argo CD or Flux to reconcile Kubernetes from Git. Compare push-based deployment with pull-based reconciliation, drift detection, rollback, promotion between environments, and secret handling.

### Terraform at scale

Create versioned modules with clear inputs and outputs. Add `fmt`, `validate`, security checks, plan review, remote state locking, drift detection, import, state migration, and automated module tests. Separate foundational networking from application workloads.

### Kubernetes platform design

Learn Helm or Kustomize, ingress and TLS, autoscaling, admission policies, multi-tenancy, cluster upgrades, node pools, storage classes, and workload identity. Understand when a managed service is better than operating the control plane yourself.

### Architecture and governance

Study multi-account or multi-project foundations, landing zones, policy as code, FinOps, data classification, disaster recovery, multi-region tradeoffs, message delivery guarantees, service mesh tradeoffs, and developer experience.

## Capstone: production platform for DevOps Essentials

Build a small but defensible platform that supports the app and `tasks-api`:

1. Provision a non-production environment with Terraform.
2. Build, scan, sign, and publish immutable images from GitHub Actions.
3. Deploy through GitOps with separate staging and production environments.
4. Use OIDC, least privilege, Kubernetes RBAC, NetworkPolicies, and external secret management.
5. Add readiness and startup probes, resource requests, autoscaling, disruption budgets, and graceful shutdown.
6. Provide logs, metrics, traces, dashboards, alerts, SLOs, and runbooks.
7. Demonstrate a rollback, a failed dependency, a restored backup, and a controlled incident.
8. Produce architecture, threat-model, cost, disaster-recovery, and operations documents.

## Definition of done

- A new contributor can deploy the service from documented steps.
- A release is traceable to source, image digest, workflow run, and deployment revision.
- A failed deployment can be detected and rolled back without manual database surgery.
- Secrets are not stored in Git or long-lived CI credentials.
- A recovery exercise proves the stated RPO and RTO.
- A monthly cost estimate and cleanup procedure exist.
- Every alert links to a runbook and has an owner.

## Mastery rubric

**Beginner:** explain the tools and run the happy path.

**Intermediate:** automate validation, deploy repeatably, secure identities, and diagnose common failures.

**Advanced:** design for failure, measure reliability, control cost, and improve delivery safety.

**Mastery:** make sound tradeoffs under constraints, teach the system to others, and build a platform that scales the team's judgment rather than just its infrastructure.

## What to look up

- [Argo CD](https://argo-cd.readthedocs.io/en/stable/)
- [Terraform testing](https://developer.hashicorp.com/terraform/language/tests)
- [CNCF landscape](https://landscape.cncf.io/)
- [FinOps Framework](https://www.finops.org/framework/)
- [AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html)

This capstone is intentionally open-ended. The final artifact is not a particular vendor stack; it is a reliable, secure, observable delivery system with evidence that it works.
