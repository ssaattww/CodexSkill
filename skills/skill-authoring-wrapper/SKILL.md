---
name: skill-authoring-wrapper
description: Create or update local skills in `/home/ibis/AI/CodexSkill/skills` by using the built-in `skill-creator` and then conforming the result to this repository's skill standards. Use when a new repo-local skill is needed, when an existing local skill must be restructured to match repo conventions, or when built-in `skill-creator` output must be wrapped with local execution-owner, contract, delegation, and design-document rules.
---

# Skill Authoring Wrapper

Create repo-standard skills without modifying the built-in `skill-creator`.

## Goal

Use the built-in `skill-creator` as the initializer, then normalize the resulting skill to this repository's standard structure and governance rules.
Use the same route for both new skill creation and substantial local skill updates whenever practical.

## Execution owner

Run this skill as: `parent`

- Parent owns local skill design, repository placement, and final adoption.
- Do not modify the built-in `skill-creator`; wrap it.

## Inputs

Before running this skill, gather:

- the requested new or updated skill's purpose
- the target location under `/home/ibis/AI/CodexSkill/skills`
- whether this is a new skill or an update to an existing local skill
- which repo-local standards must be applied
- whether the change affects the skill inventory, call graph, ownership model, or contract summary in `skills/design/skill-hierarchy-design.md`

## Typical caller

Use `development-orchestrator` as the default caller when a task or issue completion reveals that a local skill must be created or substantially updated.

If the user explicitly asks for local skill creation or restructuring outside normal implementation flow, the parent may call this skill directly, but do not leave the caller implicit.

## Required flow

1. Read the built-in `skill-creator` at `/home/ibis/.codex/skills/.system/skill-creator/SKILL.md`.
2. Decide the local skill name, scope, and whether `scripts/`, `references/`, or `assets/` are actually needed.
3. When responsibility placement, caller placement, or parent/child decision ownership is being created or changed, read [references/responsibility-placement-policy.md](references/responsibility-placement-policy.md).
4. If creating a new skill, initialize it by using the built-in `skill-creator` workflow and its `init_skill.py`.
5. If updating an existing local skill, read the current `SKILL.md`, keep the existing intent that should survive, and normalize the result through this same wrapper flow instead of editing ad hoc.
6. Replace any generic scaffold sections with this repository's standard section structure.
7. Ensure the resulting `SKILL.md` includes:
   - `## Goal`
   - `## Execution owner`
   - `## Inputs`
   - `## Outputs`
   - `## Completion condition`
8. If the skill can hand off executable work, route that policy through `codex-delegation-executor` instead of inventing an isolated policy.
9. If the skill has switchable parent/sub-agent execution, add explicit provisional numeric thresholds only when the decision is truly internal to that skill tree.
10. If the skill creates or updates governed files, state which skill paths are allowed to modify those files.
11. Update `agents/openai.yaml` so it matches the final local skill intent.
12. Update `/home/ibis/AI/CodexSkill/skills/design/skill-hierarchy-design.md` when the new or updated skill changes the local skill inventory, call graph, execution方式, role summary, or contract summary.

## Local standard sections

Use these as the default contract for repo-local skills:

- `## Goal`
- `## Execution owner`
- `## Inputs`
- `## Outputs`
- `## Completion condition`

Add these when they apply:

- `## Required flow`
- `## Rules`
- `## Large-scope delegation`
- `## Cross-cutting rule`

## Repo-specific rules

- Do not leave the built-in `skill-creator` scaffold text or TODO sections in a finished local skill.
- Do not bypass this wrapper for substantial local skill creation or restructuring when the result should conform to repo standards.
- Do not create a local skill that bypasses `codex-delegation-executor` for executable work unless that new skill is itself the policy owner.
- Do not move decision responsibility upward just because an upper skill exists; follow `references/responsibility-placement-policy.md`.
- Do not leave execution-owner ambiguity in a finished local skill.
- Do not forget to describe governed-file update restrictions when the skill owns canonical files.
- Do not forget to reflect local skill changes in the hierarchy design when they change local architecture or contract-level understanding.

## Outputs

After this skill runs, there should be:

- a repo-local skill folder with a completed `SKILL.md`
- `agents/openai.yaml` aligned with the final skill intent
- local skill wording that matches this repository's standards
- updated hierarchy design when the local skill inventory, call graph, ownership model, or contract summary changed

## Completion condition

This skill is complete only when:

- the built-in `skill-creator` output has been normalized to repo standards
- substantial local skill updates have also been normalized through this wrapper path
- the resulting local skill has the required contract sections
- delegation, governance, and design-update expectations are explicit
- any affected local design documentation has been updated
