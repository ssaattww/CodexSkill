#!/usr/bin/env python3
"""Shared helpers for flow-enforcement state scripts and hooks."""

from __future__ import annotations

import copy
import json
import os
import sys
import tempfile
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import fcntl
except ImportError:  # pragma: no cover - non-Unix fallback
    fcntl = None

try:
    import tomllib
except ImportError:  # pragma: no cover - Python < 3.11 fallback
    tomllib = None


EXIT_CODES = {
    "success": 0,
    "invalid_request_schema": 2,
    "root_contract_mismatch": 3,
    "validation_failed": 4,
    "lock_timeout": 5,
    "write_or_rollback_failed": 6,
    "user_confirmation_required": 7,
    "evidence_rejected": 8,
    "unsupported_operation": 9,
}


class FlowError(Exception):
    def __init__(self, code: str, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}
        self.exit_code = EXIT_CODES.get(code, 1)


@dataclass(frozen=True)
class Roots:
    state_root: Path
    workflow_root: Path
    step_root: Path
    started_project_root: Path | None = None
    codex_skill_root: Path | None = None

    def as_state_roots(self) -> dict[str, str]:
        roots = {
            "state_root": str(self.state_root),
            "workflow_root": str(self.workflow_root),
            "step_root": str(self.step_root),
        }
        if self.started_project_root:
            roots["started_project_root"] = str(self.started_project_root)
        if self.codex_skill_root:
            roots["codex_skill_root"] = str(self.codex_skill_root)
        return roots


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def read_json_stdin() -> dict[str, Any]:
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError as exc:
        raise FlowError("invalid_request_schema", f"invalid stdin JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise FlowError("invalid_request_schema", "request must be a JSON object")
    return data


def write_json_stdout(data: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(data, ensure_ascii=False, sort_keys=True))
    sys.stdout.write("\n")


def make_response(
    *,
    ok: bool,
    operation: str,
    request_id: str | None,
    updated_files: list[str] | None = None,
    warnings: list[Any] | None = None,
    errors: list[Any] | None = None,
    state_summary: dict[str, Any] | None = None,
    **extra: Any,
) -> dict[str, Any]:
    response = {
        "ok": ok,
        "operation": operation,
        "request_id": request_id,
        "updated_files": updated_files or [],
        "warnings": warnings or [],
        "errors": errors or [],
        "state_summary": state_summary or {},
    }
    response.update(extra)
    return response


def error_response(error: FlowError, operation: str | None, request_id: str | None) -> dict[str, Any]:
    return make_response(
        ok=False,
        operation=operation or "unknown",
        request_id=request_id,
        errors=[{"code": error.code, "message": error.message, **error.details}],
    )


def require_fields(request: dict[str, Any], fields: list[str]) -> None:
    missing = [field for field in fields if field not in request]
    if missing:
        raise FlowError("invalid_request_schema", "missing required request fields", {"missing": missing})


def _absolute_path(value: Any, field: str) -> Path:
    if not isinstance(value, str) or not value:
        raise FlowError("invalid_request_schema", f"{field} must be a non-empty string")
    path = Path(value).expanduser().resolve()
    if not path.is_absolute():
        raise FlowError("root_contract_mismatch", f"{field} must resolve to an absolute path")
    return path


def resolve_roots(request: dict[str, Any]) -> Roots:
    require_fields(request, ["state_root", "workflow_root", "step_root"])
    return Roots(
        state_root=_absolute_path(request["state_root"], "state_root"),
        workflow_root=_absolute_path(request["workflow_root"], "workflow_root"),
        step_root=_absolute_path(request["step_root"], "step_root"),
        started_project_root=_absolute_path(request["started_project_root"], "started_project_root")
        if request.get("started_project_root")
        else None,
        codex_skill_root=_absolute_path(request["codex_skill_root"], "codex_skill_root")
        if request.get("codex_skill_root")
        else None,
    )


def resolve_roots_from_env_or_config(cwd: str | None = None) -> Roots:
    started = os.environ.get("CODEX_STARTED_PROJECT_ROOT")
    started_root = Path(started).expanduser().resolve() if started else Path(cwd or os.getcwd()).resolve()
    config: dict[str, Any] = {}
    config_path = started_root / ".codex" / "config.toml"
    if config_path.exists() and tomllib is not None:
        with config_path.open("rb") as handle:
            config = tomllib.load(handle).get("flow_enforcement", {})

    def pick(env_name: str, config_name: str, default: Path | None = None) -> str:
        value = os.environ.get(env_name) or config.get(config_name)
        if value:
            return str(value)
        if default is not None:
            return str(default)
        raise FlowError("root_contract_mismatch", f"missing root: {env_name} or {config_name}")

    request = {
        "started_project_root": str(started_root),
        "state_root": pick("CODEX_FLOW_STATE_ROOT", "state_root", started_root / ".codex" / "state"),
        "workflow_root": pick("CODEX_REPO_WORKFLOW_ROOT", "workflow_root", started_root / ".codex" / "workflows"),
        "step_root": pick("CODEX_SKILL_STEP_ROOT", "step_root"),
    }
    skill_root = os.environ.get("CODEX_SKILL_ROOT") or config.get("codex_skill_root")
    if skill_root:
        request["codex_skill_root"] = str(skill_root)
    return resolve_roots(request)


def ensure_under(path: Path, root: Path, label: str) -> None:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise FlowError("root_contract_mismatch", f"{label} is outside configured root") from exc


def load_json(path: Path, default: Any | None = None) -> Any:
    if not path.exists():
        if default is not None:
            return copy.deepcopy(default)
        raise FlowError("validation_failed", f"missing JSON file: {path}")
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError as exc:
        raise FlowError("validation_failed", f"invalid JSON file: {path}: {exc}") from exc


def atomic_write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    except OSError as exc:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise FlowError("write_or_rollback_failed", f"failed to write {path}: {exc}") from exc


@contextmanager
def state_lock(state_root: Path, timeout: float = 10.0):
    state_root.mkdir(parents=True, exist_ok=True)
    lock_path = state_root / ".flow-state.lock"
    with lock_path.open("a+", encoding="utf-8") as handle:
        if fcntl is None:
            yield
            return
        deadline = time.monotonic() + timeout
        while True:
            try:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError as exc:
                if time.monotonic() >= deadline:
                    raise FlowError("lock_timeout", "timed out waiting for flow-state lock") from exc
                time.sleep(0.05)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def state_path(roots: Roots) -> Path:
    return roots.state_root / "flow_state.json"


def progress_path(roots: Roots) -> Path:
    return roots.state_root / "progress.json"


def load_flow_state(roots: Roots) -> dict[str, Any]:
    state = load_json(state_path(roots))
    if not isinstance(state, dict):
        raise FlowError("validation_failed", "flow_state.json must contain an object")
    return state


def load_progress(roots: Roots) -> dict[str, Any]:
    progress = load_json(
        progress_path(roots),
        {"schema_version": 1, "workflow": {}, "completed_nodes": []},
    )
    if not isinstance(progress, dict):
        raise FlowError("validation_failed", "progress.json must contain an object")
    progress.setdefault("completed_nodes", [])
    return progress


def save_flow_state(roots: Roots, state: dict[str, Any]) -> None:
    ensure_under(state_path(roots), roots.state_root, "flow_state.json")
    atomic_write_json(state_path(roots), state)


def save_progress(roots: Roots, progress: dict[str, Any]) -> None:
    ensure_under(progress_path(roots), roots.state_root, "progress.json")
    atomic_write_json(progress_path(roots), progress)


def validate_state_root_contract(roots: Roots, state: dict[str, Any]) -> None:
    state_roots = state.get("roots") or {}
    for key, expected in roots.as_state_roots().items():
        actual = state_roots.get(key)
        if actual and Path(actual).expanduser().resolve() != Path(expected).resolve():
            raise FlowError(
                "root_contract_mismatch",
                f"flow_state roots.{key} does not match resolved root",
                {"expected": str(expected), "actual": actual},
            )


def load_current_workflow(roots: Roots, state: dict[str, Any]) -> dict[str, Any]:
    current = state.get("current_workflow") or {}
    workflow_path_value = current.get("workflow_path")
    if not workflow_path_value:
        raise FlowError("validation_failed", "current_workflow.workflow_path is required")
    workflow_path = Path(workflow_path_value).expanduser()
    if not workflow_path.is_absolute():
        workflow_path = roots.workflow_root / workflow_path
    workflow_path = workflow_path.resolve()
    ensure_under(workflow_path, roots.workflow_root, "workflow_path")
    workflow = load_json(workflow_path)
    if not isinstance(workflow, dict):
        raise FlowError("validation_failed", "workflow must contain an object")
    workflow["_workflow_path"] = str(workflow_path)
    return normalize_workflow(workflow)


def normalize_workflow(workflow: dict[str, Any]) -> dict[str, Any]:
    normalized = copy.deepcopy(workflow)
    index: dict[str, dict[str, Any]] = {}

    def normalize_node(node: dict[str, Any], parent_path: str | None) -> None:
        if not isinstance(node, dict):
            raise FlowError("invalid_request_schema", "workflow node must be an object")
        node_id = node.get("id")
        if not isinstance(node_id, str) or not node_id:
            raise FlowError("invalid_request_schema", "workflow node id is required")
        if "step_set_ref" in node and "step_set_refs" in node:
            raise FlowError(
                "invalid_request_schema",
                "step_set_ref and step_set_refs cannot both be specified",
                {"node_id": node_id},
            )
        if "step_set_ref" in node:
            node["step_set_refs"] = [node.pop("step_set_ref")]
        refs = node.get("step_set_refs") or []
        if not isinstance(refs, list):
            raise FlowError("invalid_request_schema", "step_set_refs must be a list", {"node_id": node_id})
        seen_refs: set[tuple[str, str]] = set()
        for ref in refs:
            if not isinstance(ref, dict) or not ref.get("skill") or not ref.get("set"):
                raise FlowError("invalid_request_schema", "invalid step_set_ref", {"node_id": node_id})
            key = (str(ref.get("skill")), str(ref.get("set")))
            if key in seen_refs:
                raise FlowError("invalid_request_schema", "duplicate step_set_ref", {"node_id": node_id})
            seen_refs.add(key)
        path = f"{parent_path}/{node_id}" if parent_path else node_id
        if path in index:
            raise FlowError("invalid_request_schema", "duplicate workflow node_path", {"node_path": path})
        node["node_path"] = path
        node.setdefault("required", True)
        node.setdefault("children", [])
        if node.get("depends_on") is None:
            node["depends_on"] = []
        if not isinstance(node["depends_on"], list):
            node["depends_on"] = [node["depends_on"]]
        index[path] = node
        for child in node.get("children") or []:
            normalize_node(child, path)

    nodes = normalized.get("nodes") or []
    if not isinstance(nodes, list):
        raise FlowError("invalid_request_schema", "workflow.nodes must be a list")
    for root_node in nodes:
        normalize_node(root_node, None)
    normalized["_node_index"] = index
    return normalized


def iter_workflow_nodes(workflow: dict[str, Any]) -> list[dict[str, Any]]:
    nodes: list[dict[str, Any]] = []

    def visit(node: dict[str, Any]) -> None:
        nodes.append(node)
        for child in node.get("children") or []:
            visit(child)

    for root_node in workflow.get("nodes") or []:
        visit(root_node)
    return nodes


def load_step_set(roots: Roots, ref: dict[str, Any]) -> dict[str, Any]:
    skill = str(ref["skill"])
    set_id = str(ref["set"])
    path = (roots.step_root / skill / "steps.json").resolve()
    ensure_under(path, roots.step_root, "steps.json")
    data = load_json(path)
    for step_set in data.get("step_sets") or []:
        if step_set.get("id") == set_id:
            result = copy.deepcopy(step_set)
            result["_skill"] = skill
            result["_path"] = str(path)
            return result
    raise FlowError(
        "validation_failed",
        "referenced step set does not exist",
        {"skill": skill, "set": set_id, "path": str(path)},
    )


def compose_runtime_flow(workflow: dict[str, Any], roots: Roots) -> dict[str, Any]:
    runtime_nodes: list[dict[str, Any]] = []
    index: dict[str, dict[str, Any]] = {}

    runtime_dependencies = workflow.get("runtime_dependencies") or {}
    if not isinstance(runtime_dependencies, dict):
        raise FlowError("invalid_request_schema", "workflow.runtime_dependencies must be an object")

    def add_runtime(node: dict[str, Any]) -> None:
        if node["node_path"] in index:
            raise FlowError("invalid_request_schema", "duplicate runtime node", {"node_path": node["node_path"]})
        index[node["node_path"]] = node
        runtime_nodes.append(node)

    def visit(node: dict[str, Any]) -> None:
        refs = node.get("step_set_refs") or []
        repo_node = {
            "node_path": node["node_path"],
            "node_kind": node.get("kind", "node"),
            "required": bool(node.get("required", True)),
            "description": node.get("description", ""),
            "depends_on": list(node.get("depends_on") or []),
            "is_executable": not refs and not node.get("children"),
            "workflow_node": node,
        }
        add_runtime(repo_node)
        for ref in refs:
            step_set = load_step_set(roots, ref)
            for step in step_set.get("steps") or []:
                step_id = step.get("id")
                if not isinstance(step_id, str) or not step_id:
                    raise FlowError("invalid_request_schema", "step id is required", {"step_set": step_set.get("id")})
                node_path = f"{node['node_path']}#{step_set['id']}/{step_id}"
                step_depends = list(step.get("depends_on") or [])
                step_depends.extend(runtime_dependencies.get(node_path, []))
                add_runtime(
                    {
                        "node_path": node_path,
                        "node_kind": "step",
                        "required": bool(step.get("required", True)) and bool(node.get("required", True)),
                        "description": step.get("description", ""),
                        "depends_on": step_depends,
                        "is_executable": True,
                        "task_node_path": node["node_path"],
                        "task_id": node.get("id"),
                        "task_type": node.get("task_type"),
                        "step_set_id": step_set["id"],
                        "step_id": step_id,
                        "step": step,
                        "workflow_node": node,
                    }
                )
        for child in node.get("children") or []:
            visit(child)

    for root_node in workflow.get("nodes") or []:
        visit(root_node)
    return {"nodes": runtime_nodes, "index": index, "workflow": workflow}


def completed_node_paths(progress: dict[str, Any]) -> set[str]:
    return {
        node.get("node_path")
        for node in progress.get("completed_nodes") or []
        if isinstance(node, dict) and isinstance(node.get("node_path"), str)
    }


def confirmed_skipped_nodes(state: dict[str, Any], confirmed_overrides: list[dict[str, Any]] | None = None) -> set[str]:
    overrides = confirmed_overrides if confirmed_overrides is not None else state.get("flow_overrides") or []
    skipped: set[str] = set()
    for override in overrides:
        if (
            override.get("status") == "active"
            and override.get("confirmation") == "explicit_user_confirmed"
            and override.get("kind") == "skip_required_node"
        ):
            skipped.update(path for path in override.get("target_nodes") or [] if isinstance(path, str))
    return skipped


def node_is_effectively_completed(node_path: str, flow: dict[str, Any], completed: set[str], skipped: set[str]) -> bool:
    if node_path in completed or node_path in skipped:
        return True
    node = flow["index"].get(node_path)
    if not node:
        return False
    if node.get("is_executable"):
        return False
    prefix = f"{node_path}/"
    step_prefix = f"{node_path}#"
    descendants = [
        item
        for item in flow["nodes"]
        if item.get("required")
        and item.get("is_executable")
        and (item["node_path"].startswith(prefix) or item["node_path"].startswith(step_prefix))
    ]
    return bool(descendants) and all(item["node_path"] in completed or item["node_path"] in skipped for item in descendants)


def _dependency_satisfied(dep: str, flow: dict[str, Any], completed: set[str], skipped: set[str]) -> bool:
    return node_is_effectively_completed(dep, flow, completed, skipped)


def required_executable_nodes(flow: dict[str, Any]) -> list[dict[str, Any]]:
    return [node for node in flow["nodes"] if node.get("required") and node.get("is_executable")]


def find_current_and_next(
    state: dict[str, Any],
    progress: dict[str, Any],
    flow: dict[str, Any],
    confirmed_overrides: list[dict[str, Any]] | None = None,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    completed = completed_node_paths(progress)
    skipped = confirmed_skipped_nodes(state, confirmed_overrides)
    remaining_ready: list[dict[str, Any]] = []
    remaining_blocked: list[dict[str, Any]] = []
    for node in required_executable_nodes(flow):
        node_path = node["node_path"]
        if node_path in completed or node_path in skipped:
            continue
        if all(_dependency_satisfied(dep, flow, completed, skipped) for dep in node.get("depends_on") or []):
            remaining_ready.append(node)
        else:
            remaining_blocked.append(node)
    remaining = remaining_ready or remaining_blocked
    current = remaining[0] if remaining else None
    next_node = remaining[1] if len(remaining) > 1 else None
    return current, next_node


def path_stack_for(node_path: str) -> list[str]:
    if "#" in node_path:
        repo_path = node_path.split("#", 1)[0]
        parts = repo_path.split("/")
        stack = ["/".join(parts[: i + 1]) for i in range(len(parts))]
        stack.append(node_path)
        return stack
    parts = node_path.split("/")
    return ["/".join(parts[: i + 1]) for i in range(len(parts))]


def sync_derived_state(
    state: dict[str, Any],
    progress: dict[str, Any],
    workflow: dict[str, Any],
    roots: Roots,
    confirmed_overrides: list[dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    flow = compose_runtime_flow(workflow, roots)
    current, next_node = find_current_and_next(state, progress, flow, confirmed_overrides)
    new_state = copy.deepcopy(state)
    current_task = new_state.setdefault("current_task", {})
    cursor = new_state.setdefault("workflow_cursor", {})

    if current is None:
        current_task["status"] = "completed"
        current_task["current_step_set"] = None
        current_task["current_step"] = None
        current_task["next_step_set"] = None
        current_task["next_step"] = None
        current_task["current_node_path"] = None
        current_task["next_node_path"] = None
        cursor["current_node_path"] = None
        cursor["next_node_path"] = None
        cursor["active_path_stack"] = []
        if new_state.get("mode") == "normal":
            new_state["mode"] = "completed"
    else:
        workflow_node = current.get("workflow_node") or {}
        current_task.update(
            {
                "workflow_id": workflow.get("workflow_id"),
                "task_id": current.get("task_id") or workflow_node.get("id"),
                "task_node_path": current.get("task_node_path") or current["node_path"],
                "task_type": current.get("task_type") or workflow_node.get("task_type"),
                "status": "active",
                "current_step_set": current.get("step_set_id"),
                "current_step": current.get("step_id"),
                "next_step_set": next_node.get("step_set_id") if next_node else None,
                "next_step": next_node.get("step_id") if next_node else None,
                "current_node_path": current["node_path"],
                "next_node_path": next_node["node_path"] if next_node else None,
                "step_set_refs": workflow_node.get("step_set_refs", []),
            }
        )
        cursor["current_node_path"] = current["node_path"]
        cursor["next_node_path"] = next_node["node_path"] if next_node else None
        cursor["active_path_stack"] = path_stack_for(current["node_path"])
        if new_state.get("mode") == "completed":
            new_state["mode"] = "normal"
    summary = {
        "mode": new_state.get("mode"),
        "current_node_path": current["node_path"] if current else None,
        "next_node_path": next_node["node_path"] if next_node else None,
    }
    return new_state, summary


def has_unresolved_workflow_mutations(state: dict[str, Any]) -> bool:
    return any(mutation.get("status") in {"proposed", "failed"} for mutation in state.get("workflow_mutations") or [])


def new_input_id(request_id: str | None = None) -> str:
    return request_id if request_id else f"{utc_now()}-userprompt-{uuid.uuid4().hex[:8]}"


def evidence_requires_agent_action(evidence: Any) -> tuple[bool, list[str]]:
    codes: list[str] = []

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if key in {"workflow_mutation_required", "design_required"} and item:
                    codes.append(key)
                if isinstance(item, str) and item in {"workflow_mutation_required", "design_required"}:
                    codes.append(item)
                else:
                    visit(item)
        elif isinstance(value, list):
            for item in value:
                visit(item)
        elif isinstance(value, str) and value in {"workflow_mutation_required", "design_required"}:
            codes.append(value)

    visit(evidence)
    return bool(codes), sorted(set(codes))


def main_wrapper(handler) -> None:
    operation = None
    request_id = None
    try:
        request = read_json_stdin()
        operation = request.get("operation")
        request_id = request.get("request_id")
        response, exit_code = handler(request)
    except FlowError as exc:
        response = error_response(exc, operation, request_id)
        exit_code = exc.exit_code
    write_json_stdout(response)
    raise SystemExit(exit_code)
