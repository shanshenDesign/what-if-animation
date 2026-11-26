# Kids-Toon 3D Style Guide

An opt-in style (`kids-toon-3d`) for children's educational vertical videos (1080x1920) featuring friendly stick-toons, tactile textured backgrounds, layered 2.5D depth, soft cel shading, and bold captions.

## Look & Feel
- **Resolution**: 1080x1920 vertical format.
- **Palette**:
  - Cream: `#FFF8E7`
  - Sky: `#7AD7F0`
  - Outline: `#2B1E16` (thick warm brown)
  - Yellow: `#FFD166`
  - Coral: `#FF6B6B`
  - Mint: `#06D6A0`
  - Blush: `#FF8FA3`
  - Red: `#D93A2B`
  - Green: `#24533F`
  - Mustard: `#E5A128`
  - Sand: `#C99A55`
- **Characters**: Large off-white heads, bean-shaped bodies, thin dark limbs, mitten hands, rounded shoes, thick warm-brown outlines. Soft cel shading, rim light, contact shadows.
- **Scene Layers**: Sky layer, distance layer (clouds/horizon), main train/object layer, ground layer with texture/perspective, character layer, foreground props/foliage layer, speech bubbles, and thick-bordered captions.

## Character Rig
- Separate parts: head, eyes, eyelids, brows, mouth, hair, body, limbs, hands, shoes, accessories (hats, jackets, scarves, glasses).
- Correct pivot points and drawing order.
- Expressions: happy, shocked, laugh, curious.
- Poses: idle, point, wave, walk, think.

## Rules & Integration
- Loaded via skill options or configuration (`style: "kids-toon-3d"`).
- Uses code-drawn SVG layers with 2.5D parallax.
- Captions: 1-4 words, large bold white text with thick dark outline inside the safe area (x 60-900, y 250-1470).
