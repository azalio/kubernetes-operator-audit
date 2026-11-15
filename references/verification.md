# Verification matrix

Use this matrix to select executable tests after inspecting repository test harness and obtaining necessary authorization. Do not run the whole matrix against production. For each scenario record command, sandbox/context, expected invariant, observed result, exit code and artifact. Keep a distinction between a planned scenario, a static trace and an executed test.

## Core scenarios

1. Create one CR; observe the promised children and real operand readiness. Reconcile unchanged state repeatedly: stable desired output and no unnecessary rolling restarts or writes.
2. Change an operand child outside the operator, then delete a child: prove convergence or explicitly documented ownership boundaries. Restart controller without a fresh primary-CR event: initial list/watch must recover existing work.
3. Create two CRs with the same name in different namespaces, plus two in one namespace: detect hardcoded singleton names, wrong request handling and cross-tenant collision. A deliberately cluster-singleton API needs schema/docs/enforcement rather than this expectation.
4. Change referenced Secrets/ConfigMaps/selectors without modifying primary spec: prove watch/poll refresh. Check unrelated resource changes do not cause fleet-wide churn.
5. Inject API 409 conflict, stale cache reads and transient dependency errors: eventual recovery without data clobbering, hot loops or swallowed permanent errors. Test deterministic permanent invalid input as well.
6. Interrupt after each external side effect but before status persistence: retries must not duplicate allocations, charges or destructive actions. Resume from persisted state or discover by stable identity.
7. Delete CR during creation and during external outage. Cleanup must retry safely, avoid new creates, preserve foreign finalizers and honor data-retention policy. Deleting the same thing twice should be safe.
8. Simulate operand failure while Kubernetes object creation still succeeds. Ready must not stay falsely true; expose diagnostics without secrets and recover when the dependency returns.
9. Stop/restart or overlap controller replicas. Check election permissions and cancellation; for external systems test fencing/idempotency beyond the Kubernetes lease. Test SIGTERM during work.
10. Upgrade from a supported old release with old CRs and stored data. Test conversion round trips, read/write through each served version, interrupted migration and supported rollback constraints. Verify storage migration before retiring versions.
11. Apply invalid CRs to a real test API server to test schema/default/admission behavior. Plain JSON schema validation and fake clients are not complete substitutes. Test upgrade compatibility of stricter validation with existing objects.
12. Exercise least-privilege install plus runtime identity. Use tenant-provided unauthorized references and attempt selector/namespace escape. Do not use a cluster-admin client to claim runtime RBAC correctness.

## Conditional scenarios

- Stateful operands: restore a backup into an isolated environment, verify application-level data/invariants, measure RPO/RTO, test quorum-preserving member changes and unavailable members. Ensure test data only.
- OLM-distributed operators: install/upgrade through the supported OLM implementation, validate relevant artifacts and supported scopes. No OLM finding for Helm-only or raw-YAML distributions.
- Helm-based operators: test chart rendering and reconciliation drift/values changes, ownership collisions, release upgrades and uninstall retention; don't require a Go Reconcile function.
- Ansible/Python/custom controllers: map handlers/retries/watches and framework state to the same invariants. Missing controller-runtime boilerplate is not a defect.
- Webhooks: exercise certificate rotation, unavailable webhook, bootstrap/recovery and batches; distinguish admission policy from conversion behavior.
- Core control-plane operators: validate recovery when dependencies they maintain are themselves unavailable, with an out-of-band runbook. Never provoke a control-plane outage without explicit isolated-lab approval.

## Test-layer limits

- Unit/pure tests: desired-object construction, conversions, validation and decision branches; do not prove cluster effects.
- Fake client: convenient state store, potentially different defaults, generation, status and conflict semantics. Check pinned implementation.
- envtest: real API storage/admission semantics, but normally no GC, scheduler, kubelet or workloads. Child deletion by owner GC needs a fuller environment.
- Disposable cluster E2E: establishes behavior only for the recorded version, permissions, topology and workload. One green scenario does not prove partition or scale safety.

## Evidence economy

Prefer a minimal reproducer for each high-impact hypothesis. Record a static issue confidently when the code path itself proves it, but don't invent runtime output. Use unknown when required code/manifests/runtime are unavailable. A skipped test is a coverage gap, not a failed operator check unless the absence itself violates an explicit delivery contract.
