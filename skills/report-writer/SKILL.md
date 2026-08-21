---
name: report-writer
description: Produce evidence-faithful implementation, review, verification, independent-final-review, or consolidated reports without depending on a Codex parent or ChatGPT chat runtime.
---

# Report Writer

## Goal

Transform supplied work context and execution evidence into a durable, accurate report and an optional concise PR summary, while preserving the exact reviewed and current target identities.

## Required input

Use the output of `work-context-manager` plus implementation or review evidence. The caller owns repository writes, file naming, PR commenting, cross-runtime transport, and validation of any report-attestation commit.

For an independent-final-review report, require:

- the immutable reviewed implementation HEAD,
- reviewer identity and independence evidence,
- complete coverage dispositions, findings, held and unexplored items, validation assessment, and verdict,
- the pre-reserved report path or paths,
- the intended persistence mode.

## Modes

- implementation report,
- review report,
- verification report,
- independent final review report,
- consolidated report,
- concise PR comment.

## Evidence rules

- Preserve exact target identity, including branch, base, current HEAD, reviewed implementation HEAD, relevant commit range, verification capability, separate commit/push/CI-wait state, and report-attestation head when supplied.
- Do not convert missing, failed, blocked, or unavailable checks into success.
- Distinguish direct evidence from inference.
- Keep findings, held items, unexplored areas, unknowns, and remaining risks explicit.
- Preserve full findings rather than shortening away identity, severity, origin, location, impact, evidence, or required action.
- Preserve a source finding's severity through fix verification and consolidation. Change it only when the authoritative review evidence includes `source_severity`, `new_severity`, an evidence-based reason, and the approving authority.
- Treat an unexplained downstream severity difference as a discrepancy. Keep historical reports unchanged and emit a current erratum or correction record rather than silently normalizing the value.
- A concise PR comment summarizes but does not replace the detailed report.
- A handoff transports state but does not replace the detailed report.
- Do not claim that a report-attestation commit was reviewed as implementation.
- Do not include a report-attestation SHA inside the report body when that SHA cannot exist until the report is committed. The caller records that SHA in PR metadata, a PR comment, or another external reference after persistence.

## Required structure

A detailed report should include, as applicable:

- metadata and target identity,
- purpose, scope, and non-goals,
- authoritative requirements and design,
- inspected and changed files,
- implementation or review activity,
- validation commands and results,
- CI runs, jobs, and artifacts tied to the target HEAD,
- full findings and dispositions,
- severity reclassification records or severity errata,
- intentionally untouched areas,
- blocked, unknown, held, and unexplored items,
- remaining risks,
- next action,
- persistence mode and reserved path,
- merge boundary.

## Independent-final-review attestation content

When `report_type` is `independent final review report` and persistence mode is `report_attestation_commit`, the report must state:

- `reviewed_implementation_head`,
- that the technical verdict applies to that implementation HEAD,
- that the report is intended for one administrative attestation commit,
- the reserved report path,
- that the attestation commit must change no other path,
- that the attestation SHA will be recorded externally after commit,
- that any later Git commit invalidates completion unless a new review lifecycle is performed.

The report must not request changes to task tracking, design, Skills, workflows, configuration, implementation, or handoff after independent final review.

## Output contract

Return:

```yaml
report_type: implementation_report | review_report | verification_report | independent_final_review_report | consolidated_report | concise_pr_comment
complete_body: string
evidence_sources:
  - string
target_identity:
  branch: string | unknown
  base_ref: string | null
  current_head: full_sha | unknown
  reviewed_implementation_head: full_sha | null
verification:
  capability: local_execution_available | remote_ci_only | unknown
  technical_head: full_sha | unknown
  administrative_parent: full_sha | null
  commit_state: commit_pending | committed | not_required | unknown
  push_state: pending | pushed | not_required | unauthorized | unknown
  ci_wait_state: pending | completed | not_required | unavailable | unknown
severity_records:
  - finding_id: string
    source_severity: blocking | high | medium | low
    new_severity: blocking | high | medium | low | null
    reason: string | null
    approved_by: string | null
    record_type: preserved | reclassified | erratum
persistence:
  mode: repository_file | report_attestation_commit | external_artifact | copy_paste
  reserved_paths:
    - string
  report_attestation_head: null
concise_pr_comment_body: string | null
unresolved_discrepancies:
  - string
```

`report_attestation_head` remains null in the generated report result because the caller creates and validates that commit after generation. A generated report must use `commit_pending`, `technical_head`, and `administrative_parent` rather than require a future self-referential commit SHA.

## Boundaries

- Do not invent evidence or findings.
- Do not change implementation or review conclusions supplied by their owning Skills without identifying the discrepancy.
- Do not silently change finding identity or severity.
- Do not assume a particular reports directory or PR API; the caller supplies persistence rules.
- Do not write task, design, Skill, workflow, configuration, implementation, or handoff content as part of report-attestation mode.
- Do not merge.

## Completion condition

Complete when the report is internally consistent, evidence-faithful, preserves finding identity and severity or records an explicit reclassification or erratum, is explicit about uncertainty, records the exact reviewed implementation identity and persistence requirements, is suitable for the caller to persist or publish, and does not imply that an administrative report commit changes the reviewed implementation verdict or authorizes a merge.
