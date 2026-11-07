# lam-maps

Maps for [mg-look-at-me](../mg-look-at-me), the Look At Me game. A map here is a house: one level of rooms on a 4 m grid, on one floor or several joined by stairwells, with doors, keys, chests, levers, fuse boxes and witches dealt and proven solvable by the game's builder.

| Map id | What it is |
| --- | --- |
| `lam_villa_night` | A villa at night. You wake on the walled terrace; a hedge maze lies to the west, a fountain court between, the villa behind you. Heavy fog, near-black ambient, a few warm rooms. |
| `lam_functionalist_night` | A modernist house and its grounds at night. You wake on the entry terrace on the road side; the house lies west with a long spine hall, the radio room, a sauna and a garage workshop; the pool terrace, pergola court and tool shed are south. An open stair off the stair landing climbs to the upper floor: lounge, balcony and roof terrace over the pool side, bedrooms, a music room and a library; the gold key is up there. Heavy fog, near-black ambient. The underground level and lift are not built. |
| `lam_deco_mansion_night` | A three-storey mansion at night. You wake on the walled south lawn; the fountain court leads to the entrance hall, the ballroom, library and service rooms on the ground floor; the great stairs climb to the bedrooms and the picture gallery, the back stairs to the attic, where the gold key is. Heavy fog, near-black ambient, a few warm rooms. |

## Layout

- `tools/layouts/<id>.json`: the hand-laid plan (rooms, kinds, positions, light, and an optional `mood` with fog and ambient for the level).
- `houses/<id>/`: the generated house (`house.json` and the level document). Generated; do not edit by hand.
- `tools/build.sh`: regenerates every house from its plan with the game's `tools/build_levels.py --layout`. `tools/build.sh --check` fails when a house is stale.
- `tools/bsp_layout.py`, `tools/bsp_read.py`: launchers for the shared BSP reader and the plan tracer in `dot-map-convert` (the `mg-look-at-me` adapter). They print a rasterised floor plan of a source map to lay a plan out by hand.
- `provides.json`: the dot-cloud entry, accepted by the game as a `lookatme` map.

## Using a map in the game

The game's `.gitignore` carries a `bootstrap-link` line, so `dot-bootstrap` links `houses/<id>` into the game's `houses/`. Run the game's `./game.sh test` after adding one.

## Credits and licences

`lam_villa_night`: the plan is a loose, simplified reconstruction of the arrangement of a Steam Workshop map by korka007, https://steamcommunity.com/sharedfiles/filedetails/?id=2633639653 . The page states no licence. Nothing of the original is shipped: no geometry, textures or models, only room names and a rough arrangement; furniture comes from the game's CC0 Kenney props. Removal on request. See `licence.json`.

`lam_deco_mansion_night`: the plan is a loose, simplified reconstruction of the arrangement of a Steam Workshop map by Gastly_Furby_777, https://steamcommunity.com/sharedfiles/filedetails/?id=3698815153 . The page states no licence. Nothing of the original is shipped: no geometry, textures, models or sounds, only room names and a rough arrangement of its three storeys; furniture comes from the game's CC0 Kenney props. Removal on request. See `licence.json`.

`lam_functionalist_night`: the plan is a loose, simplified reconstruction of the arrangement of a Steam Workshop map by VITAPLEX, https://steamcommunity.com/sharedfiles/filedetails/?id=3382694345 . The page states no licence. Nothing of the original is shipped: no geometry, textures, models or sounds, only room names and a rough arrangement (the plan is scaled up to the game's room size); furniture comes from the game's CC0 Kenney props. Removal on request. See `licence.json`.

The upper level, the underground lift and the secret garage of the original need multi-floor layouts, which the builder does not have yet; only the ground floor and garden are here.

Everything else is MIT.

## Not published

This repository is not pushed and no pack is published until the licence question above is decided.
