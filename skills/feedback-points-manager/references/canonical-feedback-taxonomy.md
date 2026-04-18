# Canonical Feedback Taxonomy

Open this only when you need a canonical category value or a stable duplicate-group name.

`<repo-root>/feedback-points/feedback-points.md` uses a canonical `カテゴリ` value from this list.

## Categories

- `delegation`: delegation policy, who executes investigation/review/test
- `planning`: task/phase planning and sequencing
- `tracking`: status file sync and progress visibility
- `review`: review process, review scope, re-review loop
- `testing`: TDD, unit/integration/e2e verification policy
- `git-workflow`: branch/commit/PR workflow rules
- `design-doc`: design-first policy and design sync discipline
- `release-ops`: CI/CD, release, packaging, operational automation
- `cost-control`: execution-cost and retry/stability policies
- `handover`: restart/handover continuity and context recovery
- `other`: fallback only when no category fits

## Duplicate Group Naming

Use stable snake_case names that represent reusable intent.

Examples:

- `delegate_review_to_codex`
- `enforce_task_scoped_review`
- `sync_tasks_phases_before_implementation`
- `require_breaking_change_log_entry`

Do not encode issue numbers in group names.

## Categorization Rules

1. classify by process intent, not by implementation area
2. prefer existing duplicate groups over creating new ones
3. if a point can fit multiple categories, choose the one that drives the operational action
