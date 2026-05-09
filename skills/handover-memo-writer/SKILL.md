---
name: handover-memo-writer
description: Create a resume-ready handover memo for moving work to a new chat without losing context. Use when the user asks to prepare a handover, restart memo, transfer note, or a next-chat prompt that preserves background, decisions, unresolved work, and the exact next request.
---

# Handover Memo Writer

Create a handover memo that lets the next chat resume work with the same assumptions.

## Goal

Produce a complete handover memo for a new chat so the next agent can continue without re-deriving context from prior conversation history.

## Execution owner

Run this skill as: `parent`

- Handover quality depends on full-session context, so ownership stays with the parent.
- This skill should always create the handover as a report under `reports/` by using `report-output-manager`.
- This skill does not re-enter `development-orchestrator`; it packages current context for the next chat.

## Inputs

Before running this skill, gather:

- the current chat history
- the current work objective and intended end goal
- key background, constraints, and standing rules already agreed with the user
- important repository state, branch state, report state, and verification state when relevant
- resolved decisions, rejected alternatives, and still-open items
- the user's requested output format, if one was provided

## Required flow

1. Treat the handover as both a chat artifact and a report under `reports/`.
2. If the user supplied a required structure, preserve the requested headings, order, and numbering exactly, even if numbering is non-contiguous.
3. Reconstruct the purpose of the current chat and the final intended goal, not just the latest subtask.
4. Gather the durable background needed to resume work:
   - repository and workspace involved
   - active branch, commit, PR, report, or tracking context
   - standing workflow rules and constraints
   - external blockers or environment failures already encountered
5. Reconstruct the full path to the current state in time order:
   - what was checked
   - what was changed
   - what was rejected or deferred
   - what remains open
6. Separate decided facts from unresolved items. Do not blur completed decisions into pending work.
7. Write the next-chat request so it can be pasted directly into a new session and start useful work immediately.
8. Write the full handover body so a new chat can continue without additional clarification where practical.
9. Call `report-output-manager` for placement and naming before creating the handover report.
10. Create the handover report under `reports/`.

## Rules

- Do not collapse the handover into a short summary when important context would be lost.
- Do not omit previously agreed constraints just because they are inconvenient or older than the latest task.
- Do not silently discard rejected options, failed attempts, or review findings when they still affect the next step.
- Distinguish clearly between:
  - confirmed fact
  - inference
  - unresolved question
- Include exact filenames, branch names, PR numbers, commit hashes, report names, and commands when they materially affect restart quality.
- If some detail is uncertain, say that it is uncertain instead of presenting it as resolved.
- Prefer concrete wording over references like “see above” or “refer to prior chat”.
- The handover must be understandable on its own; do not assume the next chat can read this one.
- When the user provides a target template, do not rewrite the template into a different structure.
- Do not satisfy this task with chat text alone; always leave a handover report under `reports/`.

## Outputs

After this skill runs, there should be:

- a complete handover memo in the user-requested structure
- explicit separation of purpose, background, chronology, decisions, unresolved items, and next request
- a next-chat prompt that can be pasted directly to resume work
- a handover report under `reports/` containing the same content

## Completion condition

This skill is complete only when the produced handover is detailed enough that a new chat can continue with the same working assumptions without having to reconstruct the missing context from the old session.
