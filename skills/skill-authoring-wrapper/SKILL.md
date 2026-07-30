---
name: skill-authoring-wrapper
description: Create or update local Skills in `/home/ibis/AI/CodexSkill/skills` by using the built-in `skill-creator` and then conforming the result to this repository's core-Skill and runtime-wrapper standards. Use when a new repository-local Skill is needed or an existing Skill must be substantially restructured.
---

# Skill Authoring Wrapper

## Goal

Use the built-in `skill-creator` as the initializer, then normalize the result to this repository's standards without duplicating cross-runtime workflow semantics or depending on Skill-external shared files.

Use the same route for both new Skill creation and substantial local Skill updates whenever practical.

## Execution owner

Run this Skill as: `parent`.

- Parent owns local Skill design, repository placement, core-Skill versus wrapper responsibility, dependency declarations, and final adoption.
- Do not modify the built-in `skill-creator`; wrap it.

## Inputs

Before running this Skill, gather:

- the requested new or updated Skill's purpose,
- the target location under `/home/ibis/AI/CodexSkill/skills`,
- whether this is a new Skill or an update,
- which repository standards apply,
- whether the same semantics are required by more than one runtime,
- whether the change affects the Skill inventory, call graph, ownership model, core-Skill dependencies, release packaging, or hierarchy design documents.

## Typical caller

Use `development-orchestrator` as the default caller when task completion reveals that a local Skill must be created or substantially updated.

If the user explicitly asks for Skill creation or restructuring outside normal implementation flow, the parent may call this Skill directly, but the caller must remain explicit.

## Required flow

1. Read the built-in `skill-creator` at `/home/ibis/.codex/skills/.system/skill-creator/SKILL.md`.
2. Decide the Skill name, scope, and whether `scripts/`, `references/`, or `assets/` are actually needed inside that Skill's own directory.
3. Determine whether the requested semantics already exist in a runtime-neutral core Skill under `skills/`.
4. When multiple runtimes need the same semantics, create or update one parent-independent core Skill under `skills/<core-skill-name>/` before editing runtime wrappers.
5. Keep Codex and ChatGPT wrapper Skills limited to execution owner, dispatch, permission, persistence, reviewer or chat continuity, and runtime-specific boundaries.
6. Express wrapper dependencies by installed Skill name. Do not make one Skill depend on files outside its own Skill directory.
7. When responsibility placement, caller placement, or parent/child decision ownership changes, read [responsibility placement policy](references/responsibility-placement-policy.md).
8. If creating a new Skill, initialize it through the built-in `skill-creator` workflow and `init_skill.py`.
9. If updating an existing Skill, read its current `SKILL.md`, preserve surviving intent, and normalize it through this wrapper instead of editing ad hoc.
10. Replace generic scaffold sections with the repository's standard section structure.
11. Ensure the resulting `SKILL.md` includes `## Goal`, `## Execution owner` or an explicit runtime-independence section, `## Inputs`, `## Outputs`, and `## Completion condition`.
12. If the Skill can hand off executable Codex work, route executor selection through `codex-delegation-executor` instead of creating an isolated dispatch policy.
13. If the Skill has switchable parent/sub-agent execution, add numeric thresholds only when the decision is truly internal to that Skill tree.
14. If the Skill creates or updates governed files, state which Skill paths may modify those files.
15. If the repository has a real canonical inventory or registry, update it; do not require nonexistent files such as `agents/openai.yaml`.
16. Update `skills/design/skill-hierarchy-design.md` and `design/skill-hierarchy-design.md` together when architecture, ownership, call graph, core-Skill dependencies, or contract-level understanding changes.
17. Update `design/chat-worker-skill-design.md` when ChatGPT wrapper dependencies, handoff behavior, lifecycle, or package contents change.
18. Run the ChatGPT release builder and repository-wide Skill validator when a packaged wrapper, packaged core Skill, dependency map, or related design changes.

## Local standard sections

Use these as the default contract for repository-local Skills:

- `## Goal`
- `## Execution owner` or `## Runtime independence`
- `## Inputs` or `## Required input`
- `## Outputs` or `## Output contract`
- `## Completion condition`

Add these when they apply:

- `## Required Skills`
- `## Required flow`
- `## Rules`
- `## Large-scope delegation`
- `## Cross-cutting rule`

## Core Skill and runtime wrapper rules

- Put runtime-neutral implementation, review, reporting, validation, evidence, and lifecycle semantics in independent core Skills under `skills/`.
- Keep Codex wrappers responsible for parent/sub-agent execution, dispatch, local tooling, persistence, and Codex completion gates.
- Keep ChatGPT wrappers responsible for user-parent coordination, current-chat permissions, connector use, repository and PR persistence, chat continuity, and cross-chat handoff.
- Do not use `shared/workflow/`, `shared/chat-worker/`, or any other Skill-external file as a runtime dependency.
- Do not maintain hand-copied common contracts under wrapper `references/` directories.
- A wrapper must stop with a missing dependency when a required core Skill is unavailable; it must not reproduce the core logic locally.
- Each installable Skill must be self-contained inside its own directory.
- ChatGPT Release packaging must include every packaged wrapper and all required packaged core Skills as separate Skill root directories.

## Repository-specific rules

- Do not leave built-in scaffold text or TODO sections in a finished Skill.
- Do not bypass this wrapper for substantial Skill creation or restructuring.
- Do not create a Skill that bypasses `codex-delegation-executor` for executable Codex work unless that new Skill is itself the dispatch-policy owner.
- Do not move decision responsibility upward merely because an upper Skill exists; follow the responsibility placement policy.
- Do not leave execution-owner ambiguity.
- Do not forget governed-file update restrictions.
- Do not forget hierarchy design updates when local architecture or dependencies change.
- Do not reintroduce duplicated ChatGPT/Codex workflow semantics after a core Skill exists.
- Do not reintroduce the deleted shared-contract architecture.

## Outputs

After this Skill runs, there should be:

- a completed repository-local core Skill or runtime wrapper,
- one canonical core Skill when semantics cross runtimes,
- explicit Skill-name dependencies for wrappers,
- wording that matches repository standards,
- explicit delegation, governance, and release expectations,
- updated hierarchy design documents when architecture changed,
- a validated ChatGPT bundle when a packaged wrapper or dependency changed,
- repository-wide validation showing no broken active Markdown links or forbidden shared-contract runtime references.

## Completion condition

This Skill is complete only when the built-in output or existing Skill has been normalized, cross-runtime semantics have one core-Skill owner, wrappers contain only runtime-specific rules, every Skill is self-contained, required dependency and contract sections exist, governance and design updates are explicit, affected packaging and repository validation have succeeded, and TDD was not imposed on the CodexSkill repository.
