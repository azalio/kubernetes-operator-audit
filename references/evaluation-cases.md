# Evaluation cases and rubric

These are labeled synthetic fixtures, not copied book code and not real operator test results. Use them to test the auditor's reasoning and false-positive discipline. Do not deploy them. Record model, supplied context, findings and misses in a separate validation artifact; a static fixture evaluation is not Kubernetes E2E.

## Case A: dangerous external database controller
Input: assets/evaluation/case-a/controller.go and deployment.yaml. Ask an auditor for a targeted review with exact evidence. Expected: repeated external allocation/no idempotency; absent persisted cleanup protection before allocation; ignored cleanup error and removal of foreign finalizers; premature Ready; effective wildcard RBAC; duplicate-side-effect risk with replicas and no election/fencing. Do not claim the excerpt compiles or a live exploit ran. Recognize restart-after-side-effect as a separate failure window. Accept grouping multiple finalizer defects under one finding.

## Case B: architecture-only Helm operator
Input: assets/evaluation/case-b/contract.md. Expected: OLM-specific checks N/A; Go SDK conventions not required; custom finalizer not automatically required given stated GC-only lifecycle; stateless backup feature N/A; actual reconcile, rendered permissions and runtime evidence unknown. Replica overlap remains a question, not a proven defect. Fail the evaluation for inventing implementation/runtime success or requiring OLM/Go/finalizers for every operator.

## Case C: invalid API migration
Input: assets/evaluation/case-c/upgrade.md. Expected: None conversion incompatible with semantic representation change; storage flag is not object migration; storedVersions cannot truthfully be cleared before migration; premature removal breaks old stored objects/clients; fake-only tests do not validate API-server migration behavior. Do not prescribe a particular migration API without checking cluster version. Require preserved data and compatibility tests.

## Scoring

Track expected issue categories recalled, unsupported/false-positive claims, file/line evidence, framework applicability, version discipline and explicit runtime limitations. Do not collapse this into an operator health score. Pass requires all critical categories in A/C and no forbidden universal requirements in B. Keep actual evaluator output and rubric assessment; failures must feed corrections to the skill and a rerun.

## Mechanical checks

Run `python scripts/test_tools.py` for inventory/report-validator tests. Run the skill-creator quick validator or the agentskills reference validator for frontmatter. Verify direct local links, every chapter reference and catalog ID uniqueness. These checks validate packaging and reporting, not domain expertise.
