---
name: review-policy
description: Build a risk-based review plan, select stable review criteria, control initial/fix/final review stages, and decide pass, fail, or unstable from a structured ReviewResult. Use before review-core and after each review stage. Do not inspect product code, render reports, or create repository artifacts.
---

# Review Policy

Select the necessary review depth and stop review at a defined boundary.

## Goal

Create a bounded review plan from risk, then evaluate a structured result without relying on report prose.

## Execution owner

Run this skill as: `parent or direct review caller`

- In Codex, `review-enforcer` calls this skill.
- In standalone use, the current review worker may apply it directly.
- This skill does not dispatch agents.

## Inputs

Before planning, gather:

- authoritative requirements and design
- changed targets and direct dependency boundaries
- explicit non-goals and ownership boundaries
- previous findings and current review stage
- available test, CI, artifact, and HEAD-SHA evidence
- whether the scope or risk changed after the previous stage

## Criterion source

Read [references/code-review-criteria.md](references/code-review-criteria.md).

- Universal criteria are always selected.
- Only risk modules selected by the risk profile are required.
- Non-selected modules do not need individual `not_applicable` rows.
- The criterion file is the only source of detailed review items.

## Risk profile

### Low

Use when the change is non-behavioral and locally bounded, such as wording, formatting, a comment, or a mechanical rename that does not alter a public or workflow contract.

- Required: universal core
- Add `M-DOC` when Markdown, Skill, design, or report structure changes
- `cold_final` is not required

### Medium

Use when the change affects behavior, a public/shared contract, test or CI wiring, workflow control, or several dependent files, but does not directly create data-loss, untrusted-input, concurrency, or external-process risk.

- Required: universal core and every applicable module
- `cold_final` is required

### High

Use when the change affects state or persistence, untrusted parsing, identity or revision binding, concurrency or atomicity, external process/network/filesystem behavior, security, data loss, or latency-sensitive runtime behavior.

- Required: universal core and every applicable module
- `cold_final` is required

## Risk-module selection

Select modules by changed behavior, not by file extension.

- `M-STATE`: state, persistence, cache, migration, reviewed ranges
- `M-INPUT`: parser, deserializer, diff, URI, external payload, configuration
- `M-ATOMIC`: multiple writes, CAS, transaction, source conflict, concurrency
- `M-IDENTITY`: repository/context/revision/file/path/cache identity
- `M-EXTERNAL`: Git, subprocess, network, connector, filesystem
- `M-RUNTIME`: UI responsiveness, Extension Host, large input, complexity
- `M-DOC`: Skill, design, report, workflow policy, documentation-only behavior

If a module becomes applicable after review starts, do not silently widen the current stage. End it as `incomplete`, update the risk plan, and begin a new `initial` stage for the materially changed scope.

## Standard review lifecycle

A stable scope uses three stages.

### 1. Initial comprehensive review

- Run once for the stable scope and risk plan.
- Inspect every changed target, direct dependency boundary, universal criterion, and selected risk module.
- Continue through all planned criteria after finding Blocking or High issues.
- Report the complete finding set together instead of stopping at the first defect.
- Do not add unplanned modules during the same run.

### 2. Fix verification

- Reuse the same reviewer when available.
- Check previous finding IDs, the fix diff, direct impact, and sibling cases of the same mechanism.
- Recheck regression tests related to those findings.
- Do not explore unrelated modules or arbitrary previously untouched code.
- If the implementation materially changes scope or risk, stop verification and start a new initial cycle.
- At most two fix-verification executions are allowed for the same initial finding set. If a third would be needed, return `unstable` and require design rework or PR split.

### 3. Cold final review

- Required only for medium and high risk.
- Run once on the final HEAD with a fresh reviewer or `fresh_no_history` context.
- Confirm the selected plan, final evidence, and merge-candidate conditions.
- Do not start another ordinary review loop after this stage.
- A new independent Blocking or High finding in cold final produces `verdict=unstable` and `follow_up=design_rework` or `split_required`.

## Merge-candidate conditions

Set `merge_candidate=true` only when all conditions hold:

- no Blocking or High finding remains
- all universal and selected-module criteria are dispositioned
- no `unexplored` entry can invalidate a high-risk decision
- held concerns are non-blocking, reasoned, and compatible with the intended normal path
- validation evidence belongs to the reviewed final HEAD when HEAD identity exists
- medium/high risk completed one cold final review
- cold final introduced no new Blocking or High finding
- verdict is `pass` or `pass_with_held`

This flag is advisory. No review skill merges a PR.

## Unstable conditions

Return `verdict=unstable` and stop adding review rounds when any condition holds:

- cold final finds a new independent Blocking or High issue
- more than two focused fix-verification executions are required for the same initial finding set
- repeated `coverage_miss` findings show that the current risk plan or PR boundary is unreliable
- scope keeps changing so the same review cycle cannot retain a stable target
- one PR combines independent high-risk concerns that cannot be reviewed as one coherent unit

Use:

- `follow_up=design_rework` when architecture or contract must be reconsidered
- `follow_up=split_required` when reviewability requires smaller PRs or work items

A materially redesigned or split scope may begin a new review cycle with a new `review_id`; it is not another pass in the unstable cycle.

## Result evaluation

Use the fixed values in `review-core/references/review-contract.md`.

- `pass`: merge-candidate conditions hold and no held concern remains
- `pass_with_held`: merge-candidate conditions hold with reasoned non-blocking held concerns
- `fail`: fixable findings remain within a stable review cycle
- `incomplete`: planned evidence or coverage is unavailable, or the risk plan changed
- `unstable`: stop conditions require design rework or split

Finding origin must distinguish:

- pre-existing issue
- introduced change
- introduced fix
- coverage miss
- out-of-scope issue

## Outputs

Before review, output a plan containing:

- risk profile
- selected module IDs
- planned criterion IDs
- stage
- reviewer-context requirement
- cold-final requirement

After review, output a policy decision containing:

- verdict
- follow-up
- stop reason
- merge-candidate flag
- whether another stage is allowed

## Completion condition

This skill is complete only when:

- the risk plan is explicit and bounded
- selected criterion IDs come from the canonical source
- lifecycle stage and stop conditions are explicit
- final state is determined from structured fields, not Markdown prose
