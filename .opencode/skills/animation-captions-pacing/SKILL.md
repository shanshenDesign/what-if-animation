---
name: animation-captions-pacing
description: Subtitle timing, safe zone and transition rules for Remotion videos. Caption timing and placement rules plus scene transition patterns.
---

# Subtitle timing, safe zones and transitions

## Subtitle timing

Captions are data — process them in JSON using the `Caption` type:

```ts
import type { Caption } from "@remotion/captions";

type Caption = {
  text: string;
  startMs: number;
  endMs: number;
  timestampMs: number | null;
  confidence: number | null;
  pageBreakAfter?: boolean;
};
```

Rules:
- Caption text is whitespace sensitive — include the space before each word in `text`.
- Put the video and its captions in the same `<Sequence>` or `<TransitionSeries.Sequence>`; put `trimBefore`, `durationInFrames` and `playbackRate` on the shared parent so trimming or changing speed affects both.
- Put independently positioned clips on the shared `<Sequence>` too.
- `durationInFrames` selects a range of source frames; the group occupies `durationInFrames / playbackRate` frames in the parent timeline.
- Update the composition duration when changing the total timeline length.
- If a caption has `pageBreakAfter: true`, the current page ends after that caption and the next caption starts a new page.

## Safe zones

- Give the caption area a width and position it over the video, keeping the text inside the central safe zone.
- Example: in a 1920px-wide composition, the 900px caption area is centered by translating it `(1920 - 900) / 2 = 510` pixels from the left:

```tsx
<BasicCaptions
  width={900}
  style={{
    position: "absolute",
    bottom: 120,
    translate: "510px 0px",
  }}
  captions={[
    {
      text: "Hello",
      startMs: 5000,
      endMs: 5400,
      timestampMs: 5200,
      confidence: null,
    },
    {
      text: " world",
      startMs: 5400,
      endMs: 5900,
      timestampMs: 5650,
      confidence: null,
    },
  ]}
/>
```

## Transitions

Use `<TransitionSeries>` with `<TransitionSeries.Transition>` between scenes and `<TransitionSeries.Overlay>` for effects that don't shorten the timeline.

- Keep the outer `<TransitionSeries>` visible in the timeline.
- Children are absolutely positioned.
- Transitions overlap adjacent scenes, so the total duration is shorter than the sum of sequence durations (`durations − transition durations`). Overlays do not affect the total duration.
- A transition needs `presentation` (e.g. `fade()`, `slide()`, `wipe()`, `flip()`, `clockWipe()`) and `timing` (e.g. `linearTiming({durationInFrames: 15})` or `springTiming({config: {damping: 200}, durationInFrames: 25})`).
- `<TransitionSeries.Overlay>` accepts `durationInFrames` and an optional `offset` that shifts the overlay relative to the cut point center.
