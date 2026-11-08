#!/bin/bash
# stage_packs.sh OUT [id...] : stages the one CDN pack of this repository (OUT/lam-maps/) the way it is published.
#
# PUBLISH RULE (owner policy: licensed art must be mapped to free/open/own assets): this pack carries only the hand-laid houses
# (houses/<id>/*.json), provides.json, licence.json, LICENSE and README.md. A house names Kenney (CC0) furniture models that the
# game resolves from its own assets; no source texture, model, sound, script, workflow or plan (tools/) is ever copied.
# Source art of a Workshop map (a .bsp/.gma, decoded textures) has no place here: .gitignore keeps it out of the repository and
# tools/check_packs.py fails the stage if one turns up. With ids, only those houses are staged (provides.json and licence.json
# are cut to match). Then tools/check_packs.py verifies the result; add --strict-licence to also fail on "none stated" rows.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${1:?usage: stage_packs.sh OUT [id...]}"; shift
IDS=("$@"); [ ${#IDS[@]} -gt 0 ] || mapfile -t IDS < <(cd "$HERE/houses" && ls)
DEST="$OUT/lam-maps"
rm -rf "${DEST:?}"; mkdir -p "$DEST/houses"
for id in "${IDS[@]}"; do
    [ -d "$HERE/houses/$id" ] || { echo "no house for $id" >&2; exit 1; }
    mkdir -p "$DEST/houses/$id"
    cp "$HERE/houses/$id/"*.json "$DEST/houses/$id/"
done
cp "$HERE/LICENSE" "$HERE/README.md" "$DEST/"
python3 -I - "$HERE" "$DEST" "${IDS[@]}" <<'PY'
import json, sys
here, dest, ids = sys.argv[1], sys.argv[2], set(sys.argv[3:])
prov = json.load(open(here + "/provides.json"))
prov["entries"] = [e for e in prov["entries"] if e["id"] in ids]
lic = json.load(open(here + "/licence.json"))
keep = []
for row in lic:
    paths = row.get("paths", [])
    if paths == [""] or any(p.startswith("houses/" + i + "/") for p in paths for i in ids):
        row = dict(row, paths=[p for p in paths if not p.startswith("tools/")])
        keep.append(row)
for name, doc in (("provides.json", prov), ("licence.json", keep)):
    with open(dest + "/" + name, "w") as f:
        f.write(json.dumps(doc, indent=4) + "\n")
PY
python3 -I "$HERE/tools/check_packs.py" "$OUT" lam-maps
