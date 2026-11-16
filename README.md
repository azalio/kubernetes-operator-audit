# Kubernetes Operator Audit

An AI agent skill for **Kubernetes operator code review and production-readiness audits** in **Claude Code** and **Codex**.

Review reconciliation, CRDs, finalizers, RBAC, upgrades and recovery against **88 checks across 11 chapters**. Each chapter runs in a separate context and saves its findings before the agent combines the results. Reports include `file:line` evidence, failure scenarios, suggested fixes and explicit unknowns.

[Install](#install) · [Run an audit](#run-an-audit) · [Audit checklist](#audit-checklist) · [Chapter workflow](#chapter-workflow) · [Reports and tools](#reports-and-tools)

## Install

Clone the whole repository into your client's personal skills directory. Keep `SKILL.md`, `references/`, `scripts/` and `assets/` together.

### Claude Code

```sh
mkdir -p ~/.claude/skills
git clone https://github.com/azalio/kubernetes-operator-audit.git \
  ~/.claude/skills/kubernetes-operator-audit
```

### Codex

```sh
mkdir -p ~/.agents/skills
git clone https://github.com/azalio/kubernetes-operator-audit.git \
  ~/.agents/skills/kubernetes-operator-audit
```

For a project installation, use `.claude/skills/` or `.agents/skills/` inside the target repository. If a copy is already installed, update it instead of creating a duplicate. Restart the client if the skill does not appear.

The helper scripts require Python 3.9+ and use only the standard library. Static review needs access to the operator's source; it does not require a Kubernetes cluster, MCP server or additional cloud credentials. See the [installation guide](references/usage.md), [Claude Code skills documentation](https://code.claude.com/docs/en/skills) and [Codex skills documentation](https://learn.chatgpt.com/docs/build-skills).

## Run an audit

Open your operator repository in the agent and send one of these prompts **in chat**.

Claude Code:

```text
/kubernetes-operator-audit Review this operator for production readiness.
Start with read-only inspection. Review each chapter in a fresh context;
parallelize only independent chapters. Save audit.md and audit.json with
file:line evidence and explicit unknowns. Do not modify operator code or
deploy to a cluster.
```

Codex:

```text
$kubernetes-operator-audit Review this operator for production readiness.
Start with read-only inspection. Review each chapter in a fresh context;
parallelize only independent chapters. Save audit.md and audit.json with
file:line evidence and explicit unknowns. Do not modify operator code or
deploy to a cluster.
```

For a focused review, use the same invocation prefix with a narrower request:

| Review | Example request |
| --- | --- |
| Finalizers and stuck deletion | Trace creation, finalizer persistence, deletion retries and cleanup of external resources. Check whether watch predicates can lose required events. |
| CRD version migration | Review the v1beta1 to v1 migration: conversion, stored objects, old clients and webhook availability. Do not execute migrations. |
| RBAC and tenant isolation | Trace service accounts, bindings and tenant-controlled references to privileged effects. Inspect rendered manifests where available. |

Targeted audits mark excluded controls as out of scope. Missing evidence stays `unknown`, with a specific next verification step.

## Audit checklist

The catalog contains 70 chapter checks and 18 supplemental checks. Supplemental checks belong to individual chapter passes, so each pass loads only its own rules.

| Chapter | What it reviews |
| --- | --- |
| [1. Responsibilities and capabilities](references/ch01.md) | Operator contract, managed resources and intended automation level |
| [2. Kubernetes interaction](references/ch02.md) | Actors, API access, namespace scope and privilege boundaries |
| [3. API and reconciliation](references/ch03.md) | CRD schemas, spec/status separation, convergence and idempotency |
| [4. Implementation](references/ch04.md) | Ownership, finalizers, generated assets and implementation behavior |
| [5. Observability and availability](references/ch05.md) | Conditions, metrics, leader election and health probes |
| [6. Build and deployment](references/ch06.md) | Images, deployment configuration and installation behavior |
| [7. OLM and distribution](references/ch07.md) | Operator Lifecycle Manager packaging and distribution, where applicable |
| [8. API evolution](references/ch08.md) | Version conversion, storage migration, webhooks and compatibility |
| [9. Cross-chapter review](references/ch09.md) | Capability claims and evidence across the completed passes; runs last |
| [10. Dependencies and watches](references/ch10.md) | Configuration changes, event routing, dependency updates and drift |
| [11. Stateful recovery](references/ch11.md) | Quorum, backup, restore and failure recovery for core operators |

The rules focus on behavior across Go/controller-runtime, Kubebuilder, Operator SDK, Helm, Ansible, Python/Kopf and custom controllers. Checks adapt to the implementation and its contract; language choice, absence of OLM or absence of a custom finalizer alone do not establish a defect. Framework-specific probes need evidence from the versions used by the target operator.

## Chapter workflow

1. **Establish scope.** Record the source revision, operator contract, runtime versions, tenants and permitted tests.
2. **Review one chapter per fresh context.** Sequential execution is the default. After the common contract is established, independent chapters may run in bounded parallel batches with separate outputs.
3. **Save evidence and handoffs.** Each pass records its assigned checks, findings, unknowns and questions for other chapters. Chapter 9 consolidates the results last.
4. **Combine and validate.** The coordinator reconciles handoffs, deduplicates findings and validates the combined report.

Context isolation comes from the agent host's separate workers or fresh sessions. The Python helpers supply rules and validate artifacts; they do not launch agents. If the host cannot delegate, save progress and resume the next chapter in a fresh session. See the [execution and handoff contract](references/chapter-workflow.md).

## Reports and tools

| Artifact | Purpose |
| --- | --- |
| `audit.md` | Findings, severity, evidence, remediation and verification steps |
| `audit.json` | All 88 control records, selected scope, findings and completion state |
| `chapters/chNN.md` and `chapters/chNN.json` | Evidence and coverage for an individual chapter |
| `chapter-progress.json` | Chapter progress and outstanding handoffs |

Checks use `pass`, `fail`, `unknown` or `not_applicable`. Audit completion is tracked separately as `incomplete`, `blocked` or `complete`. A complete audit can contain confirmed failures; completion does not mean the operator is healthy. See the [report format](references/report-format.md).

From this skill's directory, use these helpers as needed, replacing the example paths with your own:

```sh
# List candidate source/configuration files for inspection.
python3 scripts/inventory.py /absolute/path/to/operator

# Plan chapter ownership and load only chapter 3's rules.
python3 scripts/chapter.py plan
python3 scripts/chapter.py context 3

# Validate reports already produced by the audit.
python3 scripts/chapter.py validate 3 /absolute/path/to/audit/chapters/ch03.json
python3 scripts/validate_report.py /absolute/path/to/audit/audit.json
```

Inventory lists candidate paths without interpreting code. Report validation checks structure, coverage and consistency; findings still require source or runtime evidence.

## Validation and contributions

The repository includes [synthetic evaluation cases](references/evaluation-cases.md), Python unit tests and an [executed validation record](references/validation-results.md). Current evidence covers helper behavior, synthetic review reasoning and a two-chapter workflow exercise. It does not establish live-cluster correctness or accuracy across every framework and model. Runtime tests require the target project's toolchain and an explicitly authorized disposable environment.

Run the helper tests from the repository root:

```sh
python3 -B -m unittest discover -s scripts -p 'test*.py' -v
```

For a missed defect, false positive or workflow problem, [open an issue](https://github.com/azalio/kubernetes-operator-audit/issues) with a minimal reproduction, relevant versions and expected behavior. Link the affected check IDs when possible and redact secrets. Changes to rules should include supporting [primary sources](references/sources.md) and a focused evaluation case.
