#!/usr/bin/env python3
"""Run existing repository validation and retain diagnostics on success or failure."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time
import traceback
import xml.etree.ElementTree as ET


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def source_identity(root: Path) -> dict:
    identity = {"head": None, "head_error": None, "files_sha256": {}}
    try:
        result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root,
                                capture_output=True, text=True, timeout=10, check=False)
        if result.returncode == 0:
            identity["head"] = result.stdout.strip()
        else:
            identity["head_error"] = "git rev-parse failed"
    except (OSError, subprocess.TimeoutExpired) as error:
        identity["head_error"] = type(error).__name__
    paths = [root / name for name in ("AGENTS.md", "README.md", ".gitignore", "package.json", "package-lock.json")]
    for name in ("skills", "scripts", "design", "tasks", "reports", ".github", "tools"):
        paths.extend((root / name).rglob("*"))
    for path in sorted(set(paths)):
        if path.is_file() and not path.is_symlink() and "__pycache__" not in path.parts:
            identity["files_sha256"][path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return identity


def run_step(name: str, command: list[str], root: Path, output: Path,
             timeout: int, skip_reason: str | None = None) -> dict:
    row = {"name": name, "command": command, "started_at": utc_now(),
           "status": "skipped" if skip_reason else "failed", "exit_code": None,
           "reason": skip_reason, "stdout": name + ".stdout.log", "stderr": name + ".stderr.log"}
    started = time.monotonic()
    with (output / row["stdout"]).open("wb") as stdout, (output / row["stderr"]).open("wb") as stderr:
        if skip_reason:
            stderr.write((skip_reason + "\n").encode("utf-8"))
        else:
            try:
                result = subprocess.run(command, cwd=root, stdout=stdout, stderr=stderr,
                                        env={**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"},
                                        timeout=timeout, check=False)
                row["exit_code"] = result.returncode
                row["status"] = "pass" if result.returncode == 0 else "failed"
            except subprocess.TimeoutExpired:
                row["reason"] = f"timeout after {timeout} seconds"
                stderr.write((row["reason"] + "\n").encode("utf-8"))
            except OSError as error:
                row["reason"] = f"{type(error).__name__}: {error}"
                stderr.write((row["reason"] + "\n").encode("utf-8"))
    row["duration_seconds"] = round(time.monotonic() - started, 6)
    row["finished_at"] = utc_now()
    print(f"{name}: {row['status']} (exit={row['exit_code']})", flush=True)
    return row


def classify_markdown_discovery(row: dict, output: Path) -> dict:
    row["unknown_term_count"] = 0
    if row["status"] == "pass" or row["exit_code"] != 1:
        return row
    try:
        lines = (output / row["stdout"]).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return row
    unknown_count = 0
    for line in lines:
        word, separator, count = line.rpartition("\t")
        if separator and word and count.isdigit():
            unknown_count += 1
    if unknown_count == 0:
        return row
    row["status"] = "needs_user_review"
    row["reason"] = (
        f"{unknown_count} unregistered terms found; exact whitelist, prh, and target-exclusion "
        "changes require user review"
    )
    row["unknown_term_count"] = unknown_count
    print(f"markdown-terminology: needs_user_review ({unknown_count} unknown terms)", flush=True)
    return row


def save_results(output: Path, summary: dict) -> None:
    write_json(output / "results.json", summary)
    steps = summary["steps"]
    suite = ET.Element("testsuite", name="repository-validation", tests=str(len(steps)),
                       failures=str(sum(r["status"] == "failed" for r in steps)),
                       skipped=str(sum(r["status"] in {"skipped", "needs_user_review"} for r in steps)))
    for row in steps:
        case = ET.SubElement(suite, "testcase", name=row["name"], time=str(row["duration_seconds"]))
        if row["status"] == "failed":
            ET.SubElement(case, "failure", message=row["reason"] or f"exit {row['exit_code']}").text = row["stderr"]
        elif row["status"] in {"skipped", "needs_user_review"}:
            fallback = "needs user review" if row["status"] == "needs_user_review" else "not run"
            ET.SubElement(case, "skipped", message=row["reason"] or fallback)
        ET.SubElement(case, "system-out").text = "See " + row["stdout"]
        ET.SubElement(case, "system-err").text = "See " + row["stderr"]
    ET.ElementTree(suite).write(output / "results.xml", encoding="utf-8", xml_declaration=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output-dir", type=Path, default=Path("validation-artifacts"))
    parser.add_argument("--timeout", type=int, default=300, help="Timeout per command, in seconds")
    args = parser.parse_args()
    if args.timeout < 1:
        parser.error("--timeout must be positive")
    root = args.repo_root.resolve()
    if not root.is_dir():
        parser.error("--repo-root must exist")
    output = args.output_dir.resolve()
    try:
        output.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        parser.error("--output-dir must be new; retain prior runs and choose a different path")
    summary = {"schema_version": 1, "started_at": utc_now(), "status": "failed", "steps": [],
               "python": platform.python_version(), "platform": platform.platform(),
               "ci": {key: os.environ.get(key) for key in
                      ("GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT", "GITHUB_EVENT_NAME", "TARGET_REF")}}
    try:
        write_json(output / "source.json", source_identity(root))
        archive = output / "chatgpt-worker-skills.zip"

        repository_row = run_step(
            "repository",
            [sys.executable, str(root / "scripts/verify_skill_repository.py")],
            root,
            output,
            args.timeout,
        )
        summary["steps"].append(repository_row)
        save_results(output, summary)

        whitelist_path = root / "tools" / "lint" / "markdown-whitelist.yaml"
        bootstrap_markdown_discovery = (
            whitelist_path.is_file()
            and whitelist_path.read_text(encoding="utf-8").strip() == "entries: []"
        )
        summary["markdown_terminology"] = {"bootstrap_discovery": bootstrap_markdown_discovery}

        npm_executable = shutil.which("npm.cmd" if os.name == "nt" else "npm")
        markdown_row = run_step(
            "markdown-terminology",
            [npm_executable, "run", "lint:md:unknown"] if npm_executable else [],
            root,
            output,
            args.timeout,
            None if npm_executable else "npm executable not found",
        )
        markdown_row = classify_markdown_discovery(markdown_row, output)
        summary["steps"].append(markdown_row)
        save_results(output, summary)

        commands = [
            ("bundle", [sys.executable, str(root / "scripts/build_chatgpt_worker_skills.py"),
                        "--repo-root", str(root), "--output", str(archive)]),
            ("zip-integrity", [sys.executable, "-c",
                               "import sys, zipfile; archive = zipfile.ZipFile(sys.argv[1]); bad = archive.testzip(); archive.close(); print('Invalid CRC: ' + bad if bad else 'ZIP integrity verified'); sys.exit(1 if bad else 0)", str(archive)]),
            ("zip-contents", [sys.executable, "-m", "zipfile", "-l", str(archive)]),
        ]
        bundle_ok = False
        for name, command in commands:
            skip = "bundle did not succeed; no archive evidence" if name.startswith("zip-") and not bundle_ok else None
            row = run_step(name, command, root, output, args.timeout, skip)
            summary["steps"].append(row)
            if name == "bundle":
                bundle_ok = row["status"] == "pass"
            save_results(output, summary)
        def pass_like(row: dict) -> bool:
            if row["status"] == "pass":
                return True
            return (
                bootstrap_markdown_discovery
                and row["name"] == "markdown-terminology"
                and row["status"] == "needs_user_review"
            )

        summary["status"] = "pass" if all(pass_like(row) for row in summary["steps"]) else "failed"
    except Exception:
        (output / "runner.stderr.log").write_text(traceback.format_exc(), encoding="utf-8")
        summary["steps"].append({"name": "runner", "command": [], "status": "failed",
                                 "exit_code": None, "reason": "runner exception; see runner.stderr.log",
                                 "duration_seconds": 0, "stdout": "runner.stdout.log", "stderr": "runner.stderr.log"})
        (output / "runner.stdout.log").touch()
    finally:
        summary["finished_at"] = utc_now()
        save_results(output, summary)
    print(f"Diagnostics: {output}")
    return 0 if summary["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
