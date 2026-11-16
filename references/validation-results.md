# Validation results

## Isolated chapter workflow (2026-11-16)

Version 1.0.2 replaces the instruction to read all applicable references together with one fresh reviewing context per chapter. Serial execution is the default; independent passes may run in bounded parallel batches. Chapter 9 consolidates the other passes last. Modern checks are assigned to chapter owners, and each pass saves a partial report plus evidence before synthesis. Hosts without delegation must use a fresh-session handoff rather than pretend that a checkpoint clears model context.

`scripts/chapter.py plan` partitions the existing 88 IDs exactly once across 11 chapters. `context N` emits only that chapter's rule headings and assigned modern sections. `validate N` checks the bounded report against those IDs, requires targeted scope and matching chapter identity, and cannot substitute for final all-catalog validation.

All 26 unit tests passed, including four new chapter-workflow tests: exact catalog partition, isolated rule output for each of 11 chapters, partial/full distinction and wrong/missing/foreign chapter records, and targeted subsets within a chapter. Ruff, Pyflakes, Pyright, the system skill-creator validator and `git diff --check` passed. The previously documented SkillStore URL heuristic limitation is unchanged.

A targeted workflow smoke test ran chapters 3 and 10 in two fresh agents with `fork_turns=none`, a shared frozen case-G input and separate output ownership. Their saved rule contexts exactly match `chapter.py context`: 10 assigned controls for chapter 3 and 7 for chapter 10, with no foreign rule headings. Both partial reports validated. The coordinator reconciled an informational handoff and merged the common defect while retaining five failed control IDs and ten specific unknowns; it did not turn a suggested B03-03 link into a failure without supporting evidence. The final targeted report contains 17 selected controls and 71 explicit exclusions and passed the all-88 validator. Its completion remains blocked by missing product artifacts, not by unfinished chapter work.

Artifacts: sibling workspace `iteration-20261116-chapter-workflow/`, including `chapters/`, per-chapter `evidence/`, `chapter-progress.json`, `workflow-summary.json`, combined `audit.md`/`audit.json` and validation logs. This proves the exercised routing/output path, not execution of all 11 chapters or an improvement in domain-audit quality. Full worker tool transcripts were not retained, so emitted-context equality and structurally correct outputs must not be presented as proof of every model read. No live cluster or executable operator fixture was run.

## Report consistency and domain review (2026-11-16)

The reviewed baseline was commit `873151ede55902fbbf2c8d7539be1236817cc3f9`. Version 1.0.1 tightens finding/check consistency without changing the 88 catalog IDs. It also adds admission-mutation, desired-set shrinkage and cache-scope guidance. A subsequent comparative review adds event-continuation and retry-semantics guidance plus case G. The external skill was read at the revision recorded in sources.md; its scripts and templates were not executed or installed.

### Mechanical evidence

- RED: the new consistency cases produced 21 failing assertions against the original validator. In particular, a report could claim complete coverage with passing/N/A controls while retaining a confirmed defect.
- GREEN: all 22 Python unit tests passed after the fix. Tests cover finding severity/confidence/status combinations, independent confirmed failures alongside risks/improvements, targeted exclusions, every link of a deduplicated defect, the full catalog, legacy singular links and malformed inputs.
- Ruff, Pyflakes, Pyright, the system skill-creator frontmatter validator and `git diff --check` passed. All 22 direct SKILL.md links and seven evaluation fixture entries were checked. No operator code or cluster was changed.
- The SkillStore-specific skill-builder validator passed before the comparative sources were added, then returned `EXTERNAL_LINKS_FORBIDDEN`. Its mixed-case/digit ID heuristic flags public Go API anchors such as `GenerationChangedPredicate` and the public comparison commit hash. Those URLs contain no private identifiers or credentials. The diagnostic is retained in `final-checks-20261116/`; the external validator was not modified, and no SkillStore upload was attempted. This is a packaging-tool limitation, not a passing SkillStore validation result.
- Validation still checks structure and internal consistency, not evidence truth or operator correctness. A confirmed failure cannot be disguised as an optional improvement merely to obtain a valid report.

