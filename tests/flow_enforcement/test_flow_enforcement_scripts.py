import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_ROOT = REPO_ROOT / "skills" / "flow-enforcement" / "scripts"
HOOK_ROOT = REPO_ROOT / "skills" / "flow-enforcement" / "hooks"


class FlowEnforcementScriptTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.state_root = self.root / ".codex" / "state"
        self.workflow_root = self.root / ".codex" / "workflows"
        self.step_root = self.root / "skills"
        self.state_root.mkdir(parents=True)
        self.workflow_root.mkdir(parents=True)
        (self.step_root / "development-lifecycle").mkdir(parents=True)

        self.workflow_path = self.workflow_root / "release-workflow.json"
        self.workflow_path.write_text(
            json.dumps(
                {
                    "workflow_id": "release-governance",
                    "version": 1,
                    "nodes": [
                        {
                            "id": "implementation_phase",
                            "kind": "phase",
                            "required": True,
                            "children": [
                                {
                                    "id": "hook_state_task",
                                    "kind": "task",
                                    "task_type": "implementation",
                                    "required": True,
                                    "step_set_ref": {
                                        "skill": "development-lifecycle",
                                        "version": 1,
                                        "set": "implementation-task",
                                    },
                                }
                            ],
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        (self.step_root / "development-lifecycle" / "steps.json").write_text(
            json.dumps(
                {
                    "skill": "development-lifecycle",
                    "version": 1,
                    "step_sets": [
                        {
                            "id": "implementation-task",
                            "task_type": "implementation",
                            "steps": [
                                {"id": "sync_design", "required": True},
                                {"id": "implement", "required": True},
                                {"id": "review", "required": True},
                            ],
                        },
                        {
                            "id": "design-task",
                            "task_type": "design",
                            "steps": [{"id": "update_design", "required": True}],
                        },
                    ],
                }
            ),
            encoding="utf-8",
        )
        self._write_state()
        self._write_progress()

    def tearDown(self):
        self.tmp.cleanup()

    def _write_state(self):
        state = {
            "schema_version": 1,
            "mode": "normal",
            "roots": {
                "started_project_root": str(self.root),
                "state_root": str(self.state_root),
                "codex_skill_root": str(REPO_ROOT),
                "workflow_root": str(self.workflow_root),
                "step_root": str(self.step_root),
            },
            "current_workflow": {
                "workflow_id": "release-governance",
                "version": 1,
                "workflow_path": str(self.workflow_path),
            },
            "current_task": {
                "workflow_id": "release-governance",
                "task_id": "hook_state_task",
                "task_node_path": "implementation_phase/hook_state_task",
                "task_type": "implementation",
                "status": "active",
            },
            "workflow_cursor": {},
            "context": [],
            "interrupt_stack": [],
            "input_journal": [],
            "flow_overrides": [],
            "workflow_mutations": [],
            "pending_user_intent": None,
        }
        (self.state_root / "flow_state.json").write_text(json.dumps(state), encoding="utf-8")

    def _write_progress(self):
        progress = {
            "schema_version": 1,
            "workflow": {"workflow_id": "release-governance", "version": 1},
            "completed_nodes": [],
        }
        (self.state_root / "progress.json").write_text(json.dumps(progress), encoding="utf-8")

    def _request_base(self, operation):
        return {
            "operation": operation,
            "request_id": f"test-{operation}",
            "actor": "unittest",
            "state_root": str(self.state_root),
            "workflow_root": str(self.workflow_root),
            "step_root": str(self.step_root),
        }

    def _run_script(self, script_name, request, expected_returncode=0):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT_ROOT / script_name)],
            input=json.dumps(request),
            text=True,
            capture_output=True,
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(
            expected_returncode,
            proc.returncode,
            msg=f"stdout={proc.stdout}\nstderr={proc.stderr}",
        )
        return json.loads(proc.stdout)

    def _run_hook(self, hook_name, payload=None):
        env = os.environ.copy()
        env.update(
            {
                "CODEX_STARTED_PROJECT_ROOT": str(self.root),
                "CODEX_FLOW_STATE_ROOT": str(self.state_root),
                "CODEX_REPO_WORKFLOW_ROOT": str(self.workflow_root),
                "CODEX_SKILL_STEP_ROOT": str(self.step_root),
                "CODEX_SKILL_ROOT": str(REPO_ROOT),
            }
        )
        proc = subprocess.run(
            [sys.executable, str(HOOK_ROOT / hook_name)],
            input=json.dumps(payload or {"cwd": str(self.root)}),
            text=True,
            capture_output=True,
            cwd=str(REPO_ROOT),
            env=env,
        )
        self.assertEqual(0, proc.returncode, msg=f"stdout={proc.stdout}\nstderr={proc.stderr}")
        return json.loads(proc.stdout)

    def _state(self):
        return json.loads((self.state_root / "flow_state.json").read_text(encoding="utf-8"))

    def _progress(self):
        return json.loads((self.state_root / "progress.json").read_text(encoding="utf-8"))

    def _workflow(self):
        return json.loads(self.workflow_path.read_text(encoding="utf-8"))

    def test_record_user_prompt_durably_appends_input_journal(self):
        request = self._request_base("record_user_prompt")
        request["record_user_prompt"] = {"text": "対象は v2 だけです", "source": "UserPromptSubmit"}

        response = self._run_script("update_input_journal.py", request)

        self.assertTrue(response["ok"])
        state = self._state()
        self.assertEqual(1, len(state["input_journal"]))
        self.assertEqual("unclassified", state["input_journal"][0]["status"])
        self.assertEqual("対象は v2 だけです", state["input_journal"][0]["text"])

    def test_classify_input_updates_applied_and_needs_confirmation_by_input_id(self):
        record = self._request_base("record_user_prompt")
        record["record_user_prompt"] = {"text": "Linux だけ", "source": "UserPromptSubmit"}
        input_id = self._run_script("update_input_journal.py", record)["state_summary"]["input_id"]

        classify = self._request_base("classify_input")
        classify["classify_input"] = {
            "input_id": input_id,
            "classification": {"intent": "additional_info", "confidence": 0.86, "summary": "Linux only"},
            "adoption": "auto",
            "state_effect": {"context_added": True, "mode_after": "normal"},
        }
        self._run_script("update_input_journal.py", classify)
        self.assertEqual("applied", self._state()["input_journal"][0]["status"])

        record2 = self._request_base("record_user_prompt")
        record2["request_id"] = "test-record-low"
        record2["record_user_prompt"] = {"text": "それ先に", "source": "UserPromptSubmit"}
        low_id = self._run_script("update_input_journal.py", record2)["state_summary"]["input_id"]
        classify2 = self._request_base("classify_input")
        classify2["request_id"] = "test-classify-low"
        classify2["classify_input"] = {
            "input_id": low_id,
            "classification": {"intent": "ambiguous", "confidence": 0.2, "summary": "unclear"},
            "adoption": "needs_confirmation",
            "state_effect": {"mode_after": "pending_user_intent"},
        }
        self._run_script("update_input_journal.py", classify2, expected_returncode=7)

        state = self._state()
        self.assertEqual("needs_confirmation", state["input_journal"][1]["status"])
        self.assertEqual("pending_user_intent", state["mode"])

    def test_propose_workflow_mutation_saves_pending_mode_and_proposed_mutation(self):
        request = self._request_base("propose_workflow_mutation")
        request["mutation"] = {
            "mutation_id": "mutation-1",
            "reason": "review requires design",
            "operations": [
                {
                    "op": "add_node",
                    "parent_node_path": "implementation_phase",
                    "node": {
                        "id": "design_revision_task",
                        "kind": "task",
                        "task_type": "design",
                        "required": True,
                        "step_set_refs": [
                            {"skill": "development-lifecycle", "version": 1, "set": "design-task"}
                        ],
                    },
                }
            ],
        }

        response = self._run_script("update_workflow.py", request, expected_returncode=7)

        self.assertFalse(response["ok"])
        state = self._state()
        self.assertEqual("pending_workflow_mutation", state["mode"])
        self.assertEqual("proposed", state["workflow_mutations"][0]["status"])
        self.assertEqual("missing", state["workflow_mutations"][0]["confirmation"])

    def test_apply_workflow_mutation_adds_node_dependency_and_restores_normal_mode(self):
        propose = self._request_base("propose_workflow_mutation")
        operations = [
            {
                "op": "add_node",
                "parent_node_path": "implementation_phase",
                "node": {
                    "id": "design_revision_task",
                    "kind": "task",
                    "task_type": "design",
                    "required": True,
                    "step_set_refs": [
                        {"skill": "development-lifecycle", "version": 1, "set": "design-task"}
                    ],
                },
            },
            {
                "op": "add_dependency",
                "target_node_path": "implementation_phase/hook_state_task#implementation-task/review",
                "depends_on": ["implementation_phase/design_revision_task"],
            },
        ]
        propose["mutation"] = {"mutation_id": "mutation-1", "reason": "review requires design", "operations": operations}
        self._run_script("update_workflow.py", propose, expected_returncode=7)

        apply = self._request_base("apply_workflow_mutation")
        apply.update(
            {
                "mutation_id": "mutation-1",
                "confirmation": "explicit_user_confirmed",
                "operations": operations,
            }
        )
        response = self._run_script("update_workflow.py", apply)

        self.assertTrue(response["ok"])
        self.assertEqual("normal", self._state()["mode"])
        self.assertEqual("active", self._state()["workflow_mutations"][0]["status"])
        workflow = self._workflow()
        children = workflow["nodes"][0]["children"]
        self.assertTrue(any(child["id"] == "design_revision_task" for child in children))
        self.assertEqual(
            ["implementation_phase/design_revision_task"],
            workflow["runtime_dependencies"]["implementation_phase/hook_state_task#implementation-task/review"],
        )

    def test_apply_workflow_mutation_rejects_request_operations_that_differ_from_proposal(self):
        proposed_operations = [
            {
                "op": "add_dependency",
                "target_node_path": "implementation_phase/hook_state_task#implementation-task/review",
                "depends_on": ["implementation_phase/hook_state_task#implementation-task/implement"],
            }
        ]
        propose = self._request_base("propose_workflow_mutation")
        propose["mutation"] = {"mutation_id": "mutation-1", "reason": "review dependency", "operations": proposed_operations}
        self._run_script("update_workflow.py", propose, expected_returncode=7)

        apply = self._request_base("apply_workflow_mutation")
        apply.update(
            {
                "mutation_id": "mutation-1",
                "confirmation": "explicit_user_confirmed",
                "operations": [
                    {
                        "op": "add_dependency",
                        "target_node_path": "implementation_phase/hook_state_task#implementation-task/review",
                        "depends_on": ["implementation_phase/hook_state_task#implementation-task/sync_design"],
                    }
                ],
            }
        )
        response = self._run_script("update_workflow.py", apply, expected_returncode=4)

        self.assertFalse(response["ok"])
        self.assertEqual("validation_failed", response["errors"][0]["code"])
        self.assertNotIn("runtime_dependencies", self._workflow())
        self.assertEqual("proposed", self._state()["workflow_mutations"][0]["status"])

    def test_apply_workflow_mutation_rejects_unproposed_mutation(self):
        apply = self._request_base("apply_workflow_mutation")
        apply.update({"mutation_id": "missing-mutation", "confirmation": "explicit_user_confirmed"})

        response = self._run_script("update_workflow.py", apply, expected_returncode=4)

        self.assertFalse(response["ok"])
        self.assertEqual("validation_failed", response["errors"][0]["code"])

    def test_apply_workflow_mutation_rejects_non_proposed_mutation(self):
        operations = [
            {
                "op": "add_dependency",
                "target_node_path": "implementation_phase/hook_state_task#implementation-task/review",
                "depends_on": ["implementation_phase/hook_state_task#implementation-task/implement"],
            }
        ]
        propose = self._request_base("propose_workflow_mutation")
        propose["mutation"] = {"mutation_id": "mutation-1", "reason": "review dependency", "operations": operations}
        self._run_script("update_workflow.py", propose, expected_returncode=7)
        state = self._state()
        state["workflow_mutations"][0]["status"] = "active"
        (self.state_root / "flow_state.json").write_text(json.dumps(state), encoding="utf-8")

        apply = self._request_base("apply_workflow_mutation")
        apply.update({"mutation_id": "mutation-1", "confirmation": "explicit_user_confirmed"})
        response = self._run_script("update_workflow.py", apply, expected_returncode=4)

        self.assertFalse(response["ok"])
        self.assertEqual("validation_failed", response["errors"][0]["code"])

    def test_update_progress_does_not_duplicate_completed_nodes(self):
        node_path = "implementation_phase/hook_state_task#implementation-task/sync_design"
        request = self._request_base("mark_completed_nodes")
        request["completed_nodes"] = [{"node_path": node_path, "evidence": {"tool_name": "Bash"}}]

        self._run_script("update_progress.py", request)
        self._run_script("update_progress.py", request)

        completed = self._progress()["completed_nodes"]
        self.assertEqual([node_path], [node["node_path"] for node in completed])

    def test_sync_flow_state_updates_derived_cache_from_canonical_node_path(self):
        request = self._request_base("sync_derived_state")

        response = self._run_script("sync_flow_state.py", request)

        self.assertTrue(response["ok"])
        state = self._state()
        self.assertEqual(
            "implementation_phase/hook_state_task#implementation-task/sync_design",
            state["current_task"]["current_node_path"],
        )
        self.assertEqual("implementation-task", state["current_task"]["current_step_set"])
        self.assertEqual("sync_design", state["current_task"]["current_step"])
        self.assertEqual(
            "implementation_phase/hook_state_task#implementation-task/implement",
            state["current_task"]["next_node_path"],
        )

    def test_validate_state_success_and_broken_refs_failure(self):
        request = self._request_base("validate")
        response = self._run_script("validate_state.py", request)
        self.assertTrue(response["ok"])

        workflow = self._workflow()
        workflow["nodes"][0]["children"][0]["step_set_refs"] = [
            {"skill": "missing-skill", "version": 1, "set": "implementation-task"}
        ]
        self.workflow_path.write_text(json.dumps(workflow), encoding="utf-8")

        response = self._run_script("validate_state.py", request, expected_returncode=4)
        self.assertFalse(response["ok"])
        self.assertTrue(response["errors"])

    def test_stop_guard_blocks_stale_derived_state_when_progress_is_complete(self):
        completed_nodes = [
            "implementation_phase/hook_state_task#implementation-task/sync_design",
            "implementation_phase/hook_state_task#implementation-task/implement",
            "implementation_phase/hook_state_task#implementation-task/review",
        ]
        progress = self._progress()
        progress["completed_nodes"] = [{"node_path": node_path} for node_path in completed_nodes]
        (self.state_root / "progress.json").write_text(json.dumps(progress), encoding="utf-8")
        state = self._state()
        state["current_task"].update(
            {
                "status": "active",
                "current_node_path": "implementation_phase/hook_state_task#implementation-task/sync_design",
                "next_node_path": "implementation_phase/hook_state_task#implementation-task/implement",
            }
        )
        state["workflow_cursor"] = {
            "current_node_path": "implementation_phase/hook_state_task#implementation-task/sync_design",
            "next_node_path": "implementation_phase/hook_state_task#implementation-task/implement",
        }
        (self.state_root / "flow_state.json").write_text(json.dumps(state), encoding="utf-8")

        response = self._run_hook("stop_guard.py")

        self.assertEqual("block", response["decision"])
        self.assertIn("derived", response["reason"])

    def test_stop_guard_stdout_uses_minimal_json_shape(self):
        response = self._run_hook("stop_guard.py")

        self.assertEqual({"decision", "reason"}, set(response))
        self.assertEqual("block", response["decision"])
        self.assertIsInstance(response["reason"], str)


if __name__ == "__main__":
    unittest.main()
