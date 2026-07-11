"""MCP形式のtool名に対するtask routine gateを検証する。"""

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


class TaskRoutineMcpToolNameTest(unittest.TestCase):
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
        routine = state.start(
            self.root,
            "issue-47-mcp-pr",
            "MCP形式のPR tool名を検証する",
        )
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
            "既存skillの責務内で対応済み",
        )
        routine = state.reflection(
            self.root,
            routine,
            "tool",
            "create-internal",
            "task_routine_hooks.py",
            "MCP形式のtool名を内部hookで正規化した",
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

    def test_prefixed_mcp_pr_tool_name_is_normalized_and_body_is_gated(self) -> None:
        self.ready_for_pr()
        self.assertEqual(
            hooks.tool_token("mcp__github__create_pull_request"),
            "create_pull_request",
        )

        result = hooks.handle_hook(
            {
                "hook_event_name": "PreToolUse",
                "cwd": str(self.root),
                "tool_name": "mcp__github__create_pull_request",
                "tool_input": {"body": "## Summary\n証跡なし"},
            }
        )

        self.assertEqual(
            result["hookSpecificOutput"]["permissionDecision"],
            "deny",
        )
        self.assertIn(
            "PR本文",
            result["hookSpecificOutput"]["permissionDecisionReason"],
        )

    def test_prefixed_mcp_contents_api_uses_submission_gate(self) -> None:
        routine = state.start(
            self.root,
            "issue-47-mcp-update",
            "MCP形式のContents API tool名を検証する",
        )
        for name in state.EARLY:
            routine = state.mark(
                self.root,
                routine,
                name,
                "done",
                f"{name} evidence",
            )

        result = hooks.handle_hook(
            {
                "hook_event_name": "PreToolUse",
                "cwd": str(self.root),
                "tool_name": "mcp__github__update_file",
                "tool_input": {"path": "README.md"},
            }
        )

        self.assertEqual(
            result["hookSpecificOutput"]["permissionDecision"],
            "deny",
        )
        self.assertIn(
            "implementation",
            result["hookSpecificOutput"]["permissionDecisionReason"],
        )


if __name__ == "__main__":
    unittest.main()
