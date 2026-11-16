# Installation and invocation

This portable package follows https://agentskills.io/specification . Its scripts use Python 3.9+ and only the standard library. No mandatory MCP, cloud key or cluster connection is needed for static review. Actual repository/runtime tests may require the project's own toolchain and an explicitly authorized disposable cluster.

## Claude Code

Place the whole `kubernetes-operator-audit` directory under `~/.claude/skills/` for personal use, or `<repo>/.claude/skills/` for a project. Invoke:

```
/kubernetes-operator-audit Review this operator for production readiness. First inspect read-only; do not deploy or change files. Produce audit.md and audit.json with file:line evidence and explicit unknowns.
```

Documentation: https://code.claude.com/docs/en/skills . Keep references/, scripts/ and assets/ together with SKILL.md.

## Codex

Place the directory under `~/.agents/skills/` or `<repo>/.agents/skills/`. Invoke:

```
$kubernetes-operator-audit Audit this operator's reconciliation, CRDs, RBAC, upgrades and recovery. Start read-only. Produce an evidence-backed report and a separate list of unverified runtime scenarios.
```

Documentation: https://learn.chatgpt.com/docs/build-skills (redirect target of https://developers.openai.com/codex/skills/). If not discovered, restart the client and check its skills list. Older clients may use different search paths; follow the installed version's documentation. Do not install duplicate copies in overlapping locations without a reason.

## Targeted request example

```
Use kubernetes-operator-audit to review only the v1beta1 -> v1 CRD migration. Verify round-trip conversion, stored object migration, old-client compatibility and webhook availability. Mark other controls out of scope, not passed. Do not execute migrations.
```

## Output expectations

Review one chapter per fresh context and persist its partial report before moving on. Independent chapters may run concurrently after the common contract is established; chapter 9 consolidates their results last. Use `python scripts/chapter.py plan` for ownership, `python scripts/chapter.py context N` for one chapter's rules, and `python scripts/chapter.py validate N chapters/chNN.json` for its partial report. See [chapter execution](chapter-workflow.md) for delegation, context-reset fallback, progress and final synthesis. Do not load all chapter references at once or ask each worker to emit all 88 controls.

A full audit has coverage records for every catalog check, but not necessarily a runtime result for every check. Unsupported claims remain unknown. Findings cite implementation or rendered manifests and describe a concrete failure path. Missing OLM, Go, custom finalizers or backup features are not automatically defects.

The included fixtures exercise review reasoning, not a live Kubernetes cluster. There is no universal correctness guarantee and no claim of testing across every framework/model.
