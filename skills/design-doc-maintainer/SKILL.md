---
name: design-doc-maintainer
description: Decide whether design documentation must be updated and perform the required design-document maintenance before implementation continues. Use when changes affect public behavior, DSL contracts, external APIs, file formats, configuration formats, workflows, or any behavior that should be reflected in existing design documents rather than implemented ad hoc.
---

# Design Doc Maintainer

Prevent implementation from getting ahead of design.

## Goal

Ensure design documentation is updated before code changes proceed when the change affects contract or intended behavior.

## Execution owner

Run this skill as: `parent`

- This skill makes contract and documentation decisions that should stay with the parent.
- Design-document editing inside this skill is implementation work and should use `design-executor`.

## Run this skill

Run this skill before implementation whenever changes affect:

- public or external behavior
- DSL or schema
- file format contracts
- template contracts
- configuration contracts
- public APIs
- workflow behavior
- documented operational procedures
- breaking changes

## Required decisions

Decide whether to:

- update an existing design document
- create a new design document
- update a breaking-changes document
- leave design unchanged because the work is internal-only

Prefer updating existing design documents over creating new ones unless the topic is truly separate.

## Strong rule

If contract or user-visible behavior changes, do not proceed directly to implementation without design reflection.

## Required outputs

Update the relevant design docs and make sure tasks and phases reflect the design work.

When the work is document editing rather than decision-making, run it through `codex-delegation-executor` and have the executor read `design-executor`.

If design changes create new implementation work, call `task-consistency-manager`.

## Cross-cutting rule

If the need for this skill was triggered by a recurring failure to update design first, call `feedback-points-manager`.
