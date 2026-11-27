import {
  closeSync,
  fstatSync,
  lstatSync,
  mkdirSync,
  mkdtempSync,
  openSync,
  realpathSync,
  rmdirSync,
  unlinkSync,
  writeFileSync,
} from 'node:fs';
import os from 'node:os';
import path from 'node:path';

function identity(info) {
  if (!Number.isSafeInteger(info.dev) || !Number.isSafeInteger(info.ino)
      || info.ino <= 0) {
    throw new Error('Stable filesystem identity is unavailable.');
  }
  return { dev: info.dev, ino: info.ino, mode: info.mode };
}

function sameIdentity(a, b) {
  return a.dev === b.dev && a.ino === b.ino && a.mode === b.mode;
}

function requireDirectory(pathname, expected) {
  const info = lstatSync(pathname);
  if (!info.isDirectory() || info.isSymbolicLink()) {
    throw new Error(`Expected a plain directory: ${pathname}`);
  }
  const current = identity(info);
  if (expected && !sameIdentity(current, expected)) {
    throw new Error(`Directory identity changed: ${pathname}`);
  }
  return current;
}

function snapshotAncestors(directory) {
  const result = [];
  let current = directory;
  for (;;) {
    result.push({ path: current, identity: requireDirectory(current) });
    const parent = path.dirname(current);
    if (parent === current) break;
    current = parent;
  }
  return result;
}

function validateRelative(relative) {
  if (typeof relative !== 'string' || relative.length === 0
      || relative.includes('\0') || relative.includes('\\')
      || path.posix.isAbsolute(relative)
      || relative.split('/').some((part) => part === '' || part === '.' || part === '..')) {
    throw new Error('Path must be a non-empty safe relative path.');
  }
}

function isWithin(parent, child) {
  const relative = path.relative(parent, child);
  return relative !== '' && relative !== '..'
    && !relative.startsWith(`..${path.sep}`)
    && !path.isAbsolute(relative);
}

/**
 * Create an exclusively named local area.
 *
 * inspectAttributes is mandatory and must return { ok: true } only when the
 * platform-specific policy can verify the parent and area. It should throw or
 * return { ok: false, reason } when any property is unknown. This module
 * deliberately does not infer Windows ACL, drive, filesystem, or reparse-point
 * safety from Node's portable APIs.
 */
