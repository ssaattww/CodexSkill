#!/usr/bin/env node
/** Internal fixture check: stage the fixed bootstrap manifest in OS temp only. */

import { createHash } from 'node:crypto';
import { fstatSync, lstatSync, mkdirSync, mkdtempSync, openSync, closeSync, readFileSync, readdirSync, realpathSync, rmdirSync, unlinkSync, writeFileSync } from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const REPOSITORY_ROOT = path.resolve(SCRIPT_DIR, '../..');
const TEMPLATE_ROOT = path.join(REPOSITORY_ROOT, 'skills/markdown-word-checker/templates/repo');
const FIXED_FILES = [
  ['tools/lint/.gitignore', 'tools/lint/.gitignore'],
  ['tools/lint/README.md', 'tools/lint/README.md'],
  ['tools/lint/requirements.txt', 'tools/lint/requirements.txt'],
  ['tools/lint/markdown-targets.json', 'tools/lint/markdown-targets.json'],
  ['tools/lint/markdown-whitelist.yaml', 'tools/lint/markdown-whitelist.yaml'],
  ['tools/lint/scripts/run_markdown_word_check.py', 'tools/lint/scripts/run_markdown_word_check.py'],
  ['skills/review-enforcer/scripts/check-markdown-whitelist-sudachi.py', 'tools/lint/scripts/check-markdown-whitelist-sudachi.py'],
];
const OPTIONAL_CI = ['.github/workflows/markdown-word-check.yml', '.github/workflows/markdown-word-check.yml'];
const FIXTURE_PROBE_FAILURE_REASON = 'Simulated fixture placement failure after the first owned asset.';

function parseArgs(argv) {
  const options = { withCi: false, simulateFailure: false, simulateFixtureFailure: false };
  for (const arg of argv) {
    if (arg === '--with-ci' && !options.withCi) options.withCi = true;
    else if (arg === '--self-check-failure-cleanup' && !options.simulateFailure) options.simulateFailure = true;
    else if (arg === '--self-check-fixture-failure' && !options.simulateFixtureFailure) options.simulateFixtureFailure = true;
    else throw new Error(`Invalid or duplicate argument: ${arg}`);
  }
  return options;
}

function hash(data) {
  return createHash('sha256').update(data).digest('hex');
}

function sameIdentity(a, b) {
  return a.dev === b.dev && a.ino === b.ino && a.mode === b.mode;
}

export function writeAndTrackOpenedFile(fd, destination, row, state, io = {
  identify: fstatSync,
  write: writeFileSync,
  close: closeSync,
}) {
  const pending = { path: destination, reason: 'created file identity unavailable' };
  state.unidentified.push(pending);
  let operationError;
  try {
    const identity = io.identify(fd);
    state.files.push({ path: destination, identity, sha256: row.sha256 });
    state.unidentified.splice(state.unidentified.indexOf(pending), 1);
    io.write(fd, row.data);
  } catch (error) {
    if (state.unidentified.includes(pending)) {
      pending.reason = `created file identity unavailable: ${error.message}`;
    }
    operationError = error;
  } finally {
    try {
      io.close(fd);
    } catch (closeError) {
      operationError = operationError
        ? new AggregateError([operationError, closeError], 'File operation and close failed.')
        : closeError;
    }
  }
  if (operationError) throw operationError;
}

function isWithin(parent, child) {
  const rel = path.relative(parent, child);
  return rel === '' || (rel !== '..' && !rel.startsWith(`..${path.sep}`) && !path.isAbsolute(rel));
}

function sourcePlan(options) {
  const manifest = options.withCi ? [...FIXED_FILES, OPTIONAL_CI] : FIXED_FILES;
  return manifest.map(([sourceRel, destination]) => {
    const source = sourceRel.startsWith('skills/')
      ? path.resolve(REPOSITORY_ROOT, sourceRel)
      : path.resolve(TEMPLATE_ROOT, sourceRel);
    const info = lstatSync(source);
    if (!info.isFile() || info.isSymbolicLink()) throw new Error(`Required source is not a regular file: ${sourceRel}`);
    const data = readFileSync(source);
    return { sourceRel, destination, data, sha256: hash(data) };
  });
}

