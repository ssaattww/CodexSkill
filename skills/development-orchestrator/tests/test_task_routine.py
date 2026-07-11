"""development-orchestrator の task routine と hook gate の単体テスト。"""

from __future__ import annotations

import json
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


class TaskRoutineTest(unittest.TestCase):
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

    def start(self) -> dict[str, object]:
        return state.start(self.root, "issue-47", "task routine hookを検証する")

    def finish_before_reflections(self, routine: dict[str, object]) -> dict[str, object]:
        for name in state.STEPS[:7]:
            routine = state.mark(self.root, routine, name, "done", f"{name} evidence")
        return routine

    def test_start_persists_state_inside_git_directory(self) -> None:
        routine = self.start()

        saved = state.load(self.root)

        self.assertEqual(saved, routine)
        self.assertEqual(state.next_step(saved), "intake")
        self.assertTrue(state.state_path(self.root).is_file())
        self.assertIn(".git", state.state_path(self.root).parts)

    def test_step_order_is_enforced(self) -> None:
        routine = self.start()

        with self.assertRaisesRegex(state.RoutineError, "intake, skill_scan, task_definition"):
            state.mark(self.root, routine, "plan", "done", "plan evidence")

    def test_structured_steps_require_dedicated_commands(self) -> None:
        routine = self.finish_before_reflections(self.start())

        with self.assertRaisesRegex(state.RoutineError, "専用command"):
            state.mark(self.root, routine, "skill_reflection", "done", "generic evidence")

    def test_reflection_and_feedback_require_target_for_non_none_decision(self) -> None:
        routine = self.finish_before_reflections(self.start())

        with self.assertRaisesRegex(state.RoutineError, "target"):
            state.reflection(
                self.root,
                routine,
                "skill",
                "update-existing",
                None,
                "skill evidence",
            )

        routine = state.reflection(
            self.root,
            routine,
            "skill",
            "none",
            None,
            "既存skillで十分",
        )
        routine = state.reflection(
            self.root,
            routine,
            "tool",
            "create-internal",
            "task_routine.py",
            "反復確認を内部CLI化",
        )

        with self.assertRaisesRegex(state.RoutineError, "target"):
            state.feedback(self.root, routine, "issue", None, "duplicate evidence")

    def test_full_lifecycle_completes_only_after_git_submission(self) -> None:
        routine = self.finish_before_reflections(self.start())
        routine = state.reflection(self.root, routine, "skill", "none", None, "変更不要")
        routine = state.reflection(
            self.root,
            routine,
            "tool",
            "create-internal",
            "task_routine.py",
            "内部toolを追加",
        )
        routine = state.feedback(
            self.root,
            routine,
            "issue",
            "#47",
            "既存issueへ統合",
        )
        routine = state.mark(self.root, routine, "progress_sync", "done", "進捗同期済み")
        self.assertEqual(routine["task"]["status"], "active")

        routine = state.mark(self.root, routine, "git_submission", "done", "commitとPR作成済み")

        self.assertEqual(routine["task"]["status"], "completed")
        self.assertIsNone(state.next_step(routine))

    def test_pre_tool_use_blocks_edit_without_active_task(self) -> None:
        result = hooks.handle_hook(
            {
                "hook_event_name": "PreToolUse",
                "cwd": str(self.root),
                "tool_name": "apply_patch",
                "tool_input": {"patch": "*** Begin Patch"},
            }
        )

        self.assertEqual(
            result["hookSpecificOutput"]["permissionDecision"],
            "deny",
        )
        self.assertIn("active task routine", result["hookSpecificOutput"]["permissionDecisionReason"])

    def test_pre_tool_use_allows_edit_after_early_steps_and_blocks_submission(self) -> None:
        routine = self.start()
        for name in state.EARLY:
            routine = state.mark(self.root, routine, name, "done", f"{name} evidence")

        edit_result = hooks.handle_hook(
            {
                "hook_event_name": "PreToolUse",
                "cwd": str(self.root),
                "tool_name": "apply_patch",
                "tool_input": {"patch": "*** Begin Patch"},
            }
        )
        submit_result = hooks.handle_hook(
            {
                "hook_event_name": "PreToolUse",
                "cwd": str(self.root),
                "tool_name": "GitHub.create_pull_request",
                "tool_input": {},
            }
        )

        self.assertIsNone(edit_result)
        self.assertEqual(submit_result["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertIn("implementation", submit_result["hookSpecificOutput"]["permissionDecisionReason"])

    def test_contents_api_writes_use_submission_gate(self) -> None:
        routine = self.start()
        for name in state.EARLY:
            routine = state.mark(self.root, routine, name, "done", f"{name} evidence")

        for tool_name in (
            "GitHub.create_file",
            "GitHub.update_file",
            "GitHub.delete_file",
        ):
            with self.subTest(tool_name=tool_name):
                result = hooks.handle_hook(
                    {
                        "hook_event_name": "PreToolUse",
                        "cwd": str(self.root),
                        "tool_name": tool_name,
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

    def test_issue_tracking_tools_do_not_require_active_routine(self) -> None:
        for tool_name in (
            "GitHub.create_issue",
            "GitHub.update_issue",
            "GitHub.add_comment_to_issue",
            "GitHub.add_review_to_pr",
        ):
            with self.subTest(tool_name=tool_name):
                result = hooks.handle_hook(
                    {
                        "hook_event_name": "PreToolUse",
                        "cwd": str(self.root),
                        "tool_name": tool_name,
                        "tool_input": {},
                    }
                )
                self.assertIsNone(result)

    def test_shell_classification_distinguishes_read_edit_and_submission(self) -> None:
        self.assertEqual(hooks.classify_shell_command("git status --short"), "other")
        self.assertEqual(hooks.classify_shell_command("printf x > result.txt"), "edit")
        self.assertEqual(hooks.classify_shell_command("git commit -m test"), "submission")
        self.assertEqual(hooks.classify_shell_command("echo ok >/dev/null"), "other")

    def test_session_start_injects_current_step_and_stop_requests_continuation(self) -> None:
        self.start()

        start_result = hooks.handle_hook(
            {"hook_event_name": "SessionStart", "cwd": str(self.root)}
        )
        stop_result = hooks.handle_hook(
            {
                "hook_event_name": "Stop",
                "cwd": str(self.root),
                "stop_hook_active": False,
            }
        )

        self.assertIn(
            "next required step: intake",
            start_result["hookSpecificOutput"]["additionalContext"],
        )
        self.assertEqual(stop_result["decision"], "block")
        self.assertIn("intake", stop_result["reason"])

    def test_stop_hook_reentry_does_not_loop(self) -> None:
        self.start()

        result = hooks.handle_hook(
            {
                "hook_event_name": "Stop",
                "cwd": str(self.root),
                "stop_hook_active": True,
            }
        )

        self.assertIsNone(result)

    def test_paused_task_does_not_force_stop_continuation(self) -> None:
        routine = state.pause(self.root, self.start(), "利用者判断待ち")

        result = hooks.handle_hook(
            {"hook_event_name": "Stop", "cwd": str(self.root)}
        )

        self.assertEqual(routine["task"]["status"], "paused")
        self.assertIsNone(result)

    def test_hook_installer_is_idempotent_and_preserves_existing_handler(self) -> None:
        target = self.root / ".codex" / "hooks.json"
        target.parent.mkdir(parents=True)
        target.write_text(
            json.dumps(
                {
                    "hooks": {
                        "PostToolUse": [
                            {
                                "hooks": [
                                    {"type": "command", "command": "python3 existing.py"}
                                ]
                            }
                        ]
                    }
                }
            ),
            encoding="utf-8",
        )
        script = self.root / "task_routine.py"

        _, first_changed = hooks.install("project", self.root, target, script)
        _, second_changed = hooks.install("project", self.root, target, script)
        installed = json.loads(target.read_text(encoding="utf-8"))
        _, removed = hooks.install("project", self.root, target, script, remove=True)
        uninstalled = json.loads(target.read_text(encoding="utf-8"))

        self.assertTrue(first_changed)
        self.assertFalse(second_changed)
        self.assertEqual(len(installed["hooks"]["SessionStart"]), 1)
        self.assertEqual(
            installed["hooks"]["PostToolUse"][0]["hooks"][0]["command"],
            "python3 existing.py",
        )
        self.assertTrue(removed)
        self.assertEqual(uninstalled["hooks"], {"PostToolUse": installed["hooks"]["PostToolUse"]})


if __name__ == "__main__":
    unittest.main()
