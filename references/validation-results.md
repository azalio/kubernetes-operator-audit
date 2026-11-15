# Validation results

## Completion-contract enhancement (2026-11-15)

- RED observed before each implementation slice: reason-only unknown accepted; invalid completion/targeted scope accepted; multi-check finding rejected and malformed enum fields raised `TypeError`.
- GREEN: `python3 -m unittest discover -s /absolute/skill/scripts -p 'test*.py' -v` — all 17 tests passed. Added completion/category matrix, targeted exclusions, blocker details, deduplicated finding linkage, legacy singular linkage, and malformed-field diagnostics. Existing inventory tests still pass.
- `ruff check --isolated /absolute/skill/scripts`, `pyflakes /absolute/skill/scripts`, `pyright /absolute/skill/scripts`, and `git diff --check` passed. No repository lint/type configuration was present. Pyright 1.1.409 emitted an update-availability notice for 1.1.414, not a code diagnostic; no tool installation was changed.
- Catalog remains 88 unique IDs with the same four statuses. Validation enforces report structure, not evidence truth, genuine blocker provenance, or runtime correctness. No operator code or cluster was changed.
- The initial-release reasoning evaluation below predates the required completion/resolution fields; its reports were not rerun against the new contract.

## Initial release

## What was actually exercised

- All 11 chapter references and direct links in SKILL.md checked for existence.
- Catalog enumerated programmatically: 70 book-derived checks plus 18 supplemental checks, 88 unique IDs.
- Sequential chapter reading manifest covers 277 physical chapter pages; diagrams were not independently visually inspected.
- Skill-creator quick_validate.py returned `Skill is valid!` (PyYAML supplied through an isolated uv environment).
- `python scripts/test_tools.py`: 12 tests passed. Coverage includes symlink exclusion/no execution by inventory, missing repositories, catalog uniqueness, invalid document shapes, missing/duplicate check coverage, evidence-less passes, unlinked failures, N/A reasons and contradictory test exit codes.

## Fresh-context reasoning evaluation

A separate gpt-6-astra agent read SKILL.md and applicable references, then audited the three included synthetic fixtures without being given the answer rubric. Parent inspected the actual report artifacts and reran validate_report.py on each: all three valid, each with 88 coverage records. This was one model family, not a cross-model benchmark.

### Case A

Detected replayed paid allocations, including the crash-before-status-persistence window; ignored deletion errors and clearing foreign finalizers; effective wildcard Role binding; premature readiness. Noted absence of finalizer persistence in the shown path while correctly leaving unknown whether an unseen component adds it. Two-replica external side-effect concurrency was framed as a risk requiring effective configuration/runtime verification, not an observed split-brain incident. Findings cited precise source lines.

Parent rubric assessment: expected critical categories found; uncertainty about incomplete code handled appropriately. No claim that the Go excerpt compiles or was deployed.

### Case B

No false defect for Helm/non-Go, no OLM, GC without a custom finalizer, or absent backups for a stateless contract. Reconciliation, rendered RBAC, ownership enforcement and rollout overlap remained unknown. Architecture-only passes did not become implementation approval.

Parent rubric assessment: false-positive guard passed for this fixture.

### Case C

Detected semantically incompatible None conversion, storage-version metadata relabeling without rewriting old objects, premature old-version removal and insufficient fake-client upgrade evidence. Kept exact API-server error behavior and actual data loss unverified rather than invented. Did not prescribe a target-version-specific migration API blindly.

Parent rubric assessment: expected migration and evidence categories found.

## Limits

No live Kubernetes cluster, envtest, production operator, Helm rendering, executable operator code or destructive scenario was run. Test commands inside generated review recommendations are proposals, not successful runs. No Claude/Codex UI invocation or cross-model validation was performed. Packaging checks and these fixtures establish a working audit workflow with basic reasoning checks, not universal correctness or production certification.

Raw local evaluation reports were retained during authoring; fixtures, rubric and this inspected result summary are distributed for reproducibility. Run fresh evaluations on real target repositories and the actual agent/model before trusting release decisions.