function assertExactTree(root, expected) {
  const found = [];
  function walk(current, prefix = '') {
    for (const entry of readdirSync(current, { withFileTypes: true })) {
      const rel = prefix ? `${prefix}/${entry.name}` : entry.name;
      if (entry.isSymbolicLink()) throw new Error(`Unexpected link in private staging tree: ${rel}`);
      if (entry.isDirectory()) walk(path.join(current, entry.name), rel);
      else if (entry.isFile()) found.push(rel);
      else throw new Error(`Unexpected filesystem object in staging tree: ${rel}`);
    }
  }
  walk(root);
  const actual = found.sort();
  const wanted = expected.map((row) => row.destination).sort();
  if (JSON.stringify(actual) !== JSON.stringify(wanted)) {
    throw new Error(`Staged manifest mismatch: expected ${wanted.length} files; found ${actual.length}.`);
  }
  for (const row of expected) {
    const staged = readFileSync(path.join(root, ...row.destination.split('/')));
    if (hash(staged) !== row.sha256) throw new Error(`Staged content hash mismatch: ${row.destination}`);
  }
  return actual;
}

function createOwnedDirectory(parent, name, state) {
  const destination = path.join(parent, name);
  mkdirSync(destination);
  const pending = { path: destination, reason: 'created directory identity unavailable' };
  state.unidentified.push(pending);
  try {
    const identity = lstatSync(destination);
    if (!identity.isDirectory() || identity.isSymbolicLink()) throw new Error(`Created path is not a directory: ${destination}`);
    state.directories.push({ path: destination, identity });
    state.unidentified.splice(state.unidentified.indexOf(pending), 1);
  } catch (error) {
    pending.reason = `created directory identity unavailable: ${error.message}`;
    throw error;
  }
  return destination;
}

function createOwnedFile(destination, row, data, state) {
  const fd = openSync(destination, 'wx');
  writeAndTrackOpenedFile(fd, destination, { ...row, data }, state);
}

function createUntrackedFixtureMarker(destination, data, reason, state, probe) {
  const fd = openSync(destination, 'wx');
  let writeError;
  try {
    writeFileSync(fd, data);
  } catch (error) {
    writeError = error;
  } finally {
    try {
      closeSync(fd);
    } catch (error) {
      writeError = writeError ? new AggregateError([writeError, error], 'Marker write and close failed.') : error;
    }
  }
  const record = { path: destination, reason };
  state.unidentified.push(record);
  const identity = lstatSync(destination);
  probe.markers.push({ path: destination, data, identity, record });
  if (writeError) throw writeError;
}

function preflightFixtureDestinations(fixtureRoot, manifest) {
  const lintRoot = path.join(fixtureRoot, 'tools/lint');
  try {
    lstatSync(lintRoot);
    return { allowed: false, reason: 'existing-tools-lint', path: 'tools/lint' };
  } catch (error) {
    if (error.code !== 'ENOENT') throw error;
  }
  for (const row of manifest) {
    const destination = path.resolve(fixtureRoot, ...row.destination.split('/'));
    if (!isWithin(fixtureRoot, destination)) return { allowed: false, reason: 'destination-outside-fixture' };
    try {
      lstatSync(destination);
      return { allowed: false, reason: 'existing-destination', path: row.destination };
    } catch (error) {
      if (error.code !== 'ENOENT') throw error;
    }
  }
  return { allowed: true };
}

