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
5. Validate the two representations separately:
   - **Embedded model:** inspect the SVG `content` and embedded draw.io `mxfile`. If a `<diagram>` payload is compressed, decode it and check the expanded `mxGraphModel` labels and connectors; if it cannot be expanded, mark those details unverified. The [official draw.io Skill](https://github.com/jgraph/drawio-mcp/blob/main/plugins/codex/drawio/skills/drawio/SKILL.md) notes CLI `-e` for embedding diagram XML in an export. Embedded XML alone does not prove an edit round-trip.
   - **Rendered drawing:** render the SVG or open its Markdown page in the normal preview. Check Japanese text, arrow connections, clipping and page bounds.
   - **Edit round-trip:** when draw.io is available and permitted, copy the existing file to a temporary path, change one visible label, save and reopen the copy, then confirm that the changed label appears in both the model and drawing and that connectors remain. Do not alter the original just to test editing.
6. Report each check independently. If the editor or renderer is unavailable, mark that check unverified and give the reason. A parse or embedded-model check alone does not prove editability or correct rendering.

### Headless CLI round-trip (tested Linux x64 path)

Prefer an existing authorized `drawio` CLI. If none is available, use an official release only when downloads are allowed. The tested reference asset is [draw.io Desktop v32.7.4](https://github.com/jgraph/drawio-desktop/releases/tag/v32.7.4), `drawio-amd64-32.7.4.deb`, SHA-256 `ffd8c110f1df8cde26a7fbd801212bd8381d257879f424a2191ec4cc491aa50b`. Confirm the selected asset's digest against its official release metadata before extracting it; do not reuse this digest for another version. Extract with `dpkg-deb -x` into a temporary directory, not with a package installer, and keep the source, profile, model, and outputs there.

For a Linux host without an X server, `--ozone-platform=headless` was necessary: the default export stopped with a missing `$DISPLAY` error. In the tested temporary package extraction, `--no-sandbox` was also necessary because Electron refused to start with its extracted `chrome-sandbox` helper not installed as root-owned setuid. Use that flag only inside an already isolated cloud/container environment; do not change helper permissions or run untrusted diagrams without an appropriate outer sandbox. `--disable-gpu` was included in the successful run, but its necessity was not tested. `-x` selects CLI export, `-f` selects the format, and SVG `-e` embeds the editable model. Set `XDG_CONFIG_HOME` and `XDG_CACHE_HOME` to temporary directories to keep the run isolated.

Use the following sequence on a temporary copy. The one-label edit below is a native mxfile XML fixture edit with Python's standard library; it is not a GUI edit. This verifies the headless import/export round-trip, not graphical-editor interaction.

```bash
set -euo pipefail
work="$(mktemp -d)"
deb="$work/drawio-amd64-32.7.4.deb"
curl -fL -o "$deb" https://github.com/jgraph/drawio-desktop/releases/download/v32.7.4/drawio-amd64-32.7.4.deb
printf '%s  %s\n' ffd8c110f1df8cde26a7fbd801212bd8381d257879f424a2191ec4cc491aa50b "$deb" | sha256sum -c -
dpkg-deb -x "$deb" "$work/root"
drawio="$work/root/opt/drawio/drawio"
mkdir -p "$work/config" "$work/cache"
export XDG_CONFIG_HOME="$work/config" XDG_CACHE_HOME="$work/cache"
cp skills/drawio-diagrams/examples/class-relations.dio.svg "$work/source.dio.svg"
flags=(--no-sandbox --disable-gpu --ozone-platform=headless)
"$drawio" "${flags[@]}" -x -f xml -o "$work/model.drawio" "$work/source.dio.svg"
cp "$work/model.drawio" "$work/edited.drawio"
python3 - "$work/edited.drawio" <<'PY'
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
path = Path(sys.argv[1])
tree = ET.parse(path)
cell = next(cell for cell in tree.iter() if cell.tag == "mxCell" and cell.get("id") == "document")
value = cell.get("value", "")
assert "DiagramDocument" in value
cell.set("value", value.replace("DiagramDocument", "DiagramDocument (編集確認)", 1))
tree.write(path, encoding="utf-8", xml_declaration=True)
PY
"$drawio" "${flags[@]}" -x -f svg -e -o "$work/edited.dio.svg" "$work/edited.drawio"
"$drawio" "${flags[@]}" -x -f xml -o "$work/reopened.drawio" "$work/edited.dio.svg"
"$drawio" "${flags[@]}" -x -f png -o "$work/edited-from-svg.png" "$work/edited.dio.svg"
```

Check the changed label in `reopened.drawio` and the SVG's embedded `content` model, then open `edited-from-svg.png` and read the visible label, Japanese glyphs, connectors, and clipping. The PNG must be generated from the newly exported `.dio.svg`. If extraction, readback, rendering, or image inspection fails, report that check as unverified; do not substitute a structural parse or an older PNG. After recording results, remove the temporary package, profile, model, and SVG; copy out only a requested PNG deliverable, never into the repository.

## Examples

- Class relationships: ![DiagramBuilder type dependencies](examples/class-relations.dio.svg)
- Processing flow: ![Decision flow and outcomes](examples/processing-flow.dio.svg)

## Outputs

Return the relative paths, the distinction each diagram communicates, and separate results for model structure, normal display and edit round-trip. List unavailable checks as unverified.

## Completion condition

Complete when each diagram has one clear purpose, Markdown references resolve, the SVG drawing and embedded model have been checked independently, and verification gaps are explicit. Add scripts or dependencies only when repeated work demonstrates a need that existing tools cannot meet.
