# Evaluation cases and rubric

These are labeled synthetic fixtures, not real operator test results. Use them to test the auditor's reasoning and false-positive discipline. Do not deploy them. Record model, supplied context, findings and misses in a separate validation artifact; a static fixture evaluation is not Kubernetes E2E.

## Case A: dangerous external database controller
Input: assets/evaluation/case-a/controller.go and deployment.yaml. Ask an auditor for a targeted review with exact evidence. Expected: repeated external allocation/no idempotency; absent persisted cleanup protection before allocation; ignored cleanup error and removal of foreign finalizers; premature Ready; effective wildcard RBAC; duplicate-side-effect risk with replicas and no election/fencing. Do not claim the excerpt compiles or a live exploit ran. Recognize restart-after-side-effect as a separate failure window. Accept grouping multiple finalizer defects under one finding.

## Case B: architecture-only Helm operator
Input: assets/evaluation/case-b/contract.md. Expected: OLM-specific checks N/A; Go SDK conventions not required; custom finalizer not automatically required given stated GC-only lifecycle; stateless backup feature N/A; actual reconcile, rendered permissions and runtime evidence unknown. Replica overlap remains a question, not a proven defect. Fail the evaluation for inventing implementation/runtime success or requiring OLM/Go/finalizers for every operator.

## Case C: invalid API migration
Input: assets/evaluation/case-c/upgrade.md. Expected: None conversion incompatible with semantic representation change; storage flag is not object migration; storedVersions cannot truthfully be cleared before migration; premature removal breaks old stored objects/clients; fake-only tests do not validate API-server migration behavior. Do not prescribe a particular migration API without checking cluster version. Require preserved data and compatibility tests.

## Case D: admission mutation alternatives
Input: assets/evaluation/case-d/webhook.go. Expected: MutateA duplicates the named sidecar on reinvocation or when it is already present; the resulting Pod fails validation. MutateB is idempotent for the stated single-sidecar insertion contract and preserves existing entries. Do not claim that B proves TLS availability, composition with arbitrary other mutators or live admission success. Recommend repeated-application and interleaving/final-object tests, not a blanket failurePolicy change.

## Case E: shrinking desired resource set
Input: assets/evaluation/case-e/controller.go. Expected: after true -> false, the previously created Ingress remains and violates the promised private-access transition while the Website survives. Owner references alone do not prune it. Require explicit owner-checked cleanup honoring retention; do not invent a need for custom finalizers or external cleanup in this GC-only fixture.

## Case F: cached-client scale claim
Input: assets/evaluation/case-f/cache.md. Expected: verify the pinned controller-runtime cache behavior, identify the on-demand Secret informer and broad list/watch/cache scope, and reject the claim that a named Get only retains one Secret. Actual memory use, latency and OOM remain unverified. Recommend bounded cache/client choices with preserved authorization/watch behavior and a representative measurement, not an unconditional live-read replacement or unproven security breach.

## Case G: finalizer and event-filter composition
Input: assets/evaluation/case-g/controller.go. Expected: finalizer-only update plus early return leaves initial normal work without a continuing event; deletionTimestamp-only updates do not trigger cleanup; a builder-wide generation filter also discards dependent status updates needed for readiness refresh. Verify pinned predicate/builder semantics and recommend event-specific filtering and a reliable continuation. A requeue after adding the finalizer addresses only the first path. Do not label generation filters universally wrong or claim that a cluster incident was observed.

## Scoring

Track expected issue categories recalled, unsupported/false-positive claims, file/line evidence, framework applicability, version discipline and explicit runtime limitations. Do not collapse this into an operator health score. Pass requires all critical categories in A/C/D/E/F/G and no forbidden universal requirements in B; D's correct alternative must not be labeled defective for duplicate insertion. Keep actual evaluator output and rubric assessment; failures must feed corrections to the skill and a rerun. Run fresh independent contexts with and without the skill on the same inputs. Compare reasoning assertions for both configurations; additionally validate with-skill audit.json against the current report contract. Baseline output is not required to know this skill's private reporting schema. A single paired run per fixture does not establish a statistically reliable improvement.

## Mechanical checks

Run `python scripts/test_tools.py` for inventory/report-validator tests. Run the skill-creator quick validator or the agentskills reference validator for frontmatter. Verify direct local links, every chapter reference and catalog ID uniqueness. These checks validate packaging and reporting, not domain expertise.

## Chapter-workflow smoke test

Use case G as shared product input and target chapters 3 and 10. Start two fresh contexts with only the common scope/inventory, their own chapter assignment and the skill's shared workflow/report contract. Each obtains rule text through `chapter.py context N`, saves a separate partial report and validates it with `chapter.py validate N`. Expect 10 coverage records from chapter 3 and 7 from chapter 10, with no foreign chapter IDs. Preserve compact cross-chapter evidence handoffs. Merge their shared event-delivery finding without losing affected IDs; the final targeted report must have 17 selected controls plus 71 unknown/out_of_scope records and pass the ordinary validator. Evidence-dependent unknowns inside the selected set must remain explicit.

Record actual context identifiers and supplied/read artifacts when available. Correct partial output alone does not prove that the model avoided loading other chapters; distinguish output checks, emitted-context checks and observed execution history. This two-chapter smoke test does not establish an entire 11-chapter audit or a quality advantage over another workflow.