function installFixtureManifest(runRoot, payloadRoot, manifest, state, options = {}) {
  const fixtureRoot = path.join(runRoot, 'consumer-fixture');
  if (!isWithin(runRoot, fixtureRoot) || fixtureRoot === runRoot) throw new Error('Fixture root must be a child of the owned run root.');
  const preflight = preflightFixtureDestinations(fixtureRoot, manifest);
  if (!preflight.allowed) return { state: 'refused-existing-destination', reason: preflight.reason, path: preflight.path };

  createOwnedDirectory(runRoot, 'consumer-fixture', state);
  for (const [index, row] of manifest.entries()) {
    const segments = row.destination.split('/');
    let current = fixtureRoot;
    for (const segment of segments.slice(0, -1)) {
      const next = path.join(current, segment);
      try {
        const existing = lstatSync(next);
        if (!existing.isDirectory() || existing.isSymbolicLink()) throw new Error(`Unexpected fixture parent type: ${segment}`);
      } catch (error) {
        if (error.code !== 'ENOENT') throw error;
        current = createOwnedDirectory(current, segment, state);
        continue;
      }
      current = next;
    }
    const destination = path.join(fixtureRoot, ...segments);
    const data = readFileSync(path.join(payloadRoot, ...segments));
    if (hash(data) !== row.sha256) throw new Error(`Payload hash mismatch: ${row.destination}`);
    createOwnedFile(destination, row, data, state);
    if (options.failureProbe && index === 0) {
      const legacyPath = path.join(fixtureRoot, ...manifest[1].destination.split('/'));
      const unknownPath = path.join(fixtureRoot, 'tools/lint/unknown-preserve.marker');
      createUntrackedFixtureMarker(legacyPath, Buffer.from('legacy fixture content\n'), 'simulated pre-existing destination; identity intentionally unavailable to installer', state, options.failureProbe);
      createUntrackedFixtureMarker(unknownPath, Buffer.from('unidentified fixture content\n'), 'simulated unidentified target; identity intentionally unavailable to installer', state, options.failureProbe);
      throw new Error(FIXTURE_PROBE_FAILURE_REASON);
    }
  }
  const verified = assertExactTree(fixtureRoot, manifest);

  const diagnosticRoot = path.join(fixtureRoot, 'tools/lint/artifacts/bootstrap/internal-stage-check');
  let current = fixtureRoot;
  for (const segment of path.relative(fixtureRoot, diagnosticRoot).split(path.sep)) {
    const next = path.join(current, segment);
    try {
      const existing = lstatSync(next);
      if (!existing.isDirectory() || existing.isSymbolicLink()) throw new Error(`Unexpected diagnostic parent type: ${segment}`);
      current = next;
    } catch (error) {
      if (error.code !== 'ENOENT') throw error;
      current = createOwnedDirectory(current, segment, state);
    }
  }
  const diagnostic = {
    state: 'fixture-manifest-installed',
    planned_files: manifest.length,
    verified_files: verified.length,
    consumer_repository_modified: false,
  };
  createOwnedFile(path.join(diagnosticRoot, 'stdout.log'), { sha256: '' }, Buffer.from(`${JSON.stringify(diagnostic)}\n`), state);
  createOwnedFile(path.join(diagnosticRoot, 'stderr.log'), { sha256: '' }, Buffer.alloc(0), state);
  createOwnedFile(path.join(diagnosticRoot, 'result.json'), { sha256: '' }, Buffer.from(`${JSON.stringify(diagnostic, null, 2)}\n`), state);
  return { ...diagnostic, verification: 'passed', diagnostics: 'tools/lint/artifacts/bootstrap/internal-stage-check' };
}

function snapshotTree(root) {
  const found = [];
  function walk(current, prefix = '') {
    for (const entry of readdirSync(current, { withFileTypes: true })) {
      const rel = prefix ? `${prefix}/${entry.name}` : entry.name;
      if (entry.isSymbolicLink()) throw new Error(`Unexpected link in fixture tree: ${rel}`);
      if (entry.isDirectory()) walk(path.join(current, entry.name), rel);
      else if (entry.isFile()) found.push([rel, hash(readFileSync(path.join(root, ...rel.split('/'))))]);
      else throw new Error(`Unexpected filesystem object in fixture tree: ${rel}`);
    }
  }
  walk(root);
  return JSON.stringify(found.sort(([a], [b]) => a.localeCompare(b)));
}

function cleanupOwned(state) {
  const remaining = [];
  for (const owned of [...state.files].reverse()) {
    try {
      const current = lstatSync(owned.path);
      if (!current.isFile() || current.isSymbolicLink() || !sameIdentity(current, owned.identity)) {
        remaining.push(owned.path);
        continue;
      }
      unlinkSync(owned.path);
    } catch (error) {
      if (error.code !== 'ENOENT') remaining.push(`${owned.path} (${error.message})`);
    }
  }
  for (const owned of [...state.directories].reverse()) {
    try {
      const current = lstatSync(owned.path);
      if (!current.isDirectory() || current.isSymbolicLink() || !sameIdentity(current, owned.identity)) {
        remaining.push(owned.path);
        continue;
      }
      rmdirSync(owned.path);
    } catch (error) {
      if (error.code !== 'ENOENT') remaining.push(`${owned.path} (${error.message})`);
    }
  }
  return { remaining, unidentified: [...state.unidentified] };
}

function inspectTemporaryRoot(stageRoot) {
  try {
    const info = lstatSync(stageRoot);
    return { state: 'present', path: stageRoot, kind: info.isDirectory() ? 'directory' : 'other' };
  } catch (error) {
    if (error.code === 'ENOENT') return { state: 'removed' };
    return { state: 'unconfirmed', path: stageRoot, reason: `${error.code ?? error.name}: ${error.message}` };
  }
}

