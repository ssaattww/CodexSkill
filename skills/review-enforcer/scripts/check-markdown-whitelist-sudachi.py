#!/usr/bin/env python3
"""Check Markdown vocabulary against tools/lint/markdown-whitelist.yaml."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


TARGET_CONFIG = Path("tools/lint/markdown-targets.json")
WHITELIST_PATH = Path("tools/lint/markdown-whitelist.yaml")
TARGET_SUFFIXES = (".md", ".txt")
DEPENDENCY_HINT = (
    "Missing dependency: {module}. Run `pip install -r tools/lint/requirements.txt` "
    "from the target repository root."
)

ENGLISH_RE = re.compile(r"(?<![A-Za-z0-9])[A-Za-z][A-Za-z0-9]*(?:[._-][A-Za-z0-9]+)*")
FENCE_RE = re.compile(r"^[ \t]*(```|~~~)[^\n]*(?:\n[\s\S]*?)?^[ \t]*\1[^\n]*(?=\n|$)", re.MULTILINE)
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
FOOTNOTE_DEF_RE = re.compile(r"^\[\^[^\]]+\]:.*$", re.MULTILINE)
URL_RE = re.compile(r"https?://[^\s)]+")
MAILTO_RE = re.compile(r"mailto:[^\s)]+")
HTML_COMMENT_RE = re.compile(r"<!--[\s\S]*?-->")
REFERENCE_LINK_RE = re.compile(r"^\[[^\]\n]+\]:\s+\S+.*$", re.MULTILINE)
INLINE_LINK_RE = re.compile(r"!?\[[^\]\n]+\]\([^)]+\)")
KATAKANA_RE = re.compile(r"[\u30A0-\u30FF]")
CJK_RE = re.compile(r"[\u3400-\u9FFF]")


@dataclass
class Whitelist:
    entries: list[dict]
    terms: set[str]
    value_pattern: re.Pattern[str] | None


@dataclass
class Violation:
    source: str
    line: int
    token: str
    normalized: str
    kind: str


@dataclass
class UnknownWord:
    word: str
    normalized: str
    kind: str
    count: int = 0
    sources: Counter[str] = field(default_factory=Counter)


def main() -> int:
    args = parse_args()
    yaml_module = import_yaml()
    tokenizer_obj, split_mode = create_sudachi_tokenizer()
    root = Path.cwd()
    target_config = read_target_config(root)
    stdin_text = sys.stdin.read() if args.stdin else None
    whitelist = read_whitelist(root, yaml_module, args.stdin, stdin_text)

    inputs = read_inputs(root, target_config, whitelist, args.stdin, stdin_text, args.files, args.changed)
    violations: list[Violation] = []
    unknown_words: dict[tuple[str, str], UnknownWord] = {}

    for relative_path, text in inputs:
        cleaned = mask_whitelist_values(strip_markdown_noise(text), whitelist.value_pattern)
        check_english_tokens(relative_path, cleaned, whitelist, violations, unknown_words)
        check_japanese_tokens(relative_path, cleaned, tokenizer_obj, split_mode, whitelist, violations, unknown_words)

    if args.list_unknown:
        print_unknown_words(unknown_words)

    if violations:
        print("Markdown whitelist violations:", file=sys.stderr)
        for violation in violations[:200]:
            print(
                f"- {violation.source}:{violation.line}: '{violation.token}' "
                f"({violation.kind}) is not in tools/lint/markdown-whitelist.yaml.",
                file=sys.stderr,
            )
        if len(violations) > 200:
            print(f"- ... {len(violations) - 200} more violations", file=sys.stderr)
        return 1

    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check Markdown vocabulary with SudachiPy.")
    parser.add_argument("--files", nargs="+", help="Specific .md/.txt files to inspect.")
    parser.add_argument("--changed", action="store_true", help="Inspect changed .md/.txt files only.")
    parser.add_argument("--stdin", metavar="PATH", help="Read one file body from stdin and use PATH for diagnostics.")
    parser.add_argument("--list-unknown", action="store_true", help="Print unknown normalized tokens.")
    return parser.parse_args()


def import_yaml():
    try:
        import yaml
    except ImportError as exc:
        print(DEPENDENCY_HINT.format(module=exc.name or "PyYAML"), file=sys.stderr)
        raise SystemExit(2) from exc
    return yaml


def create_sudachi_tokenizer():
    try:
        from sudachipy import dictionary
        from sudachipy import tokenizer as sudachi_tokenizer
    except ImportError as exc:
        print(DEPENDENCY_HINT.format(module=exc.name or "SudachiPy"), file=sys.stderr)
        raise SystemExit(2) from exc

    try:
        return dictionary.Dictionary().create(), sudachi_tokenizer.Tokenizer.SplitMode.C
    except Exception as exc:
        print(DEPENDENCY_HINT.format(module="SudachiPy dictionary"), file=sys.stderr)
        print(f"SudachiPy initialization failed: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc


def read_target_config(root: Path) -> dict[str, list[str]]:
    config_path = root / TARGET_CONFIG
    if not config_path.exists():
        print(f"{config_path}: missing. Run this script from the target repository root.", file=sys.stderr)
        raise SystemExit(2)

    data = json.loads(config_path.read_text(encoding="utf-8"))
    return {
        "ignoreDirectories": list(data.get("ignoreDirectories") or []),
        "ignoredPrefixes": [normalize_prefix(prefix) for prefix in data.get("ignoredPrefixes") or []],
    }


def read_whitelist(root: Path, yaml_module, stdin_path: str | None, stdin_text: str | None) -> Whitelist:
    if stdin_path and is_whitelist_path(stdin_path):
        data = yaml_module.safe_load(stdin_text or "") or {}
        path_label = stdin_path
    else:
        whitelist_path = root / WHITELIST_PATH
        if not whitelist_path.exists():
            print(f"{whitelist_path}: missing. Run this script from the target repository root.", file=sys.stderr)
            raise SystemExit(2)
        data = yaml_module.safe_load(whitelist_path.read_text(encoding="utf-8")) or {}
        path_label = str(WHITELIST_PATH)

    entries = data.get("entries") if isinstance(data, dict) else None
    if not isinstance(entries, list):
        raise ValueError(f"{path_label}: entries must be a list.")

    terms: set[str] = set()
    values: list[str] = []
    for index, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            raise ValueError(f"{path_label}: entry #{index} must be a mapping.")
        term = entry.get("term")
        description = entry.get("description")
        if not isinstance(term, str) or not term.strip():
            raise ValueError(f"{path_label}: entry #{index} must include term.")
        if not isinstance(description, str) or not description.strip():
            raise ValueError(f"{path_label}: entry '{term}' must include description.")

        aliases = normalize_aliases(entry.get("aliases"))
        for value in [term, *aliases]:
            values.append(value)
            terms.add(normalize_term(value))

    return Whitelist(entries=entries, terms=terms, value_pattern=build_whitelist_value_pattern(values))


def normalize_aliases(aliases) -> list[str]:
    if aliases is None:
        return []
    if isinstance(aliases, str):
        return [aliases]
    if isinstance(aliases, list) and all(isinstance(item, str) for item in aliases):
        return aliases
    raise ValueError("aliases must be a string or a list of strings.")


def read_inputs(
    root: Path,
    target_config: dict[str, list[str]],
    whitelist: Whitelist,
    stdin_path: str | None,
    stdin_text: str | None,
    explicit_files: list[str] | None,
    changed: bool,
) -> list[tuple[str, str]]:
    if stdin_path:
        normalized_stdin_path = normalize_path(Path(stdin_path))
        if is_whitelist_path(stdin_path):
            return read_whitelist_value_inputs(normalized_stdin_path, whitelist.entries)
        return [(normalized_stdin_path, stdin_text or "")]

    files = select_target_files(root, target_config, explicit_files, changed)
    inputs = [
        (normalize_path(file_path.relative_to(root)), file_path.read_text(encoding="utf-8"))
        for file_path in files
    ]
    inputs.extend(read_whitelist_description_inputs(whitelist.entries))
    return inputs


def read_whitelist_description_inputs(entries: list[dict]) -> list[tuple[str, str]]:
    return [
        (f"{WHITELIST_PATH}:{entry['term']} [whitelist description]", entry["description"])
        for entry in entries
    ]


def read_whitelist_value_inputs(relative_path: str, entries: list[dict]) -> list[tuple[str, str]]:
    inputs: list[tuple[str, str]] = []
    for entry in entries:
        for value in [entry["term"], *normalize_aliases(entry.get("aliases"))]:
            inputs.append((f"{relative_path}:{entry['term']} [whitelist value]", value))
        inputs.append((f"{relative_path}:{entry['term']} [whitelist description]", entry["description"]))
    return inputs


def select_target_files(
    root: Path,
    target_config: dict[str, list[str]],
    explicit_files: list[str] | None,
    changed: bool,
) -> list[Path]:
    if explicit_files is not None:
        candidates = [resolve_candidate(root, file_name) for file_name in explicit_files]
    elif changed:
        candidates = [root / file_name for file_name in list_changed_files(root)]
    else:
        candidates = list_all_target_files(root, target_config)

    root_resolved = root.resolve()
    return sorted(
        {
            path.resolve()
            for path in candidates
            if path is not None and path.exists() and path.is_file() and is_target_file(path)
            and not is_ignored(normalize_path(path.resolve().relative_to(root_resolved)), target_config)
        },
        key=lambda item: normalize_path(item.relative_to(root_resolved)),
    )


def resolve_candidate(root: Path, file_name: str) -> Path | None:
    path = Path(file_name)
    if path.is_absolute():
        try:
            path.resolve().relative_to(root.resolve())
        except ValueError:
            return None
        return path
    return root / path


def list_changed_files(root: Path) -> set[str]:
    candidates: set[str] = set()
    git_commands = [
        ["diff", "--name-only", "--diff-filter=ACMR"],
        ["diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        ["ls-files", "--others", "--exclude-standard"],
    ]
    for args in git_commands:
        result = subprocess.run(["git", *args], cwd=root, text=True, stdout=subprocess.PIPE, check=False)
        if result.returncode != 0:
            continue
        for line in result.stdout.splitlines():
            file_name = line.strip()
            if file_name:
                candidates.add(file_name)
    return candidates


def list_all_target_files(root: Path, target_config: dict[str, list[str]]) -> list[Path]:
    files: list[Path] = []
    ignore_directories = set(target_config["ignoreDirectories"])
    ignored_prefixes = target_config["ignoredPrefixes"]

    for current_root, directory_names, file_names in os.walk(root):
        current = Path(current_root)
        relative_current = normalize_path(current.relative_to(root)) if current != root else ""
        directory_names[:] = [
            directory_name
            for directory_name in directory_names
            if directory_name not in ignore_directories
            and not prefix_ignored(join_path(relative_current, directory_name) + "/", ignored_prefixes)
        ]
        for file_name in file_names:
            path = current / file_name
            relative_path = normalize_path(path.relative_to(root))
            if is_target_file(path) and not is_ignored(relative_path, target_config):
                files.append(path)
    return files


def is_target_file(path: Path) -> bool:
    return path.suffix.lower() in TARGET_SUFFIXES


def is_ignored(relative_path: str, target_config: dict[str, list[str]]) -> bool:
    segments = relative_path.split("/")
    return (
        any(segment in set(target_config["ignoreDirectories"]) for segment in segments)
        or prefix_ignored(relative_path, target_config["ignoredPrefixes"])
    )


def prefix_ignored(relative_path: str, ignored_prefixes: Iterable[str]) -> bool:
    return any(relative_path.startswith(prefix) for prefix in ignored_prefixes)


def normalize_prefix(prefix: str) -> str:
    return normalize_path(prefix)


def normalize_path(path: str | Path) -> str:
    return str(path).replace(os.sep, "/")


def is_whitelist_path(path: str | Path) -> bool:
    path_object = Path(path)
    if path_object.is_absolute():
        try:
            path_object = path_object.resolve().relative_to(Path.cwd().resolve())
        except ValueError:
            return False
    normalized = normalize_path(path_object)
    if normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized == normalize_path(WHITELIST_PATH)


def join_path(left: str, right: str) -> str:
    return f"{left}/{right}" if left else right


def strip_markdown_noise(text: str) -> str:
    cleaned = FENCE_RE.sub(blank_preserving, text)
    cleaned = INLINE_CODE_RE.sub(blank_preserving, cleaned)
    cleaned = FOOTNOTE_DEF_RE.sub(blank_preserving, cleaned)
    cleaned = URL_RE.sub(blank_preserving, cleaned)
    cleaned = MAILTO_RE.sub(blank_preserving, cleaned)
    cleaned = HTML_COMMENT_RE.sub(blank_preserving, cleaned)
    cleaned = REFERENCE_LINK_RE.sub(strip_reference_link_address, cleaned)
    cleaned = INLINE_LINK_RE.sub(strip_inline_link_address, cleaned)
    return cleaned


def blank_preserving(value: str | re.Match[str]) -> str:
    text = value.group(0) if isinstance(value, re.Match) else value
    return re.sub(r"[^\n]", " ", text)


def strip_reference_link_address(match: re.Match[str]) -> str:
    value = match.group(0)
    return re.sub(r":\s+\S+.*$", lambda address: ":" + blank_preserving(address.group(0)[1:]), value)


def strip_inline_link_address(match: re.Match[str]) -> str:
    value = match.group(0)
    return re.sub(r"\([^)]+\)", blank_preserving, value)


def mask_whitelist_values(text: str, value_pattern: re.Pattern[str] | None) -> str:
    if value_pattern is None:
        return text

    def replace(match: re.Match[str]) -> str:
        return f"{match.group(1)}{blank_preserving(match.group(2))}"

    return value_pattern.sub(replace, text)


def build_whitelist_value_pattern(values: list[str]) -> re.Pattern[str] | None:
    alternatives = [
        re.escape(value).replace(r"\ ", r"\s+")
        for value in sorted(set(values), key=len, reverse=True)
        if len(value) > 1
    ]
    if not alternatives:
        return None
    boundary = r"A-Za-z0-9\u3040-\u30FF\u3400-\u9FFF"
    return re.compile(rf"(^|[^{boundary}])({'|'.join(alternatives)})(?=$|[^{boundary}])", re.IGNORECASE)


def check_english_tokens(
    source: str,
    text: str,
    whitelist: Whitelist,
    violations: list[Violation],
    unknown_words: dict[tuple[str, str], UnknownWord],
) -> None:
    for match in ENGLISH_RE.finditer(text):
        token = match.group(0)
        if len(token) <= 1 or any(character.isdigit() for character in token):
            continue
        normalized = normalize_term(token)
        if normalized not in whitelist.terms:
            line = line_number_at(text, match.start())
            record_violation(source, line, token, normalized, "english", violations, unknown_words)


def check_japanese_tokens(
    source: str,
    text: str,
    tokenizer_obj,
    split_mode,
    whitelist: Whitelist,
    violations: list[Violation],
    unknown_words: dict[tuple[str, str], UnknownWord],
) -> None:
    cursor = 0
    for morpheme in tokenizer_obj.tokenize(text, split_mode):
        token = morpheme.surface()
        index = text.find(token, cursor)
        if index == -1:
            index = cursor
        cursor = index + len(token)

        if not should_check_japanese(token, morpheme):
            continue

        normalized = normalize_term(sudachi_value(morpheme, "normalized_form") or token)
        reading = normalize_term(sudachi_value(morpheme, "reading_form"))
        surface_normalized = normalize_term(token)
        if {normalized, reading, surface_normalized} & whitelist.terms:
            continue

        kind = "japanese" if CJK_RE.search(token) else "katakana"
        line = line_number_at(text, index)
        record_violation(source, line, token, normalized, kind, violations, unknown_words)


def should_check_japanese(surface: str, morpheme) -> bool:
    if not (KATAKANA_RE.search(surface) or CJK_RE.search(surface)):
        return False
    normalized = normalize_term(surface).replace("・", "").replace("ー", "").replace(".", "").replace("_", "").replace("-", "")
    if len(normalized) <= 1:
        return False
    part_of_speech = morpheme.part_of_speech()
    return bool(part_of_speech) and part_of_speech[0] == "名詞"


def sudachi_value(morpheme, name: str) -> str:
    value = getattr(morpheme, name, None)
    if value is None:
        return ""
    result = value()
    return "" if result == "*" else str(result)


def normalize_term(value: str) -> str:
    return unicodedata.normalize("NFKC", value).casefold()


def record_violation(
    source: str,
    line: int,
    token: str,
    normalized: str,
    kind: str,
    violations: list[Violation],
    unknown_words: dict[tuple[str, str], UnknownWord],
) -> None:
    violations.append(Violation(source, line, token, normalized, kind))
    key = (kind, normalized)
    current = unknown_words.get(key)
    if current is None:
        current = UnknownWord(token, normalized, kind)
        unknown_words[key] = current
    current.count += 1
    current.sources[source] += 1


def print_unknown_words(unknown_words: dict[tuple[str, str], UnknownWord]) -> None:
    for item in sorted(unknown_words.values(), key=lambda value: (value.kind, value.normalized)):
        sources = ",".join(f"{source}:{count}" for source, count in sorted(item.sources.items()))
        print(f"{item.kind}\t{item.word}\t{item.normalized}\t{item.count}\t{sources}")


def line_number_at(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


if __name__ == "__main__":
    raise SystemExit(main())
