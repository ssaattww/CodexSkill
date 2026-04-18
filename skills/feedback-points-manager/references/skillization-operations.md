# Skillization Operations

Open this only when you need issue creation flow, routing to another skill, or the required output for this run.

## Skill repository issue flow

When a duplicate group is reusable across repositories, create an issue in the skill repository.

Priority:

1. GitHub app issue creation tool
2. `gh issue create`
3. save an issue draft markdown in `reports/` if write access exists but issue creation is blocked

Title format:

- `[skillization] <duplicate-group>: <short summary>`

Body:

- use `skillization-issue-template.md`
- or generate with:
  - `scripts/build_skillization_issue.sh --group <group> --fps <fp-list> --summary <summary> --proposal <skill-or-change>`

Do not open duplicate issues for the same group unless scope materially changed.

## Recommended routing

- release/CI/version governance -> `design-doc-maintainer` plus audit report only
- issue requirement acquisition fallback -> `feedback-issue-intake-fallback-manager`
- autonomy vs stop-condition boundary -> `feedback-autonomy-boundary-manager`
- coding standards enforcement regressions -> `feedback-coding-standards-enforcer`
- feedback noise and mixed-scope cleanup -> `feedback-points-sanitizer`

## Pre-write review for active ledger updates

Before writing to `<repo-root>/feedback-points/feedback-points.md`, run a classification review with `feedback-points-sanitizer` when any are true:

- the point is new
- the point is materially rewritten
- the point may be a duplicate or near-duplicate
- classification is ambiguous
- the active ledger already looks noisy or mixed-scope

Prefer an independent sub-agent pass for this review when available.

The review should return one of:

- keep active
- merge into existing duplicate group
- move to backlog
- skip as noise or non-process content

## Required output after each run

Leave clear evidence in chat or report:

- whether a point was added or merged
- whether pre-write review ran and its decision
- duplicate group decision
- skillization status decision and reason
- related skill update or new-skill decision
- issue creation result, or why it was skipped
