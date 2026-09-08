# Document wording self-check in ChatGPT

## Scope and owner

Use this procedure when `implementation-worker` requires a document self-check.
The current implementation chat performs `document-wording-review` in
`author_self_check` mode. Do not spawn another chat, sub-agent, or agent CLI.
This procedure owns only ChatGPT evidence acquisition and execution; the
wording Skill remains the sole owner of semantic criteria and result rules.

## Read the actual source

1. Follow the wrapper's execution-location contract. The default is the
   connected-PC route through Remote Desktop Commander; an explicit user or
   Project Instruction selection takes precedence. Do not silently switch
   locations after a connection failure.
2. Resolve the repository and target through the GitHub connector. On the
   selected PC, verify the pinned device, absolute worktree path, branch,
   HEAD, ownership, and dirty-source fingerprint. Recheck after reconnecting
   and before reusing evidence. Do not touch another task's worktree.
3. Locate `document-wording-review` in the verified Skill source. Read its
   `SKILL.md` and required references through the selected route, recording
   the Skill source revision or content hashes separately from the target
   document revision. A different Skill repository is allowed when identified;
   an unidentified or stale copy is not. An actual source read is required,
   not a claim that a Skill name automatically resolved its dependencies.
4. Retrieve every in-scope before/after passage, surrounding context, and
   relevant definitions. Record paths and ranges actually read. Retrieve the
   remainder of truncated responses before claiming coverage. Hashes prove
   identity, not that the chat read the prose. Missing source, definitions,
   or references leave the affected check incomplete.
5. The current chat reads those passages and applies `document-wording-review`.
   Record dimension-level evidence, defects, and policy conflicts. A successful
   connection, command, or zero-unknown-word count cannot supply this judgment.

## Dependencies and mechanical checks

On the connected-PC route, inspect dependency declarations and executable
availability on that same PC. Run applicable existing checks there before
CI-triggering publication. Prepare missing dependencies only within the
already authorized worktree or task scratch directory, using the project's
pinned requirements when provided. Do not assume a library available inside
ChatGPT is available on the PC. Global installation, administrator access,
credential changes, or changing project dependency policy needs separate
approval under the execution-location contract.

Keep `available`, `missing`, and `not_checked` dependencies explicit. A required
command that cannot run is not a pass; a failed connection is not a fallback
permission. Do not install an agent to make the self-check happen. If normal
chat was explicitly selected, read the available text yourself and report
unavailable mechanical checks without asserting tool preparation or a PC run.
Do not withhold a possible prose assessment merely because lint is unavailable,
but do not claim the combined acceptance gate passed.

Retain successful and failed command results, stdout, stderr, and diagnostics
in a task-specific output directory. Do not change whitelist entries, aliases,
exclusions, or a standalone-word prohibition to make a check succeed.

## Return and persistence

Return the unmodified semantic result as `document_wording_review` through
`implementation-worker`. Include its `read_evidence`: actual reader identity,
execution environment, Skill source identity and read reference paths,
document base/target identities, read ranges, and missing inputs. Keep each
mechanical command's status and evidence separate. The wrapper passes the
complete implementation result to `report-writer` and `chat-handoff-manager`;
preserve the read evidence in `source_payloads`, not only a success summary.
Re-read changed passages and invalidate affected evidence after content changes.
The result is author evidence, never proof of normal or independent review.

## Acceptance examples

| Situation | Required disposition |
| --- | --- |
| The PC returned only the first part of a document. | Retrieve the remaining in-scope passages; otherwise report incomplete coverage. |
| Local lint succeeds but the chat has not read the changed prose. | No wording pass; read the prose before recording an assessment. |
| The text is readable but the required interpreter is missing. | Assess the available prose; record the missing dependency and unresolved mechanical gate separately. |
| The chat reconnects to a different HEAD or worktree. | Re-establish identity and permission before reading, editing, or reusing results. |
| Both reading and checks completed on the verified source. | Keep separate reading and command evidence; do not call the author an independent reviewer. |
