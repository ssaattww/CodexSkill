---
name: review-enforcer
description: Require a dedicated review step for every task before the task is treated as complete. Use when implementation appears done, before final progress updates, before commit/PR closure, or whenever a review result must be captured and addressed task by task.
---

# Review Enforcer

Prevent completion without review.

## Goal

Make task completion impossible until review has run and its outcome is recorded.

## Required flow

1. Prepare a task-scoped diff.
2. Run review for that task only as a `sub-agent` task through `sub-agent-task-manager`.
3. Save review output into `reports/`.
4. Address findings if any.
5. Re-run review if required.
6. Only then allow progress sync and Git submission.

When creating a new review report file, call `report-output-manager`.

## Rules

- Review one task at a time.
- Do not batch multiple unrelated tasks into one review.
- Do not mark a task complete without recorded review evidence.
- Distinguish between “no findings” and “review not run”.
- Review is mandatory sub-agent work.

## Required report contents

Include:

- task identifier
- scope reviewed
- reviewer or sub-agent used
- findings summary
- disposition of findings
- final outcome

## Cross-cutting rule

If a repeated review-related instruction appears, call `feedback-points-manager`.
