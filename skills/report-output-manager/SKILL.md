---
name: report-output-manager
description: Coordinate runtime-neutral report generation with Codex-specific path reservation, rendering, repository persistence, and validated independent-final-review report attestation.
---

# Codex Report Wrapper

## Goal

Act as the Codex runtime wrapper for report output without redefining report semantics, and persist independent-final-review evidence without creating an infinite review/commit cycle.

## Phase-specific required Skills

Required Skills depend on the report phase. Do not invoke `report-writer` during a reservation-only phase that has no complete review evidence yet.

### Normal persistence phase

Invoke:

1. `work-context-manager`
2. `report-writer`

Use for implementation, verification, normal review, fix verification, and consolidated reports.

### Independent-final-review reservation phase

Invoke:

1. `work-context-manager`

Do **not** invoke `report-writer` in this phase. The independent review has not happened yet, so complete coverage, findings, verdict, and final evidence do not exist. This phase owns only deterministic path reservation metadata and freeze-readiness checks.

### Independent-final-review attestation persistence phase

Invoke:

1. `work-context-manager`
2. `report-writer`

Enter this phase only after the independent-review lifecycle has a passing verdict and complete retained evidence.

Do not replace these Skills with `shared/` files or duplicate their semantics locally.

## Codex responsibilities

- Parent owns report phase, source selection, path reservation, template choice, persistence, and post-persistence validation.
- Reserve a path under the target repository's report rules before delegated section writing when normal persistence applies.
- For independent-final-review attestation, reserve the exact path as metadata only before freeze; do not create or pre-populate the repository file before a passing verdict.
- During reservation-only work, do not ask `report-writer` to generate content from incomplete/nonexistent review evidence.
- During content-generation phases, pass authoritative context and complete evidence to `report-writer`.
- Persist the complete result without changing verdict, severity, validation status, uncertainty, reviewed implementation identity, or reserved-path metadata.
- Preserve `verification_capability` and distinct validation, commit, push, and CI-wait state supplied by the caller.
- Leave PR commenting and handoff transport to the caller unless explicitly delegated.

## Normal persistence mode

For implementation, verification, normal review, fix verification, and consolidated reports:

- use target-repository report rules,
- invoke the normal-persistence required Skills,
- reserve and create the report path as required by the caller's normal workflow,
- persist and commit the report before the independent-final-review implementation HEAD is frozen,
- synchronize task and phase tracking before that freeze,
- preserve legacy names unless renaming is explicitly requested.

## Independent-final-review report-attestation mode

This mode has two separate phases: reservation before review and persistence after a passing verdict. Never collapse them.

### Before review: reservation only

Run only the reservation-phase required Skills.

Before the independent review starts:

- reserve the exact independent-final-review report path or paths as parent-owned metadata,
- do not invoke `report-writer`,
- do not create, pre-populate, stage, or edit those repository files,
- do not synthesize a report body or placeholder verdict,
- commit all other implementation, design, workflow, configuration, tracking, handoff, and normal-report changes,
- for `local_execution_available`, freeze the validated local committed HEAD without pre-review push; for `remote_ci_only`, record authorized pre-review push and matching current-HEAD CI,
- freeze that HEAD as `reviewed_implementation_head`.

The reserved path is not a delegated child report during review. The independent reviewer returns structured findings, coverage, commands/evidence, verdict, risks, unexplored areas, and dispatch-profile evidence to the parent. The parent retains that evidence outside frozen repository content.

If the independent review fails and requires repository changes, do not persist the reserved report path. Return through implementation and normal fix verification, keep the independent evidence as lifecycle state, then reuse the same independent reviewer for bounded closure as required. The reserved path remains unwritten until that independent lifecycle reaches a passing verdict.

### After a passing verdict: one attestation persistence

Only now enter the attestation-persistence phase and invoke `report-writer`.

