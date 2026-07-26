---
name: review-enforcer
description: Enforce the shared normal review cycle and independent final review through Codex reviewer sub-agents before a task or PR is treated as complete. Use after implementation, after review fixes, and before final progress sync or merge readiness is reported.
---

# Review Enforcer

## Goal

Apply the shared review lifecycle through Codex-specific reviewer dispatch and completion gates.

## Shared contracts

Follow:

- [Common Work Contract](../../shared/workflow/common-work-contract.md)
- [Review Contract](../../shared/workflow/review-contract.md)
- [Report Contract](../../shared/workflow/report-contract.md)

These files are the canonical review and evidence semantics shared with ChatGPT workers. This Skill owns only Codex reviewer identity, sub-agent dispatch, Markdown gates, and lifecycle enforcement.

## Execution owner

Run this Skill as: `parent`.

- Parent owns completion gating and finding disposition.
- All technical review work is mandatory reviewer sub-agent work.
- Parent review cannot replace the normal reviewer or the independent final reviewer.

## Inputs

Before running this Skill, gather:

- task-scoped diff and complete changed-file set,
- surrounding repository context and direct dependencies,
- requirements and design,
- current PR HEAD and matching validation or CI evidence,
- normal reviewer assignment and report when one exists,
- previous findings and fix-verification evidence,
- implementation agent identity,
- parent model and user reasoning-effort override,
- task-specific risk criteria,
- Markdown check evidence when Markdown is in scope.

## Codex reviewer lifecycle

### Normal review cycle

Use one dedicated reviewer sub-agent for the initial review and later fix verification while that reviewer remains available.

- Preserve finding identity, selected criteria, reviewed HEAD, and fix context.
- If the reviewer must be replaced, record the identity change and give the replacement the complete normal-cycle evidence.
- Execute `initial_review` and `fix_verification` according to the shared Review Contract.

### Independent final review

After the normal cycle converges, start a different fresh reviewer sub-agent for `independent_final_review`.

The independent reviewer must:

- differ from the implementation agent,
- differ from the normal reviewer,
- not have implemented review fixes,
- use `fork_turns: "none"` unless a strictly bounded positive partial fork is explicitly justified,
- receive requirements, design, final diff, changed files, direct dependencies, current HEAD, and target-HEAD validation evidence,
- perform an independent pass before reading earlier conclusions,
- produce a separate independent-final-review report.

A continuation of the normal reviewer session is not an independent final review.

## Required flow

1. Resolve the current PR HEAD and retain only validation and CI evidence associated with that HEAD.
2. Prepare the task-scoped diff while keeping broader repository context available.
3. For Markdown-related changes, run `markdown-word-checker` and record the result.
4. Pre-create the normal review report through `report-output-manager`.
5. Dispatch the normal reviewer through `sub-agent-task-manager` with the shared contract paths.
6. Use the parent model and `high` reasoning by default unless the user overrides it.
7. Require the reviewer to execute the shared Review Contract and materialize its result into the report.
8. Address required findings through the implementation flow.
9. Reuse the normal reviewer for fix verification when available.
10. Repeat the bounded normal cycle until required findings are resolved, dispositioned, or the shared contract returns `unstable`.
11. Freeze the independent-final-review target to the current PR HEAD.
12. Pre-create a separate independent-final-review report.
13. Spawn a new reviewer sub-agent with no inherited review conversation.
14. Require the independent reviewer to execute the shared Review Contract before consulting earlier findings.
15. If a required finding causes a fix, return to implementation and normal fix verification.
16. After the HEAD changes, start another fresh independent final reviewer against the new HEAD.
17. Allow progress sync and merge-readiness reporting only after the unchanged current HEAD passes independent final review.

## Markdown gate

- Treat `failed gate` as blocking unless the task intentionally introduces a stricter failing gate and records that state.
- Treat `needs user review` as stopped until the approved repository-specific setting is applied and lint is rerun.
- Treat `unsupported` as requiring explicit disposition; it is not success.
- Exact whitelist, `prh`, or target-exclusion changes require explicit user review and rerun evidence.
- Include focused and full results, aggregate gate state, and remaining risks in applicable review reports.

## Codex adapter rules

- Review one task or PR scope at a time.
- Do not substitute parent review for reviewer sub-agent work.
- Do not complete while either required report is missing.
- Do not reuse an independent final review from an earlier HEAD.
- Do not cancel an in-flight reviewer merely because it is slow.
- Review requests ask for review, not a diff summary.
- Reviewers may fill only intended report sections and must preserve parent-owned report structure.
- Reviewers do not implement findings or merge.

## Outputs

After this Skill runs, there must be:

- a normal review report,
- fix-verification evidence when fixes occurred,
- a separate independent-final-review report for the unchanged current HEAD,
- reviewer identity and independence evidence,
- findings or explicit no findings from each applicable stage,
- coverage, held, unexplored, validation, CI, verdict, and next-action evidence required by the shared contracts,
- confirmation that no merge was performed.

## Completion condition

This Skill is complete only when the shared Common Work and Review contracts are satisfied, the normal cycle has converged, a different fresh reviewer has passed independent final review of the unchanged current HEAD, required reports and current-HEAD evidence exist, no unresolved Blocking or High finding remains, no verdict-invalidating unexplored area remains, and no merge was performed.

## Cross-cutting rule

If a repeated review-related instruction appears, call `feedback-points-manager`.
