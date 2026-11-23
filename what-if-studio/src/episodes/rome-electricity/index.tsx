import React from 'react';
import { defineEpisode, Timeline, LookDef, HudChip } from '../../engine';
import timeline from './timeline.json';
import { S1, S2, S3, S4, S5, S6, S7, S8, S9, S10, S11, S12, S13, S14, S15, S16, S17, S18 } from './shots';

// The power's look: while the spark runs, a SPARK chip (icon 'dot') blinks on in the upper left.
const sparkLook: LookDef = {
  Overlay: ({ f }) => <HudChip f={f} label="SPARK" icon="dot" />,
};

export const romeElectricity = defineEpisode('RomeElectricity', {
  timeline: timeline as Timeline,
  shots: { S1, S2, S3, S4, S5, S6, S7, S8, S9, S10, S11, S12, S13, S14, S15, S16, S17, S18 },
  looks: { spark: sparkLook },
});