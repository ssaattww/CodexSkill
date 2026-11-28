import { lstatSync, realpathSync, statfsSync } from 'node:fs';
import path from 'node:path';

const TMPFS_MAGIC = 0x01021994;
const OWNER_MODE_0700 = 0o700;
const PERMISSION_BITS = 0o7777;

function refuse(reason) {
  return { ok: false, reason };
}

function inspectDirectory(pathname, uid) {
  const canonical = realpathSync(pathname);
  if (canonical !== pathname) {
    throw new Error(`Path is not canonical: ${pathname}`);
  }

  const info = lstatSync(pathname);
  if (!info.isDirectory() || info.isSymbolicLink()) {
    throw new Error(`Not a plain directory: ${pathname}`);
  }
  if (!Number.isSafeInteger(info.dev) || !Number.isSafeInteger(info.uid)) {
    throw new Error(`Filesystem identity is unavailable: ${pathname}`);
  }
  if (info.uid !== uid && info.uid !== 0) {
    throw new Error(`Directory owner is neither root nor the current UID: ${pathname}`);
  }

  const mode = info.mode & PERMISSION_BITS;
  const writableByOthers = (mode & 0o022) !== 0;
  const rootStickyAncestor = info.uid === 0 && (mode & 0o1000) !== 0;
  if (writableByOthers && !rootStickyAncestor) {
    throw new Error(`Ancestor is writable by other users: ${pathname}`);
  }
  return info;
}

function inspectPrivateDirectory(pathname, uid) {
  const info = inspectDirectory(pathname, uid);
  if (info.uid !== uid || (info.mode & PERMISSION_BITS) !== OWNER_MODE_0700) {
    throw new Error(`Directory must be owned by the current UID with mode 0700: ${pathname}`);
  }
  // With a POSIX extended ACL, the group mode bits reflect the ACL mask.
  // Therefore 0700 makes the effective group-class mask and other bits zero.
  return info;
}

export function inspectLocalAreaAttributes({
  phase,
  parent,
  root,
  sourceRoot,
  ancestors,
  platform,
}) {
  if (platform !== 'linux' || process.platform !== 'linux') {
    return refuse('Linux attribute inspection is the only implemented platform.');
  }
  if (typeof process.getuid !== 'function') {
    return refuse('Current UID cannot be determined.');
  }
  if (!Array.isArray(ancestors) || ancestors.length === 0) {
    return refuse('Ancestor list is unavailable.');
  }

  try {
    const uid = process.getuid();
    const canonicalParent = realpathSync(path.resolve(parent));
    if (canonicalParent !== parent) return refuse('Temporary parent is not canonical.');

    for (const ancestor of ancestors) inspectDirectory(ancestor, uid);

    const parentInfo = inspectPrivateDirectory(parent, uid);
    if (Number(statfsSync(parent).type) !== TMPFS_MAGIC) {
      return refuse('Temporary parent is not on tmpfs.');
    }

    const canonicalSource = realpathSync(path.resolve(sourceRoot));
    const sourceInfo = lstatSync(canonicalSource);
    if (!sourceInfo.isDirectory() || sourceInfo.isSymbolicLink()) {
      return refuse('Source worktree is not a plain directory.');
    }
    if (!Number.isSafeInteger(sourceInfo.dev) || sourceInfo.dev === parentInfo.dev) {
      return refuse('Temporary area is not on a distinct filesystem device from the source.');
    }

    if (root !== null) {
      const canonicalRoot = realpathSync(root);
      if (canonicalRoot !== root || path.dirname(root) !== parent) {
        return refuse('Created area is not a direct child of the verified parent.');
      }
      const rootInfo = inspectPrivateDirectory(root, uid);
      if (rootInfo.dev !== parentInfo.dev
          || Number(statfsSync(root).type) !== TMPFS_MAGIC) {
        return refuse('Created area filesystem differs from the verified tmpfs parent.');
      }
    }

    return { ok: true };
  } catch (error) {
    return refuse(`${phase}: ${error.message}`);
  }
}
