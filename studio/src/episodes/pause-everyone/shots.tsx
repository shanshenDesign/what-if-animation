import React from 'react';
import {
  Hero, Pose, basePose, poseAt, kf, clamp, lerp, camT, LOOKS, LEG_LEN,
  walkPose, hipGround, stand, joints, toWorld, reachAngle,
  Stairwell, Banister, Kitchen, KITCHEN, Cookie, Plate, Rooftop, TitleCard,
} from '../../engine';
import { ShotProps } from '../../engine';

// "What if you could pause everyone but you?" Thirteen shots on three sets (stairwell, kitchen, rooftop).
// The power: a red PAUSE chip (in the power look) shows while it runs; the press flash (episode.json)
// lands on the first "Pause"; mum's freeze: a pulsing red ring around her (S12).
// Each shot is a pure function of its own clock t, so the engine can play it back or hold it.

const PIP = LOOKS.pipHood;
const MO = LOOKS.mo;
const MUM = LOOKS.mom;
const SC = 0.9;
const RED = '#FF3344';

const walkP = (x: number, phase: number, extra: Partial<Pose> = {}): Pose => walkPose(x, phase, hipGround, SC, extra);

// ---------- S1: wide, the stairs: Pip walks down; Mo ahead, about to wave ----------
export const S1: React.FC<ShotProps> = ({ t, len }) => {
  const x = lerp(300, 540, t / len);
  const pose = walkP(x, t * 0.6);
  const mo = poseAt(t, [{ f: 0, p: { x: 620, y: hipGround(620) - LEG_LEN * SC, scale: SC, yaw: 0.3, look: 0.6, armR: { a: 148, b: 10 }, expr: 'happy' } }]);
  return (
    <g transform={camT(540, 450, 1.0)}>
      <Stairwell t={t} id="p1" />
      <Hero look={PIP} pose={pose} rimId="rimR" shadow={0.5} />
      <Hero look={MO} pose={mo} rimId="rimR" shadow={0.5} />
      <Banister />
    </g>
  );
};

// ---------- S2: medium: Mo frozen mid-wave, arm up, smile stuck ----------
export const S2: React.FC<ShotProps> = ({ t }) => {
  const mo = poseAt(t, [{ f: 0, p: { x: 620, y: hipGround(620) - LEG_LEN * SC, scale: SC, yaw: 0.3, look: 0.6, armR: { a: 150, b: 12 }, expr: 'happy' } }]);
  return (
    <g transform={camT(540, 450, 1.0)}>
      <Stairwell t={t} id="p2" />
      <Hero look={MO} pose={mo} rimId="rimR" shadow={0.5} />
      <Banister />
    </g>
  );
};

// ---------- S3: medium: Pip slips past the frozen Mo ----------
export const S3: React.FC<ShotProps> = ({ t, len }) => {
  const x = lerp(520, 640, t / len);
  const pose = walkP(x, t * 0.6);
  const mo = poseAt(t, [{ f: 0, p: { x: 620, y: hipGround(620) - LEG_LEN * SC, scale: SC, yaw: 0.3, armR: { a: 150, b: 12 }, expr: 'happy' } }]);
  return (
    <g transform={camT(560, 450, 1.0)}>
      <Stairwell t={t} id="p3" />
      <Hero look={PIP} pose={pose} rimId="rimR" shadow={0.5} />
      <Hero look={MO} pose={mo} rimId="rimR" shadow={0.5} />
      <Banister />
    </g>
  );
};

// ---------- S4: wide, the kitchen: mum passing the counter, reaching for a cookie ----------
const mumSt = stand(KITCHEN, 0.28, 0.5);
export const S4: React.FC<ShotProps> = ({ t }) => {
  const mum = poseAt(t, [{ f: 0, p: { ...mumSt, yaw: 0.2, armR: { a: 50, b: -12 }, expr: 'neutral' } }]);
  return (
    <g transform={camT(960, 560, 1.1)}>
      <Kitchen t={t} id="p4" />
      <Hero look={MUM} pose={mum} rimId="rimR" shadow={0.4} />
    </g>
  );
};

