# lam-maps

Look At Me houses for mg-look-at-me. Read the game's `CLAUDE.md` and `docs/levels.md` first.

- A map is a plan in `tools/layouts/<id>.json` plus the generated `houses/<id>/`. Change the plan and run `tools/build.sh`; never hand-edit `houses/`. The plan builds only with the game checked out beside this repo (or `LAM_GAME`).
- Plan rules: rooms on a 4 m cell grid, no overlaps, every room touching another so the doors form one tree from the first room (the spawn). Corridors want a run of 3+ cells for the game's glimpses. Room names pick furniture themes (`tools/lm_furnish.py` THEMES in the game). `light` 0..1 is a room's warm lamp; `mood` sets the level's fog and ambient (see the game's `_level_mood`). Several floors: `floor` per room (0 ground, none below), `stair` rooms with `up`, 4+ cells long, opening only at their foot (own floor) and head (next floor), and `from` to pick which neighbour a room's door comes from; the game's `docs/map-bases.md` has the rules.
- The builder fits a document in 48,000 bytes compact, so a plan of about 40 to 55 rooms is the ceiling.
- Source-map names stay out of everything here (public repository): ids are neutral, the credit is the author and Workshop page in the README and `licence.json` only. Never ship source textures, models or geometry.
- Tracing a source BSP: convert with `dot-map-convert` `bsp.py convert`, then `tools/bsp_layout.py` for a plan. Props such as hedges are not brushes and do not show in the raster; read them from the intermediate's `static_props`.
- Not pushed or published without the owner's decision.
