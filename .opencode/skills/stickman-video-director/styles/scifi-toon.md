---
name: scifi-toon
description: Sci-Fi Sitcom Toon style preset (Adult-animation sci-fi sitcom: thick boiling outlines, flat colour, a duo whose reactions don't match, a glowing portal, and one palette per world).
---

# Sci-Fi Sitcom Toon Style Preset

This reusable style preset implements the **Sci-Fi Sitcom Toon** aesthetic from `shanshenDesign/lemo-opuscar` for stickman and animated short video projects.

## 1. Exact Hex Color Palette & Project Constants

Each world or sequence features a distinct 4-5 color palette (maximally different in hue and value from preceding worlds). Below is the standard master palette mapped to project constants (`BG`, `PRIMARY`, `ACCENT`, `OUTLINE`, `CAPTION`):

```typescript
export const SCIFI_TOON_PALETTE = {
  // Master dark purple-black outline used across all worlds
  OUTLINE: "#1A1528",
  
  // Subtitle styling
  CAPTION_BG: "#1A1528",
  CAPTION_TEXT: "#FFFFFF",
  
  // World 1: Sage Lab (Default Laboratory / Starting World)
  WORLD_1: {
    BG: "#E2ECD0",         // Pale sage green background
    PRIMARY: "#3C5A32",     // Deep olive/sage green for character outfits & props
    ACCENT: "#00E5FF",      // Neon cyan glow for portals & futuristic HUD elements
    SECONDARY: "#F4F9EE",   // Light highlights
  },

  // World 2: Magenta & Lime Jelly Dimension
  WORLD_2: {
    BG: "#FFE5FF",         // Light pinkish/magenta wash
    PRIMARY: "#9C1A6E",     // Deep magenta
    ACCENT: "#76FF03",      // Neon lime green glow
    SECONDARY: "#FFF0FF",
  },

  // World 3: Orange & Teal Wasteland
  WORLD_3: {
    BG: "#FFE0B2",         // Warm desert orange/tan
    PRIMARY: "#D84315",     // Burnt orange
    ACCENT: "#00B0FF",      // Neon bright blue glow
    SECONDARY: "#FFF3E0",
  },

  // World 4: Retro Monolith / Boring Office
  WORLD_4: {
    BG: "#CFD8DC",         // Muted steel grey
    PRIMARY: "#37474F",     // Dark slate
    ACCENT: "#FFEA00",      // Warning yellow glow
    SECONDARY: "#ECEFF1",
  }
};
```

## 2. Python Drawing Helper Patterns (`src/scenes.py` / Remotion Engine)

When building Python drawing routines or Remotion SVG scenes for `scifi-toon`, follow these precise grammar rules:

### A. Thick Toon Outlines & Boil
- **Line Weight**: Uniform ~7 px for characters and foreground props, 4–6 px for background details with rounded joins (`stroke-linecap="round" stroke-linejoin="round"`).
- **Line Boil**: Resample outlines in screen space with low-frequency noise (amplitude ~1.7 px), cycling 3 distinct boil drawings at 12 fps. Everything boils (characters, props, and background lines) so a still frame is never dead.
- **Flat Fills & Hard Shadows**: No gradients on fills! Shadows are hard-edged darker polygons clipped inside the fill shape, positioned opposite the light source.

### B. Sci-Fi HUD Panels & Retro Terminals
- **Monospace Terminal Text**: Use retro terminal typography (`VT323` or monospace fonts) rendered in the world's accent colour.
- **HUD Elements**: Thick boxed frames with notched corners, blinking warning lights (stepped opacity at 12 fps), and oscillating waveform lines (`<path d="M... L..." fill="none" stroke={ACCENT} stroke-width="4" />`).

### C. Glowing Accents & Portals
- **Exclusive Glow**: Only portals, energy devices, and laser/plasma cores emit glowing accents (`ACCENT`). Nothing else in the scene uses the portal glow color.
- **Portal Rendering**: A lumpy, hand-drawn organic rim with a thick outline, rotating multi-arm spiral inside, pale glowing core, orbiting sparks/drips, and a flat translucent wash over the scene. Opens with a gentle back-ease overshoot (~12%).

### D. Preserving the Stickman Rig
- **Bold & Recognizable**: Maintain simple, high-contrast stick figure proportions (solid black/primary silhouettes that read instantly) enhanced with signature oversized white eyes, tiny pupils (4-5 px), heavy deadpan lids, and parametric elastic mouths.

---