1. Re-resolve authoritative context with `work-context-manager` for the reviewed implementation identity and retained evidence.
2. Invoke `report-writer` with persistence mode `report_attestation_commit`, the complete retained independent-review evidence, and the pre-reserved path or paths.
3. Persist the generated report for the first time without modifying any other path.
4. Create at most one commit whose first parent is `reviewed_implementation_head`.
5. Validate that the commit diff contains only the reserved independent-final-review report path or paths.
6. Validate that the report names `reviewed_implementation_head`, describes itself as administrative attestation, and does not claim its own commit SHA was reviewed implementation.
7. Record the resulting `report_attestation_head` externally in the PR body, PR comment, or handoff returned outside the branch.
8. Do not create another repository commit.

Generated reports and tracking must not require their own future commit SHA. Before persistence, use `commit_pending` with `technical_head` and, for an attestation, `administrative_parent`; record the resulting SHA only externally after the commit is created and validated.

The completion identity is:

```yaml
reviewed_implementation_head: full_sha
report_attestation_head: full_sha
```

Any pre-verdict write to the reserved report path, premature `report-writer` invocation that invents unavailable verdict evidence, extra changed path, parent mismatch, second attestation commit, or later repository commit invalidates the terminal state and requires normal fix verification plus same-reviewer bounded closure before a new attestation decision.

## Default path rules

- Place reports under `<repo-root>/reports/` unless target-repository instructions override it.
- Use existing repository filename, language, and template rules.
- Preserve legacy names unless renaming is explicitly requested.
- Existing helper references in this Skill directory remain available for deterministic path construction.
- Reserve independent-final-review report paths before freezing the reviewed implementation HEAD, but treat reservation as metadata only until a passing verdict.

## Boundaries

- Do not invent evidence.
- Do not invoke `report-writer` during independent-final-review reservation.
- Do not convert missing current-HEAD CI into success.
- Do not let a concise PR comment replace the detailed report.
- Do not modify implementation merely to improve a report.
- Do not redefine report rules locally when `report-writer` is unavailable in a phase that requires it.
- In independent-final-review reservation, do not create or modify the reserved report file before a passing verdict.
- In report-attestation persistence, do not modify tasks, phases, design, Skills, workflows, configuration, implementation, handoffs, or non-reserved report paths.
- Do not create more than one report-attestation commit.
- Do not merge.

## Outputs

### Normal persistence

Return:

- report mode and phase,
- authoritative source identities,
- complete report body,
- reserved/persisted report path,
- created or updated outcome,
- preserved unknowns and remaining risks.

### Independent-final-review reservation

Return:

- report mode: `independent_final_review`,
- phase: `reservation_only`,
- authoritative context identity,
- reviewed implementation candidate HEAD,
- reserved report path or paths,
- reservation state: `metadata_only`,
- report body: absent,
- `report_writer_invoked: false`,
- persistence outcome: not started.

### Independent-final-review attestation persistence

Return:

- report mode: `independent_final_review`,
- phase: `attestation_persistence`,
- authoritative source identities,
- reviewed implementation HEAD,
- retained independent-review evidence identity,
- complete report body,
- reserved/persisted report path or paths,
- report-attestation head or explicit absence,
- attestation diff validation,
- preserved unknowns and remaining risks,
- any persistence limitation.

## Completion condition

Normal persistence completes when the normal-phase required Skills have produced an evidence-faithful report and it is persisted before the final-review freeze.

Independent-final-review reservation completes before review when `work-context-manager` has established authoritative context, the exact path is reserved as metadata, `report-writer` was not invoked, no repository file exists or changes at that path, and the reviewed implementation HEAD can be frozen repository-stable.

Independent-final-review attestation persistence completes only after a passing verdict when the persistence-phase required Skills have produced one evidence-faithful report-attestation commit satisfying every allowlist condition. A concrete target path or explicit persistence limitation is available, authoritative sources and uncertainty are preserved, no later repository commit exists in attestation mode, and no merge was performed.
