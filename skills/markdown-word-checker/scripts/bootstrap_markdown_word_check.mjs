#!/usr/bin/env node
/** Read-only by default; install the fixed Markdown checker manifest only with --install. */

import { createHash, randomUUID } from 'node:crypto';
import {
  closeSync, fstatSync, lstatSync, mkdirSync, openSync, readFileSync,
  realpathSync, rmdirSync, unlinkSync, writeFileSync,
} from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { runBootstrapGit } from './bootstrap-local-git.mjs';

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const REPOSITORY_ROOT = path.resolve(SCRIPT_DIR, '../../..');
const PLANNER = path.join(SCRIPT_DIR, 'plan_markdown_word_check_bootstrap.mjs');

function parseArgs(argv) {
  const options = { target: null, expectedHead: null, withCi: false, install: false, exclusive: false, tempParent: null };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--target' && options.target === null && argv[i + 1]) options.target = argv[++i];
    else if (arg === '--expected-head' && options.expectedHead === null && argv[i + 1]) options.expectedHead = argv[++i];
    else if (arg === '--with-ci' && !options.withCi) options.withCi = true;
    else if (arg === '--install' && !options.install) options.install = true;
    else if (arg === '--confirm-exclusive' && !options.exclusive) options.exclusive = true;
    else if (arg === '--temp-parent' && options.tempParent === null && argv[i + 1]) options.tempParent = argv[++i];
    else if (arg === '--help' && argv.length === 1) {
      process.stdout.write(
        'Usage: node bootstrap_markdown_word_check.mjs --target <worktree-root> ' +
        '[--expected-head <40-hex-sha>] [--with-ci] [--install --confirm-exclusive] [--temp-parent <Windows-directory>]\n',
      );
      process.exit(0);
    } else {
      throw new Error(`Invalid or duplicate argument: ${arg}`);
    }
  }
  if (!options.target) throw new Error('--target is required.');
  if (options.expectedHead && !/^[0-9a-f]{40}$/i.test(options.expectedHead)) {
    throw new Error('--expected-head must be a full 40-character commit SHA.');
  }
  if (options.install && !options.expectedHead) {
    throw new Error('--install requires --expected-head.');
  }
  if (options.install !== options.exclusive) {
    throw new Error('--install requires --confirm-exclusive; omit both for a read-only plan.');
  }
  return options;
}

function plannerArgs(options) {
  const args = [PLANNER, '--target', options.target];
  if (options.expectedHead) args.push('--expected-head', options.expectedHead);
  if (options.withCi) args.push('--with-ci');
  return args;
}

function runPlanner(options) {
  const run = spawnSync(process.execPath, plannerArgs(options), {
    cwd: REPOSITORY_ROOT,
    encoding: 'utf8',
    windowsHide: true,
  });
  if (run.error) throw run.error;
  return {
    status: run.status ?? 1,
    stdout: run.stdout ?? '',
    stderr: run.stderr ?? '',
    plan: run.status === 0 ? JSON.parse(run.stdout) : null,
  };
}

function hash(data) {
  return createHash('sha256').update(data).digest('hex');
}

function sameIdentity(a, b) {
  return a.dev === b.dev && a.ino === b.ino && a.mode === b.mode;
}

function isWithin(parent, child) {
  const rel = path.relative(parent, child);
  return rel === '' || (rel !== '..' && !rel.startsWith(`..${path.sep}`) && !path.isAbsolute(rel));
}

function createOwnedDirectory(parent, name, state) {
  const destination = path.join(parent, name);
  mkdirSync(destination);
  const pending = { path: destination, reason: 'created directory identity unavailable' };
  state.unidentified.push(pending);
  try {
    const identity = lstatSync(destination);
    if (!identity.isDirectory() || identity.isSymbolicLink()) throw new Error('Created path is not a plain directory.');
    state.directories.push({ path: destination, identity });
    state.unidentified.splice(state.unidentified.indexOf(pending), 1);
  } catch (error) {
    pending.reason = `created directory identity unavailable: ${error.message}`;
    throw error;
  }
  return destination;
}

