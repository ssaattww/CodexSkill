---
name: feedback-points-manager
description: Maintain feedback-points.md as a cross-cutting record of reusable workflow lessons, repeated process failures, skill adoption status, and skillization candidates. Use from any skill whenever a new process-related instruction appears, a repeated point reoccurs, a workflow problem is discovered, or a decision must be made about whether a repeated point should become a skill.
---

# Feedback Points Manager

Maintain `feedback-points.md` as the system of record for reusable workflow lessons.

## Goal

Capture process-level feedback, detect repetition, and decide when repeated points should be skillized.

## This skill is cross-cutting

Allow any other skill to call this skill.

Typical callers include:

- `development-orchestrator`
- `task-consistency-manager`
- `design-doc-maintainer`
- `codex-delegation-executor`
- `review-enforcer`
- `progress-sync-manager`
- `git-workflow-manager`
- `execution-cost-stabilizer`

## What belongs here

Record workflow and development-method points, not issue-specific feature design decisions.

Good examples:

- delegation policy
- TDD policy
- review policy
- progress update policy
- task sizing policy
- Git workflow policy
- restart or handover policy

Do not keep one-off feature specifications here if they belong in design docs, reports, tasks, or phases.

## Required fields for each point

Maintain fields that make reuse status visible:

- FP identifier
- content
- category
- skillization status
- related skill
- duplicate group
- state
- date

## Required skillization statuses

Use these states:

- 未整理
- 検討中
- skill化済み
- 不要

## Duplicate handling

When a new point appears:

1. check whether the same or similar point already exists
2. if similar, place it in the same duplicate group
3. do not create redundant isolated entries when consolidation is possible

## Skillization rule

Use this default decision policy:

- first occurrence: record it
- second occurrence: mark as 検討中
- third or later occurrence: normally skillize it unless it is clearly one-off

Skillize when the point is:

- cross-task or cross-issue
- process-related
- costly when repeated
- dependent on humans remembering it manually

Do not skillize when the point is:

- issue-specific design content
- one-time specification
- externally constrained and not reusable

## Required actions after skillization

When a point is skillized:

- set `skillization status` to `skill化済み`
- set `related skill`
- keep historical traceability for earlier duplicate entries
- update wording so the point reflects the reusable rule, not only the original incident

## Strong rule

Whenever the same process-related point appears again, explicitly decide whether to skillize it instead of merely appending another unstructured note.