// ---------- S5: close-up, the kitchen: mum frozen mid-step; Pip grabs the cookie off the plate ----------
const mumSt5: Pose = { ...basePose, ...stand(KITCHEN, 0.3, 0.5), armR: { a: 92, b: -6 } };
const pipSt5: Pose = { ...basePose, ...stand(KITCHEN, 0.38, 0.45) };
export const S5: React.FC<ShotProps> = ({ t }) => {
  const mum = poseAt(t, [{ f: 0, p: { ...mumSt5, yaw: 0.2 } }]);
  const hand = toWorld(mum, joints(mum).armR.end);
  const pip = poseAt(t, [{ f: 0, p: { ...pipSt5, armR: { a: reachAngle(pipSt5, { x: hand.x + 8, y: hand.y + 4 }), b: 0 }, handR: 'point' } }]);
  return (
    <g transform={camT(960, 525, 2.4)}>
      <Kitchen t={t} id="p5" veil={0.3} />
      <Hero look={MUM} pose={mum} rimId="rimR" shadow={0.4} />
      <Hero look={PIP} pose={pip} rimId="rimR" shadow={0} />
      <Plate x={hand.x + 20} y={hand.y + 34} s={1.0} />
      <Cookie x={hand.x + 26} y={hand.y + 26} s={0.9} rot={12} />
    </g>
  );
};

// ---------- S6: medium, the kitchen: Pip eats the cookie, alone ----------
export const S6: React.FC<ShotProps> = ({ t }) => {
  const pip = poseAt(t, [{ f: 0, p: { ...stand(KITCHEN, 0.35, 0.5), yaw: 0.2, armR: { a: 40, b: -6 } } }]);
  const h = toWorld(pip, joints(pip).armR.end);
  return (
    <g transform={camT(960, 590, 1.2)}>
      <Kitchen t={t} id="p6" />
      <Hero look={PIP} pose={pip} rimId="rimR" shadow={0.4} />
      <Cookie x={h.x + 6} y={h.y + 30} s={1.0} rot={14} />
    </g>
  );
};

// ---------- S7: wide, the stairs: Pip's friend (Mo) stepping onto the stairs ----------
export const S7: React.FC<ShotProps> = ({ t, len }) => {
  const mo = walkPose(lerp(430, 590, t / len), t * 0.6, hipGround, SC);
  const pip = walkP(lerp(520, 570, t / len), t * 0.6);
  return (
    <g transform={camT(540, 450, 1.0)}>
      <Stairwell t={t} id="p7" />
      <Hero look={MO} pose={mo} rimId="rimR" shadow={0.5} />
      <Hero look={PIP} pose={pip} rimId="rimR" shadow={0.5} />
      <Banister />
    </g>
  );
};

// ---------- S8: close-up, the stairs: the friend frozen mid-step; Pip's hand reaching toward him ----------
const moSt8: Pose = { ...basePose, x: 620, y: hipGround(620) - LEG_LEN * SC, scale: SC, armL: { a: 40, b: 10 }, armR: { a: 20, b: -8 } };
export const S8: React.FC<ShotProps> = ({ t, len }) => {
  const aim = reachAngle(walkP(lerp(540, 570, t / len), 0), moSt8);
  const mo = poseAt(t, [{ f: 0, p: moSt8 }]);
  return (
    <g transform={camT(700, 430, 3.0)}>
      <Stairwell t={t} id="p8" />
      <Hero look={MO} pose={mo} rimId="rimR" shadow={0.5} />
      <Hero look={PIP} pose={walkP(lerp(540, 570, t / len), 0, { armR: { a: aim, b: 0 }, handR: 'point' })} rimId="rimR" shadow={0.5} />
      <Banister />
    </g>
  );
};

// ---------- S9: wide, the roof at dusk: the title over the city ----------
export const S9: React.FC<ShotProps> = ({ t }) => {
  const pose = poseAt(t, [{ f: 0, p: { x: 900, y: 818 - LEG_LEN * 0.7, scale: 0.7, yaw: 0.3, armL: { a: 20, b: 6 }, armR: { a: 20, b: 6 } } }]);
  return (
    <g transform={camT(960, 520, 1.05)}>
      <Rooftop t={t} />
      <Hero look={PIP} pose={pose} rimId="rimR" shadow={0.6} />
      <TitleCard t={t} lines={['WHAT IF YOU COULD', 'PAUSE EVERYONE BUT YOU?']} accent="YOU?" accentT={42} size={88} y={170} />
    </g>
  );
};

