"use strict";

const path = require("path");
const { execFileSync, spawnSync } = require("child_process");

const root = process.cwd();
const checker = path.join(root, "skills", "review-enforcer", "scripts", "check-markdown-whitelist.js");
const listUnknown = process.argv.includes("--list-unknown");
const tracked = execFileSync("git", ["ls-files", "--", "*.md"], { cwd: root, encoding: "utf8" })
  .split(/\r?\n/)
  .map((value) => value.trim())
  .filter(Boolean);

if (tracked.length === 0) {
  process.exit(0);
}

const args = [checker];
if (listUnknown) {
  args.push("--list-unknown");
}
args.push("--files", ...tracked);

const result = spawnSync(process.execPath, args, { cwd: root, stdio: "inherit" });
if (result.error) {
  console.error(result.error.message);
  process.exit(1);
}
process.exit(result.status ?? 1);
