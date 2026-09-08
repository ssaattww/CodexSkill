---
name: document-wording-review
description: Review human-facing document changes for preserved meaning, identifiable terminology, approved usage, and readability, including Japanese rewrites that already pass a word whitelist. Use for document creation, wording changes, and changes to terminology definitions or approvals.
---

# Document Wording Review

## Goal

Reject wording regressions that mechanical terminology checks cannot detect. Keep whitelist eligibility and document quality as separate decisions. Neither zero unknown words nor a technically explainable translation proves that a sentence is suitable for its readers.

## Runtime independence

Run inside the invoking author or existing reviewer. Do not create another agent, choose a model, modify files, approve terminology entries, or issue an independent review verdict. The caller owns execution, identity, permission, persistence, and the final acceptance gate.

Author self-checks are implementation evidence, not normal or independent review. Both Codex and ChatGPT use this same contract through their core workers.

## Inputs

Require:

- repository, base revision, target revision or working-tree identity, and review mode;
- complete changed-file list and diff, including removals and terminology-configuration changes;
- original and replacement sentences, surrounding paragraphs, headings, tables, and relevant definitions;
- intended readers, document purpose, authoritative requirements, and project terminology policy;
- exact approved phrases, their meanings and usage restrictions, and approval evidence when relevant;
- mechanical lint results, with missing or unsupported checks explicitly identified;
- prior finding identities and coverage for bounded fix verification.

For new documents, mark the baseline as absent because the file is new and use requirements and definitions instead. An unavailable baseline for an existing document is missing evidence, not a new-document exemption. Request only the missing evidence from the caller; do not invent it.

If discovery confirms no project-specific approval registry applies, record that fact and assess approved usage as `not_applicable`; do not invent entries or an implicit single-word permission. An expected registry that cannot be read is missing evidence, not this exemption.

## Scope

Inspect all changed human-facing prose, not just registration candidates or unknown-word diagnostics. Include passages whose English or katakana has disappeared, headings, tables, glossary entries, and explanations around actual identifiers. When definitions or approvals change, inspect affected occurrences even if their prose did not change.

List each changed file with its covered ranges or an explicit exclusion reason. Mechanical lint exclusions do not automatically exclude wording review. Respect the caller's explicit audience/scope decisions for generated, external, or historical material; do not expand exclusions to make the gate pass.

## Required flow

1. Resolve scope and immutable target evidence. Read the [decision examples](references/decision-examples.md) before the first review; use relevant cases again when verifying fixes.
2. Compare original and replacement sentences in context. For new text, compare against requirements and defined concepts.
3. Assess each dimension independently:
   - **Meaning:** preserve quantities, units, negation, conditions, boundaries, actor/object relations, and technical guarantees.
   - **Identification:** preserve the identity of algorithms, standards, types, commands, fields, units, and named concepts. A descriptive paraphrase is not necessarily an equivalent identifier.
   - **Approved usage:** compare each relevant occurrence with its approved meaning and restrictions. Exact spelling, a multiword form, or earlier approval does not license a different sense.
   - **Readability:** identify ambiguous referents, broken modifiers, unexplained renamed concepts, mistranslations, and unnecessary repeated expansions. Evaluate sentences and paragraphs, not character classes.
4. Check for policy-driven distortion: invented translations, repeated explanatory names, words added only to meet a minimum phrase length, or ordinary prose hidden as code. Real identifiers, commands, paths, and UI labels may legitimately use code notation.
5. State concrete evidence for every finding: before/after text, location, changed meaning or reader burden, applicable definition or requirement, and the necessary correction. "Unnatural" alone is not a finding.
6. When established usage is material, prefer project definitions and authoritative domain documentation. Keep sources and uncertainty. Frequency counts, dictionary suggestions, and character ratios are supporting evidence only; do not invent popularity evidence or rank whole sentences by isolated word counts.
7. If no demonstrated policy-compliant wording is available, return `needs_policy_decision` with the conflicting constraints, exact candidates, and unresolved questions. Do not silently allow standalone words, widen phrases or aliases, rewrite approved meanings, expand exclusions, or accept an awkward substitute to finish.
8. Return dimension-level dispositions, complete findings, coverage gaps, policy conflicts, and a wording result separate from mechanical lint.

## Decision rules

- Preserve a target repository's standalone-word prohibition. Do not propose global single-word permission as the default repair.
- A refusal to register a word does not establish that its replacement is acceptable.
- A multiword whitelist reduces lexical scope but does not prove meaning at every occurrence. Check the actual use as well.
- Kanji, katakana, English, acronyms, and familiar technical terms are not intrinsically pass or fail. Do not introduce a global vocabulary blacklist or a "translate everything" rule.
- A clear first-use explanation may help; mechanically repeating that explanation instead of an established name may obscure the document. Show the actual repetition and its effect.
- Do not reject an authorized specification change merely because it changes meaning. Identify its authority and review the new wording against the changed specification.
- A known incorrect replacement remains a finding even when its repair also needs a policy decision. Report both; do not downgrade the defect to uncertainty.
- In fix verification, preserve finding identity and severity, check every affected occurrence and sibling case in the authorized scope, and record complete closure evidence. Do not reopen unrelated closed findings or expand an independent-closure lifecycle.

## Outputs

Return `document_wording_review` with:

- mode: `author_self_check` or the caller's actual review mode;
- target identity, base or explicit new-file baseline status, and reviewer identity supplied by the caller;
- coverage by file/range, exclusions with reasons, and unresolved evidence gaps;
- per-dimension dispositions: `checked_no_finding`, `checked_finding`, `not_applicable`, or `unexplored`;
- supplied mechanical-lint state without changing its meaning;
- wording result: `pass`, `fail`, `needs_policy_decision`, `incomplete`, or `not_applicable`;
- findings with identity, severity, origin, location, before/after evidence, impact, required action, and definition/source references;
- exact policy conflicts and candidates, without granting approval;
- closure evidence, remaining risks, and next required action.

Result precedence is `fail` for demonstrated required defects, then `needs_policy_decision`, then `incomplete` for missing required evidence. Use `pass` only after all in-scope dimensions and occurrences have evidence. Use `not_applicable` only when scope discovery confirms there is no relevant prose or terminology change, not because lint is absent or already green.

## Caller integration

`implementation-worker` invokes this Skill for an author self-check after applicable writing. `review-worker` invokes it inside the existing reviewer for initial review, relevant fix verification, and the authorized independent-review scope. The same reviewer remains responsible; this is not an extra reviewer lifecycle.

The caller combines mechanical compliance, preserved meaning/identity/usage, and readability. A wording pass cannot override failed, unsupported, or approval-blocked mechanical checks. Mechanical success cannot override wording defects, missing coverage, or a policy conflict. Unresolved required wording checks cannot be converted to nonblocking held items merely to obtain approval.

Missing this required Skill produces a dependency gap, not a substitute local copy of its rules. Do not recurse into the caller or the mechanical checker from this Skill. Configuration changes go back to the existing authorized entry-approval process.

## Completion condition

Complete only when every in-scope change has a coverage disposition, each required dimension has evidence or an explicit unresolved status, concrete defects and policy conflicts are preserved, and the caller receives a wording result that cannot be mistaken for mechanical-lint success or an independent verdict on the author's own work. Do not modify repository content or merge.
