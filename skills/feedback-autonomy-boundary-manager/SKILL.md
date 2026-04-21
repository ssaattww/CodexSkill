---
name: feedback-autonomy-boundary-manager
description: Maximize autonomous execution while enforcing clear stop conditions for high-risk ambiguity, external contract changes, and approval-required operations. Use when deciding whether to proceed or ask the user.
---

# Autonomy Boundary Manager

Keep momentum high without crossing unsafe decision boundaries.

## Goal

Proceed autonomously by default, but stop consistently for the right reasons.

## Execution owner

Run this skill as: `parent`

- This skill decides whether the parent continues or stops for user input.

## Inputs

Before running this skill, gather:

- the next planned action
- assumptions required to proceed
- user approval requirements or irreversible risk if any

## Default policy

- Continue execution without confirmation for internal, reversible, low-risk work.
- Avoid unnecessary check-ins that do not change scope or risk.

## Mandatory stop conditions

Stop and ask the user when any apply:

1. external/public contract change with ambiguous intent
2. destructive or irreversible operation not explicitly requested
3. missing credentials, access, or legal/organizational approval
4. conflicting requirements with no defensible interpretation
5. acceptance criteria are materially unclear and affect architecture or scope
6. any planned skill still has execution owner `どちらでも良い` and the ownership choice affects the workflow
7. a required skill step is mandatory `sub-agent` work, but the current run does not have explicit user permission to delegate or cannot satisfy that execution mode safely

If item 6 applies, ask once before work starts and batch all such ownership confirmations into that same pre-work question set. Do not wait until the middle of implementation.

If item 7 applies, stop before substituting a parent-side fallback. Ask the user whether to permit delegation, change the workflow requirement, or stop the task.

If a borderline process classification or FP registration decision is not obvious, prefer an independent classification pass via `feedback-points-sanitizer` before deciding.

## Decision protocol

For each borderline case:

1. state assumed path
2. state risk if assumption is wrong
3. decide continue vs stop using the rules above
4. log the decision in report/chat evidence

## Outputs

After this skill runs, the next step should be explicit:

- continue now with stated assumptions
- or stop with one concise blocking question

## Completion condition

This skill is complete only when the workflow has an explicit continue-or-stop decision with rationale.

## Cross-cutting rule

If unnecessary stop/ask cycles recur, call `feedback-points-manager`.
