#!/usr/bin/env python3
"""Publish gate: a staged Look At Me map pack carries houses and listing files, nothing else.

    check_packs.py PACKS_DIR [id...] [--strict-licence]     PACKS_DIR holds the staged pack (tools/stage_packs.sh OUT)

This pack is built from hand-laid plans (tools/layouts), not converted from a source BSP, so it has no texture or model
coverage to map: its only art is the game's own CC0 Kenney furniture, named in each house. The gate keeps it that way.
The rules, all deterministic:

  1. the pack holds only provides.json, licence.json, LICENSE, README.md and houses/<id>/*.json; any other file (plans under
     tools/, scripts, workflows, images, audio, models, .import markers, .bsp/.gma/.vtf/.mdl/...) is an offence;
  2. provides.json: schema 1, kinds has "map", games is exactly the Look At Me game, each entry is kind map with an id of
     [a-z0-9_], map_kind "lookatme", a scene that exists as houses/<id>/house.json, whose own `id` equals the entry id, beside
     at least one level document (kind "level") that carries the house's rooms;
  3. no house document names an outside asset: no res://, user://, http(s)://, absolute path or asset/script file extension;
  4. licence.json covers every house: a row whose paths include houses/<id>/ with licence, and for a row that is not MIT
     the author, source_url and removal_contact. A row whose licence is "none stated" is reported as HOLD (the owner decides
     whether a loose reconstruction of an unlicensed Workshop map may go out); with --strict-licence it is an offence.

Exit 1 with one line per offence. Standard library only.
"""
import json
import os
import re
import sys

GAMES = {"gamemann/mg-look-at-me"}
MAP_KINDS = {"lookatme"}
TOP_FILES = {"provides.json", "licence.json", "LICENSE", "README.md"}
ASSET_EXT = (".png", ".jpg", ".jpeg", ".webp", ".tga", ".bmp", ".dds", ".exr", ".hdr", ".glb", ".gltf", ".obj", ".fbx",
             ".wav", ".mp3", ".ogg", ".vtf", ".vmt", ".mdl", ".vtx", ".vvd", ".bsp", ".vpk", ".gma",
             ".gd", ".tscn", ".tres", ".res", ".py", ".sh", ".yml", ".yaml", ".import")
ID_RE = re.compile(r"[a-z0-9_]+")


def _load(path, bad, label):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        bad.append("%s: cannot read %s (%s)" % (label, os.path.basename(path), e))
        return None


def _strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for k, v in node.items():
            yield str(k)
            yield from _strings(v)
    elif isinstance(node, list):
        for v in node:
            yield from _strings(v)


def _outside_ref(s):
    low = s.lower()
    if low.startswith(("res://", "user://", "http://", "https://", "file://")) or s.startswith(("/", "~")):
        return True
    return low.endswith(ASSET_EXT)


