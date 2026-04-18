---
name: feedback-points-sanitizer
description: Sanitize noisy feedback-points by separating reusable process rules from issue-specific product decisions, consolidating duplicates, and moving non-process entries to backlog or task/design tracking. Use during periodic cleanup or before skillization analysis.
---

# Feedback Sanitizer

Keep feedback points actionable and reusable.

## Goal

Ensure `<repo-root>/feedback-points/feedback-points.md` contains process-level reusable lessons, not mixed operational noise.

## Run this skill

Run this skill when:

- active feedback list has grown noisy
- many entries are issue-specific and no longer reusable
- skillization decisions are blocked by mixed-quality data
- a new active feedback-point candidate needs pre-write review before being recorded

## Classification rules

Classify each active point as one of:

1. reusable process rule (keep active)
2. duplicate of existing rule (merge by duplicate group)
3. issue/task-specific product decision (move to backlog with link)
4. obsolete/no longer relevant (close or archive)

Use this skill as the pre-write reviewer for active feedback-point additions; return one of: keep active, merge duplicate, move to backlog, or skip.

## Cleanup flow

1. classify all active points
2. merge duplicates into representative rule entries
3. move non-process items to backlog with destination links
4. keep only high-signal active process rules
5. update skillization status and related skill mapping

## Required outputs

Produce cleanup evidence in `reports/`:

- counts before/after
- moved FP IDs and destination
- merged duplicate groups
- newly identified skillization candidates

## Strong rules

- Do not discard history without traceability.
- Keep FP identifiers stable; do not reuse IDs.
- Separate feedback governance from feature design governance.

## Cross-cutting rule

After cleanup, call `feedback-points-manager` to finalize status updates.
