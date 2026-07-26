#!/usr/bin/env python3
"""Contract tests for standalone ChatGPT chat worker skills."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHARED_CONTRACT = ROOT / "skills" / "chat-worker-shared" / "references" / "handoff-contract.md"
DESIGN_FILES = (
    ROOT / "design" / "chat-worker-skill-design.md",
    ROOT / "skills" / "design" / "chat-worker-skill-design.md",
)

SKILLS = {
    "chat-implementation-worker": ROOT / "skills" / "chat-implementation-worker" / "SKILL.md",
    "chat-review-worker": ROOT / "skills" / "chat-review-worker" / "SKILL.md",
    "chat-report-writer": ROOT / "skills" / "chat-report-writer" / "SKILL.md",
}

FORBIDDEN_ORCHESTRATION_DEPENDENCIES = (
    "sub-agent-task-manager",
    "codex-delegation-executor",
    "spawn_agent",
)

COMMON_REQUIRED_MARKERS = (
    "## Execution model",
    "利用者が親",
    "別workerを起動しない",
    "../chat-worker-shared/references/handoff-contract.md",
    "## Inputs",
    "## Outputs",
    "## Completion condition",
)

SKILL_SPECIFIC_MARKERS = {
    "chat-implementation-worker": (
        "initial implementation",
        "review follow-up",
        "test-first",
        "最終review判定を行わない",
        "narrative reportを作成しない",
        "mergeしない",
    ),
    "chat-review-worker": (
        "initial review",
        "fix verification",
        "cold final review",
        "unstable",
        "product codeを変更しない",
    ),
    "chat-report-writer": (
        "implementation report",
        "review report",
        "verification report",
        "事実を発明しない",
        "codeまたはtestを変更しない",
    ),
}

HANDOFF_REQUIRED_MARKERS = (
    "task_id",
    "repository",
    "branch",
    "base_ref",
    "head_sha",
    "authorized_actions",
    "write_boundary",
    "scope",
    "non_goals",
    "authoritative_requirements",
    "files",
    "commands",
    "tests",
    "ci",
    "implementation",
    "review",
    "report",
    "findings",
    "held",
    "unexplored",
    "remaining_risks",
    "next_action",
    "next_chat_input",
    "requested_authorized_actions",
    "requested_write_boundary",
)


class ChatWorkerSkillContractTests(unittest.TestCase):
    def read_required(self, path: Path) -> str:
        self.assertTrue(path.is_file(), f"required file is missing: {path.relative_to(ROOT)}")
        return path.read_text(encoding="utf-8")

    def test_required_skill_files_exist_and_are_standalone(self) -> None:
        for skill_name, path in SKILLS.items():
            with self.subTest(skill=skill_name):
                text = self.read_required(path)
                frontmatter = text.split("---", maxsplit=2)
                self.assertGreaterEqual(len(frontmatter), 3, f"{skill_name} requires YAML frontmatter")
                self.assertIn(f"name: {skill_name}", frontmatter[1])
                self.assertIn("description:", frontmatter[1])
                for marker in COMMON_REQUIRED_MARKERS:
                    self.assertIn(marker, text, f"{skill_name} is missing marker: {marker}")
                for marker in SKILL_SPECIFIC_MARKERS[skill_name]:
                    self.assertIn(marker, text, f"{skill_name} is missing marker: {marker}")
                for forbidden in FORBIDDEN_ORCHESTRATION_DEPENDENCIES:
                    self.assertNotIn(
                        forbidden,
                        text,
                        f"{skill_name} must not depend on agent orchestration: {forbidden}",
                    )

    def test_shared_handoff_contract_is_complete(self) -> None:
        text = self.read_required(SHARED_CONTRACT)
        for marker in HANDOFF_REQUIRED_MARKERS:
            self.assertIn(marker, text, f"handoff contract is missing field: {marker}")
        self.assertIn("利用者", text)
        self.assertIn("次のchat", text)
        self.assertIn("unknown", text)
        self.assertIn("not_applicable", text)
        self.assertIn("次のchatへ自動継承しない", text)

    def test_chat_worker_designs_are_identical_and_register_workers(self) -> None:
        primary = self.read_required(DESIGN_FILES[0])
        mirrored = self.read_required(DESIGN_FILES[1])
        self.assertEqual(primary, mirrored, "the two chat worker design files must be byte-identical")
        self.assertIn("利用者が親となるChatGPT chat worker flow", primary)
        self.assertIn("既存Codex向けskill hierarchyとは分離", primary)
        for skill_name in SKILLS:
            self.assertIn(skill_name, primary)


if __name__ == "__main__":
    unittest.main(verbosity=2)
