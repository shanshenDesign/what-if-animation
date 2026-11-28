import React, { useMemo } from 'react';
import {
  AbsoluteFill,
  Audio,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
} from 'remotion';
import { ThreeCanvas } from '@remotion/three';
import { useThree } from '@react-three/fiber';
import * as THREE from 'three';
import { buildStoryScene } from './worlds';
import sentenceTimes from './sentence_times.json';

// On-screen caption component – house style: lower-middle safe zone, ink-outline,
// cream fill, clean wrapping, zero clipping.
const OnScreenCaption = ({ text }) => {
  if (!text) return null;
  const visibleLines = text.split(' ').reduce((acc, word) => {
    const lastLine = acc[acc.length - 1];
    if (!lastLine || lastLine.join(' ').split(' ').length >= 12) {
      acc.push([word]);
    } else {
      lastLine.push(word);
    }
    return acc;
  }, []).slice(0, 3).map((words) => words.join(' '));

  return (
    <div
      style={{
        position: 'absolute',
        bottom: 60,
        left: '50%',
        transform: 'translateX(-50%)',
        color: '#351f22',
        fontFamily: 'Georgia, serif',
        fontSize: 18,
        fontWeight: 'bold',
        lineHeight: 1.3,
        textAlign: 'center',
        width: '90%',
        maxWidth: 560,
        padding: '6px 12px',
        background: 'rgba(244, 235, 217, 0.9)',
        border: '2px solid #351f22',
        borderRadius: 6,
        pointerEvents: 'none',
        zIndex: 50,
        textShadow: '0 2px 4px rgba(0,0,0,0.3)',
        whiteSpace: 'pre-wrap',
      }}
    >
      {visibleLines.join(' ')}
    </div>
  );
};

// Smooth camera travel curve between the cut timestamps of a shot (house style).
export function warpU(T, t) {
  const n = T.length;
  if (t <= T[0]) return 0;
  if (t >= T[n - 1]) return 1;
  const sec = [];
  for (let i = 0; i < n - 1; i++) sec.push((1 / (n - 1)) / (T[i + 1] - T[i]));
  const m = [0];
  for (let i = 1; i < n - 1; i++)
    m.push((2 * sec[i - 1] * sec[i]) / (sec[i - 1] + sec[i]));
  m.push(0);
  let i = 0;
  while (t > T[i + 1]) i++;
  const h = T[i + 1] - T[i],
    x = (t - T[i]) / h,
    x2 = x * x,
    x3 = x2 * x;
  return (
    (2 * x3 - 3 * x2 + 1) * (i / (n - 1)) +
    (x3 - 2 * x2 + x) * h * m[i] +
    (-2 * x3 + 3 * x2) * ((i + 1) / (n - 1)) +
    (x3 - x2) * h * m[i + 1]
  );
}

const CUTS = sentenceTimes.cuts || [0, 4.399, 8.798, 13.496, 17.895, 22.593, 27.29, 31.988, 36.387, 41.085, 45.186];

// The one camera in the scene: moved and aimed on every Remotion frame.
const CameraRig = ({ position, lookAt, fov = 80 }) => {
  const { camera } = useThree();
  camera.position.set(position[0], position[1], position[2]);
  camera.lookAt(lookAt[0], lookAt[1], lookAt[2]);
  if (camera.fov !== fov) {
    camera.fov = fov;
    camera.updateProjectionMatrix();
  }
  return null;
};

const SceneRunner = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  const { staticObjects, dynamicActors, characters, shots } = useMemo(
    () => buildStoryScene(),
    []
  );

  let shotIdx = 0;
  for (let i = 0; i < shots.length; i++) {
    const start = CUTS[i] ?? i * 4.5;
    const end = CUTS[i + 1] ?? start + 4.5;
    if (t >= start && (t < end || i === shots.length - 1)) {
      shotIdx = i;
      break;
    }
  }

  const activeShot = shots[shotIdx];
  const sStart = CUTS[shotIdx] ?? shotIdx * 4.5;
  const sEnd = CUTS[shotIdx + 1] ?? sStart + 4.5;
  const u = warpU([sStart, (sStart + sEnd) / 2, sEnd], t);

  const camX = THREE.MathUtils.lerp(activeShot.camStart[0], activeShot.camEnd[0], u);
  const camY = THREE.MathUtils.lerp(activeShot.camStart[1], activeShot.camEnd[1], u);
  const camZ = THREE.MathUtils.lerp(activeShot.camStart[2], activeShot.camEnd[2], u);

  const camPos = new THREE.Vector3(camX, camY, camZ);
  characters.forEach((c) => c.userData.update(frame, camPos));
  dynamicActors.forEach((a) => a.update(t, frame));

  // Determine the current sentence text for on-screen captions
  let captionText = null;
  for (const sent of sentenceTimes.sentences) {
    if (t >= sent.start && t < sent.end) {
      captionText = sent.text;
      break;
    }
  }

  return (
    <>
      <color attach="background" args={['#e9decb']} />
      <fog attach="fog" args={['#e9decb', 9, 25]} />

      <directionalLight
        position={[camX - 7, 14, 9]}
        intensity={1.85}
        color="#fff2dc"
        castShadow
      />
      <hemisphereLight args={['#fff7e8', '#7d6855', 0.85]} />

      <mesh position={[200, 0, 0]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[600, 120]} />
        <meshToonMaterial color="#6e5641" />
      </mesh>

      {staticObjects.map((obj, idx) => (
        <primitive key={`s-${idx}`} object={obj} />
      ))}
      {dynamicActors.map((actor, idx) => (
        <primitive key={`d-${idx}`} object={actor.mesh} />
      ))}
      {characters.map((char, idx) => (
        <primitive key={`c-${idx}`} object={char} />
      ))}

      <CameraRig
        position={[camX, camY, camZ]}
        lookAt={activeShot.lookAt}
        fov={80}
      />

</>
  );
};

export const Full = () => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const t = frame / fps;

  let creamOpacity = 0;
  for (const cut of CUTS.slice(1)) {
    const dist = Math.abs(t - cut);
    if (dist < 0.2) {
      creamOpacity = Math.max(creamOpacity, interpolate(dist, [0, 0.2], [1, 0]));
    }
  }

  // Determine the current sentence text for on-screen captions
  let captionText = null;
  for (const sent of sentenceTimes.sentences) {
    if (t >= sent.start && t < sent.end) {
      captionText = sent.text;
      break;
    }
  }

  return (
    <AbsoluteFill>
      <ThreeCanvas
        width={width}
        height={height}
        shadows
        camera={{ fov: 80, near: 0.1, far: 100, position: [-1.4, 1.95, 5.2] }}
      >
        <SceneRunner />
      </ThreeCanvas>
      {sentenceTimes.hasAudio ? (
        <Audio src={staticFile('voiceover.wav')} />
      ) : null}
      <AbsoluteFill
        style={{
          backgroundColor: '#f4ebd9',
          opacity: creamOpacity,
          pointerEvents: 'none',
        }}
      />
      {/* On-screen caption synced to narration beats */}
      <OnScreenCaption text={captionText} />
    </AbsoluteFill>
  );
};
