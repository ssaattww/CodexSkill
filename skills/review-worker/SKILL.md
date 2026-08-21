---
name: review-worker
description: Review an implementation against requirements, design, changed files, dependencies, and validation evidence without depending on a Codex parent or ChatGPT chat runtime.
---

# Review Worker

## Goal

Perform a complete review of one immutable implementation target and return findings, coverage evidence, a verdict, and the exact reviewed identity to the caller.

## Required input

Use the output of `work-context-manager`, plus the implementation diff and available validation evidence. The caller owns reviewer creation, reviewer continuity, persistence, comments, handoff transport, and validation of any later report-attestation commit.

Required input includes:

- review mode,
- reviewed implementation HEAD,
- base and relevant commit range,
- accepted scope, requirements, and design,
- complete changed-file set and direct dependencies,
- current-HEAD validation and CI evidence,
- `verification_capability` and separate commit, push, and CI evidence state,
- previous findings and reviewed HEAD for fix verification,
- reviewer identity and independence evidence,
- any pre-reserved independent-final-review report path.

## Modes

### Initial review

Inspect the accepted scope, requirements, design, entire diff, every changed file, direct dependencies, tests, configuration, workflows, reports, tracking, and current-HEAD evidence.

### Fix verification

Verify each applicable finding by identity and reviewed HEAD. Inspect the fix diff, direct impact, affected contract, and sibling cases of the same defect class. Also inspect newly changed areas for additional defects.

Preserve each source finding's severity. A severity may change only through an explicit reclassification record containing the source severity, new severity, evidence-based reason, and approving authority. A transcription correction is an erratum, not an implicit reclassification, and must not silently rewrite historical review evidence.

### Independent final review

Review the frozen implementation HEAD independently. The reviewer must not have implemented the change, implemented review fixes, or served as the normal reviewer. Perform an independent pass before relying on previous review conclusions.

Before this mode starts, every implementation, design, workflow, configuration, task-tracking, handoff, and non-final report change must already be committed. For `local_execution_available`, freeze that validated local committed HEAD without pre-review push. For `remote_ci_only`, authorized pre-review push and matching current-HEAD CI are formal route evidence. The independent-final-review report path should be reserved before the reviewed implementation HEAD is frozen.

This mode performs exactly one exhaustive, independent coverage pass per task lifecycle. If its findings require a new reviewed HEAD, the same independent reviewer performs only finding- and CI-delta-limited closure verification after the completeness matrix is satisfied; it does not perform another exhaustive pass or introduce new review criteria.

### Independent final closure

Use this mode only with the same reviewer that completed the single exhaustive
independent review. Review the updated immutable HEAD against the carried
finding identities and CI delta only. Record the initial and closure reviewed
HEADs, preserve terminal-attestation conditions, and return `incomplete` if
the closure matrix is absent or scope expands.

## Required coverage

At minimum evaluate:

- requirement and design conformance,
- correctness and edge cases,
- scope discipline and unrelated changes,
- changed files and direct dependency impact,
- API, data, configuration, workflow, and compatibility effects,
- error handling and failure diagnostics,
- security and secret handling where applicable,
- tests and validation adequacy,
- current-HEAD CI evidence,
- report, tracking, and documentation accuracy,
- regression and maintainability risks.

For every required criterion, record one of:

- `checked_no_finding`,
- `checked_finding`,
- `held`,
- `not_applicable`,
- `unexplored`.

## Findings

Each finding must include identity, severity, origin, location, description, impact, evidence, and required action. Do not hide uncertainty or convert missing evidence into success.

Finding identity and severity are continuity-bearing review data. Fix verification and report consolidation must preserve them unless an explicit reclassification record is supplied. When a downstream report contains a severity transcription error, preserve the historical report and publish a current erratum identifying the source severity and the incorrect downstream value.

## Finding closure readiness

Before a caller requests finding-limited closure, require a completeness matrix
for each applicable finding. Every matrix row must identify and evidence:

- every required action,
- the production path that implements it,
- the actual composition fixture that exercises the composed behavior, and
- focused validation evidence.

If any required cell is absent, partial, blocked, or mismatched to the reviewed
HEAD, return it as incomplete and do not start closure review. This is a
review-evidence requirement; this runtime-neutral Skill does not schedule push
or CI waits.

## Verdicts

- `pass`: no required finding and no verdict-blocking unexplored area.
- `pass_with_held`: no required finding, with explicitly owned held items that do not block acceptance.
- `fail`: one or more required findings.
- `incomplete`: required review evidence, reviewer independence, or coverage is unavailable.
- `unstable`: the implementation target changed during review or the supplied evidence no longer belongs to the reviewed implementation HEAD.

## Reviewed identity and report attestation

The technical verdict applies to `reviewed_implementation_head`, not automatically to every later Git HEAD.

A caller may persist the independent-final-review report as one administrative report-attestation commit without invalidating the technical verdict only when all of these conditions are satisfied:

- the report path or paths were reserved before review,
- exactly one commit follows `reviewed_implementation_head`,
- that commit's first parent is `reviewed_implementation_head`,
- the diff changes only the reserved independent-final-review report path or paths,
- the report states the reviewed implementation HEAD and that the commit is an administrative attestation,
- no executable, Skill, design, workflow, configuration, task-tracking, handoff, or product file changed,
- no later repository commit exists,
- the caller validates and records the attestation diff.

This does not transfer the verdict to new implementation content. It creates a completion identity pair:

```yaml
reviewed_implementation_head: full_sha
report_attestation_head: full_sha | null
```

Any other post-review commit invalidates completion. Return to normal fix verification, update the reviewed HEAD, and use the same independent reviewer only for bounded finding/CI-delta closure before a new attestation decision.

## Boundaries

- Do not implement fixes while acting as reviewer.
- Do not perform runtime-specific report persistence or handoff transport.
- Do not merge.
- If the implementation target changes after review, the previous verdict does not apply to the new implementation target.
- Do not review the content of an attestation commit as though it were implementation; validate it only against the administrative allowlist above.

## Output contract

Return:

- review mode,
- `reviewed_implementation_head`,
- `initial_independent_reviewed_head` and any closure reviewed HEAD,
- independent-review continuity and bounded finding/CI-delta closure scope,
- base and commit range,
- reviewer identity and independence evidence,
- required coverage dispositions,
- full findings,
- finding completeness matrix with a disposition for every required action,
- any explicit severity reclassification records,
- held items,
- unexplored areas,
- validation assessment,
- verdict,
- remaining risks,
- next action,
- `reserved_report_paths`,
- `report_attestation_allowed: true | false`,
- the exact conditions the caller must validate before accepting an attestation head.

## Completion condition

A review round is complete when the immutable reviewed implementation HEAD is explicit, all required coverage has a disposition, findings and uncertainty are evidence-based, finding identity and severity continuity are preserved or explicitly reclassified, the verdict follows the stated rules, and no implementation or merge was performed.

The overall independent-final-review lifecycle is complete only when either:

- no repository report commit is required and the verdict remains attached to the unchanged reviewed implementation HEAD, or
- one validated report-attestation head satisfies every allowlist condition and no later repository commit exists.