export function createIsolatedArea({ parent, inspectAttributes, prefix = 'codexskill-87-' }) {
  if (typeof inspectAttributes !== 'function') {
    throw new Error('A fail-closed platform attribute inspector is required.');
  }
  if (typeof prefix !== 'string' || !/^[a-zA-Z0-9_-]{1,40}$/.test(prefix)) {
    throw new Error('Invalid isolated-area prefix.');
  }

  const anchor = realpathSync(path.resolve(parent));
  const anchorInfo = requireDirectory(anchor);
  const ancestors = snapshotAncestors(anchor);

  function inspect(phase, root) {
    const result = inspectAttributes({
      phase,
      parent: anchor,
      root,
      ancestors: ancestors.map(({ path: item }) => item),
      platform: process.platform,
    });
    if (result?.ok !== true) {
      throw new Error(result?.reason || `Attributes unverified during ${phase}.`);
    }
  }

  inspect('before-create', null);

  let root;
  try {
    root = mkdtempSync(path.join(anchor, prefix));
  } catch (error) {
    throw new Error(`Could not create isolated area: ${error.message}`, { cause: error });
  }

  let rootIdentity;
  try {
    root = realpathSync(root);
    if (path.dirname(root) !== anchor) {
      throw new Error('Created area is not a direct child of the verified parent.');
    }
    rootIdentity = requireDirectory(root);
    inspect('after-create', root);
  } catch (error) {
    // The path was created by this call, but its attributes could not be
    // confirmed. Do not write diagnostics or attempt automatic deletion.
    error.isolationPath = root;
    throw error;
  }

  const ownedFiles = new Map();
  const ownedDirectories = new Map();
  const unconfirmed = [];
  let closed = false;

  function guard(phase) {
    if (closed) throw new Error('Isolated area is already closed.');

    for (const item of ancestors) {
      requireDirectory(item.path, item.identity);
    }
    requireDirectory(anchor, anchorInfo);

    if (realpathSync(root) !== root) {
      throw new Error('Isolated area path resolution changed.');
    }
    requireDirectory(root, rootIdentity);

    for (const [directory, expected] of ownedDirectories) {
      requireDirectory(directory, expected);
    }

    inspect(phase, root);
  }

  function resolveChild(relative) {
    validateRelative(relative);
    const destination = path.resolve(root, ...relative.split('/'));
    if (!isWithin(root, destination)) {
      throw new Error('Destination escaped the isolated area.');
    }
    return destination;
  }

  function ensureParents(relative) {
    const parts = relative.split('/');
    parts.pop();
    let current = root;

    for (const part of parts) {
      guard('create-parent');
      const next = path.join(current, part);

      try {
        const known = ownedDirectories.get(next);
        if (!known) {
          throw new Error(`Unexpected existing path inside isolated area: ${next}`);
        }
        requireDirectory(next, known);
      } catch (error) {
        if (error.code !== 'ENOENT') throw error;

        // A directory is created one level at a time after the common guard.
        guard('create-parent');
        mkdirSync(next);
        try {
          const createdIdentity = requireDirectory(next);
          ownedDirectories.set(next, createdIdentity);
        } catch (identityError) {
          unconfirmed.push({ path: next, reason: identityError.message });
          throw identityError;
        }
      }
      current = next;
    }
  }

  function createFile(relative, data, phase = 'create-file') {
    const destination = resolveChild(relative);
    guard(phase);
    ensureParents(relative);
    guard(phase);

    let fd;
    try {
      fd = openSync(destination, 'wx', 0o600);
      const createdIdentity = identity(fstatSync(fd));
      ownedFiles.set(destination, createdIdentity);
      writeFileSync(fd, data);
    } catch (error) {
      throw error;
    } finally {
      if (fd !== undefined) closeSync(fd);
    }

    // Detect a changed root/ancestor before reporting the operation as usable.
    guard(`${phase}-verify`);
    const current = lstatSync(destination);
    if (!current.isFile() || current.isSymbolicLink()
        || !sameIdentity(identity(current), ownedFiles.get(destination))) {
      throw new Error(`Created file identity changed: ${destination}`);
    }
    return destination;
  }

  function writeDiagnostic(relative, data) {
    validateRelative(relative);
    return createFile(`diagnostics/${relative}`, data, 'write-diagnostic');
  }

  function cleanup() {
    const removed = [];
    const remaining = [...unconfirmed];

    for (const [pathname, expected] of [...ownedFiles].reverse()) {
      try {
        guard('cleanup-file');
        const current = lstatSync(pathname);
        if (!current.isFile() || current.isSymbolicLink()
            || !sameIdentity(identity(current), expected)) {
          remaining.push({ path: pathname, reason: 'file identity changed; preserved' });
          continue;
        }
        unlinkSync(pathname);
        ownedFiles.delete(pathname);
        removed.push(pathname);
      } catch (error) {
        remaining.push({ path: pathname, reason: error.message });
        // Subsequent cleanup requires a fresh successful common guard.
      }
    }

    for (const [pathname, expected] of [...ownedDirectories].reverse()) {
      try {
        guard('cleanup-directory');
        requireDirectory(pathname, expected);
        rmdirSync(pathname); // Empty directories only; never recursive.
        ownedDirectories.delete(pathname);
        removed.push(pathname);
      } catch (error) {
        remaining.push({ path: pathname, reason: error.message });
      }
    }

    if (remaining.length === 0) {
      try {
        guard('cleanup-root');
        requireDirectory(root, rootIdentity);
        rmdirSync(root);
        removed.push(root);
        closed = true;
      } catch (error) {
        remaining.push({ path: root, reason: error.message });
      }
    } else {
      remaining.push({ path: root, reason: 'retained because owned or unconfirmed items remain' });
    }

    return { removed, remaining, rootRemoved: closed };
  }

  return Object.freeze({
    root,
    createFile: (relative, data) => createFile(relative, data),
    writeDiagnostic,
    cleanup,
  });
}
