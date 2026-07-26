---
name: report-output-manager
description: Coordinate runtime-neutral report generation with Codex-specific path reservation, rendering, and persistence.
---

# Codex Report Wrapper

## Goal

Act as the Codex runtime wrapper for report output without redefining report semantics.

## Required Skills

Invoke:

1. `work-context-manager`
2. `report-writer`

Do not replace these Skills with `shared/` files.

## Codex responsibilities

- Parent owns report mode, source selection, path reservation, template choice, and persistence.
- Reserve a path under the target repository's report rules before delegated section writing.
- Pass authoritative context and evidence to `report-writer`.
- Persist the complete result without changing verdict, severity, validation status, or uncertainty.
- Leave PR commenting and handoff transport to the caller unless explicitly delegated.

## Default path rules

- Place reports under `<repo-root>/reports/` unless target-repository instructions override it.
- Use existing repository filename, language, and template rules.
- Preserve legacy names unless renaming is explicitly requested.
- Existing helper references in this Skill directory remain available for deterministic path construction.

## Boundaries

- Do not invent evidence.
- Do not convert missing current-HEAD CI into success.
- Do not let a concise PR comment replace the detailed report.
- Do not modify implementation merely to improve a report.
- Do not redefine report rules locally when `report-writer` is unavailable.
- Do not merge.

## Completion condition

Complete when the required Skills have produced an evidence-faithful report, a concrete target path or explicit persistence limitation is available, authoritative sources and uncertainty are preserved, and no merge was performed.
