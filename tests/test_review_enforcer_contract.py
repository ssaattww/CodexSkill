from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "review-enforcer" / "SKILL.md"
REPORT_MANAGER = ROOT / "skills" / "report-output-manager" / "SKILL.md"
CHECKLIST = (
    ROOT
    / "skills"
    / "review-enforcer"
    / "references"
    / "code-review-coverage-checklist.md"
)
REVIEW_TEMPLATE = (
    ROOT
    / "skills"
    / "report-output-manager"
    / "references"
    / "review-report-template.md"
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
    report_manager = REPORT_MANAGER.read_text(encoding="utf-8")

    require(CHECKLIST.exists(), "code review coverage checklist is missing")
    checklist = CHECKLIST.read_text(encoding="utf-8")

    require(REVIEW_TEMPLATE.exists(), "review report template is missing")
    review_template = REVIEW_TEMPLATE.read_text(encoding="utf-8")

    require(ANALYSIS.exists(), "source review analysis report is missing")
    analysis = ANALYSIS.read_text(encoding="utf-8")

    require(
        "[references/code-review-coverage-checklist.md]"
        "(references/code-review-coverage-checklist.md)" in skill,
        "review-enforcer does not route reviewers to the coverage checklist",
    )
    require(
        "[review report template]"
        "(../report-output-manager/references/review-report-template.md)" in skill,
        "review-enforcer does not require the dedicated review report template",
    )
    require(
        "[references/review-report-template.md]"
        "(references/review-report-template.md)" in report_manager,
        "report-output-manager does not expose the review report template",
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

    required_template_headings = (
        "# コードレビュー報告書",
        "## タスクとレビュー情報",
        "## 確認項目",
        "## 確認したファイル",
        "## 実行・確認したテストとコマンド",
        "## 指摘事項",
        "## 保留・対象外",
        "## 未確認領域",
        "## CI証跡",
        "## 最終判定",
    )
    for heading in required_template_headings:
        require(
            heading in review_template,
            f"missing review report template heading: {heading}",
        )

    required_template_items = (
        "レビュー基準",
        "変更・依存範囲",
        "契約・仕様",
        "状態・identity・永続化",
        "境界・不正入力",
        "Atomicity・失敗動作",
        "テスト品質・回帰保持",
        "性能・副作用",
        "文書・設計整合",
        "CI・証跡",
        "再レビュー拡張",
    )
    for item in required_template_items:
        require(
            item in review_template,
            f"review report template does not list coverage item: {item}",
        )

    for state in (
        "確認済み・指摘なし",
        "確認済み・指摘あり",
        "保留",
        "対象外",
        "未確認",
    ):
        require(
            state in review_template,
            f"review report template does not define coverage state: {state}",
        )

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
        "review-report-template.md" in hierarchy_design,
        "skill hierarchy design does not describe the review report template",
    )
    require(
        "coverage matrix" in hierarchy_design,
        "skill hierarchy design does not describe the coverage matrix contract",
    )

    print("review-enforcer contract validation passed")


if __name__ == "__main__":
    main()
