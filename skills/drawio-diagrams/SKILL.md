---
name: drawio-diagrams
description: Create and maintain small design diagrams in editable draw.io SVG files. Use when a repository needs class or component relationships, processing or data flows, or an existing `.dio.svg` diagram reviewed or updated.
---

# draw.io Diagrams

## Goal

Create compact design diagrams that remain readable in Markdown and editable in draw.io.

## Runtime independence

Use repository files and available local tools. Do not assume a particular operating system, editor installation, MCP connection, or permission to change files outside the task scope.

## Inputs

- Design prose, code or an existing diagram that defines what the drawing must show.
- Repository instructions for paths, Markdown references, diagram conventions and document checks.
- Existing diagram files when updating a drawing.

## Required flow

1. Check for an existing diagram skill, related examples and repository conventions before choosing a format or path.
2. Choose a **class relationship** diagram for types, responsibilities and dependencies. Choose a **flow** diagram for ordered steps, data movement, decisions and failure outcomes. Split the views when combining them makes either one hard to read; use the same names for shared components.
3. Create or update a real draw.io `.dio.svg`. Keep both the standalone SVG drawing and the embedded draw.io model. Do not rename a plain SVG or substitute a screenshot. Reference the file from Markdown with an image embed and repository-relative path.
4. Keep labels short. Make arrow direction and relationship meaning clear. Include boundaries only when they explain ownership or an external dependency. Preserve repository vocabulary and document rules.
5. Validate the model and its two display paths separately:
   - **Embedded model:** inspect the SVG `content` and embedded draw.io `mxfile`. If a `<diagram>` payload is compressed, decode it and check the expanded `mxGraphModel` labels and connectors; if it cannot be expanded, mark those details unverified. The [official draw.io Skill](https://github.com/jgraph/drawio-mcp/blob/main/plugins/codex/drawio/skills/drawio/SKILL.md) notes CLI `-e` for embedding diagram XML in an export. Embedded XML alone does not prove an edit round-trip.
   - **Model redraw:** use draw.io to export a PNG from the `.dio.svg`, which asks draw.io to read its embedded model and redraw it. Attempt this independently from the static render so one failure does not skip the other. Record its command status and whether output was produced.
   - **Static SVG drawing:** render the same `.dio.svg` directly with an SVG renderer such as Inkscape, without routing it through draw.io. Attempt it even if model redraw failed. Check Japanese text, connectors, clipping and page bounds; record it separately. This confirms the standalone SVG artwork, not the embedded model.
   - **Edit round-trip:** when draw.io is available and permitted, copy the existing file to a temporary path, change one visible label, save and reopen the copy, then confirm that the changed label appears in both the model and drawing and that connectors remain. Do not alter the original just to test editing.
6. Report each check independently. If the editor or renderer is unavailable, mark that check unverified and give the reason. A parse or embedded-model check alone does not prove editability or correct rendering.

### Default: existing CLI with its sandbox enabled

Prefer an already installed, authorized `drawio` CLI. The default route uses no download and leaves Electron's sandbox enabled. Before opening or rendering a diagram, inspect it for external image references (`<image href="https://…">`, CSS `url(https://…)`, or linked assets). Importing or rendering such content can make network requests; use trusted local-only inputs or an appropriately network-restricted environment, and record any external references that cannot be resolved safely. Do not treat permission to download the application as permission for a diagram to fetch remote content.

The input path is relative to the current repository root. Set it explicitly before running the workflow; do not assume the current directory is the CodexSkill checkout:

```bash
# From the CodexSkill repository root:
DIAGRAM_INPUT=skills/drawio-diagrams/examples/class-relations.dio.svg
# Class example edit target:
EDIT_CELL_ID=document
EDIT_OLD_LABEL=DiagramDocument
EDIT_NEW_LABEL='DiagramDocument (編集確認)'

# For the flow example, select these instead:
# DIAGRAM_INPUT=skills/drawio-diagrams/examples/processing-flow.dio.svg
# EDIT_CELL_ID=inspect
# EDIT_OLD_LABEL='内容を読む'
# EDIT_NEW_LABEL='内容を読む (編集確認)'

# From a consumer repository root after its .agents/skills link is configured,
# use the same edit target above and select one input path:
# DIAGRAM_INPUT=.agents/skills/drawio-diagrams/examples/class-relations.dio.svg
# DIAGRAM_INPUT=.agents/skills/drawio-diagrams/examples/processing-flow.dio.svg
```

CodexSkill's `scripts/link_consumer_skills.py <consumer-repo>` creates that consumer link; use the consumer's existing `.agents/skills` setup and do not replace paths manually.

Run the commands in the same Bash session with `set -euo pipefail`. Install an EXIT trap before creating a fresh temporary directory so that ordinary success and command failures both remove it while preserving the original exit status:

```bash
set -euo pipefail
work=
cleanup() {
  status=$?
  trap - EXIT
  if [[ -n "$work" && -d "$work" ]]; then
    rm -rf -- "$work" || { printf 'temporary cleanup failed: %s\n' "$work" >&2; status=1; }
  fi
  if [[ -n "$work" && -e "$work" ]]; then
    printf 'temporary directory remains: %s\n' "$work" >&2
    status=1
  fi
  if [[ -n "$work" && ! -e "$work" ]]; then
    printf 'temporary cleanup: removed\n'
  fi
  exit "$status"
}
trap cleanup EXIT
work="$(mktemp -d)"
mkdir -p "$work/config" "$work/cache"
export XDG_CONFIG_HOME="$work/config" XDG_CACHE_HOME="$work/cache"
diagram="${DIAGRAM_INPUT:?Set DIAGRAM_INPUT to a path relative to the current repository root}"
[[ -f "$diagram" ]] || { printf 'diagram input not found: %s\n' "$diagram" >&2; exit 2; }
cp -- "$diagram" "$work/source.dio.svg"
drawio=drawio
drawio_flags=()
# On a headless host, an installed CLI may need only this flag; keep its sandbox enabled.
# drawio_flags=(--ozone-platform=headless)
```

If the installed CLI is missing, stop and report the CLI route as unverified unless the optional fallback below is explicitly allowed. Select one CLI route before continuing. For the default installed CLI, leave `drawio=drawio` and `drawio_flags=()` as shown. The one-label edit below uses Python's standard library on the temporary mxfile; it is not a GUI edit. The import/export sequence verifies a headless model round-trip, not graphical-editor interaction.

```bash
static_status=0
if inkscape "$work/source.dio.svg" --export-filename="$work/static-original.png"; then
  [[ -s "$work/static-original.png" ]] || static_status=1
else
  static_status=$?
fi

import_status=0
if "$drawio" "${drawio_flags[@]}" -x -f xml -o "$work/model.drawio" "$work/source.dio.svg" && [[ -s "$work/model.drawio" ]]; then
  :
else
  import_status=$?
fi
edit_status=0
if [[ "$import_status" -eq 0 ]] && cp -- "$work/model.drawio" "$work/edited.drawio"; then
  python3 - "$work/edited.drawio" "${EDIT_CELL_ID:?Set EDIT_CELL_ID for the selected example}" "${EDIT_OLD_LABEL:?Set EDIT_OLD_LABEL for the selected example}" "${EDIT_NEW_LABEL:?Set EDIT_NEW_LABEL for the selected example}" <<'PY'
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
path = Path(sys.argv[1])
tree = ET.parse(path)
cell = next(cell for cell in tree.iter() if cell.tag == "mxCell" and cell.get("id") == sys.argv[2])
value = cell.get("value", "")
assert sys.argv[3] in value
cell.set("value", value.replace(sys.argv[3], sys.argv[4], 1))
tree.write(path, encoding="utf-8", xml_declaration=True)
PY
  edit_status=$?
else
  edit_status=1
fi
export_status=0
if [[ "$edit_status" -eq 0 ]] && "$drawio" "${drawio_flags[@]}" -x -f svg -e -o "$work/edited.dio.svg" "$work/edited.drawio" && [[ -s "$work/edited.dio.svg" ]]; then
  :
else
  export_status=$?
fi
reload_status=0
model_status=0
if [[ "$export_status" -eq 0 ]]; then
  if "$drawio" "${drawio_flags[@]}" -x -f xml -o "$work/reopened.drawio" "$work/edited.dio.svg" && [[ -s "$work/reopened.drawio" ]]; then
    :
  else
    reload_status=$?
  fi
  if "$drawio" "${drawio_flags[@]}" -x -f png -o "$work/model-redraw.png" "$work/edited.dio.svg" && [[ -s "$work/model-redraw.png" ]]; then
    :
  else
    model_status=$?
  fi
else
  reload_status=1
  model_status=1
fi
printf 'original SVG static render exit=%s\n' "$static_status"
printf 'draw.io import exit=%s\n' "$import_status"
printf 'temporary model edit exit=%s\n' "$edit_status"
printf 'editable SVG export exit=%s\n' "$export_status"
printf 'XML reload exit=%s\n' "$reload_status"
printf 'model redraw exit=%s\n' "$model_status"
model_png_out="${MODEL_PNG_OUT:-}"
static_png_out="${STATIC_SVG_PNG_OUT:-}"
save_status=0
save_new_png() {
  python3 - "$1" "$2" <<'PY'
import os
import shutil
import sys
source, destination = sys.argv[1:]
flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
fd = os.open(destination, flags, 0o600)
created = os.fstat(fd)
try:
    with os.fdopen(fd, "wb") as output, open(source, "rb") as input_file:
        shutil.copyfileobj(input_file, output)
except BaseException:
    try:
        current = os.stat(destination, follow_symlinks=False)
        if (current.st_dev, current.st_ino) == (created.st_dev, created.st_ino):
            os.unlink(destination)
    except FileNotFoundError:
        pass
    raise
PY
}
if [[ -n "$model_png_out" ]]; then
  if [[ "$model_status" -eq 0 && -s "$work/model-redraw.png" ]] && save_new_png "$work/model-redraw.png" "$model_png_out"; then
    :
  else
    printf 'requested model PNG not saved (destination must be a new path)\n' >&2
    save_status=1
  fi
fi
if [[ -n "$static_png_out" ]]; then
  if [[ "$static_status" -eq 0 && -s "$work/static-original.png" ]] && save_new_png "$work/static-original.png" "$static_png_out"; then
    :
  else
    printf 'requested static SVG PNG not saved (destination must be a new path)\n' >&2
    save_status=1
  fi
fi
overall_status=0
if [[ "$import_status" -ne 0 || "$edit_status" -ne 0 || "$export_status" -ne 0 || "$reload_status" -ne 0 || "$model_status" -ne 0 || "$static_status" -ne 0 || "$save_status" -ne 0 ]]; then
  overall_status=1
fi
printf 'overall exit=%s\n' "$overall_status"
```

Check the selected label in `reopened.drawio` and the exported SVG's embedded `content` model when XML reload succeeds. Inspect `$work/static-original.png` (raw SVG artwork) and `$work/model-redraw.png` (draw.io's model redraw of the edited SVG) separately while the Bash session is still open. The raw SVG render runs before draw.io import and export, so it is still attempted if either draw.io operation fails; record its input and result separately. Set `MODEL_PNG_OUT` or `STATIC_SVG_PNG_OUT` only when the user explicitly requests that image, to a new destination outside the repository; the save uses exclusive creation and fails without changing an existing file, directory entry or symlink. No images are copied by default. Record import, edit, export, XML reload, both renderers and requested-copy statuses before finishing. A failed import or export does not skip the independent raw SVG render; a failed XML reload does not skip model redraw or a successful requested-image copy. Then run `exit "$overall_status"`; any import, edit, export, readback, renderer or copy failure makes the final status nonzero. The EXIT trap removes the temporary package, profile, model, SVG and PNG on both success and ordinary failure, and reports whether the directory was removed. If cleanup itself fails, report it instead of claiming a clean run. Abrupt process termination can bypass a shell EXIT trap.

