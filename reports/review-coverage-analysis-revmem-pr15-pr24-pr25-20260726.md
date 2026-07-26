# RevMem PR Review Coverage Analysis

- Date: 2026-07-26
- Source repository: `ssaattww/RevMem`
- Reviewed pull requests: PR #15, PR #24, PR #25
- Purpose: identify the concrete review dimensions that were repeatedly used and
  convert them into a reusable `review-enforcer` checklist.

## Summary

The three reviews did not stop at checking the modified lines. They repeatedly
expanded into contracts, dependency boundaries, malformed input, persisted state,
realistic tests, regression retention, performance, documentation, CI evidence,
and scope protection.

The common review dimensions were:

1. Confirm the task exit criteria and authoritative design before reading the
   implementation.
2. Inspect every changed file and the production or test code that consumes the
   changed contract.
3. Verify identity, revision, path, state, and persistence invariants at runtime
   boundaries instead of trusting static types.
4. Reject malformed, partial, contradictory, stale, duplicate, or unsupported
   input atomically.
5. Ensure tests use inputs that can exist in the real protocol or file format.
6. Preserve earlier regression cases while adding new ones during re-review.
7. Check observable side effects, transaction count, process count, and algorithmic
   complexity.
8. Keep source documentation, design documents, reports, and PR evidence aligned
   with the current implementation.
9. Validate only the workflow run associated with the reviewed branch HEAD SHA.
10. Record unrelated findings separately and do not modify work owned by another
    task or pull request.

## PR #15: Document Context Routing and Review State Ownership

The review covered the following points.

### Context resolution and specification

- Git ownership must be resolved before workspace membership.
- Git working tree, untracked file, detached HEAD, non-Git workspace, external
  file, remote file, and UNC identity paths must follow the intended precedence.
- Git inspection failures must distinguish non-repository, unborn HEAD, missing
  object, and unknown failures instead of collapsing all exit codes into one case.
- Repository, context, file, branch, detached revision, workspace, and external
  identities must be canonical and stable.

### Persistence and atomicity

- A new branch or detached context must not overwrite repository-wide Global state.
- Empty lower-owner state must still produce an explicit empty baseline.
- Initial promotion, all source deltas, and all baselines must be committed in one
  atomic compare-and-swap operation.
- Commit failure must not leave ranges, baselines, or only one source partially
  persisted.
- Persisted reconciliation metadata must be part of a formal core contract and
  validated on load, save, and commit.
- Reviewed intervals must be canonical and within the declared line count.

### Reconciliation semantics

- One writable open must observe each lower owner once and use the same immutable
  snapshot for promotion, delta calculation, and baseline recording.
- Workspace and external-file sources need an explicit priority rule when their
  additions and removals conflict.
- Deleting and recreating a lower-owner context must not reuse an obsolete baseline
  as a common ancestor.
- Reconciliation must preserve higher-priority decisions and apply only
  non-conflicting lower-priority changes.

### Performance and side effects

- Writable open and decoration refresh must not duplicate active-owner Git
  inspection.
- The review estimated process multiplication in remote repositories rather than
  accepting functionally correct but excessively repeated inspection.

### Design, tests, CI, and scope

- Design documents must describe the feature rather than an Issue or Task history.
- Related ownership, storage, and reconciliation design must be consolidated by
  feature into one authoritative document.
- Tests must cover branch, detached HEAD, untracked, external, UNC, empty baseline,
  conflicting sources, malformed metadata, and failed atomic commits.
- The final verdict must use the workflow run for the pull request branch HEAD SHA.
- Changes owned by T300, PR #22, and other merged work must remain untouched.
- The separate `objectExists` exit-code problem was recorded as held instead of
  being silently folded into this pull request.

## PR #24: File-Level State Transitions

The review covered the following points.

### Transition semantics

- Rename chains, directory moves, swaps, copy, addition, deletion, ambiguous rename,
  and split-like transitions must be order independent.
- All source file IDs must be resolved from the pre-change snapshot.
- Copy must preserve the source state while creating the destination state with the
  intended reviewed status and revision semantics.
- A rename back to a previous path must update `previousPaths` correctly.
- Delete and rename of the same source must be rejected rather than returning a
  state that is both present and deleted.

### Parser and validator consistency

- The authoritative diff parser and the transition validator must agree on path
  decoding, quoted paths, tabs, timestamps, and `/dev/null`.
- Duplicate destination paths must be rejected across copy, rename, and ordinary
  additions.
- `rename from` and `rename to` must appear exactly once as a pair.
- `new file mode`, `deleted file mode`, and old or new `/dev/null` sides must form a
  consistent status matrix.
- Missing mandatory paths, malformed sections, contradictory metadata, and partial
  transitions must fail atomically rather than being ignored with `continue`.
- Duplicate parser logic was treated as a structural risk because future fixes can
  diverge between implementations.

### Snapshot and runtime state invariants

- Existing and generated states must pass the same public validator.
- `schemaVersion`, `fileId`, `currentPath`, `previousPaths`, `lineCount`,
  `contentHash`, and reviewed intervals must be validated.
