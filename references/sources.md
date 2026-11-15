# Sources and provenance

## Authoring guidance consulted

- S1: Agent Skills specification, https://agentskills.io/specification . Portable SKILL.md YAML frontmatter, concise entrypoint, references/scripts, progressive disclosure and structure validation.
- S2: Anthropic skill-authoring guidance, https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices . Match specificity to risk, avoid redundant context, link resources directly, test on real tasks and multiple models when available. This package does not claim cross-model evaluation unless a validation artifact explicitly records it.

## Domain sources consulted

- B: Michael Dame, The Kubernetes Operator Framework Book, Packt, 2022, ISBN 978-1-80323-285-0. User-supplied PDF, 328 physical pages. Chapter notes are original condensed audit guidance, not reproduced book text or code. See book-coverage.json for sequential reading provenance and page ranges. The PDF/full extracted text is intentionally NOT distributed in this skill.
- S3: Kubebuilder good practices, https://book.kubebuilder.io/reference/good-practices . Idempotency, API conventions, responsibility separation, status and instrumentation. One-primary-kind guidance is a design heuristic, not a ban on watching/managing many dependent kinds.
- S4: Kubernetes custom resources, https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/ . Declarative API boundary, CRDs versus other storage and services. Do not use CRs as bulk application data storage.
- S5: Kubernetes CRD versioning, https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definition-versioning/ . Served/storage distinctions, conversion and migration before version removal.
- S6: Kubernetes finalizers, https://kubernetes.io/docs/concepts/overview/working-with-objects/finalizers/ . Deletion timestamp, cleanup responsibilities, qualified names and unsafe forced removal.
- S7: Kubernetes RBAC good practices, https://kubernetes.io/docs/concepts/security/rbac-good-practices/ . Least privilege, Secret list/watch disclosure, workload creation and escalation risks.
- S8: Kubebuilder envtest, https://book.kubebuilder.io/reference/envtest . API server and etcd, normally no kubelet or controller-manager; do not treat integration tests as cluster E2E.
- S9: Kubernetes owners/dependents, https://kubernetes.io/docs/concepts/overview/working-with-objects/owners-dependents/ . UID and namespace/cluster scope restrictions; labels differ from ownership.
- S10: client-go leader election documentation, https://pkg.go.dev/k8s.io/client-go/tools/leaderelection . Explicitly does not guarantee fencing; check pinned library version before applying options.

M-01..M-18 are audit synthesis extending the book, not quotations or claims that every detail appears in those sources. A rule's failure requires applicability and concrete evidence. Source pages may evolve; resolve version-sensitive assertions against the audited software's target versions. Tool/framework choices are not compliance requirements in themselves.
