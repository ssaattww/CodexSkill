---
name: review-enforcer
description: Require normal review, fix verification, and an independent final review before a Codex task or PR is treated as complete. Use after implementation, after review fixes, before final progress sync, and before merge readiness is reported.
---

# Review Enforcer

Prevent completion without both iterative review and an independent final review.

## Goal

Make task completion impossible until:

1. a dedicated reviewer has completed the normal review cycle,
2. all required findings have been addressed or explicitly dispositioned, and
3. a fresh reviewer sub-agent has independently reviewed the final current HEAD.

## Execution owner

Run this skill as: `parent`.

- Parent owns completion gating and finding disposition.
- All review work remains mandatory sub-agent work.
- Parent review cannot replace either review stage.

## Review stages

### Normal review cycle

Use one dedicated reviewer sub-agent for:

- initial review,
- review of newly discovered scope within the same task,
- fix verification and re-review.

Reuse the same reviewer during this cycle when it remains available. This preserves finding identity and review criteria across fixes.

### Independent final review

After the normal review cycle is complete, start a different, fresh reviewer sub-agent for one independent final review of the final current HEAD.

The independent final reviewer must:

- not be the implementation sub-agent,
- not be the normal-cycle reviewer,
- not have implemented review fixes,
- be spawned with `fork_turns: "none"` unless a strictly bounded positive partial fork is explicitly justified,
- receive requirements, design, final diff, validation evidence, and the current HEAD,
- perform an independent pass before reading earlier review conclusions,
- inspect all changed files and direct contract dependencies,
- produce a separate final-review report.

A continuation of the normal reviewer session is not an independent final review.

## Inputs

Before running this skill, gather:

- task-scoped diff or changed-file set,
- surrounding repository context,
- relevant requirements and design,
- validation and CI evidence for the current HEAD,
- current task and PR identifiers,
- normal reviewer assignment and report,
- finding disposition and fix-verification evidence,
- parent model and any user reasoning-effort override,
- task-specific review criteria,
- Markdown check evidence when Markdown-related work is in scope.

## Required flow

1. Prepare the task-scoped diff while keeping broader workspace context available.
2. Resolve the current PR HEAD and use only validation and CI evidence associated with that HEAD.
3. For Markdown-related changes, run `markdown-word-checker` and record its result.
4. Pre-create the normal review report through `report-output-manager`.
5. Dispatch the normal reviewer through `sub-agent-task-manager`.
6. Use the parent model and `high` reasoning by default unless the user overrides it.
7. Require findings-first, severity-ordered review with locations where available.
8. Materialize the review result into the pre-created report.
9. Address required findings through the implementation flow.
10. Re-run the same normal reviewer for fix verification when available.
11. Repeat until required findings are resolved or explicitly dispositioned.
12. Freeze the final review target to the current PR HEAD.
13. Pre-create a separate independent-final-review report.
14. Spawn a new reviewer sub-agent with no inherited conversation history.
15. Require the new reviewer to perform an independent pass before consulting earlier findings.
16. If the independent reviewer finds a required issue, return to implementation and the normal review cycle.
17. After any subsequent fix, run fix verification and then start another fresh independent final reviewer against the new HEAD.
18. Only after the independent final review passes may progress sync and merge readiness proceed.

## Reviewer identity rules

- The implementation agent cannot review its own work.
- The normal reviewer cannot serve as the independent final reviewer.
- The independent final reviewer cannot implement its own findings.
- A new HEAD produced after final-review findings invalidates the previous independent final review.
- The replacement independent final review must target the new current HEAD.

## Markdown gate

- Treat `failed gate` as blocking unless the task intentionally introduces a stricter failing gate and records that state.
- Treat `needs user review` as stopped until the approved repository-specific setting is applied and lint is rerun.
- Treat `unsupported` as requiring explicit disposition; it is not success.
- Exact whitelist, `prh`, or target-exclusion changes require explicit user review and rerun evidence.
- Include focused/full results, aggregate gate state, and remaining risks in both applicable review reports.

## Finding disposition

- Address findings that break the intended normal path.
- If scope expansion requires a product decision, stop for user disposition.
- Record avoidable non-blocking concerns as held when the intended path remains usable.
- Do not convert missing review or missing evidence into `no findings`.
- CI success alone is not an independent review.

## Required reports

Normal review report must include:

- task and target HEAD,
- normal reviewer identity,
- review criteria,
- changed and dependent files,
- findings or explicit no findings,
- validation evidence,
- finding disposition,
- re-review evidence.

Independent final review report must include:

- target final HEAD,
- fresh reviewer identity,
- confirmation that it differs from the normal reviewer and implementation agent,
- confirmation of no inherited review conversation,
- independently selected coverage,
- findings or explicit no findings,
- held and unexplored areas,
- final verdict and merge-readiness impact.

## Rules

- Review one task or PR scope at a time.
- Review and independent final review are mandatory sub-agent work.
- Do not substitute parent review.
- Do not complete while either report is missing.
- Do not use an independent final review from an earlier HEAD.
- Do not silently omit the independent final review because the normal review had no findings.
- Do not cancel an in-flight reviewer merely because it is slow.
- Review requests must ask for review, not a diff summary.
- Reviewers may fill only the intended report sections and must preserve parent-owned report structure.

## Outputs

After this skill runs, there must be:

- a normal review report,
- fix-verification evidence when fixes occurred,
- a separate independent final review report for the current HEAD,
- explicit findings or explicit no findings from both applicable stages,
- a final disposition stating whether implementation follow-up is required,
- confirmation that merge has not been performed by the agent.

## Completion condition

This skill is complete only when:

- the normal review cycle has completed,
- required findings have been addressed or explicitly dispositioned,
- the current HEAD is explicit,
- a different fresh reviewer sub-agent independently reviewed that current HEAD,
- the independent final review report exists,
- no unresolved Blocking or High finding remains,
- any verdict-invalidating unexplored area is resolved,
- required current-HEAD validation evidence is recorded.

## Cross-cutting rule

If a repeated review-related instruction appears, call `feedback-points-manager`.