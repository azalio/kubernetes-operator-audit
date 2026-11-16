# Modern supplement and compatibility gate

These engineering checks complement the chapter rules. Re-check APIs against the audited repository's supported versions. Source IDs refer to sources.md. Severity depends on reachable consequences, not the check name.

## M-01 — Replay-safe reconciliation (S3)
Applies to every controller. Trace two identical reconciles, replay after restart, partial creation, duplicate events and lost intermediate events. Fail when behavior requires an in-memory previous event or repeats a destructive/chargeable action. Stable identifiers and persisted progress must recover interrupted side effects. No-op reconcile should not cause endless API writes; a custom framework can implement this without Go helpers.

## M-02 — Deletion and external lifecycle (S6)
Applies when owned data or external resources require cleanup/retention. Persist a qualified finalizer before creating an external resource; handle deletionTimestamp before normal creation; remove only the controller's finalizer after successful idempotent cleanup. Check retries, absent dependencies, lost credentials, orphan policy and an operational escape hatch. A finalizer is unnecessary if valid garbage collection or explicitly documented retention provides the whole contract. Do not recommend blind finalizer removal.

## M-03 — Ownership and adoption boundaries (S9)
Inspect owner UID, scope and controller ownership before mutation. Cross-namespace owner references are invalid; cluster-scoped dependents cannot have namespaced owners. Labels alone are not ownership proof. Reject or explicitly authorize name collisions/adoption. Trace child deletion/updates back to owner watches. Not all external resources support Kubernetes owner references: require an equivalent explicit lifecycle contract.

## M-04 — Cache, concurrency and conflicts
Trace cache reads after writes, mutable cache objects, stale resourceVersion, retry paths, per-object concurrency and optimistic locking. Avoid overwriting unrelated fields or statuses from other controllers. Prove bounded retries and eventual retry via watch or timed requeue. Handle NotFound in deletion separately from permission or network errors. No general claim that every cache read must be replaced with a live API read.

For cached clients, inspect effective informer creation and per-kind/namespace/label scope at the pinned framework version. A first Get/List of a previously unwatched kind may start a broad informer and retain far more objects than that request returns. Conversely, a cache filter can hide existing objects: do not interpret cache-local NotFound as authoritative absence before collision-sensitive creation/adoption. Evaluate explicit informers, narrower caches or deliberate direct reads against the dependency/watch and memory contracts; no single cache option is mandatory (S12/S13).

## M-05 — Dependency graph and event completeness
Enumerate every input: primary CR, child status, referenced Secret/ConfigMap, selectors, namespace labels and external state. Verify watch/index/map functions or a justified polling strategy for each. Check predicates do not discard deletionTimestamp/finalizer/dependency updates. Generation-only predicates can be correct for one watch and wrong for another; inspect actual wiring. Test unrelated updates do not enqueue the whole fleet unnecessarily.

After a metadata-only write followed by an early return, identify the event or explicit requeue that continues reconciliation. Adding a finalizer does not change a CR's generation; a generation-only filter can discard that update and the later deletionTimestamp update. A builder-wide filter may also discard dependent status changes. Trace each watch separately and verify initial creation, deletion and readiness refresh; do not ban generation predicates where their narrower event contract is sufficient (S15/S16).

## M-06 — Structural schema and field ownership (S4)
Inspect rendered apiextensions.k8s.io/v1 schemas for meaningful types, required/default semantics, bounds, enums, list/map topology and pruning behavior. Verify nil vs zero behavior in APIs, units and immutable fields where necessary. Arbitrary embedded JSON may justify preserve-unknown-fields for a bounded subtree, not a blanket failure. CEL or webhooks are options, not universal requirements; pin supported Kubernetes features before recommending them.

## M-07 — Status semantics (S3)
If status exposes progress/readiness, verify conditions and/or documented equivalent accurately represent operand state. observedGeneration, when used, must match what was processed, not merely read. Avoid unconditional Ready=True after create. Update lastTransitionTime on status transitions, preserve unrelated conditions, use status subresource where appropriate, handle patch conflicts and avoid timestamp-driven event storms. A condition called Degraded has negative polarity; don't assume all True values mean health.

## M-08 — CRD storage migration (S5)
For multiversion APIs verify one storage version, supported served versions, explicit conversion semantics, round-trip preservation, defaulting/pruning interactions, and old clients. Changing storage:true does not rewrite existing objects. Do not remove an old version or edit storedVersions merely to silence validation: first prove object migration and compatible clients. None conversion is appropriate only when representation semantics are compatible. Current migration APIs must be verified on the target Kubernetes version.

## M-09 — Admission/conversion behavior and availability
If webhooks exist, inspect certificates/CA rotation, service reachability, selectors, timeout, supported review versions, side effects and failure policy. Conversion and admission webhooks have different APIs; do not prescribe admission failurePolicy for a conversion webhook. Exercise installation/upgrade bootstrapping so a webhook does not prevent installing or recovering itself. Conversion must preserve permitted metadata and support batch requests. Do not mandate webhooks when schemas or built-in validation suffice.