function writeTrackedFile(fd, destination, data, state) {
  const pending = { path: destination, reason: 'created file identity unavailable' };
  state.unidentified.push(pending);
  let failure;
  try {
    const identity = fstatSync(fd);
    state.files.push({ path: destination, identity });
    state.unidentified.splice(state.unidentified.indexOf(pending), 1);
    writeFileSync(fd, data);
  } catch (error) {
    if (state.unidentified.includes(pending)) {
      pending.reason = `created file identity unavailable: ${error.message}`;
    }
    failure = error;
  } finally {
    try {
      closeSync(fd);
    } catch (error) {
      failure = failure
        ? new AggregateError([failure, error], 'File operation and close failed.')
        : error;
    }
  }
  if (failure) throw failure;
}

function createOwnedFile(destination, data, state) {
  writeTrackedFile(openSync(destination, 'wx'), destination, data, state);
}

function verifyParentChain(root, destination, baseline, state) {
  const relative = path.relative(root, path.dirname(destination));
  if (path.isAbsolute(relative) || relative === '..' || relative.startsWith(`..${path.sep}`)) {
    throw new Error('Destination parent is outside the target.');
  }
  let current = root;
  for (const next of ['', ...relative.split(path.sep).filter(Boolean)]) {
    current = path.join(current, next);
    let info;
    try {
      info = lstatSync(current);
    } catch (error) {
      throw new Error('Parent cannot be inspected; preserved.', { cause: error });
    }
    const expected = state.directories.find((entry) => entry.path === current)?.identity ?? baseline.get(current);
    if (!info.isDirectory() || info.isSymbolicLink() || !expected || !sameIdentity(info, expected)) {
      throw new Error('Parent identity could not be confirmed; preserved.');
    }
  }
}

function cleanupOwned(root, baseline, state) {
  const removed = [];
  const remaining = [];
  for (const owned of [...state.files].reverse()) {
    try {
      verifyParentChain(root, owned.path, baseline, state);
      const current = lstatSync(owned.path);
      if (!current.isFile() || current.isSymbolicLink() || !sameIdentity(current, owned.identity)) {
        remaining.push({ path: owned.path, reason: 'file identity changed; preserved' });
        continue;
      }
      unlinkSync(owned.path);
      removed.push(owned.path);
    } catch (error) {
      if (error.code !== 'ENOENT') remaining.push({ path: owned.path, reason: error.message });
    }
  }
  for (const owned of [...state.directories].reverse()) {
    try {
      verifyParentChain(root, owned.path, baseline, state);
      const current = lstatSync(owned.path);
      if (!current.isDirectory() || current.isSymbolicLink() || !sameIdentity(current, owned.identity)) {
        remaining.push({ path: owned.path, reason: 'directory identity changed; preserved' });
        continue;
      }
      rmdirSync(owned.path);
      removed.push(owned.path);
      state.directories = state.directories.filter((entry) => entry.path !== owned.path);
    } catch (error) {
      if (error.code !== 'ENOENT') remaining.push({ path: owned.path, reason: error.message });
    }
  }
  return { removed, remaining, unidentified: [...state.unidentified] };
}

function captureParentIdentities(root, files) {
  const rootInfo = lstatSync(root);
  if (!rootInfo.isDirectory() || rootInfo.isSymbolicLink()) throw new Error('Target root is not a plain directory.');
  const identities = new Map([[root, rootInfo]]);
  for (const row of files) {
    const parent = path.dirname(path.resolve(root, ...row.destination.split('/')));
    if (!isWithin(root, parent)) throw new Error('Destination is outside the target.');
    let current = root;
    for (const part of path.relative(root, parent).split(path.sep).filter(Boolean)) {
      current = path.join(current, part);
      try {
        const info = lstatSync(current);
        if (info.isSymbolicLink() || !info.isDirectory()) {
          throw new Error(`Unsafe destination parent: ${path.relative(root, current)}`);
        }
        identities.set(current, info);
      } catch (error) {
        if (error.code === 'ENOENT') break;
        throw error;
      }
    }
  }
  return identities;
}

