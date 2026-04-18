---
name: design-executor
description: Execute concrete design-document updates after design scope has been decided. Use when a design doc, breaking-changes log, or related design artifact must be edited as implementation work.
---

# Design Executor

Perform the actual design-document editing work.

## Goal

Turn an already-decided design change into concrete document updates without re-deciding scope.

## Execution owner

Run this skill as: `parent`

- This skill describes the execution work for design-document editing.
- `codex-delegation-executor` may assign that editing work to the parent or a `sub-agent`.

## Inputs

Before running this skill, make sure the parent has already decided:

- which design files must change
- what the intended behavioral or contract change is
- whether `Design/BreakingChanges.md` must be updated

## Use this skill when

- `design-doc-maintainer` has already determined that design documentation must change
- a breaking change entry must be added or updated
- an existing design doc needs concrete edits to reflect already-approved intent

## Required flow

1. read the target design files
2. edit only the files needed for the decided design scope
3. keep terminology and structure aligned with nearby design docs
4. update `Design/BreakingChanges.md` when the change is breaking and already approved as such
5. report which files changed and any remaining ambiguity

## Rules

- Do not re-decide whether design work is needed; `design-doc-maintainer` owns that decision.
- Do not invent new product scope while editing docs.
- Prefer updating an existing design document over creating a parallel duplicate.
- Keep edits concrete enough that implementation work can proceed without guessing.

For executor choice, follow the switchable implementation thresholds defined in `codex-delegation-executor`.

Common provisional triggers for assigning this work to a `sub-agent` are:

- target design files are 3 or more
- one file would require 4 or more separate edit blocks
- the parent would otherwise need to compare 4 or more related design files before editing

## Outputs

After this skill runs, the required design artifacts are updated and ready for implementation to follow.

## Completion condition

This skill is complete only when:

- required design files have been edited
- breaking-change logging is updated when applicable
- remaining ambiguity is reported back to the parent