function canonicalOwnedPath(value) {
  return typeof value === 'string' ? value.split(' (')[0] : '';
}

function stableSet(values) {
  return [...values].sort();
}

export function fixtureFailureEvidenceMatches(actual, expected) {
  const actualUnknown = (actual.possibleUnownedArtifacts ?? [])
    .map(({ path, reason }) => JSON.stringify([path, reason]));
  const expectedUnknown = (expected.possibleUnownedArtifacts ?? [])
    .map(({ path, reason }) => JSON.stringify([path, reason]));
  const actualOwned = (actual.ownedLeftovers ?? []).map(canonicalOwnedPath);
  return actual.failureReason === expected.failureReason
    && JSON.stringify(actual.outcome) === JSON.stringify(expected.outcome)
    && JSON.stringify(stableSet(actualOwned)) === JSON.stringify(stableSet(expected.ownedLeftoverPaths ?? []))
    && JSON.stringify(stableSet(actualUnknown)) === JSON.stringify(stableSet(expectedUnknown));
}

export function reconcileFinalOutcome(outcome, temporaryRoot, failure, cleanup) {
  const finalOutcome = { ...outcome };
  const ownedLeftovers = [...cleanup.remaining];
  let reason = failure?.message;
  if (temporaryRoot.state !== 'removed') {
    const rootReason = temporaryRoot.state === 'present'
      ? `Temporary root remains: ${temporaryRoot.path}`
      : `Temporary root removal could not be confirmed: ${temporaryRoot.reason}`;
    reason ??= rootReason;
    const rootPath = temporaryRoot.path ?? '[temporary root path unavailable]';
    if (!ownedLeftovers.some((item) => canonicalOwnedPath(item) === rootPath)) {
      ownedLeftovers.push(`${rootPath} (${rootReason})`);
    }
    if (outcome.verification === 'passed') {
      finalOutcome.state = 'verification-passed-cleanup-failed';
      finalOutcome.cleanup = 'failed';
    } else {
      finalOutcome.state = 'stage-failed-cleanup-incomplete';
      finalOutcome.cleanup = 'incomplete';
    }
  }
  const failed = Boolean(failure) || finalOutcome.cleanup !== 'complete' || temporaryRoot.state !== 'removed';
  const exitCode = !failed ? 0 : finalOutcome.cleanup === 'complete' ? 1 : 5;
  return { ...finalOutcome, reason, ownedLeftovers, exitCode };
}