function ensureParents(root, destination, baseline, state) {
  const rel = path.relative(root, path.dirname(destination));
  if (rel === '..' || rel.startsWith(`..${path.sep}`) || path.isAbsolute(rel)) {
    throw new Error('Destination parent escaped the target root.');
  }
  const rootInfo = lstatSync(root);
  if (!rootInfo.isDirectory() || rootInfo.isSymbolicLink() || !sameIdentity(rootInfo, baseline.get(root))) {
    throw new Error('Target root changed during installation.');
  }
  let current = root;
  for (const part of rel.split(path.sep).filter(Boolean)) {
    const next = path.join(current, part);
    try {
      const info = lstatSync(next);
      if (info.isSymbolicLink() || !info.isDirectory()) {
        throw new Error(`Unsafe destination parent: ${path.relative(root, next)}`);
      }
      const owned = state.directories.find((entry) => entry.path === next);
      const prior = baseline.get(next);
      if (owned ? !sameIdentity(info, owned.identity) : !prior || !sameIdentity(info, prior)) {
        throw new Error(`Destination parent changed during installation: ${path.relative(root, next)}`);
      }
      current = next;
    } catch (error) {
      if (error.code !== 'ENOENT') throw error;
      if (baseline.has(next) || state.directories.some((entry) => entry.path === next)) {
        throw new Error(`Previously confirmed parent is missing: ${path.relative(root, next)}`);
      }
      current = createOwnedDirectory(current, part, state);
    }
  }
}

function assertExpectedHead(root, expectedHead) {
  if (path.relative(root, realpathSync(root)) !== '') throw new Error('Target root identity changed.');
  const run = runBootstrapGit(['-C', root, 'rev-parse', 'HEAD']);
  if (run.error || run.status !== 0) throw new Error('Could not verify target HEAD.');
  if (run.stdout.trim().toLowerCase() !== expectedHead.toLowerCase()) {
    throw new Error('Target HEAD changed during installation.');
  }
}

function requireLintRootAbsent(root) {
  try {
    lstatSync(path.join(root, 'tools', 'lint'));
    throw new Error('tools/lint appeared after the installation was planned.');
  } catch (error) {
    if (error.code !== 'ENOENT') throw error;
  }
}

function samePlan(a, b) {
  return a.target_root === b.target_root
    && a.target_head === b.target_head
    && JSON.stringify(a.files.map(({ source, destination, sha256 }) => [source, destination, sha256]))
      === JSON.stringify(b.files.map(({ source, destination, sha256 }) => [source, destination, sha256]));
}

function saveDiagnostics(root, runId, report, failure, baseline, state) {
  const guard = baseline.guard;
  if (typeof guard !== 'function') {
    throw new Error('Isolated-area guard is unavailable; diagnostics were not written.');
  }

  const relative = `tools/lint/artifacts/bootstrap/install-${runId}`;
  report.diagnostics = relative;
  const directory = path.resolve(root, relative);
  if (!isWithin(root, directory)) throw new Error('Diagnostics path escaped the isolated checkout.');

  const pending = { ...report, diagnostics_state: 'pending' };
  const complete = { ...report, diagnostics_state: 'complete' };

  for (const [name, data] of [
    ['stdout.log', JSON.stringify(pending, null, 2) + '\n'],
    ['stderr.log', failure ? failure + '\n' : ''],
    ['result.json', JSON.stringify(complete, null, 2) + '\n'],
  ]) {
    const filename = path.join(directory, name);
    const bytes = Buffer.from(data);

    guard('diagnostic-before-parents');
    ensureParents(root, filename, baseline, state);
    guard('diagnostic-after-parents');
    verifyParentChain(root, filename, baseline, state);

    guard('diagnostic-before-create');
    createOwnedFile(filename, bytes, state);
    guard('diagnostic-after-create');

    verifyParentChain(root, filename, baseline, state);
    const saved = lstatSync(filename);
    const owned = state.files.at(-1);
    if (!saved.isFile() || saved.isSymbolicLink()
        || !sameIdentity(saved, owned.identity)
        || !readFileSync(filename).equals(bytes)) {
      throw new Error(`Diagnostic could not be verified: ${name}`);
    }
    guard('diagnostic-after-verify');
  }

  report.diagnostics_state = 'complete';
}


