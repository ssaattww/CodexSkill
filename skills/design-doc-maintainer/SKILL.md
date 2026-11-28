---
name: design-doc-maintainer
description: Decide whether design documentation must be updated and perform the required design-document maintenance before implementation continues. Use when changes affect public behavior, DSL contracts, external APIs, file formats, configuration formats, workflows, or any behavior that should be reflected in existing design documents rather than implemented ad hoc. Also consult the layout guidance when deciding where to place any new document, including design, phase/status, task/status, report, or other documents; routine generation or updates at established paths do not trigger this placement guidance.
---

# Design Doc Maintainer

Prevent implementation from getting ahead of design.

## Goal

Ensure design documentation is updated before code changes proceed when the change affects contract or intended behavior.

## Execution owner

Run this skill as: `parent`

- This skill makes contract and documentation decisions that should stay with the parent.
- Design-document editing inside this skill is implementation work and should use `design-executor`.
- For large or unclear design surface, the parent may request a design-impact scan from a `sub-agent`, but final design judgment remains parent work.

## Inputs

Before running this skill, gather:

- the current task or issue scope
- intended behavioral or contract change
- affected APIs, schemas, workflows, or documents
- current related design documents

## Run this skill

Before creating a document whose location has not yet been established, read
the [multi-project document layout guidance](references/multi-project-document-layout.md).
This includes new documents added to an existing project. For a new project,
make the initial placement decision once before creating its first documents.
Routine generation or updates at established paths do not repeat this placement
check. A placement check does not replace the design-impact judgment below.

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

For a new design document or a substantial revision, use the copyable [design document template](references/design-document-template.md) as the starting point. For a minor addition, preserve the existing document structure and update only the necessary sections. Keep a shared-library design focused on its responsibility boundary, integration points, and inputs/outputs; put product-specific startup paths and operating instructions in a separate document when they need design coverage. Treat README as a short entry point and do not prescribe README placement in the design document. Do not migrate unrelated existing design documents as part of this work.

## Strong rule

If contract or user-visible behavior changes, do not proceed directly to implementation without design reflection.

## Outputs

Update the relevant design docs and make sure tasks and phases reflect the design work.

When the work is document editing rather than decision-making, run it through `codex-delegation-executor` and have the executor read `design-executor`.

If design changes create new implementation work, call `task-consistency-manager`.

## Completion condition

This skill is complete only when:

- design impact has been explicitly judged
- required design artifacts to update are identified
- needed document edits have been completed or routed through `design-executor`
- tracking reflects any design-driven work additions

## Large-scope delegation

If the possible design impact spans many documents, contracts, or external behaviors, the parent may:

1. use `sub-agent-task-manager`
2. ask a `sub-agent` for a bounded impact scan covering affected docs and contract surfaces
3. require a report under `reports/`
4. make the final update/no-update decision in the parent

Use these provisional thresholds as the default trigger:

- candidate design documents to inspect are 3 or more
- affected contract surfaces are 2 or more among API, schema, file format, configuration, and workflow
- external or user-visible behavior changes appear in 2 or more places
- the parent would otherwise need to compare 4 or more design-related files before judging impact

## Cross-cutting rule

If the need for this skill was triggered by a recurring failure to update design first, call `feedback-points-manager`.
