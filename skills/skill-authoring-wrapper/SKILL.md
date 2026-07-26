---
name: skill-authoring-wrapper
description: Create or update local skills in `/home/ibis/AI/CodexSkill/skills` by using the built-in `skill-creator` and then conforming the result to this repository's skill standards. Use when a new repo-local skill is needed, when an existing local skill must be restructured to match repo conventions, or when built-in `skill-creator` output must be wrapped with local execution-owner, shared-contract, delegation, and design-document rules.
---

# Skill Authoring Wrapper

## Goal

Use the built-in `skill-creator` as the initializer, then normalize the result to this repository's standards without duplicating cross-runtime workflow semantics.

Use the same route for both new Skill creation and substantial local Skill updates whenever practical.

## Execution owner

Run this Skill as: `parent`.

- Parent owns local Skill design, repository placement, shared-contract placement, and final adoption.
- Do not modify the built-in `skill-creator`; wrap it.

## Inputs

Before running this Skill, gather:

- the requested new or updated Skill's purpose,
- the target location under `/home/ibis/AI/CodexSkill/skills`,
- whether this is a new Skill or an update,
- which repository standards apply,
- whether the same semantics are required by both Codex and ChatGPT,
- whether the change affects the Skill inventory, call graph, ownership model, shared contracts, release packaging, or contract summary in the hierarchy design documents.

## Typical caller

Use `development-orchestrator` as the default caller when task completion reveals that a local Skill must be created or substantially updated.

If the user explicitly asks for Skill creation or restructuring outside normal implementation flow, the parent may call this Skill directly, but the caller must remain explicit.

## Required flow

1. Read the built-in `skill-creator` at `/home/ibis/.codex/skills/.system/skill-creator/SKILL.md`.
2. Decide the Skill name, scope, and whether `scripts/`, `references/`, or `assets/` are actually needed.
3. Determine whether the requested semantics already exist under `shared/workflow/` or another canonical shared contract.
4. When Codex and ChatGPT need the same semantics, create or update one runtime-neutral contract under `shared/workflow/` before editing runtime adapters.
5. Keep Codex and ChatGPT Skill files limited to execution-owner, dispatch, permission, persistence, and runtime-specific boundary rules.
6. When responsibility placement, caller placement, or parent/child decision ownership changes, read [responsibility placement policy](references/responsibility-placement-policy.md).
7. If creating a new Skill, initialize it through the built-in `skill-creator` workflow and `init_skill.py`.
8. If updating an existing Skill, read its current `SKILL.md`, preserve surviving intent, and normalize it through this wrapper instead of editing ad hoc.
9. Replace generic scaffold sections with the repository's standard section structure.
10. Ensure the resulting `SKILL.md` includes `## Goal`, `## Execution owner`, `## Inputs`, `## Outputs`, and `## Completion condition`.
11. If the Skill can hand off executable work, route that policy through `codex-delegation-executor` instead of creating an isolated policy.
12. If the Skill has switchable parent/sub-agent execution, add numeric thresholds only when the decision is truly internal to that Skill tree.
13. If the Skill creates or updates governed files, state which Skill paths may modify those files.
14. If the repository has a real canonical inventory or registry, update it; do not require nonexistent files such as `agents/openai.yaml`.
15. Update `skills/design/skill-hierarchy-design.md` and `design/skill-hierarchy-design.md` together when architecture, ownership, call graph, shared contracts, or contract-level understanding changes.
16. For ChatGPT adapters under `skills/chat-*`, use repository-relative links to canonical shared files. Do not commit copied shared contracts inside each ChatGPT Skill.
17. Run the ChatGPT release builder when a `skills/chat-*` adapter or referenced shared contract changes.

## Local standard sections

Use these as the default contract for repository-local Skills:

- `## Goal`
- `## Execution owner`
- `## Inputs`
- `## Outputs`
- `## Completion condition`

Add these when they apply:

- `## Shared contracts`
- `## Required flow`
- `## Rules`
- `## Large-scope delegation`
- `## Cross-cutting rule`

## Cross-runtime contract rules

- Put runtime-neutral implementation, review, reporting, validation, evidence, and lifecycle semantics under `shared/workflow/`.
- Keep Codex adapters responsible for parent/sub-agent execution, dispatch, local tooling, and Codex completion gates.
- Keep ChatGPT adapters responsible for user-parent coordination, direct-chat execution, permission boundaries, report persistence, and cross-chat handoff.
- Do not maintain hand-copied common contract files under `skills/chat-*/references/`.
- ChatGPT Release packaging must discover every `skills/chat-*` Skill and include its referenced shared dependencies.
- A shared reference is not an installable fourth Skill.

## Repository-specific rules

- Do not leave built-in scaffold text or TODO sections in a finished Skill.
- Do not bypass this wrapper for substantial Skill creation or restructuring.
- Do not create a Skill that bypasses `codex-delegation-executor` for executable Codex work unless that new Skill is itself the policy owner.
- Do not move decision responsibility upward merely because an upper Skill exists; follow the responsibility placement policy.
- Do not leave execution-owner ambiguity.
- Do not forget governed-file update restrictions.
- Do not forget hierarchy design updates when local architecture or shared contracts change.
- Do not reintroduce duplicated ChatGPT/Codex workflow rules after a shared contract exists.

## Outputs

After this Skill runs, there should be:

- a completed repository-local Skill or runtime adapter,
- a canonical shared contract when semantics cross runtimes,
- wording that matches repository standards,
- explicit delegation, governance, and release expectations,
- updated hierarchy design documents when architecture changed,
- a validated ChatGPT bundle when a ChatGPT adapter or dependency changed.

## Completion condition

This Skill is complete only when the built-in output or existing Skill has been normalized, shared semantics have one canonical owner, runtime adapters contain only runtime-specific rules, required contract sections exist, governance and design updates are explicit, and affected ChatGPT packaging has been validated without applying TDD to the CodexSkill repository.