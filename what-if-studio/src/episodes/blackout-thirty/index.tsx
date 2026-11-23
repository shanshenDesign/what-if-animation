import React from 'react';
import { defineEpisode, Timeline, LookDef } from '../../engine';
import timeline from './timeline.json';
import { Sh1, Sh2, Sh3, Sh4, Sh5, Sh6, Sh7, Sh8 } from './shots';

export const blackoutThirty = defineEpisode('BlackoutThirty', {
  timeline: timeline as Timeline,
  shots: { Sh1, Sh2, Sh3, Sh4, Sh5, Sh6, Sh7, Sh8 },
  looks: {},
});