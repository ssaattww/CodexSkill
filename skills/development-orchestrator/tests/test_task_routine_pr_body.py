"""PR本文のtask routine証跡ゲートを検証する。"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import task_routine_hooks as hooks
import task_routine_state as state


class TaskRoutinePRBodyTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        result = subprocess.run(
            ["git", "init", "-q", str(self.root)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def ready_for_pr(self) -> dict[str, object]:
        routine = state.start(self.root, "issue-47", "PR本文証跡ゲートを検証する")
        for name in state.STEPS[:7]:
            routine = state.mark(
                self.root,
                routine,
                name,
                "done",
                f"{name} evidence",
            )
        routine = state.reflection(
            self.root,
            routine,
            "skill",
            "none",
            None,
            "既存skill更新は現在の差分に含まれる",
        )
        routine = state.reflection(
            self.root,
            routine,
            "tool",
            "create-internal",
            "task_routine.py",
            "task routineを内部toolとして実装した",
        )
        routine = state.feedback(
            self.root,
            routine,
            "issue",
            "#47",
            "Issue #47へ追跡を統合した",
        )
        return state.mark(
            self.root,
            routine,
            "progress_sync",
            "done",
            "review reportとIssueを同期した",
        )

    def pre_tool_use(self, body: str | None) -> dict[str, object] | None:
        return hooks.handle_hook(
            {
                "hook_event_name": "PreToolUse",
                "cwd": str(self.root),
                "tool_name": "GitHub.create_pull_request",
                "tool_input": {"body": body},
            }
        )

    def test_missing_required_pr_sections_is_blocked(self) -> None:
        self.ready_for_pr()

        result = self.pre_tool_use("## Summary\n変更概要")

        self.assertEqual(
            result["hookSpecificOutput"]["permissionDecision"],
            "deny",
        )
        reason = result["hookSpecificOutput"]["permissionDecisionReason"]
        self.assertIn("task routine", reason)
        self.assertIn("skill action", reason)
        self.assertIn("tool action", reason)

    def test_placeholder_only_pr_sections_are_blocked(self) -> None:
        self.ready_for_pr()

        result = self.pre_tool_use(
            """## Task routine evidence
TODO

## Skill action
none

## Tool action
未記入
"""
        )

        self.assertEqual(
            result["hookSpecificOutput"]["permissionDecision"],
            "deny",
        )

    def test_evidence_backed_pr_sections_are_allowed(self) -> None:
        self.ready_for_pr()

        result = self.pre_tool_use(
            """## Summary
task routine hookを追加した。

## Task routine evidence
- verification、review、feedback、progress syncを完了した。

## Skill action
- update-existing: development-orchestratorとfeedback-points-managerを更新した。

## Tool action
- create-internal: task_routine.pyとlifecycle hookを追加した。
"""
        )

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
