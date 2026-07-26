---
name: review-enforcer
description: Run the Codex review lifecycle as a parent-side gate. Build a risk-based ReviewRequest, dispatch review-core for a structured ReviewResult, enforce bounded initial/fix/final stages, and then hand the result to rendering and artifact adapters. Use before progress sync, commit, or PR completion. Do not perform the review itself or make report prose the workflow state.
---

# Review Enforcer

Run a bounded Codex review cycle and gate task completion on a structured result.

## Goal

Obtain a valid `ReviewResult`, apply explicit stop conditions, and keep review judgment separate from presentation and repository artifacts.

## Execution owner

Run this skill as: `parent`

- Parent owns lifecycle orchestration, reviewer assignment, and task completion gating.
- `review-core` owns the actual review judgment.
- `review-policy` owns risk selection, lifecycle scope, merge-candidate conditions, and unstable conditions.
- `review-result-renderer` owns presentation.
- `report-output-manager` owns repository report artifact placement.

## Inputs

Before running this skill, gather:

- task, Issue, PR, branch, commit, or diff identifier
- authoritative requirements, design, repository instructions, scope, and non-goals
- changed targets and direct dependency boundaries
- available test, command, CI, artifact, and immutable HEAD-SHA evidence
- previous structured findings and current lifecycle stage
- active reviewer assignment, if any
- parent model and user override of reviewer reasoning effort
- whether repository report and PR comment artifacts are required

## Required flow

1. Call `review-policy` to classify `low | medium | high`, select risk modules, select stable criterion IDs, and choose `initial | fix_verification | cold_final`.
2. Build a `ReviewRequest` using `review-core/references/review-contract.md`.
3. When Markdown-related evidence applies, call `markdown-word-checker` and add its structured evidence to the request. Do not make the Markdown report itself the review input contract.
4. Select the reviewer profile:
   - initial and fix verification: reuse the same reviewer when available
   - cold final: use a fresh reviewer or `fresh_no_history`
   - model: parent model
   - reasoning: `high` unless the user overrides it
5. Call `sub-agent-task-manager` in `structured_result` evidence mode and dispatch a reviewer that reads and executes `review-core`.
6. Require the reviewer to return one `ReviewResult`; do not ask it to choose a report path, edit a template, or write a repository file.
7. Validate the returned contract and call `review-policy` for verdict, follow-up, stop reason, merge-candidate, and whether another stage is permitted.
8. Follow the bounded lifecycle:
   - initial: finish the full planned coverage even after findings
   - fix verification: check previous findings, fixes, direct impact, and sibling cases only
   - cold final: medium/high risk only, one fresh pass on final HEAD
9. If policy returns `unstable`, stop ordinary review rounds and route to design rework or PR split. Do not request another incremental re-review.
10. After the structured result is final for the stage, optionally call `review-result-renderer` for Markdown, chat, or concise PR-comment text.
11. When repository artifacts are required, pass already-rendered text to `report-output-manager`; repository write failure does not change the `ReviewResult`.
12. Use the structured result, not report wording, to decide whether progress sync and Git submission may continue.

If mandatory reviewer dispatch is unavailable in the current Codex mode, stop and report that the Codex runner cannot execute. Direct or ChatGPT use should invoke `review-core` through the separate standalone flow tracked by Issue #51 rather than silently replacing this runner.

## Lifecycle rules

- One stable scope has one initial comprehensive review.
- Fix verification must stay focused and may run at most twice for the same initial finding set.
- Medium/high risk has one cold final review.
- Scope or risk change ends the current stage and starts a new initial cycle with a new review ID.
- A new independent Blocking/High in cold final, repeated coverage miss, or a third required fix-verification produces `unstable`.
- Resolved GitHub comments alone do not prove review completion.
- Fix verification does not expand into arbitrary unrelated unexplored areas.

## Rules

- Review one coherent task or PR scope at a time.
- Do not perform product-code edits from this skill.
- Do not embed detailed criterion text; read it from `review-policy`.
- Do not select a Markdown template or prescribe headings to the reviewer.
- Do not require the reviewer to edit a file.
- Do not derive verdict, follow-up, or merge-candidate from prose.
- Do not select every risk module by default.
- Do not ignore direct dependencies that are part of the selected plan.
- Do not stop initial review at the first finding.
- Do not widen fix verification beyond the bounded policy.
- Do not continue review after `unstable` without material design or scope change.
- Do not use another branch's or repository-latest CI run when immutable HEAD evidence exists.
- Do not merge a PR.

## Artifact boundary

The review decision and artifact pipeline are separate:

```text
review-policy
  -> ReviewRequest
  -> review-core
  -> ReviewResult
  -> review-result-renderer
  -> rendered text
  -> report-output-manager / GitHub adapter
```

- Review completion is represented by `ReviewResult`.
- Repository workflow completion may additionally require a persisted report and concise PR comment.
- Renderer or artifact failure is reported separately and never rewrites review findings.

## Outputs

Return:

- review plan
- reviewer assignment and context
- structured `ReviewResult`
- policy decision and allowed next stage
- rendered artifact references when requested
- explicit stop or follow-up route

## Completion condition

The review gate is complete only when:

- a valid `ReviewResult` exists
- every planned criterion has one disposition
- lifecycle and stop conditions have been applied
- Blocking/High, unexplored high-risk areas, and validation evidence are reflected in the structured verdict
- repository artifacts required by the surrounding Codex workflow have been produced or their separate artifact failure is explicit
- progress and Git submission proceed only when policy permits them

## Cross-cutting rule

If repeated review-process failures appear, call `feedback-points-manager`.
