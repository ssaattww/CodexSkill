---
name: review-worker
description: Review an implementation against requirements, design, changed files, dependencies, and validation evidence without depending on a Codex parent or ChatGPT chat runtime.
---

# Review Worker

## Goal

Perform a complete review of one target HEAD and return findings, coverage evidence, and a verdict to the caller.

## Required input

Use the output of `work-context-manager`, plus the implementation diff and available validation evidence. The caller owns reviewer creation, reviewer continuity, persistence, comments, and handoff transport.

## Modes

### Initial review

Inspect the accepted scope, requirements, design, entire diff, every changed file, direct dependencies, tests, configuration, workflows, and current-HEAD evidence.

### Fix verification

Verify each applicable finding by identity and reviewed HEAD. Inspect the fix diff, direct impact, affected contract, and sibling cases of the same defect class. Also inspect newly changed areas for additional defects.

### Independent final review

Review the final current HEAD independently. The reviewer must not have implemented the change, implemented review fixes, or served as the normal reviewer. Perform an independent pass before relying on previous review conclusions.

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
- report and documentation accuracy,
- regression and maintainability risks.

For every required criterion, record one of:

- `checked_no_finding`,
- `checked_finding`,
- `held`,
- `not_applicable`,
- `unexplored`.

## Findings

Each finding must include identity, severity, origin, location, description, impact, evidence, and required action. Do not hide uncertainty or convert missing evidence into success.

## Verdicts

- `pass`: no required finding and no verdict-blocking unexplored area.
- `pass_with_held`: no required finding, with explicitly owned held items that do not block acceptance.
- `fail`: one or more required findings.
- `incomplete`: required review evidence or coverage is unavailable.
- `unstable`: target HEAD changed or evidence no longer belongs to the reviewed HEAD.

## Boundaries

- Do not implement fixes while acting as reviewer.
- Do not perform runtime-specific report persistence or handoff transport.
- Do not merge.
- If HEAD changes after review, the previous verdict does not apply to the new HEAD.

## Output contract

Return review mode, reviewed HEAD, required coverage dispositions, findings, held items, unexplored areas, validation assessment, verdict, remaining risks, and next action.

## Completion condition

Complete when the final reviewed HEAD is explicit, all required coverage has a disposition, findings and uncertainty are evidence-based, the verdict follows the stated rules, and no implementation or merge was performed.
