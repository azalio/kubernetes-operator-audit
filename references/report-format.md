# Audit report contract

For chapter passes use the partial-report scope defined in [chapter execution](chapter-workflow.md) and validate with `scripts/chapter.py validate N`. The all-88 coverage requirement below applies to the final report; individual workers report only their chapter's assigned controls. Keep the chapter progress manifest and link partial reports from the final human report.

## Human report: audit.md

1. Scope: repository/revision/dirty state, framework/version, Kubernetes matrix, installation method, primary resources, namespace/tenant boundaries, data responsibilities; exclusions and authorization.
2. Verdict: concise risk summary, not a numeric quality score. State static-only/partially verified/runtime-verified scenarios explicitly.
3. Findings sorted by impact: ID/check ID; severity; title; exact file and line range; expected contract; reachable failure scenario; evidence and confidence; minimal fix; regression test.
4. Coverage: all checklist IDs mapped to pass/fail/unknown/not_applicable, justification and evidence. Deduplicate findings spanning multiple controls rather than repeating the same bug.
5. Executed checks: commands, environment/context, exit codes, artifact paths. Separately list not-run scenarios and blockers.
6. Next steps: prioritize concrete fixes and the smallest tests needed to resolve unknowns.

## Severity

- critical: supported scenario can destroy irrecoverable data or compromise broad trust boundaries.
- high: sustained outage, privilege boundary break, broken upgrades or deletion, serious reachable data loss.
- medium: bounded correctness/availability/operability defect with a feasible workaround.
- low: limited operational/maintenance problem.
- info: optional improvement, not a correctness failure.

Severity is not confidence. `confirmed`, `probable`, `needs_validation` describe confidence. A high-impact hypothesis without a verified path should be a risk/unknown, not a confirmed bug. N/A needs a scope reason. A missing searched string alone cannot prove failure or pass.

## Machine report: audit.json

Top-level keys:
- `scope`: object containing nonempty `repository`, `revision`, `mode` (`full` or `targeted`), `completion` (`incomplete`, `blocked`, or `complete`), and `limitations` array of nonempty strings (may be empty). Use an explicit unavailable revision string rather than invent a commit. Targeted mode additionally requires `check_ids`: a nonempty array of unique catalog IDs selected for inspection; full mode covers the entire catalog.
- `checks`: array with exactly one record for every check ID from `validate_report.py --list-checks`, even in targeted mode (excluded checks must be `unknown` with resolution category `out_of_scope`, not N/A). The 88 IDs and four statuses are unchanged.
- `findings`: array of finding objects.
- `tests`: array of test records (may be empty for static-only audits).

Check record:
```json
{
  "id":"M-02", "status":"unknown",
  "reason":"External cleanup implementation not supplied", "evidence":[],
  "resolution":{
    "category":"missing_artifact",
    "inspected_evidence":["inventory.json: controller sources absent from the supplied archive"],
    "missing_requirement":"Controller source at the audited revision",
    "next_action":"Obtain that revision and trace cleanup retries and ownership checks"
  }
}
```
Every check requires a nonempty `reason`. `pass` and `fail` require nonempty `evidence` strings naming inspected file:line ranges or test artifacts. `not_applicable` requires an applicability explanation; do not use N/A to hide an uninspected applicable area. `fail` must have a linked confirmed defect (non-`info` severity and `confirmed` confidence).

Every `unknown` requires a `resolution` object; a generic reason alone is invalid:

| Field | Contract |
| --- | --- |
| `category` | `not_inspected`, `missing_artifact`, `requires_runtime`, or `out_of_scope` |
| `inspected_evidence` | Array of nonempty strings describing attempted probes and results; nonempty for `missing_artifact` and `requires_runtime`, may be empty for the other categories |
| `missing_requirement` | Nonempty string identifying what is needed to resolve this check |
| `next_action` | Nonempty string describing the next concrete inspection/verification action |

`out_of_scope` is valid only in targeted mode for an ID absent from `scope.check_ids`. Explain the exclusion and what scope expansion would permit inspection. Before declaring an artifact missing, inspect accessible companion delivery artifacts and identify their repository/revision separately in the evidence. A blocker describes an actual unavailable prerequisite or required runtime observation, not work the auditor has yet to perform.

| `scope.completion` | Gate |
| --- | --- |
| `incomplete` | Inspection remains; structured unknowns allowed |
| `blocked` | No `not_inspected`; at least one in-scope `missing_artifact` or `requires_runtime` unknown with inspected evidence |
| `complete` | No `not_inspected` and no in-scope unknown; targeted exclusions remain allowed |

Completion is independent of mode, runtime assurance and pass/fail. A complete audit may contain failures; a full-mode report may still be incomplete. The validator checks these structural gates, not whether evidence or a claimed blocker is true.

Finding record (illustrative schema, not a discovered defect):
```json
{
  "id":"F-001", "check_ids":["M-02", "M-03"], "severity":"high",
  "title":"Cleanup finalizer removed before cleanup completes",
  "location":"controllers/example.go:80-94",
  "scenario":"Delete the CR while the external API is unavailable",
  "evidence":["controllers/example.go:80-94: cleanup error is ignored"],
  "confidence":"confirmed",
  "remediation":"Keep the finalizer until successful cleanup; make cleanup retry-safe",
  "verification":"Regression test: failed cleanup retains finalizer, recovery removes it"
}
```

`check_ids` is a nonempty array of unique catalog IDs. Link every affected failed control to the deduplicated finding. The legacy singular `check_id` is also accepted, but never supply both fields.

### Finding/check consistency

Use the existing severity and confidence fields to distinguish findings; no additional type field is required:

| Finding | Linked check statuses |
| --- | --- |
| Confirmed defect: non-`info` severity, `confidence=confirmed` | Every linked check must be `fail` |
| Risk: non-`info` severity, `confidence=probable` or `needs_validation` | `unknown`, or `fail` supported by a separate confirmed defect |
| Optional improvement: `severity=info`, any valid confidence | `pass`, `unknown`, or `fail` supported by a separate confirmed defect |

Every failed check needs at least one confirmed defect; risks and improvements cannot establish failure on their own. A failed control may also have unresolved risks or optional improvements: retain the confirmed failure rather than downgrading it to unknown. Every finding must link only applicable, in-scope checks; `not_applicable` and targeted exclusions cannot have findings. Expand the declared scope before including an incidental finding about an excluded control. These rules also apply to every ID of a deduplicated finding and to the legacy `check_id` field.

Test record:
```json
{"command":"inspected test command","environment":"isolated local test harness","status":"not_run","reason":"Dependencies unavailable"}
```
For executed tests use `status` passed/failed, integer `exit_code`, nonempty `artifact` path; passed requires zero, failed requires nonzero. A valid report need not be a passing operator. Validator checks shape/coverage, not the truth of evidence.
