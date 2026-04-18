---
name: feedback-points-manager
description: Maintain feedback-points.md as a cross-cutting record of reusable workflow lessons, repeated process failures, skill adoption status, and skillization candidates. Use from any skill whenever a new process-related instruction appears, a repeated point reoccurs, a workflow problem is discovered, or a decision must be made about whether a repeated point should become a skill.
---

# Feedback Points Manager

Maintain `feedback-points.md` as the system of record for reusable workflow lessons.

## Goal

Capture process-level feedback, detect repetition, and decide when repeated points should be skillized.

## This skill is cross-cutting

Allow any other skill to call this skill.

Typical callers include:

- `development-orchestrator`
- `task-consistency-manager`
- `design-doc-maintainer`
- `codex-delegation-executor`
- `review-enforcer`
- `progress-sync-manager`
- `git-workflow-manager`
- `execution-cost-stabilizer`

## Run this skill

Run this skill when:

- a new process instruction appears
- a known process problem happens again
- workflow mistakes keep recurring
- a point seems reusable across repositories
- you need to decide if a point should become a skill or a skill update

## Inputs to read

Read in this order:

1. `tasks/feedback-points.md` (required if present)
2. `tasks/feedback-points-backlog.md` (if present)
3. related `tasks-status.md` and `phases-status.md` only when needed for context

## Scope filter

Record workflow and development-method points, not issue-specific feature design details.

Good examples:

- delegation policy
- TDD policy
- review policy
- progress update policy
- task sizing policy
- Git workflow policy
- restart or handover policy

Do not keep one-off feature specifications here if they belong in design docs, reports, tasks, or phases.

## Canonical feedback format

Standardize on one cross-repository format.

`tasks/feedback-points.md` should use this active table schema:

- `FP`
- `内容`
- `カテゴリ`
- `重複グループ`
- `skill化状態`
- `関連skill`
- `状態`
- `記録日`
- `最終更新日`
- `根拠リンク`

`tasks/feedback-points-backlog.md` should keep completed/closed points.
Backlog may contain a one-time `Legacy Archive` section in old schema for historical preservation.

`カテゴリ` and `重複グループ` naming rules:

- see [references/canonical-feedback-taxonomy.md](references/canonical-feedback-taxonomy.md)

### Canonical statuses

`状態`:

- `記録`
- `対応中`
- `対応済み`
- `不要`

`skill化状態`:

- `未整理`
- `検討中`
- `skill化済み`
- `不要`

## Bootstrap cleanup rule

If current feedback data contains noise or stale entries, do a one-time cleanup:

1. move current active rows into `tasks/feedback-points-backlog.md` as `Legacy Archive` without conversion
2. rebuild `tasks/feedback-points.md` active section with canonical header only
3. re-register only high-signal active points that still affect current operations
4. continue FP numbering without reuse

## Duplicate grouping rules

When a new point appears:

1. detect whether an equivalent intent already exists
2. append the FP to that duplicate group
3. avoid creating isolated near-duplicate rows
4. keep traceability to all source FP IDs

Group by intent, not by literal wording.

## Skillization decision rule

Default threshold:

- first occurrence: record only
- second occurrence: set to `検討中`
- third occurrence or more: skillize by default unless clearly one-off

Early skillization is allowed even at first occurrence when all are true:

- cross-repository applicability is obvious
- recurrence cost is high
- omission risk is high if not automated by skill

Do not skillize when the point is:

- issue-specific design content
- one-time feature decision
- externally constrained and not reusable as workflow

## Skillization actions

When a point is skillized:

1. set status to `skill化済み`
2. set `関連skill`
3. keep links to source FP IDs
4. rewrite wording from incident-specific to reusable rule

If existing skill is close but insufficient, file a skill-improvement task instead of creating overlapping new skills.

## Skill repository issue flow

When a duplicate group is reusable across repositories, create an issue in the skill repository.

Use this priority:

1. GitHub app issue creation tool
2. `gh issue create`
3. if neither is available, save an issue draft markdown in `reports/`

Title format:

- `[skillization] <duplicate-group>: <short summary>`

Issue body template:

- use [references/skillization-issue-template.md](references/skillization-issue-template.md)
- or use script for draft/create:
  - draft body only:
    - `scripts/build_skillization_issue.sh --group <group> --fps <fp-list> --summary <summary> --proposal <skill-or-change>`
  - create via `gh`:
    - `scripts/build_skillization_issue.sh --group <group> --fps <fp-list> --summary <summary> --proposal <skill-or-change> --repo <owner/repo> --title "[skillization] <group>: <summary>" --create`

Do not open duplicate issues for the same group unless scope has materially changed.

## Recommended routing for common groups

When a recurring group maps cleanly to an existing skill, prefer updating that skill first.

- release/CI/version governance -> `design-doc-maintainer` + audit report only (no workflow/publish edits unless user explicitly requests)
- issue requirement acquisition fallback -> `feedback-issue-intake-fallback-manager`
- autonomy vs stop-condition boundary -> `feedback-autonomy-boundary-manager`
- coding standards enforcement regressions -> `feedback-coding-standards-enforcer`
- feedback noise and mixed-scope cleanup -> `feedback-points-sanitizer`

## Required output after each run

After running this skill, leave clear evidence in chat or report:

- whether a new point was added or merged
- duplicate group decision
- skillization status decision and reason
- related skill update/new-skill decision
- issue creation result (issue URL/number, or draft file path)

## Strong rules

- Always make an explicit skillization decision for repeated process points.
- Keep process feedback and feature specifications separated.
- Keep canonical table fields current when recurrence status changes.
