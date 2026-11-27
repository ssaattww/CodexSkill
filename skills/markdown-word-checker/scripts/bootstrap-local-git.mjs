import { spawnSync } from 'node:child_process';
import { devNull } from 'node:os';

/** Read the caller's Git worktree without inheriting machine-level Git overrides. */
export function runBootstrapGit(args, { configFile = devNull, hooksDirectory = devNull } = {}) {
  const env = Object.fromEntries(
    Object.entries(process.env).filter(([key]) => !key.toUpperCase().startsWith('GIT_'))
  );
  Object.assign(env, {
    GIT_CONFIG_NOSYSTEM: '1',
    GIT_CONFIG_GLOBAL: configFile,
    GIT_TERMINAL_PROMPT: '0',
    GIT_OPTIONAL_LOCKS: '0',
    GIT_CONFIG_COUNT: '1',
    GIT_CONFIG_KEY_0: 'core.hooksPath',
    GIT_CONFIG_VALUE_0: hooksDirectory,
  });
  return spawnSync('git', args, { encoding: 'utf8', windowsHide: true, env });
}
