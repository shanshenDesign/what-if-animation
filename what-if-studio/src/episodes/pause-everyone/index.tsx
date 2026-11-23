import React from 'react';
import { defineEpisode, Timeline, LookDef, HudChip } from '../../engine';
import timeline from './timeline.json';
import { S1, S2, S3, S4, S5, S6, S7, S8, S9, S10, S11, S12, S13 } from './shots';

// The power's look: while the power runs, a PAUSE chip (icon 'pause') blinks on in the upper left.
const pauseLook: LookDef = {
  Overlay: ({ f }) => <HudChip f={f} label="PAUSE" icon="pause" />,
};

export const pauseEveryone = defineEpisode('PauseEveryone', {
  timeline: timeline as Timeline,
  shots: { S1, S2, S3, S4, S5, S6, S7, S8, S9, S10, S11, S12, S13 },
  looks: { pause: pauseLook },
});
