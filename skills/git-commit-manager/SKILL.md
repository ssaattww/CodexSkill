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

## Rules

- Keep commit scope aligned to the current task.
- Avoid mixing unrelated work.
- Default to one commit for the current task.
- Split one task into multiple commits only when `git-workflow-manager` has determined that the task contains independently reviewable sub-units or when the user explicitly requests split history.
- Make sure verification and review results exist before final task commit.
- Stage intentionally; do not include noise or irrelevant generated files.
- Default to a multi-line commit message, not a subject-only commit.
- Write commit messages in Japanese unless the repository or the user explicitly requests another language.
- Prefer a fixed message structure so reviewers can scan intent, change scope, and validation quickly.

## Pre-commit checks

Confirm:

- task scope is correct
- tests or validation have run as required
- review outcome exists
- tracking updates are included if they are part of the task

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
- Keep the subject focused on the user-visible or reviewer-relevant outcome, not the editing activity.
- Use a blank line between subject and body.
- Use Markdown section headings and bullets in the body by default.
- Always include `## 背景`, `## 変更内容`, and `## 検証` sections for non-trivial commits.
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

## Good defaults

- Aim for a subject that is usually within about 50 to 72 characters.
- Aim for a body that is usually 3 sections with 1 to 3 bullets each.
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