- `modifiedReviewed` and `originalReviewedByDiff` must be sorted, canonical,
  non-overlapping, non-adjacent, and within their declared bounds.
- Snapshot paths and file IDs must be unique.
- The final result must be validated again after the transition engine returns.

### Text and diff evidence

- Whitespace or EOL-only classification must be proven from complete old and new
  text, not inferred from incomplete hunks.
- Old and new text must be tied to the same path, revision, line count, and hunk
  coordinates as the transition being applied.
- Removed and added lines reconstructed from text must exactly match the parsed
  zero-context diff.

### Test quality, performance, CI, and scope

- Tests must include malformed rename metadata, mode and `/dev/null` contradictions,
  duplicate destinations, timestamped headers, state validation, generated state,
  rename history, and delete-plus-rename conflicts.
- Tests must be added before the fix and connected to the normal unit-test command.
- Failure diagnostics must preserve stdout, stderr, source, tests, configuration,
  and generated files as artifacts.
- The final CI decision must use the run associated with the branch HEAD SHA after
  current `main` is incorporated.
- Repeated destination scans were examined for quadratic behavior.

## PR #25: Pull Request Diff Progress Calculation

The review covered the following points.

### Progress numerator and denominator

- Only actual addition and deletion coordinates may contribute to progress.
- Context lines, unknown coordinates, Global state, another revision, or another
  context must not increase the numerator.
- Unique addition and deletion coordinates must exactly match the source statistics
  for each side; clipping an inconsistent result is not acceptable.
- File-level and aggregate reviewed count, total count, and percentage must remain
  internally consistent, including the zero-denominator rule.
- Addition and deletion counts must remain available to downstream UI instead of
  being irreversibly collapsed into one total.

### Contract and identity integrity

- Existing `PullRequestFileChange`, `DiffHunk`, and `DiffLine` contracts must be
  reused so status, old path, new path, file ID, and hunks are not lost.
- Context ID, base SHA, head SHA, original diff ID, and changed files must be carried
  in one validated snapshot.
- Stale cached files must not be combinable with a current pull-request context.
- The canonical diff identity must be checked against the base and head revisions.
- Review state map key, payload file ID, revision, current path, line count, and
  interval bounds must match the changed file.

### Unified diff validation

- Runtime `DiffLine.kind` and file status must be exhaustively validated.
- Hunk header counts, line body counts, old and new cursor movement, opposite-side
  coordinate absence, ordering, gaps, and cumulative delta must be coherent.
- Duplicate actual coordinates, missing coordinates, no-op hunks, and context-only
  hunks must be rejected.
- Added and deleted files must provide complete file diffs rather than an arbitrary
  partial hunk that happens to match statistics.
- Modified-side hunk extent and zero-count anchors must remain inside the current
  file line count when same-head state exists.
- Status, old path, new path, side usage, and line-count combinations must follow a
  complete matrix for added, deleted, modified, renamed, and copied files.

### Exclusion policy

- Binary and glob exclusion affects aggregation, not the validity of the diff or
  state snapshot.
- Non-binary files must be structurally validated before an exclusion can skip
  counting.
- Both old and new paths must be repository-relative and canonical.
- Canonical path duplicates must be rejected even when file IDs differ.
- Excluded results must retain source counts, classification, and exclusion reason.

### Test quality and regression retention

- Fixtures must represent unified diffs that Git can actually produce.
- Tests must cover additions, deletions, replacements, multiple hunks, partial
  progress, exclusion, binary files, stale identity, non-PR context, invalid state,
  duplicate IDs and paths, malformed coordinates, and zero denominators.
- New re-review tests must accumulate; earlier regression cases must not be removed
  when a fixture suite is reorganized.
- Implementation reports must list the tests that still exist in the current suite.

### Documentation, performance, and CI

- Public DTO properties and calculator behavior must document coordinate bases,
  normalized paths, exclusions, zero denominators, ordering, parameters, returns,
  and validation failures.
- The PR description and implementation report must be refreshed after each major
  contract change so Red, Green, final HEAD, and workflow run remain accurate.
- Reviewed intervals must not be expanded line by line when changed-coordinate
  lookup can use normalized intervals and bounded search.
- CI success alone is insufficient when the malformed cases under review have no
  regression tests.
- The final CI decision must use the workflow run associated with the branch HEAD
  SHA, and failure artifacts must be used to diagnose intermediate failures.

## Cross-PR Review Requirements Derived From the Analysis

A reusable code review must explicitly cover or disposition all of the following:

- task exit criteria and authoritative design
- changed files and dependent call sites
- public and persisted contracts
- identity, revision, path, and state invariants
- malformed, stale, partial, duplicate, contradictory, and unknown input
- atomicity and failure behavior
- realistic test fixtures and test-first evidence
- cumulative regression retention
- performance, repeated I/O, repeated process launches, and algorithmic complexity
- source documentation and design consistency
- report and PR evidence consistency
- branch-HEAD-specific CI and failure artifacts
- scope boundaries, held findings, and unrelated-owner protection
- re-review of previously uninspected code, not only verification of the last fix

These requirements are implemented in
`skills/review-enforcer/references/code-review-coverage-checklist.md`.