// ---------- S10: medium, the roof, low angle: Pip amazed ----------
export const S10: React.FC<ShotProps> = ({ t }) => {
  const pose = poseAt(t, [{ f: 0, p: { x: 900, y: 818 - LEG_LEN * 0.7, scale: 1.5, yaw: 0.2, armR: { a: 30, b: 8 }, expr: 'shock' } }]);
  return (
    <g transform={camT(960, 500, kf(t, [[0, 1.0], [30, 1.05]]))}>
      <Rooftop t={t} />
      <Hero look={PIP} pose={pose} rimId="rimR" shadow={0.4} />
    </g>
  );
};

// ---------- S11: medium, the kitchen: Pip presses Pause on mum ----------
const mumSt11: Pose = { ...basePose, ...stand(KITCHEN, 0.3, 0.5) };
export const S11: React.FC<ShotProps> = ({ t }) => {
  const mum = poseAt(t, [{ f: 0, p: { ...mumSt11, yaw: 0.2, armR: { a: 52, b: -12 } } }]);
  const reach = reachAngle({ ...basePose, ...stand(KITCHEN, 0.36, 0.45) }, mumSt11);
  const pip = poseAt(t, [{ f: 0, p: { ...stand(KITCHEN, 0.36, 0.45), armR: { a: reach, b: 0 }, handR: 'point' } }]);
  return (
    <g transform={camT(960, 560, kf(t, [[0, 1.1], [126, 1.15]]))}>
      <Kitchen t={t} id="p11" />
      <Hero look={MUM} pose={mum} rimId="rimR" shadow={0.4} />
      <Hero look={PIP} pose={pip} rimId="rimR" shadow={0.4} />
    </g>
  );
};

// ---------- S12: close-up, the kitchen: mum fully frozen with the red pulse; Pip holds the cookie ----------
export const S12: React.FC<ShotProps> = ({ t }) => {
  const mum = poseAt(t, [{ f: 0, p: { ...mumSt5, yaw: 0.2 } }]);
  const h = toWorld(mum, joints(mum).armR.end);
  const pip = poseAt(t, [{ f: 0, p: { ...pipSt5, armR: { a: reachAngle(pipSt5, { x: h.x + 10, y: h.y + 12 }), b: 0 }, handR: 'point' } }]);
  const pulse = 0.45 + 0.45 * Math.sin(t * 2.4);
  return (
    <g transform={camT(960, 525, 2.4)}>
      <Kitchen t={t} id="p12" veil={0.3} />
      <Hero look={MUM} pose={mum} rimId="rimR" shadow={0.4} />
      <Hero look={PIP} pose={pip} rimId="rimR" shadow={0} />
      <Plate x={h.x + 18} y={h.y + 34} s={1.0} />
      <Cookie x={h.x + 24} y={h.y + 26} s={0.9} rot={12} />
      <circle cx={mumSt5.x} cy={mumSt5.y} r={150} fill={RED} opacity={pulse * 0.28} style={{ mixBlendMode: 'screen' }} />
    </g>
  );
};

// ---------- S13: medium, the kitchen: Pip walks away with the cookie; mum stays frozen ----------
export const S13: React.FC<ShotProps> = ({ t, len }) => {
  const x = lerp(mumSt5.x + 70, mumSt5.x + 150, t / len);
  const pip = walkP(x, t * 0.6);
  const mum = poseAt(t, [{ f: 0, p: { ...mumSt5, yaw: 0.2 } }]);
  const h = toWorld(pip, joints(pip).armR.end);
  return (
    <g transform={camT(kf(t, [[0, 880], [len, 840]]), 590, 1.15)}>
      <Kitchen t={t} id="p13" />
      <Hero look={MUM} pose={mum} rimId="rimR" shadow={0.4} />
      <Hero look={PIP} pose={pip} rimId="rimR" shadow={0.4} />
      <Cookie x={h.x + 6} y={h.y + 30} s={1.0} rot={14} />
    </g>
  );
};
