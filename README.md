Maps for [mg-look-at-me](https://github.com/zees-games/mg-look-at-me), the Look At Me game. A map is a house: rooms on a 4 m grid, on one floor or several joined by stairs, with doors, keys, chests, levers, fuse boxes and witches. The game's builder deals them and proves each house can be solved.

## Maps

| Map id | What it is |
| --- | --- |
| `lam_villa_night` | A villa at night. You start on a walled terrace. A hedge maze lies west, a fountain court in the middle, the villa behind. Heavy fog, dark ambient light, a few warm rooms. |
| `lam_functionalist_night` | A modernist house and grounds at night, on three levels: a ground floor with a long hall, radio room, sauna and garage workshop; an upper floor with a lounge, balcony, roof terrace, bedrooms, music room and library (the gold key is here); and an underground level reached by a lift, with a wine cellar, plant room and a secret garage whose door has no power until a switch is flipped. |
| `lam_deco_mansion_night` | A three-storey mansion at night. You start on the south lawn. The ground floor has the entrance hall, ballroom, library and service rooms. The great stairs go up to the bedrooms and gallery, the back stairs to the attic, where the gold key is. |

## Using a map

The game's `.gitignore` has a `bootstrap-link` line, so [dot-bootstrap](https://github.com/gamespice-platform/bootstrap) links `houses/<id>` into the game's `houses/`. After adding a map, run the game's test command.

## Layout of this repository

| Path | What it is |
| --- | --- |
| `tools/layouts/<id>.json` | The hand-laid plan: rooms, kinds, positions, light, and an optional `mood` (fog and ambient light) |
| `houses/<id>/` | The generated house (`house.json` and the level document). Do not edit by hand. |
| `tools/build.sh` | Regenerates every house from its plan with the game's `tools/build_levels.py --layout`. `--check` fails when a house is stale. |
| `tools/bsp_layout.py`, `tools/bsp_read.py` | Launchers for the shared BSP reader and plan tracer in dot-map-convert. They print a floor plan of a source map to lay a plan out by hand. |
| `tools/stage_packs.sh`, `tools/check_packs.py` | Stage the pack and check it (see below) |
| `provides.json` | The dot-cloud entry; the game accepts it as a `lookatme` map |

`tools/stage_packs.sh OUT [id...]` stages the pack into `OUT/lam-maps/` (provides.json, licence.json, LICENSE, README.md and the house JSON, nothing else) and runs `tools/check_packs.py` on it. The check rejects source textures, models, sounds, scripts and outside assets, and wants a licence row for every house. Maps whose licence is "none stated" print as HOLD; add `--strict-licence` to make them fail. `python3 tools/test_check_packs.py` runs the checker's own tests.

## Quality and ongoing improvement

The maps, models, textures and sounds in this pack are being improved over time, and some of them are low quality today. Improvement is driven by the Nightly queue, a work queue where agents pick up items, and by a visual judge loop that views rendered frames and files defects until each asset passes repeated clean reviews. Known defects are filed there and fixed in later releases, and the screenshots here are regenerated as the assets improve.

## Credits

Each plan is a loose reconstruction of the room arrangement of a Steam Workshop map. Nothing of the original is shipped: no geometry, textures, models or sounds. Furniture comes from the game's CC0 Kenney props.

| Map | Author | Source | Licence |
| --- | --- | --- | --- |
| `lam_villa_night` | korka007 | [Steam Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=2633639653) | none stated |
| `lam_deco_mansion_night` | Gastly_Furby_777 | [Steam Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=3698815153) | none stated |
| `lam_functionalist_night` | VITAPLEX | [Steam Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=3382694345) | none stated |

If you made one of these maps and want it removed, open an issue at <https://github.com/zees-games/lam-maps/issues> and it goes. See [licence.json](licence.json).

Everything else is MIT, see [LICENSE](LICENSE).

## Publishing

No pack is published until the owner decides the licence question above.
