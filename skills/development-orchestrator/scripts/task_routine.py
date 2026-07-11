#!/usr/bin/env python3
"""Persistent one-task routine CLI and Codex hook entrypoint."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Sequence

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from task_routine_state import *
from task_routine_hooks import *

def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    subs = result.add_subparsers(dest="command", required=True)
    def common(item: argparse.ArgumentParser) -> None:
        item.add_argument("--repo-root")
    start_p = subs.add_parser("start"); start_p.add_argument("--id", required=True); start_p.add_argument("--summary", required=True); common(start_p)
    status_p = subs.add_parser("status"); status_p.add_argument("--json", action="store_true"); common(status_p)
    for command in ("complete", "skip"):
        item = subs.add_parser(command); item.add_argument("step", choices=STEPS); item.add_argument("--evidence" if command == "complete" else "--reason", required=True); common(item)
    reflect_p = subs.add_parser("reflect"); reflect_p.add_argument("kind", choices=("skill", "tool")); reflect_p.add_argument("--decision", required=True); reflect_p.add_argument("--target"); reflect_p.add_argument("--evidence", required=True); common(reflect_p)
    feedback_p = subs.add_parser("feedback"); feedback_p.add_argument("--decision", choices=sorted(FEEDBACK_DECISIONS), required=True); feedback_p.add_argument("--target"); feedback_p.add_argument("--evidence", required=True); common(feedback_p)
    for command in ("pause", "abort"):
        item = subs.add_parser(command); item.add_argument("--reason", required=True); common(item)
    resume_p = subs.add_parser("resume"); common(resume_p)
    reopen_p = subs.add_parser("reopen"); reopen_p.add_argument("step", choices=STEPS); reopen_p.add_argument("--reason", required=True); common(reopen_p)
    subs.add_parser("hook")
    for command in ("install-hooks", "uninstall-hooks"):
        item = subs.add_parser(command); item.add_argument("--scope", choices=("project", "user"), default="project"); item.add_argument("--target", type=Path); item.add_argument("--script-path", type=Path); common(item)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "hook":
            payload = json.load(sys.stdin)
            output = handle_hook(payload)
            if output is not None:
                print(json.dumps(output, ensure_ascii=False))
            return 0
        if args.command in {"install-hooks", "uninstall-hooks"}:
            candidate = Path(args.repo_root or os.getcwd())
            root = repo_root(candidate)
            path, changed = install(args.scope, root, args.target, args.script_path, args.command == "uninstall-hooks")
            print(f"hooks: {path} ({'changed' if changed else 'unchanged'})")
            return 0
        root = require_root(args.repo_root)
        if args.command == "start":
            state = start(root, args.id.strip(), args.summary.strip())
        elif args.command == "status":
            state = load(root)
            print(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) if args.json else render(state, root))
            return 0
        else:
            state = require_state(root)
            if args.command == "complete":
                state = mark(root, state, args.step, "done", args.evidence)
            elif args.command == "skip":
                state = mark(root, state, args.step, "not_applicable", args.reason)
            elif args.command == "reflect":
                state = reflection(root, state, args.kind, args.decision, args.target, args.evidence)
            elif args.command == "feedback":
                state = feedback(root, state, args.decision, args.target, args.evidence)
            elif args.command == "pause":
                state = pause(root, state, args.reason)
            elif args.command == "abort":
                state = pause(root, state, args.reason, abort=True)
            elif args.command == "resume":
                state = resume(root, state)
            elif args.command == "reopen":
                state = reopen_step(root, state, args.step, args.reason)
            else:
                raise RoutineError(f"未対応commandです: {args.command}")
        print(render(state, root))
        return 0
    except (RoutineError, json.JSONDecodeError) as exc:
        print(f"task-routine error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
