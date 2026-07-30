---
name: chat-report-writer
description: Coordinate report generation in one ChatGPT chat by invoking runtime-neutral Skills and adding ChatGPT-specific permissions, persistence, PR comment, and handoff behavior.
---

# Chat Report Wrapper

## Goal

Act as the ChatGPT runtime wrapper for report-only work. The user is the parent. This Skill must not redefine report semantics.

## Required Skills

Invoke these Skills in order:

1. `work-context-manager`
2. `report-writer`
3. `chat-handoff-manager`

All three must be installed. Do not replace them with repository-external shared files.

## Runtime responsibilities

- Use the current chat and available connectors.
- Resolve report destination, naming rules, and permissions before writes.
- Persist the detailed report under target-repository rules, or return it in full.
- Post the concise PR comment when authorized, or return its complete body.
- Persist the handoff under target-repository rules, or return the complete packet.
- The user chooses the next chat and merge action.

## Boundaries

- Do not start another worker or sub-agent.
- Do not modify implementation files.
- Do not create new technical findings or change a supplied verdict.
- Do not redefine report rules locally when `report-writer` is unavailable; report the missing dependency.
- Do not exceed current-chat permissions.
- Do not merge.

## Completion condition

Complete when the required Skills have produced context, evidence-faithful report output, optional concise PR comment, and a transportable handoff; authorized persistence is complete; and no implementation, new review judgment, or merge was performed.
