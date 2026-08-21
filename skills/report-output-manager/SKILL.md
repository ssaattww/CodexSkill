---
name: report-output-manager
description: Coordinate runtime-neutral report generation with Codex-specific path reservation, rendering, repository persistence, and validated independent-final-review report attestation.
---

# Codex Report Wrapper

## Goal

Act as the Codex runtime wrapper for report output without redefining report semantics, and persist independent-final-review evidence without creating an infinite review/commit cycle.

## Required Skills

Invoke:

1. `work-context-manager`
2. `report-writer`

Do not replace these Skills with `shared/` files or duplicate their semantics locally.

## Codex responsibilities

- Parent owns report mode, source selection, path reservation, template choice, persistence, and post-persistence validation.
- Reserve a path under the target repository's report rules before delegated section writing.
- Pass authoritative context and complete evidence to `report-writer`.
- Persist the complete result without changing verdict, severity, validation status, uncertainty, reviewed implementation identity, or reserved-path metadata.
- Preserve `verification_capability` and distinct validation, commit, push, and
  CI-wait state supplied by the caller.
- Leave PR commenting and handoff transport to the caller unless explicitly delegated.

## Normal persistence mode

For implementation, verification, normal review, fix verification, and consolidated reports:

- use target-repository report rules,
- persist and commit the report before the independent-final-review implementation HEAD is frozen,
- synchronize task and phase tracking before that freeze,
- preserve legacy names unless renaming is explicitly requested.

## Independent-final-review report-attestation mode

Use this mode only after a fresh independent reviewer has passed a frozen implementation HEAD.

Before review:

- reserve the exact independent-final-review report path or paths,
- commit and push all other implementation, design, workflow, configuration, tracking, handoff, and report changes,
- freeze the current HEAD as `reviewed_implementation_head`.

After a passing verdict:

1. Invoke `report-writer` with persistence mode `report_attestation_commit` and the pre-reserved path or paths.
2. Persist the generated report without modifying any other path.
3. Create at most one commit whose first parent is `reviewed_implementation_head`.
4. Validate that the commit diff contains only the reserved independent-final-review report path or paths.
5. Validate that the report names `reviewed_implementation_head`, describes itself as administrative attestation, and does not claim its own commit SHA was reviewed implementation.
6. Record the resulting `report_attestation_head` externally in the PR body, PR comment, or handoff returned outside the branch.
7. Do not create another repository commit.

Generated reports and tracking must not require their own future commit SHA.
Before persistence, use `commit_pending` with `technical_head` and, for an
attestation, `administrative_parent`; record the resulting SHA only externally
after the commit is created and validated.

The completion identity is:

```yaml
reviewed_implementation_head: full_sha
report_attestation_head: full_sha
```

Any extra changed path, parent mismatch, second attestation commit, or later repository commit invalidates the terminal state and requires the normal review lifecycle to resume.

## Default path rules

- Place reports under `<repo-root>/reports/` unless target-repository instructions override it.
- Use existing repository filename, language, and template rules.
- Preserve legacy names unless renaming is explicitly requested.
- Existing helper references in this Skill directory remain available for deterministic path construction.
- Reserve independent-final-review report paths before freezing the reviewed implementation HEAD.

## Boundaries

- Do not invent evidence.
- Do not convert missing current-HEAD CI into success.
- Do not let a concise PR comment replace the detailed report.
- Do not modify implementation merely to improve a report.
- Do not redefine report rules locally when `report-writer` is unavailable.
- In report-attestation mode, do not modify tasks, phases, design, Skills, workflows, configuration, implementation, handoffs, or non-reserved report paths.
- Do not create more than one report-attestation commit.
- Do not merge.

## Outputs

Return:

- report mode,
- authoritative source identities,
- reviewed implementation HEAD,
- reserved report path or paths,
- complete report body,
- persistence mode,
- created or updated outcome,
- report-attestation head or explicit absence,
- attestation diff validation,
- preserved unknowns and remaining risks,
- any persistence limitation.

## Completion condition

Complete when the required Skills have produced an evidence-faithful report and either normal persistence completed before the final-review freeze or one independent-final-review report-attestation commit satisfies every allowlist condition. A concrete target path or explicit persistence limitation is available, authoritative sources and uncertainty are preserved, no later repository commit exists in attestation mode, and no merge was performed.
