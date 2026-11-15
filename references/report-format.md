# Audit report contract

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
- `scope`: object containing nonempty `repository`, `revision`, `mode` (full or targeted), and `limitations` array. Use an explicit unavailable revision string rather than invent a commit.
- `checks`: array with exactly one record for every check ID from `validate_report.py --list-checks`, even in targeted mode (out-of-scope checks are unknown with that reason, not N/A).
- `findings`: array of finding objects.
- `tests`: array of test records (may be empty for static-only audits).

Check record:
```json
{"id":"M-02","status":"unknown","reason":"External cleanup implementation not supplied","evidence":[]}
```
`pass` and `fail` require nonempty `evidence` strings naming inspected file:line ranges or test artifacts. `unknown` and `not_applicable` require a reason; do not use N/A to hide an uninspected applicable area. `fail` must have a linked finding.

Finding record (illustrative schema, not a discovered defect):
```json
{
  "id":"F-001", "check_id":"M-02", "severity":"high",
  "title":"Cleanup finalizer removed before cleanup completes",
  "location":"controllers/example.go:80-94",
  "scenario":"Delete the CR while the external API is unavailable",
  "evidence":["controllers/example.go:80-94: cleanup error is ignored"],
  "confidence":"confirmed",
  "remediation":"Keep the finalizer until successful cleanup; make cleanup retry-safe",
  "verification":"Regression test: failed cleanup retains finalizer, recovery removes it"
}
```

Test record:
```json
{"command":"inspected test command","environment":"isolated local test harness","status":"not_run","reason":"Dependencies unavailable"}
```
For executed tests use `status` passed/failed, integer `exit_code`, nonempty `artifact` path; passed requires zero, failed requires nonzero. A valid report need not be a passing operator. Validator checks shape/coverage, not the truth of evidence.
