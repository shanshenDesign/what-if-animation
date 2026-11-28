import React from 'react';
import { Composition } from 'remotion';
import { Full } from './Full';
import sentenceTimes from './sentence_times.json';

export const RemotionRoot = () => {
  const fps = 30;
  const lastEnd = sentenceTimes.sentences?.length
    ? sentenceTimes.sentences[sentenceTimes.sentences.length - 1].end
    : 45;
  const durationInFrames = Math.max(90, Math.ceil((lastEnd + 0.8) * fps));

  return (
    <Composition
      id="AnimatedStory"
      component={Full}
      durationInFrames={durationInFrames}
      fps={fps}
      width={720}
      height={1280}
    />
  );
};