function finalizeFixtureFailureProbe(stageRoot, plan, state, probe, failure) {
  const afterFailureCleanup = cleanupOwned(state);
  const failedOutcome = classifyStageOutcome(undefined, failure, afterFailureCleanup);
  const rootAfterInstallerCleanup = inspectTemporaryRoot(stageRoot);
  const managedAsset = path.join(stageRoot, 'consumer-fixture', ...plan[0].destination.split('/'));
  let managedAssetRemoved = false;
  try {
    lstatSync(managedAsset);
  } catch (error) {
    if (error.code === 'ENOENT') managedAssetRemoved = true;
    else throw error;
  }
  let markersPreserved = true;
  for (const marker of probe.markers) {
    const current = lstatSync(marker.path);
    if (!current.isFile() || current.isSymbolicLink() || !sameIdentity(current, marker.identity)
      || !readFileSync(marker.path).equals(marker.data)) {
      markersPreserved = false;
    }
  }
  const fixtureRoot = path.join(stageRoot, 'consumer-fixture');
  const expected = {
    failureReason: FIXTURE_PROBE_FAILURE_REASON,
    outcome: { state: 'stage-failed-cleanup-incomplete', verification: 'not-passed', cleanup: 'incomplete' },
    ownedLeftoverPaths: [
      path.join(fixtureRoot, 'tools/lint'),
      path.join(fixtureRoot, 'tools'),
      fixtureRoot,
      stageRoot,
    ],
    possibleUnownedArtifacts: [
      {
        path: path.join(fixtureRoot, ...plan[1].destination.split('/')),
        reason: 'simulated pre-existing destination; identity intentionally unavailable to installer',
      },
      {
        path: path.join(fixtureRoot, 'tools/lint/unknown-preserve.marker'),
        reason: 'simulated unidentified target; identity intentionally unavailable to installer',
      },
    ],
  };
  const actual = {
    failureReason: failure.message,
    outcome: failedOutcome,
    ownedLeftovers: afterFailureCleanup.remaining,
    possibleUnownedArtifacts: afterFailureCleanup.unidentified,
  };
  if (!fixtureFailureEvidenceMatches(actual, expected) || !managedAssetRemoved || !markersPreserved
    || rootAfterInstallerCleanup.state !== 'present') {
    throw new Error('Fixture failure evidence differed from the exact expected reason, outcome, and residual set.');
  }

  // The self-check harness removes only its own markers after proving the installer left them intact.
  for (const marker of probe.markers) {
    const current = lstatSync(marker.path);
    if (!current.isFile() || current.isSymbolicLink() || !sameIdentity(current, marker.identity)) {
      throw new Error(`Self-check marker ownership changed: ${path.basename(marker.path)}`);
    }
    unlinkSync(marker.path);
    state.unidentified.splice(state.unidentified.indexOf(marker.record), 1);
  }
  const finalCleanup = cleanupOwned(state);
  const rootStatus = inspectTemporaryRoot(stageRoot);
  if (finalCleanup.remaining.length || finalCleanup.unidentified.length || rootStatus.state !== 'removed') {
    throw new Error('Self-check harness could not remove its identified fixture markers and remaining owned directories.');
  }
  return {
    state: 'fixture-failure-self-check-passed',
    injected_failure: failure.message,
    observed_outcome: failedOutcome,
    exact_expected_evidence_matched: true,
    installer_cleanup_diagnostics: {
      temporary_root: rootAfterInstallerCleanup,
      owned_leftovers: afterFailureCleanup.remaining,
      possible_unowned_artifacts: afterFailureCleanup.unidentified,
    },
    installer_owned_first_asset_removed: true,
    legacy_destination_preserved: true,
    unidentified_target_preserved: true,
    expected_residuals_reported: true,
    final_harness_cleanup: 'complete',
    temporary_root: rootStatus,
  };
}

export function classifyStageOutcome(summary, failure, cleanup) {
  const cleanupComplete = cleanup.remaining.length === 0 && cleanup.unidentified.length === 0;
  if (failure) {
    return {
      state: cleanupComplete ? 'stage-failed-cleanup-complete' : 'stage-failed-cleanup-incomplete',
      verification: summary ? 'passed-before-failure' : 'not-passed',
      cleanup: cleanupComplete ? 'complete' : 'incomplete',
    };
  }
  if (!summary) {
    return { state: 'stage-failed-cleanup-incomplete', verification: 'not-passed', cleanup: 'incomplete' };
  }
  if (!cleanupComplete) {
    return { state: 'verification-passed-cleanup-failed', verification: 'passed', cleanup: 'failed' };
  }
  return { state: 'staged-manifest-verified', verification: 'passed', cleanup: 'complete' };
}

