---
name: git-commit-manager
description: Prepare and create commits with appropriate scope, evidence, and cleanliness for the current task. Use after reviewable changes are ready, after verification has completed, or when a task needs to be checkpointed in a way that preserves clear history and supports PR creation.
---

# Git Commit Manager

Create clean, scoped commits.

## Goal

Produce commits that map cleanly to the current task and can be reviewed without guesswork.

## Execution owner

Run this skill as: `parent`

- Final staging and commit creation should remain a parent responsibility.

## Inputs

Before running this skill, gather:

- current task scope
- staged or candidate file set
- review evidence
- validation results or explicit non-validation state
- commit purpose and state: `review_target`, `final_task`, `normal_report`, or `report_attestation`

## Rules

- Keep commit scope aligned to the current task.
- Avoid mixing unrelated work.
- Default to one implementation commit for the current task.
- Additional commits are permitted when their purpose is a review target, normal report, or the one allowed report attestation; this is a lifecycle exception, not an independently reviewable task split.
- Split implementation content into multiple commits only when `git-workflow-manager` has determined that the task contains independently reviewable sub-units or when the user explicitly requests split history.
- Apply the purpose-specific gates below instead of requiring a review outcome for every commit.
- Stage intentionally; do not include noise or irrelevant generated files.
- Default to a multi-line commit message, not a subject-only commit.
- Write commit messages in Japanese unless the repository or the user explicitly requests another language.
- Prefer a fixed message structure so reviewers can scan intent, change scope, and validation quickly.

## Pre-commit checks

For every commit, confirm:

- task scope is correct
- tracking updates are included if they are part of the task

Then apply its purpose gate:

- `review_target`: relevant local validation and scope evidence exist; a review
  outcome is not required because this commit fixes the target before review.
- `final_task`: required validation and normal review or finding-closure
  outcome exist for the included implementation scope.
- `normal_report`: the report faithfully records available implementation or
  review evidence; it must not require its own future SHA.
- `report_attestation`: one exhaustive independent review has passed, or its
  same-reviewer bounded closure has passed for the updated reviewed HEAD; first
  parent, reserved-path allowlist, and no-later-commit conditions are explicit. This is
  the only post-review commit and its SHA is recorded externally after commit.

Keep commit, push, and CI-wait state distinct. `local_execution_available`
does not make a review-target or normal-report commit an automatic push.

## Commit message format

Use this default format unless the repository or the user explicitly requests a different convention:

```text
<type>(<scope>): <short imperative summary>

## 背景
- <この変更が必要な理由>

## 変更内容
- <主要な変更内容>

## 検証
- <実行したテスト・確認、または「未実施」>
```

If `scope` is not useful, omit it:

```text
<type>: <short imperative summary>
```

## Format rules

- Keep the first line concise, imperative, and specific.
- Preserve the `<type>(<scope>): ...` shape whenever `scope` helps GitHub readers scan the history quickly.
- Keep the subject focused on the user-visible or reviewer-relevant outcome, not the editing activity.
- Use a blank line between subject and body.
- Use Markdown section headings and bullets in the body by default.
- Always include `## 背景`, `## 変更内容`, and `## 検証` sections for non-trivial commits.
- Write the body at roughly the same granularity as a good user-facing change summary: a reviewer should understand what changed without reopening the diff immediately.
- In `## 変更内容`, prefer 2 to 4 concrete bullets that name the main files, skills, flows, or policies that changed when that naming helps understanding.
- For `docs` or `skills` commits, do not hide the real scope behind vague words like `整備した`; say which skills or design docs were added or updated.
- Expand `変更内容` to 2 or more bullets when one point is too compressed.
- Write `- 未実施` in `## 検証` when no verification was executed; never imply validation that did not happen.
- Split the work into multiple commits instead of hiding unrelated changes inside one long body.

## Type guidance

Choose the closest fit:

- `feat`: new behavior or capability
- `fix`: bug fix or behavior correction
- `refactor`: internal restructuring without intended behavior change
- `test`: tests added or updated
- `docs`: documentation-only changes
- `chore`: maintenance or tooling work with no direct feature/fix impact

## Scope guidance

When `scope` improves GitHub readability, keep it instead of omitting it.

Do not hardcode repository-specific scope candidates inside this skill.

Derive `scope` from the current repository context in this order:

1. current task wording in `tasks-status.md` or equivalent task tracking
2. current phase wording in `phases-status.md` when it sharpens the area better than the task title
3. recent commit history in the repository, so the scope naming stays consistent with nearby commits
4. touched files and the primary reviewer-facing area when tracking does not provide a good label

Choose the narrowest scope that still helps a reader predict the affected area from the GitHub commit list.

If recent commits already use a stable naming pattern for adjacent work, prefer following that pattern.

If no stable or helpful `scope` emerges from task context and recent commits, omit `scope` instead of inventing a repository-local taxonomy here.

## Good defaults

- Aim for a subject that is usually within about 50 to 72 characters.
- Aim for a body that is usually 3 sections with 1 to 3 bullets each.
- When multiple touched items matter to the reviewer, prefer naming them in the body instead of collapsing them into an abstract summary.
- Mention the most important verification command or check result in `## 検証`.

## Example

```text
fix(export): 集計シートの結合セル書式欠落を防ぐ

## 背景
- 集計シート再生成後に結合セルの罫線が失われていた

## 変更内容
- シート書き換え時に元の結合範囲メタデータを保持するようにした
- 結合復元後に罫線スタイルを再適用して見た目の崩れを防いだ

## 検証
- dotnet test
```

## Outputs

After this skill runs, the task has one coherent commit by default, or an explicitly justified split commit set suitable for PR submission.

## Completion condition

This skill is complete only when:

- commit scope is intentionally staged
- commit message follows the required format
- one coherent commit exists for the task by default, or a justified split commit set exists
