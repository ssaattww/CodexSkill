---
name: report-writer
description: Produce evidence-faithful implementation, review, verification, or consolidated reports without depending on a Codex parent or ChatGPT chat runtime.
---

# Report Writer

## Goal

Transform supplied work context and execution evidence into a durable, accurate report and an optional concise PR summary.

## Required input

Use the output of `work-context-manager` plus implementation or review evidence. The caller owns repository writes, file naming, PR commenting, and cross-runtime transport.

## Modes

- implementation report,
- review report,
- verification report,
- independent final review report,
- consolidated report,
- concise PR comment.

## Evidence rules

- Preserve exact target identity, including branch, base, current HEAD, and reviewed HEAD.
- Do not convert missing, failed, blocked, or unavailable checks into success.
- Distinguish direct evidence from inference.
- Keep findings, held items, unexplored areas, unknowns, and remaining risks explicit.
- A concise PR comment summarizes but does not replace the detailed report.
- A handoff transports state but does not replace the detailed report.

## Required structure

A detailed report should include, as applicable:

- metadata and target identity,
- purpose, scope, and non-goals,
- authoritative requirements and design,
- inspected and changed files,
- implementation or review activity,
- validation commands and results,
- CI runs, jobs, and artifacts tied to the target HEAD,
- findings and dispositions,
- intentionally untouched areas,
- blocked, unknown, held, and unexplored items,
- remaining risks,
- next action,
- merge boundary.

## Boundaries

- Do not invent evidence or findings.
- Do not change implementation or review conclusions supplied by their owning Skills without identifying the discrepancy.
- Do not assume a particular reports directory or PR API; the caller supplies persistence rules.
- Do not merge.

## Output contract

Return the complete report body, report type, evidence sources, target identity, concise PR comment body when requested, persistence requirements, and unresolved discrepancies.

## Completion condition

Complete when the report is internally consistent, evidence-faithful, explicit about uncertainty, suitable for the caller to persist or publish, and does not imply a merge action.