function main() {
  let options;
  try {
    options = parseArgs(process.argv.slice(2));
  } catch (error) {
    process.stderr.write(`${error.message}\n`);
    process.exitCode = 2;
    return;
  }

  let plan;
  try {
    plan = sourcePlan(options);
  } catch (error) {
    process.stderr.write(`Manifest preflight failed before staging: ${error.message}\n`);
    process.exitCode = 3;
    return;
  }

  let tempBase;
  let stageRoot;
  try {
    tempBase = realpathSync(os.tmpdir());
    const repositoryRoot = realpathSync(REPOSITORY_ROOT);
    if (isWithin(repositoryRoot, tempBase)) throw new Error('OS temp directory resolves inside the source repository.');
    stageRoot = mkdtempSync(path.join(tempBase, 'codexskill-87-manifest-stage-'));
  } catch (error) {
    process.stderr.write(`Cannot create isolated stage: ${error.message}\n`);
    process.exitCode = 4;
    return;
  }

  const state = { files: [], directories: [], unidentified: [] };
  let summary;
  let failure;
  let fixtureFailureProbeState;
  try {
    try {
      state.directories.push({ path: stageRoot, identity: lstatSync(stageRoot) });
    } catch (error) {
      state.unidentified.push({ path: stageRoot, reason: `stage-root identity unavailable: ${error.message}` });
      throw error;
    }
    const payloadRoot = createOwnedDirectory(stageRoot, 'payload', state);
    for (const [index, row] of plan.entries()) {
      const segments = row.destination.split('/');
      let current = payloadRoot;
      for (const segment of segments.slice(0, -1)) {
        current = path.join(current, segment);
        try {
          const existing = lstatSync(current);
          if (!existing.isDirectory() || existing.isSymbolicLink()) throw new Error(`Unexpected staging parent type: ${current}`);
        } catch (error) {
          if (error.code !== 'ENOENT') throw error;
          mkdirSync(current);
          const pendingDirectory = { path: current, reason: 'created directory identity unavailable' };
          state.unidentified.push(pendingDirectory);
          try {
            state.directories.push({ path: current, identity: lstatSync(current) });
            state.unidentified.splice(state.unidentified.indexOf(pendingDirectory), 1);
          } catch (identityError) {
            pendingDirectory.reason = `created directory identity unavailable: ${identityError.message}`;
            throw identityError;
          }
        }
      }
      const destination = path.join(payloadRoot, ...segments);
      const fd = openSync(destination, 'wx');
      writeAndTrackOpenedFile(fd, destination, row, state);
      if (options.simulateFailure && index === 0) throw new Error('Requested internal cleanup self-check after first staged asset.');
    }
    const staged = assertExactTree(payloadRoot, plan);
      fixtureFailureProbeState = options.simulateFixtureFailure ? { markers: [] } : undefined;
      const installed = installFixtureManifest(stageRoot, payloadRoot, plan, state, { failureProbe: fixtureFailureProbeState });
    if (installed.state !== 'fixture-manifest-installed') throw new Error(`Fixture install failed: ${installed.reason ?? installed.state}`);
    const fixtureRoot = path.join(stageRoot, 'consumer-fixture');
    const beforeRerun = snapshotTree(fixtureRoot);
    const rerun = installFixtureManifest(stageRoot, payloadRoot, plan, state);
    const afterRerun = snapshotTree(fixtureRoot);
    if (rerun.state !== 'refused-existing-destination' || beforeRerun !== afterRerun) throw new Error('Fixture rerun did not refuse without changing the fixture.');
    summary = {
      state: 'fixture-manifest-verified',
      planned_files: plan.length,
      staged_files: staged.length,
      installed_files: plan.length,
      rerun: rerun.state,
      rerun_tree_unchanged: true,
      consumer_repository_modified: false,
      writes_enabled_for_consumer: false,
    };
  } catch (error) {
    failure = error;
  }

  let cleanup;
  let outcome;
  let fixtureFailureProbe;
  if (options.simulateFixtureFailure && failure) {
    try {
      fixtureFailureProbe = finalizeFixtureFailureProbe(stageRoot, plan, state, fixtureFailureProbeState, failure);
      failure = undefined;
      summary = { state: 'fixture-failure-self-check-passed' };
      cleanup = { remaining: [], unidentified: [] };
      outcome = classifyStageOutcome(summary, undefined, cleanup);
    } catch (probeError) {
      failure = probeError;
      cleanup = cleanupOwned(state);
      outcome = classifyStageOutcome(summary, failure, cleanup);
    }
  } else {
    cleanup = cleanupOwned(state);
    outcome = classifyStageOutcome(summary, failure, cleanup);
  }
  const tempRootStatus = inspectTemporaryRoot(stageRoot);
  const finalOutcome = reconcileFinalOutcome(outcome, tempRootStatus, failure, cleanup);
  const { ownedLeftovers, exitCode, reason, ...reportedOutcome } = finalOutcome;
  const finalState = exitCode === 0 && fixtureFailureProbe
    ? fixtureFailureProbe.state
    : reportedOutcome.state;
  const result = {
    temporary_root: tempRootStatus,
    ...reportedOutcome,
    state: finalState,
    exit_code: exitCode,
    planned_files: summary?.planned_files ?? plan.length,
    verified_files: summary?.installed_files ?? 0,
    staged_files: summary?.staged_files ?? 0,
    rerun: summary?.rerun,
    rerun_tree_unchanged: summary?.rerun_tree_unchanged ?? false,
    consumer_repository_modified: summary?.consumer_repository_modified ?? false,
    fixture_failure_probe: fixtureFailureProbe,
    reason,
    owned_leftovers: ownedLeftovers,
    possible_unowned_artifacts: cleanup.unidentified,
    writes_enabled_for_consumer: false,
  };
  if (exitCode !== 0) {
    process.stderr.write(`${JSON.stringify(result, null, 2)}\n`);
    process.exitCode = exitCode;
    return;
  }
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) main();
