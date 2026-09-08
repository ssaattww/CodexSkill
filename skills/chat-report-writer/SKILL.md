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

## Execution location

Use the connected-PC route through Remote Desktop Commander by default.
Follow an explicit user selection first, then Project Instruction. Use normal
chat only when one of those authorities explicitly selects it. For the PC route,
discover Remote Desktop Commander tools, confirm the specified device with a
read-only call, and pin evidence reads to it. Resolve the path, source
identity, and ownership through `work-context-manager.execution_environment`
before reading or saving reports, and recheck after reconnection or change.
Keep remote-machine paths distinct from current-chat paths and uploaded files.

Use PC access only for existing evidence and authorized report/handoff files.
Do not execute new tests, install project dependencies, launch agent CLIs,
change product files, or turn a missing result into a new technical judgment.
A failed requested connection blocks dependent evidence collection; do not
switch to another machine or normal chat without authorization.

GitHub repository reads and writes, report commits, PR updates, and comments
still use the GitHub connector, not terminal `gh`, authenticated Git network
operations, or REST calls. Preserve supplied execution locations, source
fingerprints, missing dependencies, and successful/failed diagnostic evidence
without claiming that report generation reran those checks.

## Boundaries

- Do not start another worker or sub-agent.
- Do not modify implementation files.
- Do not create new technical findings or change a supplied verdict.
- Do not redefine report rules locally when `report-writer` is unavailable; report the missing dependency.
- Do not exceed current-chat permissions.
- Do not merge.

## Completion condition

Complete when the required Skills have produced context, evidence-faithful report output, optional concise PR comment, and a transportable handoff; authorized persistence is complete; and no implementation, new review judgment, or merge was performed.
