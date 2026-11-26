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
  // Smooth glide camera interpolation based on shot
  return {
    pos: [0, 1.8 + t * 0.2, 4.2 - t * 0.5],
    target: [0, 1.2, 0],
    fov: 40
  };
}

export function dofAt(f) {
  return { focus: 3.5, blur: 0.015 };
}

export const LIGHTS = {
  day: { az: 45, el: 60, col: [1.0, 0.98, 0.9] },
  night: { az: 30, el: 25, col: [0.4, 0.6, 0.9] }
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
  // Return actor card positions and poses for the scene
  return [
    { id: 'archaeologist', x: 0, z: 0, outfit: 'hazmat', pose: 'reach', expr: 'squint', f }
  ];
}

export function fxAt(f, T) {
  return [];
}
