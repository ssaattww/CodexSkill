# Decision examples

Use these as contextual review cases, not as global allowed or forbidden words. Each row supplies assumptions; changing those assumptions can change the result. Example code notation quotes the expression under examination and is not permission to hide ordinary prose in a real document.

These are contract examples for a reviewer to evaluate. A script finding the examples in this file does not demonstrate that a model can reliably make the decisions.

## Cases

| ID | Context and change | Expected wording result | Evidence required |
| --- | --- | --- | --- |
| DW-01 | The contract requires the named algorithm `SHA-256`. Replace it with 「要約値-256」. | `fail` | The replacement no longer identifies that algorithm; another 256-bit digest could satisfy the sentence. Preserve the specified algorithm's identity. |
| DW-02 | A wire format consists of 18 bytes. Replace the length with 「18個の8桁単位」 without defining the radix or unit. | `fail` | A digit count is not an unambiguous byte unit. State the unit and keep length/offset requirements consistent. |
| DW-03 | The approved phrase is `8-bit byte`. Define one format unit as that phrase, then use 「全長18単位、位置0から17」 with a nearby unambiguous definition. | `pass` | The unit, total length, and positions remain identifiable. This case does not approve `byte` as a standalone whitelist entry. |
| DW-04 | `release candidate` is approved only as a prerelease build. A paragraph calls memory regions considered for freeing `release candidate`. | `fail` | The occurrence has a different referent from the approved meaning despite matching the exact phrase. |
| DW-05 | A project's established language name is `Rust`. Every mention is expanded to `Rust programming language` solely to satisfy a minimum phrase length, without adding necessary information. | `fail` plus a policy conflict if no compliant repair is known | Show the redundant repetitions and the stated registration-only reason. Do not automatically approve the standalone name. The longer phrase is not globally forbidden in contexts where it is useful. |
| DW-06 | Introduce SIMD to the stated unfamiliar audience with 「SIMDは、単一の命令で複数の値を処理する方式です」. The supplied terminology policy allows this exact use. | `pass` | The first-use explanation serves the audience and preserves the concept. Long Japanese wording is not intrinsically a defect. |
| DW-07 | A glossary already defines SIMD. Replace each mention in a short operation table with the full first-use explanation, obscuring which cells refer to the same defined operation. | `fail` | Quote the repeated cells and glossary; identify the lost correspondence and redundant expansion. A repair must still satisfy the whitelist policy. |
| DW-08 | The project defines 「ハッシュ値」 as its canonical concept name. Replace it with 「散列」 without defining a mapping, while the other sections retain 「ハッシュ値」. | `fail` | The concept name becomes inconsistent. Do not base the finding solely on unfamiliar kanji or unsupported claims about word popularity. |
| DW-09 | The project explicitly defines 「散列」 as its canonical term and uses it consistently with its required meaning. | `pass` | The authorized definition and actual context support the term. DW-08 is not a blacklist entry. |
| DW-10 | Preserve the real field identifier `caseId` as inline code and write the explanation outside it. | `pass` | The marked text is an actual identifier, not ordinary prose disguised as code. |
| DW-11 | Wrap an entire ordinary explanatory sentence in backticks only because its terms fail lint. | `fail` | Show that the sentence is prose, identify the hidden terms, and return policy conflicts rather than suggesting another mask. |
| DW-12 | Replace an ambiguous term whose original paragraph and definition cannot be obtained. | `incomplete` | Identify the missing evidence. Do not guess the original sense and report either a semantic pass or an unsupported mistranslation finding. |
| DW-13 | The only demonstrated clear expression violates the current entry rule, and no acceptable alternative is established. | `needs_policy_decision` | Return exact constraints and candidates. Do not permit a standalone word or choose an awkward substitution just to finish. |
| DW-14 | A new document has no previous revision; the supplied requirements and definitions fully explain its new prose. | Evaluate the full new prose; `pass` only with evidence | Record `baseline_absent_new_file`. Missing historical prose alone is not a defect, but missing requirements are still a gap. |
| DW-15 | A document rewrites every English expression into Japanese and produces zero unknown-word diagnostics. | Not enough evidence for `pass` | Compare all changed prose, including the Japanese-only replacements. Mechanical success proves none of the four review dimensions by itself. |
| DW-16 | Only executable code changes; there are no prose, explanations, definitions, or approval changes in the authorized scope. | `not_applicable` | Record the changed-file inventory and absence of a wording target. Lack of lint configuration is not this exemption. |
| DW-17 | A whitelist description changes its permitted meaning while document text remains unchanged. | Review the affected occurrences | Include unchanged usages impacted by the changed approval. Exact text equality does not preserve approval semantics. |
| DW-18 | A user-authorized specification change replaces the selected algorithm, and the document accurately names and explains the new one. | Do not reject solely for changed meaning | Cite the authority for the specification change, then assess identification, approved usage, and readability under the new requirements. |

## Finding record example

For DW-01, a sufficient record includes:

- Identity: `DW-01-algorithm-identity`.
- Severity: the caller's severity appropriate to changing a required algorithm, not a style-only classification.
- Origin and location: the actual introducing change and file/line, supplied by the caller rather than fabricated from this example.
- Before: the sentence requiring `SHA-256`.
- After: the corresponding sentence requiring 「要約値-256」.
- Impact: the set of implementations allowed by the contract becomes broader.
- Evidence: the specification selecting the named algorithm and the two complete sentences.
- Required action: restore the authorized algorithm identity without changing its semantics or bypassing the terminology rules.
- Policy conflict: record separately when the exact expression cannot be used under current entry rules; do not erase the demonstrated defect.

## Closure and negative controls

For each correction, check the cited occurrence and the same changed usage in headings, tables, summaries, and definitions within scope. Keep the original finding identity and severity. Do not close a unit finding after correcting the main definition while a summary still uses the ambiguous unit.

Pair rejection cases with DW-03, DW-06, DW-09, DW-10, and DW-18. A review that rejects everything containing English or everything containing unfamiliar kanji fails these controls. An author running through these cases still has not supplied an independent reviewer verdict.
