# Skillization Operations

Open this only when you need issue creation flow, routing to another skill, or the required output for this run.

## Skill repository issue flow

When a duplicate group is reusable across repositories, create an issue in the skill repository.

At commit timing for a skill/process improvement loop, do not stop at the commit alone. Create or confirm the follow-up issue in the skill repository before considering the loop handed off.

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

The issue body must preserve the full FP meaning, not just a short summary. Carry over:

- duplicate group
- original FP wording
- why it recurred or still matters
- related skills
- unresolved scope or remaining gap
- references needed to continue the loop

Once the issue exists:

1. remove the active FP row from `feedback-points/feedback-points.md`
2. move it to `feedback-points/feedback-points-backlog.md` or otherwise archive it outside the active ledger
3. include the created issue URL in `根拠リンク`

Do not open duplicate issues for the same group unless scope materially changed.

## Recommended routing

- release/CI/version governance -> `design-doc-maintainer` plus audit report only
- issue requirement acquisition fallback -> `feedback-issue-intake-fallback-manager`
- autonomy vs stop-condition boundary -> `feedback-autonomy-boundary-manager`
- coding standards enforcement regressions -> `feedback-coding-standards-enforcer`
- feedback noise and mixed-scope cleanup -> `feedback-points-sanitizer`

## Skill lifecycle execution

If classification is `new skill candidate`:

1. prepare a concise user recommendation
2. explain why existing skills are insufficient
3. stop before implementation

If classification is `existing skill update`:

1. identify the owning skill
2. create or switch to a dedicated branch in the skill repository
3. use focused sub-agents for narrow analysis or review when useful
4. update the skill and any references/scripts
5. collect evidence if behavior or routing changed
6. commit the change
7. create or confirm the follow-up issue if ongoing loop tracking still matters after the commit
8. create a PR
9. tell the user the PR is ready to review

Suggested supporting skills:

- branch/commit/PR execution -> `git-workflow-manager`
- report filename and placement -> `report-output-manager`

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
- `次アクション対応`
- issue creation result, or why it was skipped
