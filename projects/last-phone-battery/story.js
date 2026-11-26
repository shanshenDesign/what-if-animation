// Story definition for "The Last Phone Battery on Earth"
// Compatible with cartoon-short-kit engine

export const SHOTS = [
  { f0: 0, f1: 100, words: "In the year 3000, archaeologists uncovered a functional smartphone with one percent battery remaining." },
  { f0: 101, f1: 250, words: "Deep inside the radioactive ruins of a forgotten metropolis, a hazmat-suited team brushed away centuries of dust." },
  { f0: 251, f1: 450, words: "They pressed the power button, holding their breath as the cracked OLED screen flickered back to life." },
  { f0: 451, f1: 600, words: "But as the lead scientist reached out to tap the screen, a notification popped up." },
  { f0: 601, f1: 750, words: "Unlocking it triggered an ancient automated firmware update that instantly rebooted the planetary core." }
];

export function shotAt(f) {
  for (const s of SHOTS) {
    if (f >= s.f0 && f <= s.f1) return s;
  }
  return SHOTS[SHOTS.length - 1];
}

export function camAt(f) {
  const s = shotAt(f);
  const t = Math.max(0, Math.min(1, (f - s.f0) / (s.f1 - s.f0 || 1)));
  // Dynamic camera movement per shot
  if (s.f0 === 0) {
    return { pos: [0, 1.5, 3.5 - t * 0.5], target: [0, 1.0, 0], fov: 38 };
  } else if (s.f0 === 101) {
    return { pos: [-1.5 + t * 0.5, 2.2, 4.0 - t * 1.0], target: [0, 1.2, 0], fov: 42 };
  } else if (s.f0 === 251) {
    return { pos: [0, 1.2 + t * 0.3, 2.5 - t * 0.4], target: [0, 1.0, 0], fov: 35 };
  } else if (s.f0 === 451) {
    return { pos: [0.5 - t * 0.5, 1.4, 2.2 - t * 0.6], target: [0, 1.1, 0], fov: 32 };
  } else {
    return { pos: [0, 1.6 + t * 0.8, 3.0 + t * 2.0], target: [0, 1.2, 0], fov: 45 };
  }
}

export function dofAt(f) {
  return { focus: 3.0, blur: 0.015 };
}

export const LIGHTS = {
  day: { az: 45, el: 60, col: [1.0, 0.98, 0.9] },
  night: { az: 30, el: 25, col: [0.35, 0.55, 0.85] }
};

export function lightFor(f) {
  return f < 250 ? LIGHTS.night : LIGHTS.day;
}

export function worldAt(f) {
  return {
    ruinCollapse: Math.min(1, f / 300),
    screenGlow: f > 250 ? 1 : 0
  };
}

export function actorsAt(f, T) {
  // Return actor card positions and poses for both the archaeologist and robot sentinel across beats
  const isReboot = f >= 601;
  const robotPose = isReboot ? 'sleep' : (f > 250 ? 'amazed' : 'guard');
  const robotExpr = isReboot ? 'loading' : 'shock';
  
  return [
    { id: 'archaeologist', x: -0.4, z: 0.2, outfit: 'hazmat', pose: f > 450 ? 'reach' : 'inspect', expr: f > 450 ? 'gasp' : 'squint', f },
    { id: 'sentinel', x: 1.2, z: -0.5, outfit: 'robot', pose: robotPose, expr: robotExpr, f }
  ];
}

export function fxAt(f, T) {
  if (f >= 601 && f <= 610) {
    return [{ type: 'flash', intensity: 1.0 - (f - 601) / 9 }];
  }
  return [];
}
