# Sources and provenance

## Authoring guidance consulted

- S1: Agent Skills specification, https://agentskills.io/specification . Portable SKILL.md YAML frontmatter, concise entrypoint, references/scripts, progressive disclosure and structure validation.
- S2: Anthropic skill-authoring guidance, https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices . Match specificity to risk, avoid redundant context, link resources directly, test on real tasks and multiple models when available. This package does not claim cross-model evaluation unless a validation artifact explicitly records it.

## Domain sources consulted

- S3: Kubebuilder good practices, https://book.kubebuilder.io/reference/good-practices . Idempotency, API conventions, responsibility separation, status and instrumentation. One-primary-kind guidance is a design heuristic, not a ban on watching/managing many dependent kinds.
- S4: Kubernetes custom resources, https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/ . Declarative API boundary, CRDs versus other storage and services. Do not use CRs as bulk application data storage.
- S5: Kubernetes CRD versioning, https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definition-versioning/ . Served/storage distinctions, conversion and migration before version removal.
- S6: Kubernetes finalizers, https://kubernetes.io/docs/concepts/overview/working-with-objects/finalizers/ . Deletion timestamp, cleanup responsibilities, qualified names and unsafe forced removal.
- S7: Kubernetes RBAC good practices, https://kubernetes.io/docs/concepts/security/rbac-good-practices/ . Least privilege, Secret list/watch disclosure, workload creation and escalation risks.
- S8: Kubebuilder envtest, https://book.kubebuilder.io/reference/envtest . API server and etcd, normally no kubelet or controller-manager; do not treat integration tests as cluster E2E.
- S9: Kubernetes owners/dependents, https://kubernetes.io/docs/concepts/overview/working-with-objects/owners-dependents/ . UID and namespace/cluster scope restrictions; labels differ from ownership.
- S10: client-go leader election documentation, https://pkg.go.dev/k8s.io/client-go/tools/leaderelection . Explicitly does not guarantee fencing; check pinned library version before applying options.
- S11: Kubernetes admission webhook good practices, https://kubernetes.io/docs/concepts/cluster-administration/admission-webhooks-good-practices/ . Reinvocation, idempotence of individual/composed mutations, field preservation and final-state validation.
- S12: controller-runtime cache options, https://pkg.go.dev/sigs.k8s.io/controller-runtime/pkg/cache#Options . On-demand informers, ReaderFailOnMissingInformer, per-kind/namespace selectors and cache-visible object scope; inspect the audited dependency version.
- S13: Operator SDK designing lean operators, https://sdk.operatorframework.io/docs/best-practices/designing-lean-operators/ . Cache and watch scope, memory consumption and deliberate client use; framework-specific options are implementation choices.
- S14: Kubernetes garbage collection, https://kubernetes.io/docs/concepts/architecture/garbage-collection/#cascading-deletion . Owner deletion drives cascading cleanup; a controller must separately reconcile resources removed from the desired set while their owner survives.
- S15: controller-runtime generation predicate, https://pkg.go.dev/sigs.k8s.io/controller-runtime@v0.20.4/pkg/predicate#GenerationChangedPredicate . Generation-only update filtering excludes metadata changes and may exclude status changes; verify each resource's generation semantics.
- S16: controller-runtime builder event filter, https://pkg.go.dev/sigs.k8s.io/controller-runtime@v0.20.4/pkg/builder#TypedBuilder.WithEventFilter . Builder-wide predicates apply to watched objects; inspect primary and dependent watches rather than assuming a primary-only filter.
- S17: controller-runtime reconcile contract, https://pkg.go.dev/sigs.k8s.io/controller-runtime@v0.20.4/pkg/reconcile#Reconciler . Error/backoff precedence over Result, timed requeue and terminal errors at this pinned version.

## Comparative material

The community kubernetes-operator skill was inspected at commit `4680893d91f2aee6f77ca1519fd1b86b7a104c87`: https://github.com/alirezarezvani/claude-skills/tree/4680893d91f2aee6f77ca1519fd1b86b7a104c87/engineering/kubernetes-operator . Its finalizer/predicate skeleton inspired the independently written negative fixture G and closer event-flow/retry checks. It is not a normative source or a dependency. No external scripts/templates were installed or executed. Regex matches and capability keywords are discovery hints, not proof of operator correctness or maturity.

M-01..M-18 complement the chapter checks using the domain guidance above. A rule's failure requires applicability and concrete evidence. Source pages may evolve; resolve version-sensitive assertions against the audited software's target versions. Tool/framework choices are not compliance requirements in themselves.