### Paired reasoning evaluations

Independent fresh-context agents reviewed the same synthetic inputs with the updated skill and without an audit skill. Executors were instructed not to read the rubric, other outputs or validation summaries. Separate graders inspected their reports against the same assertions. The no-skill baseline was not required to produce this skill's private JSON schema. This measures skill-versus-no-skill behavior, not a controlled comparison with the original skill version.

| Case | With skill | Without skill |
| --- | --- | --- |
| A: external database lifecycle | 5/5 | 5/5 |
| B: Helm architecture false positives | 4/4 | 4/4 |
| C: API storage migration | 4/4 | 4/4 |
| D: admission mutation, initial run | 3/4 | 4/4 |
| E: desired-set shrinkage | 4/4 | 4/4 |
| F: cache scale claim | 4/4 | 4/4 |

Initial totals: 24/25 with skill and 25/25 without skill. The with-skill D report found duplicate sidecar insertion but omitted its invalid-Pod/API-validation consequence. M-09 was clarified to trace static API-contract consequences while distinguishing them from observed runtime incidents. A separate paired D rerun scored 4/4 with skill and 3/4 without skill; the baseline omitted that consequence on the rerun. The original scores remain retained. This reversal shows variability and is not evidence of reliable superiority.

Case G was then run separately against the peer-review follow-up snapshot: both configurations scored 4/4. Both found lost continuation after finalizer registration, missed deletion cleanup and missed dependent readiness updates, with correct version-pinned evidence and scoped remediation. This case confirms the fixture is answerable but establishes no skill advantage. The grader also compared four retained controller-runtime source files with the pinned upstream files; hashes matched.

All eight with-skill reports from these runs passed the current report validator with 88 coverage records each. This does not mean all 88 checks passed or were in scope. Output-based grading does not independently verify every executor tool-use claim; complete execution transcripts were not captured. Executors inherited the session model, but exact model IDs and token usage were unavailable. Concurrent wall times are not used for speed comparisons.

Artifacts are retained outside the distributed skill in the sibling `kubernetes-operator-audit-workspace/`: `iteration-20261116-1002/`, `iteration-20261116-webhook-followup/` and `iteration-20261116-peer-event-flow/`. Each includes a frozen skill snapshot, reports, grading, benchmark data and a standalone `review.html`. The first iteration also holds RED/GREEN and lint/type/package logs; final packaging diagnostics are in `final-checks-20261116/`. No live Kubernetes, envtest or executable operator fixture was run. These small synthetic cases do not certify production audit quality or generalization to unseen operators.

## Completion-contract enhancement (2026-11-15)

- RED observed before each implementation slice: reason-only unknown accepted; invalid completion/targeted scope accepted; multi-check finding rejected and malformed enum fields raised `TypeError`.
- GREEN: `python3 -m unittest discover -s /absolute/skill/scripts -p 'test*.py' -v` — all 17 tests passed. Added completion/category matrix, targeted exclusions, blocker details, deduplicated finding linkage, legacy singular linkage, and malformed-field diagnostics. Existing inventory tests still pass.
- `ruff check --isolated /absolute/skill/scripts`, `pyflakes /absolute/skill/scripts`, `pyright /absolute/skill/scripts`, and `git diff --check` passed. No repository lint/type configuration was present. Pyright 1.1.409 emitted an update-availability notice for 1.1.414, not a code diagnostic; no tool installation was changed.
- Catalog remains 88 unique IDs with the same four statuses. Validation enforces report structure, not evidence truth, genuine blocker provenance, or runtime correctness. No operator code or cluster was changed.
- The initial-release reasoning evaluation below predates the required completion/resolution fields; its reports were not rerun against the new contract.

## Initial release

## What was actually exercised

- All 11 chapter references and direct links in SKILL.md checked for existence.
- Catalog enumerated programmatically: 70 chapter checks plus 18 supplemental checks, 88 unique IDs.
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
