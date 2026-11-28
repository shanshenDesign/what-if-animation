# Camera Plan — Episode 4 (New Madrid 1811–1812)

All camera motion goes through `warpU([start, mid, end], t)` in `src/Full.jsx`
(cubic Hermite with finite-difference tangents → eased in/out, never a linear crawl),
then lerps `camStart → camEnd` and aims at `lookAt`.

## Locations (spaced 40 units along x)

| Location | x | Shot | camStart | camEnd | lookAt |
|----------|---|------|----------|--------|--------|
| Levee, 16 Dec 1811 | 0 | 0 | -1.4, 1.95, 5.2 | 1.0, 2.25, 4.0 | 0.2, 1.8, -2.0 |
| New Madrid fissure | 40 | 1 | 38.6, 1.7, 4.8 | 41.0, 2.1, 3.6 | 40.2, 1.5, -1.6 |
| Falling chimneys | 80 | 2 | 78.4, 2.1, 5.0 | 81.4, 2.4, 3.9 | 80.4, 2.0, -2.4 |
| Belfry / felt in Boston | 120 | 3 | 118.6, 2.0, 5.4 | 121.0, 2.4, 4.2 | 120.4, 2.3, -3.0 |
| River runs backward | 160 | 4 | 158.6, 1.9, 5.4 | 161.0, 2.3, 4.2 | 160.2, 1.7, -1.8 |
| Settlers flee | 200 | 5 | 198.6, 1.85, 4.9 | 201.6, 2.2, 3.7 | 200.4, 1.7, -2.4 |
| **Pivot:** land sinks | 240 | 6 | 237.8, 3.1, 7.6 | 240.4, 2.4, 6.3 | 240.3, 1.1, 1.0 |
| Reelfoot Lake fills | 280 | 7 | 278.6, 2.2, 6.0 | 281.2, 2.5, 5.4 | 280.4, 1.5, -1.6 |
| Depth gauge 5–18 ft | 320 | 8 | 318.6, 2.3, 4.6 | 321.8, 2.15, 2.8 | 320.6, 1.5, -2.0 |
| The lake today | 360 | 9 | 358.6, 2.1, 5.6 | 361.6, 2.45, 4.4 | 360.4, 1.7, -1.8 |

- One shot per sentence, one location per shot → **10 shots / 10 cuts boundaries** in `src/sentence_times.json`.
- Cuts: `0, 4.399, 8.798, 13.496, 17.895, 22.593, 27.29, 31.988, 36.387, 41.085, 45.186`.
- `#f4ebd9` dip-to-cream lasts 0.4 s (0.2 s in + 0.2 s out) over every cut boundary.
- Shot 7 is the only pull-down move: the camera descends **with** the sinking farm block so the
  pivot lands physically, not just verbally.

## Per-shot animation (driven by `u(t, shotIndex)` in `src/worlds.js`)

| Shot | Animation |
|------|-----------|
| 0 | Ripples drift +x (normal flow); keelboat bobs and rolls |
| 1 | Ground shake decays over the shot; sand blow grows and spins |
| 2 | Chimney eases over and topples 71° at 30–75 % of the shot |
| 3 | Bell swings, `sin(p·π)·sin(7.5t)` envelope so it rings then settles |
| 4 | Ripples run **−x (reverse)**, keelboat pitches harder, facade rattles |
| 5 | Crate hops away and a barrel rolls off down the boardwalk |
| 6 | Field + fence + barrel sink 1.5 units into the block; block shivers |
| 7 | Water level rises −0.45 → +0.05 as the lake fills |
| 8 | Water bobs, gauge tilts with the swell |
| 9 | Slow ripples, two cypress sway |

## Character rule (unchanged from house style)
`createCharacter` per location, ground/deck contact shadow at 0.28 opacity,
camera-facing yaw clamped to ±0.7 rad, only `coatColor` / `vestColor` / `hat` / `glasses` vary.