def check_pack(root, pid, strict_licence=False):
    """(offences, holds) for the staged pack at root."""
    bad, holds = [], []
    if not os.path.isdir(root):
        return ["%s: pack directory is missing" % pid], holds
    # 1. whitelist
    for d, _, files in os.walk(root):
        for fn in files:
            rel = os.path.relpath(os.path.join(d, fn), root).replace(os.sep, "/")
            parts = rel.split("/")
            if rel in TOP_FILES or (len(parts) == 3 and parts[0] == "houses" and fn.endswith(".json")):
                continue
            ext = os.path.splitext(fn)[1].lower()
            why = "a source-engine, art, sound, script or import file" if ext in ASSET_EXT else "not part of a house pack"
            bad.append("%s: %s is %s" % (pid, rel, why))
    # 2. provides.json
    prov = _load(os.path.join(root, "provides.json"), bad, pid)
    houses = []
    if prov is not None:
        if prov.get("schema") != 1:
            bad.append("%s: provides.json schema must be 1" % pid)
        if "map" not in prov.get("kinds", []):
            bad.append("%s: provides.json kinds must include map" % pid)
        games = prov.get("games", [])
        if not games or set(games) != GAMES:
            bad.append("%s: provides.json games must be %s, found %s" % (pid, sorted(GAMES), games))
        seen = set()
        entries = prov.get("entries", [])
        if not entries:
            bad.append("%s: provides.json has no entries" % pid)
        for e in entries:
            eid = str(e.get("id", ""))
            if e.get("kind") != "map":
                bad.append("%s: entry %s is not kind map" % (pid, eid))
            if not ID_RE.fullmatch(eid) or eid in seen:
                bad.append("%s: bad or repeated entry id %r" % (pid, eid))
            seen.add(eid)
            if e.get("map_kind") not in MAP_KINDS:
                bad.append("%s: entry %s map_kind must be one of %s" % (pid, eid, sorted(MAP_KINDS)))
            scene = e.get("scene", "")
            if scene != "houses/%s/house.json" % eid:
                bad.append("%s: entry %s scene must be houses/%s/house.json, found %r" % (pid, eid, eid, scene))
            houses.append(eid)
            hdir = os.path.join(root, "houses", eid)
            hdoc = _load(os.path.join(hdir, "house.json"), bad, pid) if os.path.isfile(os.path.join(hdir, "house.json")) else None
            if hdoc is None:
                bad.append("%s: entry %s has no houses/%s/house.json" % (pid, eid, eid))
                continue
            if hdoc.get("id") != eid:
                bad.append("%s: houses/%s/house.json id %r does not equal the entry id" % (pid, eid, hdoc.get("id")))
            levels = 0
            for fn in sorted(os.listdir(hdir)):
                if fn == "house.json" or not fn.endswith(".json"):
                    continue
                doc = _load(os.path.join(hdir, fn), bad, pid)
                if doc and doc.get("kind") == "level" and doc.get("rooms"):
                    levels += 1
            if not levels:
                bad.append("%s: houses/%s holds no level document with rooms" % (pid, eid))
        for hd in os.listdir(os.path.join(root, "houses")) if os.path.isdir(os.path.join(root, "houses")) else []:
            if hd not in seen:
                bad.append("%s: houses/%s is not listed in provides.json" % (pid, hd))
    # 3. no outside asset references in any house document
    for eid in houses:
        hdir = os.path.join(root, "houses", eid)
        if not os.path.isdir(hdir):
            continue
        for fn in sorted(os.listdir(hdir)):
            if not fn.endswith(".json"):
                continue
            try:
                with open(os.path.join(hdir, fn), encoding="utf-8") as f:
                    doc = json.load(f)
            except (OSError, ValueError):
                continue
            for s in _strings(doc):
                if _outside_ref(s):
                    bad.append("%s: houses/%s/%s names an outside asset %r" % (pid, eid, fn, s[:80]))
                    break
    # 4. licence rows
    lic = _load(os.path.join(root, "licence.json"), bad, pid)
    if lic is not None:
        rows = lic if isinstance(lic, list) else []
        if not rows:
            bad.append("%s: licence.json must be a list of rows" % pid)
        for eid in houses:
            hit = [r for r in rows if any(p.startswith("houses/%s/" % eid) for p in r.get("paths", []))]
            if not hit:
                bad.append("%s: houses/%s has no licence.json row" % (pid, eid))
                continue
            r = hit[0]
            lic_name = str(r.get("licence", "")).strip()
            if not lic_name:
                bad.append("%s: licence row for %s has no licence" % (pid, eid))
            if lic_name.upper() != "MIT":
                for k in ("author", "source_url", "removal_contact"):
                    if not r.get(k):
                        bad.append("%s: licence row for %s lacks %s" % (pid, eid, k))
            if lic_name.lower() == "none stated":
                msg = "%s: HOLD %s, licence none stated (Workshop map by %s)" % (pid, eid, r.get("author", "?"))
                (bad if strict_licence else holds).append(msg)
    return bad, holds


def main(argv):
    strict = "--strict-licence" in argv
    argv = [a for a in argv if a != "--strict-licence"]
    if not argv:
        print(__doc__)
        return 2
    out = argv[0]
    ids = argv[1:] or sorted(n for n in os.listdir(out) if os.path.isdir(os.path.join(out, n)))
    bad, holds = [], []
    for pid in ids:
        b, h = check_pack(os.path.join(out, pid), pid, strict)
        bad += b
        holds += h
    for line in holds:
        print("check_packs: " + line, file=sys.stderr)
    for line in bad:
        print("check_packs: " + line, file=sys.stderr)
    print("check_packs: %d pack(s), %s%s" % (len(ids), "%d offence(s)" % len(bad) if bad else "clean",
                                             ", %d hold(s)" % len(holds) if holds else ""))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
