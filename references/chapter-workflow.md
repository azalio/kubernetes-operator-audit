# Isolated chapter execution

The review unit is one chapter. Each unit reads its own rules, investigates the operator and persists its result. The coordinator routes work and reconciles results; it does not accumulate all rule text and re-audit the operator in one context.

## 1. Establish a small common packet

Save repository/revision/dirty-state identity, intended operator contract, framework and supported versions, install mode, tenant/data boundaries, authorized actions and artifact locations in `scope.md`. Generate `inventory.json` and `chapter-plan.json` using the inventory script and `python /skill/scripts/chapter.py plan`. Paths and short observations are enough: do not paste whole source trees or all chapter references into the packet. Preserve fingerprints for relevant uncommitted inputs; if they change, revisit affected chapter evidence rather than silently mixing snapshots.

The coordinator keeps `chapter-progress.json`: the common snapshot identity and one entry per planned chapter with `chapter`, `check_ids`, `state` (`pending`, `running`, `reviewed`, or `excluded`), `completion` (the partial report's value once available), `context_id`, `report`, `summary`, and unresolved `handoffs`. `excluded` requires a targeted scope that omits the chapter and an explicit reason; it is unavailable in full mode. Record the actual context identifier when available, otherwise explicitly say unavailable. `reviewed` means evidence disposition is finished, not that every check passed. An incomplete chapter stays pending/running; a genuinely blocked chapter can be reviewed with its exact blocker preserved. No generic N/A or blocked placeholder for uninspected work.

## 2. Route checks without loading their contents

`scripts/chapter.py` is the authoritative ownership map. Chapter checks belong to their numbered chapter. Each modern check belongs to exactly one pass; every full-audit ID is assigned once.

| Chapter | Assigned modern checks | Scheduling |
| --- | --- | --- |
| 1: responsibility and capability contract | none | First; establishes the shared contract |
| 2: actors, permissions and scope | M-10, M-11 | After the common contract |
| 3: API and convergence | M-01, M-04, M-06 | After the common contract |
| 4: implementation and lifecycle | M-02, M-03, M-17 | After the common contract |
| 5: reporting and operational behavior | M-07, M-12, M-13 | After the common contract |
| 6: deployment and release lifecycle | M-16 | After the common contract |
| 7: OLM/distribution applicability | none | After install mode is established |
| 8: API evolution and webhooks | M-08, M-09 | After the common contract |
| 9: cross-chapter consistency | M-18 | Last; consumes compact chapter summaries |
| 10: dependencies and configuration | M-05 | After the common contract |
| 11: stateful/core safety | M-14, M-15 | After the common contract |

Default serial order: 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 9. A full review accounts for every chapter even when specific checks are inapplicable. For a targeted review schedule only chapters owning selected IDs; leave other chapter entries explicitly excluded by the requested scope, not reviewed. Chapter 1 and 9 need not become extra in-scope reviews for a narrowly targeted task, but the common contract and final coverage reconciliation are still required.

## 3. Use one fresh reviewing context per chapter

With agent delegation, start a fresh worker for each chapter without inheriting prior review transcripts. Even in serial mode, use a new worker rather than assigning the next chapter to a context that already holds the previous one. Give it the common packet, its chapter number and selected IDs, artifact paths and the bounded task below. The worker loads `SKILL.md`, this workflow and the report contract, then runs `python /skill/scripts/chapter.py context N` to obtain only its chapter text and assigned modern sections. It opens relevant operator files and pinned upstream sources as needed. The entire source file for a necessary call path may be read; chapter isolation must not prevent checking callers or contracts.

After chapter 1, independent workers may run concurrently in a small batch (normally 2–4; adjust to context/tool limits). Each owns only `chapters/chNN.*` and its own evidence directory. They are not alone in the workspace and must preserve other workers' outputs. A common infrastructure test runs under one designated owner; others consume its recorded result. Do not share a mutable report file among workers.

Pass dependencies through compact handoffs containing the originating check, question, inspected evidence, snapshot identity, receiving chapter and the selected IDs whose conclusion requires the answer (if any). Distinguish required evidence from informational cross-links. The receiver opens the cited evidence when needed; it does not load another chapter's entire transcript. If a needed contract is unresolved, defer the dependent conclusion and request that specific artifact. In a targeted audit, an informational handoff to an excluded chapter remains an explicitly out-of-scope follow-up; it does not silently expand the review. Newly discovered evidence can invalidate a prior chapter; reopen only the affected pass in a fresh context.

If delegation is unavailable, save the packet, partial report and progress after each chapter, then use the host's fresh-session/context-reset facility with a resume packet for the next chapter. Automatic compaction or a new section heading is not a guaranteed reset. If the host cannot reset context, complete and save the current chapter, state this limitation and hand off the next chapter to a fresh session. Do not silently fall back to loading all chapters together.

## 4. Produce a bounded chapter artifact

`chapters/chNN.json` uses the normal finding/check/test shapes with these scope differences:

- `scope.mode` is `targeted`, `scope.chapter` is integer N, and `scope.check_ids` contains the selected IDs owned by this chapter.
- `checks` contains exactly the IDs assigned to this chapter by `chapter.py plan`, not all 88. In a full audit all of these are selected. For a targeted subset, remaining IDs within the chapter use unknown/out_of_scope.
- Completion, unknown-resolution and finding/check consistency rules remain unchanged. Every selected rule gets its own evidence-based disposition. Any confirmed defect links only IDs owned by this pass; send other affected controls to their owners through handoffs.
- Use chapter-prefixed finding IDs such as `CH03-F001` until final deduplication. Additional `handoffs` may record questions for other passes; they are not confirmed findings by themselves.

`chapters/chNN.md` gives a compact summary, per-check evidence, findings, attempted verification, exact blockers and handoffs. Keep a short summary separate from large logs so the coordinator can compare conclusions without loading raw evidence. Save full logs/source excerpts under `evidence/chNN/` and link them. Preserve source locations and snapshot identity so the next pass does not rely on unsupported prose.

Validate each part with `python /skill/scripts/chapter.py validate N chapters/chNN.json`. The command validates the partial structure and ownership only. It does not establish evidence truth, actual context isolation, or a complete operator audit. A chapter report cannot pass the full-report validator without the other catalog records.

Example worker task:

```text
Review chapter N only for the operator identified by scope.md and inventory.json.
Use the skill's chapter workflow and report contract. Load rules through
scripts/chapter.py context N; do not load other chapter references or the full
modern supplement. Selected checks: <IDs from chapter-plan.json>.
Inspect relevant source/callers/contracts and record a disposition for every
selected rule. Send cross-chapter questions as handoffs with precise evidence.
You own only chapters/chNN.md, chapters/chNN.json and evidence/chNN/.
You are not alone; preserve other workers' edits and outputs.
Validate your partial report and return its paths, compact findings/blockers
summary and unresolved handoffs. Follow scope.md authorization boundaries.
```

## 5. Synthesize without repeating the whole review

After the substantive passes, chapter 9 checks its own rules and M-18 using the common packet, compact summaries and specifically requested evidence. Reuse an inspected fact by reference; do not treat repeated citations as separate tests. Resolve contradictions with the responsible chapter rather than choosing the more optimistic result.

The coordinator checks that every selected chapter/check has an artifact and that snapshot identity and handoffs are reconciled. Merge the partial check records into one `audit.json`, retain final mode full/targeted as requested, remove chapter-local `scope.chapter`, union selected IDs for targeted scope, and supply unknown/out_of_scope records for excluded chapters. Every catalog ID must appear exactly once in the final coverage. Deduplicate the same defect across chapters, union its affected failed IDs, and retain a mapping to original chapter finding IDs and evidence. Do not lose an independently confirmed failure when another chapter has an unresolved risk.

Set final completion from actual dispositions: outstanding in-scope inspection or an unanswered required handoff to a scheduled pass means incomplete; only genuine inspected missing-artifact/runtime blockers justify blocked; complete requires no in-scope unknown. Informational follow-ups outside targeted scope do not prevent completion. Missing chapter output cannot be replaced by a generic pass, N/A or missing-artifact claim. Link the progress manifest and chapter reports from `audit.md`, then run the ordinary `validate_report.py audit.json`. This final validator checks coverage and consistency; the manifest and actual execution records supply the separate process evidence.
