#!/usr/bin/env node
/** Read-only planner for the Issue #87 consumer bootstrap. */

import { createHash } from 'node:crypto';
import { lstatSync, readFileSync, realpathSync } from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const REPOSITORY_ROOT = path.resolve(SCRIPT_DIR, '../../..');
const TEMPLATE_ROOT = path.join(REPOSITORY_ROOT, 'skills', 'markdown-word-checker', 'templates', 'repo');

const FILES = [
  ['tools/lint/.gitignore', 'tools/lint/.gitignore'],
  ['tools/lint/README.md', 'tools/lint/README.md'],
  ['tools/lint/requirements.txt', 'tools/lint/requirements.txt'],
  ['tools/lint/markdown-targets.json', 'tools/lint/markdown-targets.json'],
  ['tools/lint/markdown-whitelist.yaml', 'tools/lint/markdown-whitelist.yaml'],
  ['tools/lint/scripts/run_markdown_word_check.py', 'tools/lint/scripts/run_markdown_word_check.py'],
  ['skills/review-enforcer/scripts/check-markdown-whitelist-sudachi.py', 'tools/lint/scripts/check-markdown-whitelist-sudachi.py'],
];
const CI_FILE = ['.github/workflows/markdown-word-check.yml', '.github/workflows/markdown-word-check.yml'];

function fail(message, code = 2) {
  process.stderr.write(`${message}\n`);
  process.exit(code);
}

function parseArgs(argv) {
  const parsed = { target: null, withCi: false, expectedHead: null };
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === '--target' && parsed.target === null && argv[index + 1]) {
      parsed.target = argv[++index];
    } else if (arg === '--with-ci' && !parsed.withCi) {
      parsed.withCi = true;
    } else if (arg === '--expected-head' && parsed.expectedHead === null && argv[index + 1]) {
      parsed.expectedHead = argv[++index];
    } else if (arg === '--help' && argv.length === 1) {
      process.stdout.write('Usage: node plan_markdown_word_check_bootstrap.mjs --target <git-worktree-root> [--with-ci] [--expected-head <40-hex-sha>]\n');
      process.exit(0);
    } else {
      fail(`Invalid or duplicate argument: ${arg}`);
    }
  }
  if (!parsed.target) fail('--target is required.');
  if (parsed.expectedHead && !/^[0-9a-f]{40}$/i.test(parsed.expectedHead)) {
    fail('--expected-head must be a full 40-character commit SHA.');
  }
  return parsed;
}

function runGit(args) {
  const result = spawnSync('git', args, { encoding: 'utf8', windowsHide: true });
  if (result.error || result.status !== 0) {
    const detail = result.error?.message || result.stderr.trim() || `exit ${result.status}`;
    fail(`Git inspection failed (${args.join(' ')}): ${detail}`, 4);
  }
  return result.stdout.trim();
}

function targetIdentity(targetInput) {
  let target;
  try {
    target = realpathSync(targetInput);
  } catch (error) {
    fail(`Target cannot be resolved: ${error.message}`);
  }
  const root = path.resolve(runGit(['-C', target, 'rev-parse', '--show-toplevel']));
  if (path.relative(root, target) !== '') fail(`--target must be the Git worktree root; resolved root is ${root}.`);
  const head = runGit(['-C', root, 'rev-parse', 'HEAD']);
  if (!/^[0-9a-f]{40}$/i.test(head)) fail('Git returned an invalid HEAD identity.', 4);
  return { root, head };
}

function inspectPath(root, relative) {
  const destination = path.resolve(root, relative);
  const rel = path.relative(root, destination);
  if (!rel || rel === '..' || rel.startsWith(`..${path.sep}`) || path.isAbsolute(rel)) {
    return { path: relative, state: 'unsafe-path' };
  }
  const parts = rel.split(path.sep);
  let current = root;
  for (let index = 0; index < parts.length; index += 1) {
    current = path.join(current, parts[index]);
    try {
      const info = lstatSync(current);
      if (info.isSymbolicLink()) return { path: relative, state: 'link-or-reparse-point', at: path.relative(root, current) };
      if (index < parts.length - 1 && !info.isDirectory()) {
        return { path: relative, state: 'non-directory-parent', at: path.relative(root, current) };
      }
      if (index === parts.length - 1) return { path: relative, state: 'exists' };
    } catch (error) {
      if (error.code === 'ENOENT' || error.code === 'ENOTDIR') return { path: relative, state: 'absent' };
      return { path: relative, state: 'inspection-failed', reason: error.message };
    }
  }
  return { path: relative, state: 'absent' };
}

function sourceHash(sourceRelative) {
  const source = path.resolve(REPOSITORY_ROOT, sourceRelative.startsWith('skills/') ? sourceRelative : path.join('skills/markdown-word-checker/templates/repo', sourceRelative));
  const rel = path.relative(REPOSITORY_ROOT, source);
  if (rel === '..' || rel.startsWith(`..${path.sep}`) || path.isAbsolute(rel)) fail(`Source escaped repository: ${sourceRelative}`);
  let info;
  try {
    info = lstatSync(source);
  } catch (error) {
    fail(`Required source is missing: ${sourceRelative} (${error.message})`, 5);
  }
  if (!info.isFile() || info.isSymbolicLink()) fail(`Required source is not a regular file: ${sourceRelative}`, 5);
  const digest = createHash('sha256').update(readFileSync(source)).digest('hex');
  return { source: rel.split(path.sep).join('/'), sha256: digest };
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const { root, head } = targetIdentity(args.target);
  if (args.expectedHead && args.expectedHead.toLowerCase() !== head.toLowerCase()) {
    fail(`HEAD mismatch: expected ${args.expectedHead.toLowerCase()}, checked out ${head.toLowerCase()}.`, 6);
  }
  const manifest = args.withCi ? [...FILES, CI_FILE] : FILES;
  const planned = manifest.map(([source, destination]) => ({
    destination,
    ...sourceHash(source),
    target: inspectPath(root, destination),
  }));
  const conflicts = planned.filter((row) => row.target.state !== 'absent');
  const lintRoot = inspectPath(root, 'tools/lint');
  if (lintRoot.state !== 'absent') {
    conflicts.push({ destination: 'tools/lint/', target: { ...lintRoot, state: `existing-install-root:${lintRoot.state}` } });
  }
  const result = {
    schema_version: 1,
    operation: 'read-only-plan',
    writes_enabled: false,
    runtime: `Node.js ${process.versions.node}`,
    target_root: root,
    target_head: head,
    expected_head: args.expectedHead,
    with_ci: args.withCi,
    planned_file_count: planned.length,
    status: conflicts.length ? 'refused-existing-or-unsafe-destination' : 'plan-ready-no-writes',
    files: planned,
    conflicts: conflicts.map(({ destination, target }) => ({ destination, ...target })),
    deferred: [
      'No files or directories are created; the former Python writer is never invoked.',
      'Installation transaction ownership, rollback, checker execution, and R05 result classification remain unimplemented.',
      'Node.js is required to run this planner and is not assumed to be preinstalled on consumer repositories.',
    ],
  };
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
  if (conflicts.length) process.exitCode = 3;
}

main();
