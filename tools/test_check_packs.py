#!/usr/bin/env python3
"""Tests for check_packs.py and stage_packs.sh: python3 tools/test_check_packs.py"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import check_packs  # noqa: E402


def write(root, rel, text):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        f.write(text if isinstance(text, str) else json.dumps(text))


def good_pack(root, hid="lam_a", licence="MIT"):
    write(root, "provides.json", {"schema": 1, "kinds": ["map"], "games": ["gamemann/mg-look-at-me"], "entries": [
        {"kind": "map", "id": hid, "name": "A", "scene": "houses/%s/house.json" % hid, "map_kind": "lookatme"}]})
    row = {"paths": ["houses/%s/" % hid], "licence": licence, "title": "A"}
    if licence != "MIT":
        row.update(author="x", source_url="https://example.invalid/1", removal_contact="https://example.invalid/i")
    write(root, "licence.json", [{"paths": [""], "licence": "MIT"}, row])
    write(root, "LICENSE", "MIT")
    write(root, "README.md", "x")
    write(root, "houses/%s/house.json" % hid, {"kind": "house", "id": hid, "name": "A"})
    write(root, "houses/%s/%s_01.json" % (hid, hid), {"kind": "level", "id": hid + "_01", "rooms": [{"id": "r0"}],
                                                       "models": {"bed": [1, 1, 1]}, "props": [["bed", "r0", 1, 1, 0]]})


class CheckPacks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = os.path.join(self.tmp, "lam-maps")
        good_pack(self.root)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def offences(self, strict=False):
        return check_packs.check_pack(self.root, "lam-maps", strict)

    def test_clean(self):
        self.assertEqual(self.offences(), ([], []))

    def test_extra_files_are_offences(self):
        for rel in ("textures/wall.png", "tools/build.sh", "houses/lam_a/wall.png", ".github/workflows/x.yml",
                    "houses/lam_a/models/x.glb", "houses/lam_a/wall.png.import", "x.bsp", "sound.ogg", "a.gd"):
            write(self.root, rel, "x")
            bad, _ = self.offences()
            self.assertTrue(any(rel in b for b in bad), rel)
            os.remove(os.path.join(self.root, rel))

    def test_provides_rules(self):
        p = os.path.join(self.root, "provides.json")
        doc = json.load(open(p))
        for mut, needle in ((lambda d: d.update(games=["gamemann/game-arena"]), "games"),
                            (lambda d: d["entries"][0].update(map_kind="arena"), "map_kind"),
                            (lambda d: d["entries"][0].update(kind="model"), "not kind map"),
                            (lambda d: d["entries"][0].update(id="Bad-Id"), "bad or repeated"),
                            (lambda d: d.update(kinds=["model"]), "kinds"),
                            (lambda d: d["entries"][0].update(scene="houses/lam_b/house.json"), "scene")):
            d = json.loads(json.dumps(doc))
            mut(d)
            write(self.root, "provides.json", d)
            bad, _ = self.offences()
            self.assertTrue(any(needle in b for b in bad), needle)
        write(self.root, "provides.json", doc)

    def test_house_id_and_level(self):
        write(self.root, "houses/lam_a/house.json", {"kind": "house", "id": "other"})
        self.assertTrue(any("does not equal" in b for b in self.offences()[0]))
        write(self.root, "houses/lam_a/house.json", {"kind": "house", "id": "lam_a"})
        os.remove(os.path.join(self.root, "houses/lam_a/lam_a_01.json"))
        self.assertTrue(any("no level document" in b for b in self.offences()[0]))

    def test_unlisted_house(self):
        write(self.root, "houses/lam_z/house.json", {"id": "lam_z"})
        self.assertTrue(any("not listed" in b for b in self.offences()[0]))

    def test_outside_asset_reference(self):
        for s in ("res://assets/x.glb", "textures/wall.png", "https://example.invalid/a", "/etc/passwd", "a/b.gd"):
            write(self.root, "houses/lam_a/lam_a_01.json", {"kind": "level", "rooms": [1], "x": s})
            self.assertTrue(any("outside asset" in b for b in self.offences()[0]), s)

    def test_licence_rows(self):
        write(self.root, "licence.json", [{"paths": [""], "licence": "MIT"}])
        self.assertTrue(any("no licence.json row" in b for b in self.offences()[0]))
        write(self.root, "licence.json", [{"paths": ["houses/lam_a/"], "licence": "CC-BY"}])
        self.assertTrue(any("lacks author" in b for b in self.offences()[0]))

    def test_none_stated_is_hold_then_offence_when_strict(self):
        shutil.rmtree(self.root)
        good_pack(self.root, licence="none stated")
        bad, holds = self.offences()
        self.assertEqual(bad, [])
        self.assertEqual(len(holds), 1)
        bad, _ = self.offences(strict=True)
        self.assertTrue(any("HOLD" in b for b in bad))

    def test_cli_exit_codes(self):
        py = [sys.executable, "-I", os.path.join(HERE, "check_packs.py")]
        r = subprocess.run(py + [self.tmp, "lam-maps"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        write(self.root, "textures/a.png", "x")
        r = subprocess.run(py + [self.tmp, "lam-maps"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        self.assertEqual(subprocess.run(py, capture_output=True, text=True).returncode, 2)


class StageScript(unittest.TestCase):
    def test_stage_real_repo(self):
        with tempfile.TemporaryDirectory() as out:
            r = subprocess.run(["bash", os.path.join(HERE, "stage_packs.sh"), out], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            names = sorted(os.listdir(os.path.join(out, "lam-maps")))
            self.assertEqual(names, ["LICENSE", "README.md", "houses", "licence.json", "provides.json"])
            r = subprocess.run(["bash", os.path.join(HERE, "stage_packs.sh"), out, "lam_villa_night"], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            prov = json.load(open(os.path.join(out, "lam-maps", "provides.json")))
            self.assertEqual([e["id"] for e in prov["entries"]], ["lam_villa_night"])
            self.assertEqual(os.listdir(os.path.join(out, "lam-maps", "houses")), ["lam_villa_night"])

    def test_unknown_house_fails(self):
        with tempfile.TemporaryDirectory() as out:
            r = subprocess.run(["bash", os.path.join(HERE, "stage_packs.sh"), out, "nope"], capture_output=True, text=True)
            self.assertNotEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()