After inspection and any explicitly requested image copy, finish the Bash session with:

```bash
exit "$overall_status"
```

### Optional fallback: approved official release in an isolated environment

Use this only if no existing CLI is available, downloading the official asset is authorized, and the cloud/container supplies an outer sandbox suitable for running the extracted Electron app. Run this setup in the already trapped Bash session, before the shared import/export commands above. The tested reference asset is [draw.io Desktop v32.7.4](https://github.com/jgraph/drawio-desktop/releases/tag/v32.7.4), `drawio-amd64-32.7.4.deb`, SHA-256 `ffd8c110f1df8cde26a7fbd801212bd8381d257879f424a2191ec4cc491aa50b`. Confirm the exact selected asset and digest against official release metadata; do not reuse this digest for another version. Extract with `dpkg-deb -x` under the already trapped `$work`, not with a package installer:

```bash
deb="$work/drawio-amd64-32.7.4.deb"
curl -fL -o "$deb" https://github.com/jgraph/drawio-desktop/releases/download/v32.7.4/drawio-amd64-32.7.4.deb
printf '%s  %s\n' ffd8c110f1df8cde26a7fbd801212bd8381d257879f424a2191ec4cc491aa50b "$deb" | sha256sum -c -
dpkg-deb -x "$deb" "$work/root"
drawio="$work/root/opt/drawio/drawio"
drawio_flags=(--ozone-platform=headless)
```

Only for this extracted-app fallback, a Linux host without an X server needed `--ozone-platform=headless`; the default export failed with missing `$DISPLAY`. The extracted helper also refused to run without `--no-sandbox` because it was not root-owned setuid. Add `--no-sandbox` to `drawio_flags` only when the outer cloud/container sandbox is confirmed; never change helper permissions or run untrusted diagrams without isolation. `--disable-gpu` was used in the successful run, but its necessity was not tested. Do not add these flags to the default installed-CLI example. If the download, digest, sandbox condition or cleanup cannot be confirmed, stop and report the check as unverified.

## Examples

- Class relationships: ![DiagramBuilder type dependencies](examples/class-relations.dio.svg)
- Processing flow: ![Decision flow and outcomes](examples/processing-flow.dio.svg)

## Outputs

Return the relative paths, the distinction each diagram communicates, and separate results for model structure, normal display and edit round-trip. List unavailable checks as unverified.

## Completion condition

Complete when each diagram has one clear purpose, Markdown references resolve, the SVG drawing and embedded model have been checked independently, and verification gaps are explicit. Add scripts or dependencies only when repeated work demonstrates a need that existing tools cannot meet.
