from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "review-enforcer" / "SKILL.md"
CHECKLIST = (
    ROOT
    / "skills"
    / "review-enforcer"
    / "references"
    / "code-review-coverage-checklist.md"
)
ANALYSIS = (
    ROOT
    / "reports"
    / "review-coverage-analysis-revmem-pr15-pr24-pr25-20260726.md"
)
HIERARCHY_DESIGN = ROOT / "design" / "skill-hierarchy-design.md"
SKILL_HIERARCHY_DESIGN = ROOT / "skills" / "design" / "skill-hierarchy-design.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    skill = SKILL.read_text(encoding="utf-8")

    require(CHECKLIST.exists(), "code review coverage checklist is missing")
    checklist = CHECKLIST.read_text(encoding="utf-8")

    require(ANALYSIS.exists(), "source review analysis report is missing")
    analysis = ANALYSIS.read_text(encoding="utf-8")

    require(
        "[references/code-review-coverage-checklist.md]"
        "(references/code-review-coverage-checklist.md)" in skill,
        "review-enforcer does not route reviewers to the coverage checklist",
    )
    require(
        "coverage matrix" in skill,
        "review report contract does not require a coverage matrix",
    )
    require(
        "unexplored areas" in skill,
        "review report contract does not require unexplored areas",
    )

    required_headings = (
        "# Code Review Coverage Checklist",
        "## Review Basis",
        "## Change and Dependency Scope",
        "## Contract and Specification",
        "## State, Identity, and Persistence",
        "## Boundary and Malformed Input",
        "## Test Quality and Regression Retention",
        "## Performance and Side Effects",
        "## Documentation and Design Consistency",
        "## CI and Evidence",
        "## Re-review Expansion",
    )
    for heading in required_headings:
        require(heading in checklist, f"missing checklist heading: {heading}")

    for pr_number in (15, 24, 25):
        require(
            f"PR #{pr_number}" in analysis,
            f"analysis report does not cover RevMem PR #{pr_number}",
        )

    hierarchy_design = HIERARCHY_DESIGN.read_text(encoding="utf-8")
    skill_hierarchy_design = SKILL_HIERARCHY_DESIGN.read_text(encoding="utf-8")
    require(
        hierarchy_design == skill_hierarchy_design,
        "duplicated skill hierarchy designs are not synchronized",
    )
    require(
        "code-review-coverage-checklist.md" in hierarchy_design,
        "skill hierarchy design does not describe the review coverage checklist",
    )
    require(
        "coverage matrix" in hierarchy_design,
        "skill hierarchy design does not describe the coverage matrix contract",
    )

    print("review-enforcer contract validation passed")


if __name__ == "__main__":
    main()
