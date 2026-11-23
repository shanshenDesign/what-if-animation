import React from 'react';
import { defineEpisode, Timeline } from '../../engine';
import timeline from './timeline.json';
import * as shots from './shots';

export const romeElectricity = defineEpisode('RomeElectricity', {
  timeline: timeline as Timeline,
  shots: shots as Record<string, React.FC<any>>,
});