function reportPath(root, value) {
  const rel = path.relative(root, value);
  return rel === '..' || rel.startsWith(`..${path.sep}`) ? '[outside-target]' : rel || '.';
}

function main() {
  const run = async () => {
    let options;
    try {
      options = parseArgs(process.argv.slice(2));
    } catch (error) {
      process.stderr.write(`${error.message}\n`);
      process.exitCode = 2;
      return;
    }

    let selectedRoot;
    let selectedRootIdentity;
    let first;
    try {
      if (options.install) {
        selectedRoot = realpathSync(options.target);
        selectedRootIdentity = lstatSync(selectedRoot);
        if (!selectedRootIdentity.isDirectory() || selectedRootIdentity.isSymbolicLink()) {
          throw new Error('Selected target root is not a plain directory.');
        }
      }
      first = runPlanner(options);
    } catch (error) {
      process.stderr.write(`Planner failed: ${error.message}\n`);
      process.exitCode = 4;
      return;
    }

    // Keep the existing planner path read-only. It does not import the
    // platform adapter, create a temp area, or create diagnostics.
    if (!options.install || first.status !== 0) {
      process.stdout.write(first.stdout);
      process.stderr.write(first.stderr);
      process.exitCode = first.status;
      return;
    }

    const sourcePlan = first.plan;
    const expectedCount = options.withCi ? 8 : 7;
    if (sourcePlan.status !== 'plan-ready-no-writes'
        || sourcePlan.files.length !== expectedCount) {
      process.stdout.write(first.stdout);
      process.stderr.write('Plan is not ready for installation.\n');
      process.exitCode = 3;
      return;
    }

    const assets = [];
    try {
      if (path.relative(sourcePlan.target_root, selectedRoot) !== ''
          || !sameIdentity(lstatSync(selectedRoot), selectedRootIdentity)) {
        throw new Error('Selected source root changed during planning.');
      }
      requireLintRootAbsent(selectedRoot);

      for (const row of sourcePlan.files) {
        const source = path.resolve(REPOSITORY_ROOT, ...row.source.split('/'));
        if (!isWithin(REPOSITORY_ROOT, source)) {
          throw new Error('Manifest source escaped the source repository.');
        }
        const data = readFileSync(source);
        if (hash(data) !== row.sha256) throw new Error(`Source hash changed: ${row.source}`);
        assets.push({ ...row, data });
      }
    } catch (error) {
      process.stderr.write(`Source preflight failed: ${error.message}\n`);
      process.exitCode = 5;
      return;
    }

    let area;
    let areaGuard;
    let isolatedRoot;
    let source;
    let assertSourceUnchanged;
    try {
      source = {
        root: selectedRoot,
        identity: selectedRootIdentity,
        head: sourcePlan.target_head,
      };

      assertSourceUnchanged = () => {
        if (realpathSync(source.root) !== source.root) {
          throw new Error('Source root resolution changed.');
        }
        const current = lstatSync(source.root);
        if (!current.isDirectory() || current.isSymbolicLink()
            || !sameIdentity(current, source.identity)) {
          throw new Error('Source root identity changed.');
        }
        const head = runBootstrapGit(['-C', source.root, 'rev-parse', 'HEAD']);
        if (head.error || head.status !== 0
            || head.stdout.trim().toLowerCase() !== source.head.toLowerCase()) {
          throw new Error('Source HEAD changed or could not be verified.');
        }
      };

      assertSourceUnchanged();

      const { createIsolatedArea } = await import('./isolated-local-area.mjs');
      const platform = process.platform;
      const parent = platform === 'win32' ? options.tempParent : process.env.XDG_RUNTIME_DIR;
      if (platform !== 'linux' && platform !== 'win32') {
        throw new Error('Installation is unsupported on this platform.');
      }
      if (!parent) throw new Error(platform === 'win32'
        ? 'Windows requires an explicit --temp-parent.'
        : 'XDG_RUNTIME_DIR is unavailable; refusing installation.');
      const { inspectLocalAreaAttributes } = await import(platform === 'win32'
        ? './windows-local-area-attributes.mjs'
        : './linux-local-area-attributes.mjs');

      const anchor = realpathSync(parent);
      if (isWithin(source.root, anchor)) {
        throw new Error("Isolated-area parent must be outside the source checkout.");
      }
      const anchorChain = [];
      for (let current = anchor; ; current = path.dirname(current)) {
        const info = lstatSync(current);
        if (!info.isDirectory() || info.isSymbolicLink()) {
          throw new Error(`Unsafe isolated-area ancestor: ${current}`);
        }
        if (!Number.isSafeInteger(info.dev) || !Number.isSafeInteger(info.ino) || info.ino <= 0
            || !Number.isSafeInteger(source.identity.dev)
            || !Number.isSafeInteger(source.identity.ino) || source.identity.ino <= 0) {
          throw new Error("Cannot verify separation from the source checkout.");
        }
        if (info.dev === source.identity.dev && info.ino === source.identity.ino) {
          throw new Error("Isolated-area ancestry includes the source checkout.");
        }
        anchorChain.push({ path: current, identity: info });
        if (path.dirname(current) === current) break;
      }

      const inspect = (context) => inspectLocalAreaAttributes({
        ...context,
        sourceRoot: source.root,
      });

      area = createIsolatedArea({
        parent: anchor,
        inspectAttributes: inspect,
        prefix: 'codexskill-87-',
      });

      const areaIdentity = lstatSync(area.root);
      let refusal = null;
      areaGuard = (phase) => {
        if (refusal) throw new Error(`Isolated area permanently refused: ${refusal}`);
        try {
          for (const ancestor of anchorChain) {
            const current = lstatSync(ancestor.path);
            if (!current.isDirectory() || current.isSymbolicLink()
                || !sameIdentity(current, ancestor.identity)) {
              throw new Error(`Ancestor changed: ${ancestor.path}`);
            }
          }
          if (realpathSync(area.root) !== area.root) {
            throw new Error('Isolated-area resolution changed.');
          }
          const current = lstatSync(area.root);
          if (!current.isDirectory() || current.isSymbolicLink()
              || !sameIdentity(current, areaIdentity)) {
            throw new Error('Isolated-area identity changed.');
          }
          const answer = inspect({
            phase,
            parent: anchor,
            root: area.root,
            ancestors: anchorChain.map((item) => item.path),
            platform: process.platform,
          });
          if (answer?.ok !== true) {
            throw new Error(answer?.reason || 'Area attributes are unknown.');
          }
        } catch (error) {
          refusal = `${phase}: ${error.message}`;
          throw new Error(refusal);
        }
      };

      areaGuard('before-clone');

      const emptyConfig = path.join(area.root, 'owned-empty-gitconfig');
      const emptyHooks = path.join(area.root, 'owned-empty-hooks');
      isolatedRoot = path.join(area.root, 'checkout');
      writeFileSync(emptyConfig, '', { flag: 'wx', mode: 0o600 });
      areaGuard('after-empty-config');
      mkdirSync(emptyHooks, { mode: 0o700 });
      areaGuard('after-empty-hooks');
      const isolatedGitOptions = { configFile: emptyConfig, hooksDirectory: emptyHooks };
      const clone = runBootstrapGit([
        'clone', '--no-local', '--no-checkout',
        '--', source.root, isolatedRoot,
      ], isolatedGitOptions);
      if (clone.error || clone.status !== 0) {
        throw new Error(clone.error?.message || clone.stderr?.trim() || 'Local clone failed.');
      }

      areaGuard('after-clone');
      for (const reference of ['alternates', 'http-alternates']) {
        try {
          lstatSync(path.join(isolatedRoot, '.git', 'objects', 'info', reference));
          throw new Error('Isolated copy unexpectedly uses an external object store.');
        } catch (error) {
          if (error.code !== 'ENOENT') throw error;
        }
      }
      assertSourceUnchanged();

      const checkout = runBootstrapGit([
        '-C', isolatedRoot,
        'checkout', '--detach', options.expectedHead,
      ], isolatedGitOptions);
      if (checkout.error || checkout.status !== 0) {
        throw new Error(checkout.error?.message || checkout.stderr?.trim() || 'Expected-HEAD checkout failed.');
      }

      areaGuard('after-checkout');
      const actualHead = runBootstrapGit(['-C', isolatedRoot, 'rev-parse', 'HEAD'], isolatedGitOptions);
      if (actualHead.error || actualHead.status !== 0
          || actualHead.stdout.trim().toLowerCase() !== options.expectedHead.toLowerCase()) {
        throw new Error('Isolated checkout HEAD mismatch.');
      }
      assertSourceUnchanged();
    } catch (error) {
      process.stderr.write(`Isolated checkout refused: ${error.message}\n`);
      if (error.isolationPath) {
        process.stderr.write(`Unverified residual: ${error.isolationPath}\n`);
      } else if (area?.root) {
        process.stderr.write(`Retained isolated checkout: ${area.root}\n`);
      }
      process.exitCode = 7;
      return;
    }

    const isolatedOptions = { ...options, target: isolatedRoot };
    let fresh;
    try {
      areaGuard('before-final-plan');
      fresh = runPlanner(isolatedOptions);
      areaGuard('after-final-plan');
    } catch (error) {
      process.stderr.write(`Isolated plan failed: ${error.message}\n`);
      process.stderr.write(`Retained isolated checkout: ${area.root}\n`);
      process.exitCode = 4;
      return;
    }

    const sameManifest = fresh.status === 0
      && fresh.plan.target_head === sourcePlan.target_head
      && JSON.stringify(fresh.plan.files.map(({ source, destination, sha256 }) =>
        [source, destination, sha256]))
        === JSON.stringify(sourcePlan.files.map(({ source, destination, sha256 }) =>
          [source, destination, sha256]));

    if (!sameManifest || fresh.plan.files.length !== expectedCount) {
      process.stdout.write(fresh.stdout);
      process.stderr.write('Isolated manifest differs from the source plan; no assets were written.\n');
      process.stderr.write(`Retained isolated checkout: ${area.root}\n`);
      process.exitCode = 6;
      return;
    }

    const plan = fresh.plan;
    const root = plan.target_root;
    let baseline;
    const state = { files: [], directories: [], unidentified: [] };
    let failure;

    try {
      areaGuard('before-copy-plan');
      if (realpathSync(root) !== isolatedRoot) throw new Error('Planner selected an unexpected checkout.');
      baseline = captureParentIdentities(root, plan.files);
      baseline.guard = areaGuard;
      requireLintRootAbsent(root);

      for (const row of assets) {
        areaGuard('before-asset-write');
        assertExpectedHead(root, options.expectedHead);
        const destination = path.resolve(root, ...row.destination.split('/'));
        if (!isWithin(root, destination) || destination === root) {
          throw new Error(`Unsafe destination: ${row.destination}`);
        }
        ensureParents(root, destination, baseline, state);
        areaGuard('before-asset-create');
        try {
          lstatSync(destination);
          throw new Error(`Destination appeared during installation: ${row.destination}`);
        } catch (error) {
          if (error.code !== 'ENOENT') throw error;
        }
        createOwnedFile(destination, row.data, state);
        areaGuard('after-asset-create');
      }

      for (const row of assets) {
        areaGuard('before-asset-verify');
        const destination = path.resolve(root, ...row.destination.split('/'));
        verifyParentChain(root, destination, baseline, state);
        const owned = state.files.find((entry) => entry.path === destination);
        const info = lstatSync(destination);
        if (!owned || !info.isFile() || info.isSymbolicLink()
            || !sameIdentity(info, owned.identity)
            || hash(readFileSync(destination)) !== row.sha256) {
          throw new Error(`Installed file verification failed: ${row.destination}`);
        }
      }
      areaGuard('after-asset-verify');
      assertExpectedHead(root, options.expectedHead);
      assertSourceUnchanged();
    } catch (error) {
      failure = error;
    }

    // Keep the isolated checkout. Never delete after an unverified change.
    const cleanup = {
      removed: [],
      remaining: [...state.files, ...state.directories].map(({ path: value }) => ({
        path: value,
        reason: 'retained in the isolated checkout',
      })),
      unidentified: [...state.unidentified],
    };

    const runId = randomUUID();
    const report = {
      operation: 'install-fixed-manifest',
      status: failure ? 'failed' : 'installed',
      target_head: plan.target_head,
      with_ci: options.withCi,
      planned_files: expectedCount,
      installed_files: failure ? 0 : expectedCount,
      created_before_failure: failure ? state.files.length : 0,
      files: assets.map(({ destination }) => destination),
      removed_owned_paths: [],
      owned_leftovers: cleanup.remaining.map(({ path: value, reason }) => ({
        path: reportPath(root, value),
        reason,
      })),
      possible_unowned_artifacts: cleanup.unidentified.map(({ path: value, reason }) => ({
        path: reportPath(root, value),
        reason,
      })),
      workspace: 'isolated-local-checkout',
      workspace_retained: true,
    };

    let diagnosticsFailure;
    const diagnosticState = {
      files: [],
      directories: [...state.directories],
      unidentified: [],
    };
    try {
      if (failure) throw new Error('Installation stopped; the isolated area is retained without diagnostic writes.');
      areaGuard('before-diagnostics');
      saveDiagnostics(root, runId, report, failure?.message, baseline, diagnosticState);
      areaGuard('after-diagnostics');
    } catch (error) {
      diagnosticsFailure = error;
      report.diagnostics_state = 'incomplete';
      report.diagnostics_failure = error.message;
      report.diagnostic_partial_paths = [
        ...diagnosticState.files,
        ...diagnosticState.directories.filter((item) =>
          !state.directories.some((owned) => owned.path === item.path)),
      ].map(({ path: value }) => reportPath(root, value));
      report.diagnostic_unidentified_paths = diagnosticState.unidentified.map(
        ({ path: value, reason }) => ({ path: reportPath(root, value), reason }),
      );
      if (!failure) report.status = 'installed-diagnostics-incomplete';
    }

    process.stdout.write(`isolated_workspace=${isolatedRoot}\n`);
    process.stdout.write(`${JSON.stringify(report, null, 2)}\n`);
    if (diagnosticsFailure) {
      process.stderr.write(`Diagnostics could not be saved: ${diagnosticsFailure.message}\n`);
    }
    if (failure) process.stderr.write(`Installation failed: ${failure.message}\n`);
    process.exitCode = failure || diagnosticsFailure ? 1 : 0;
  };

  run().catch((error) => {
    process.stderr.write(`Bootstrap failed: ${error.message}\n`);
    process.exitCode = 1;
  });
}
main();
