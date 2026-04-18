# feedback-points skillization analysis (2026-04-18)

## Scope

Analyze `tasks/feedback-points.md` (ExcelReport) and extract reusable process rules that should be skillized in `CodexSkill`.

Reviewed skills:

- `codex-delegation-executor` and all related core workflow skills
- GitHub plugin skills used for issue/PR/CI workflows

## Key findings

1. A large portion of active FP entries are process rules and can be skillized.
2. Some FP entries are issue-specific feature decisions and should not stay as reusable process rules.
3. Release-related FP entries require a strict operational boundary:
   - NuGet pre-release flow is fully automated (`master` push trigger).
   - Stable release is user manual.
   - Agent must not edit workflow/publish settings unless the user explicitly instructs.

## Implemented skill additions

Added new skills in this repo:

- `skills/feedback-issue-intake-fallback-manager/SKILL.md`
- `skills/feedback-autonomy-boundary-manager/SKILL.md`
- `skills/feedback-coding-standards-enforcer/SKILL.md`
- `skills/feedback-points-sanitizer/SKILL.md`

Updated:

- `skills/feedback-points-manager/SKILL.md`
  - canonical handling for noisy feedback cleanup
  - skillization issue flow
  - routing guidance for common duplicate groups
  - release-related routing changed to audit/report-only guidance

## Rules converted to skills

- FP111 class: issue intake fallback when `gh` path fails
- FP21/141/144 class: autonomy with explicit stop boundaries
- FP19 class: coding-standard enforcement (including XML docs on public/protected APIs)
- mixed noisy FP management: sanitize, deduplicate, and keep only reusable process points

## Not skillized in this pass

- Release automation mutation workflow as a dedicated skill
  - excluded by user policy (automation-owned, explicit user instruction required before edits)
- Feature/issue-specific DSL/design decisions
  - these belong to issue/task/design tracking, not reusable process skills

## Suggested next operation

Run `feedback-points-sanitizer` against current active FP set, then re-register only high-signal reusable process points and map each to related skills.