For mutating admission webhooks, verify idempotence on an already-mutated object and independence from invocation order. Test reinvocation, user-supplied fields/sidecars, interaction with another mutator and validation of the final object. Preserve unrelated fields and existing array entries. A successful first mutation or a healthy TLS endpoint cannot establish these properties. Enforce security-critical final-state invariants through the appropriate validation mechanism; do not blindly change failurePolicy or require a webhook where schema/policy suffices (S11).

Trace invalid mutation output through the relevant API schema/admission rules to its expected request outcome. State that consequence conditional on the object reaching validation, with source evidence; distinguish it from an observed rejection or incident. Missing runtime evidence does not erase a statically established API-contract violation.

## M-10 — Permissions and tenant authorization (S7)
Trace effective Role/ClusterRole bindings, wildcard grants, Secret get/list/watch, impersonate/bind/escalate, workload creation and arbitrary service-account selection. Namespace watch scope is not an authorization boundary. Validate CR references and selectors against allowed namespaces and trust levels before privileged actions. Distinguish install-time CRD permissions from runtime controller permissions. Cluster-wide controllers can legitimately need ClusterRoles; require narrow resources/verbs and a rationale, not blanket namespaced RBAC.

## M-11 — Credentials and workload isolation (S7)
Check logs/status/events/metrics for credentials, secret references rather than plaintext where practical, credential rotation, registry permissions and filesystem/network privileges. Evaluate non-root, dropped capabilities, seccomp, read-only root filesystems and resource budgets against actual workload needs. Controller service-account tokens may be necessary; don't disable them blindly. Separate controller identity from operand identities.

## M-12 — Leader election and external fencing (S10)
For replicas, rollout overlap or background workers sharing responsibility, verify lock identity/namespace, permissions, lease timing, cancellation on loss and graceful termination. Kubernetes leader election alone does not guarantee fencing of an old process still writing an external system. Check transactions/conditional writes/leases or idempotency at that system. Singletons can legitimately omit election when overlap and duplicate side effects are otherwise handled; state the availability trade-off.

## M-13 — Resource bounds and operational health
Check workqueue rate limiting, backoff, bounded parallelism, API QPS/burst, indexed rather than unbounded cluster-wide lists, metrics-label cardinality and controller resource requests. Liveness should detect process inability to progress without restart storms on external outages; readiness should reflect the service being gated (especially webhooks). healthz.Ping is not proof of operand health, nor automatically a defect in a controller with no serving endpoint. Require recoverability under API outage and cancellation/timeouts for external calls.

Trace blocking waits, sleeps and nested retries through helpers: long waits can occupy all workers and delay unrelated objects. Prefer persisted progress and events or timed requeues when the contract permits; choose budgets from actual dependencies rather than a universal duration. Check return semantics at the pinned framework version: in controller-runtime an ordinary non-nil error triggers backoff and ignores Result, including RequeueAfter; scheduled successful polling uses RequeueAfter with nil error. Account separately for terminal-error semantics where supported (S17).

## M-14 — Data protection and restoration
For stateful/external operands verify backup consistency, encryption/access, retention, failure-domain isolation, restore drills, RPO/RTO, upgrade compatibility and retention on CR/uninstall deletion. A successful snapshot job does not prove recoverability. If operator intentionally does not own backups, verify a clear documented responsibility boundary rather than demanding a backup feature in every operator.

## M-15 — Stateful rollout and quorum
For consensus/data systems verify member identity, quorum-aware one-step-at-a-time operations, membership changes, partition handling, stale member removal, version skew and destructive recovery authorization. Do not derive quorum policy from replica count alone or equate Ready Pods with healthy consensus. Control-plane dependency cycles need a recovery path that still works when API access is impaired. Evaluate the actual operand protocol, deployment topology and supported recovery procedures.

## M-16 — Installation, uninstall and upgrades
Trace rendered manifests/Helm/OLM/GitOps installation in its supported mode. Test old-to-new upgrades with persisted CRs and data, interrupted rollout, supported rollback or explicit irreversible-step constraints, uninstall retention and orphan cleanup. Validate claimed Kubernetes matrix. OLM CSV/channels/OperatorCondition rules apply only to the OLM implementation actually used; classic OLM concepts are not universal to all versions or distribution systems.

## M-17 — Test fidelity and generated artifacts (S8)
Separate unit/fake client, real API-server/envtest and disposable-cluster E2E coverage. Fakes do not establish admission/defaulting/resourceVersion behavior; envtest usually lacks controller-manager/kubelet. Inspect generated schema/RBAC drift, golden render tests, retry/restart/deletion paths and negative multitenant cases. Run regeneration in an isolated worktree only after inspecting generators; generated files are evidence of shipped behavior, not evidence of hand-authored implementation quality.

## M-18 — Version and evidence discipline
Record exact revisions and supported versions; verify deprecated APIs, framework options and storage migration tools before recommending replacements. Check that documentation matches actual deployment flags and permission scope. Treat unresolved documentation/code conflicts as findings requiring resolution, not license to force the code to match stale prose. Every claim of runtime behavior must link to a trace/test or be labeled unverified.
