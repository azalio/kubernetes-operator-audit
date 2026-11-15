# SYNTHETIC architecture-only fixture

This project is a Helm-based operator, not Go. It is distributed via a signed Helm chart; OLM/OperatorHub are explicitly unsupported. The CR is namespaced. Its operand is stateless and creates only same-namespace Kubernetes Deployments/Services with owner UID references. It creates no external resources and intentionally uses garbage collection for their lifecycle; no custom finalizer is needed by this contract. The controller's reconciliation and render code, rendered RBAC and test results have NOT been supplied.

Requested review: assess the supplied architecture only. Do not infer implementation quality or claim E2E success. No live cluster or executable code is available. A single controller replica is documented, but overlap behavior on rolling updates is not specified. No backup capability is promised for this stateless workload.
