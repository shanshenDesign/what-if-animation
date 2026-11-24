// HEAVY SHADOWS: 50 KG : the shot list (Stick Story, heavy-shadows-35s).
// One picture per clause. A shot: { id, at, cam: [cx, cy], zoom, note, draw(lt, d, t) }. cut(i) = just before line i,
// Wd('word', i) = when the word is said. Sound: cue(t, type, { gain, dur }).
// Set: one street, all video (noon sun overhead -> low 4 PM sun -> cloud). The shadow is the antagonist.
import { ctx, W, H, TAU, clamp, lerp, seg, eo, eio, eob, rnd, rr, circle, ell, line } from './core/lib.js';
import { L, Le, Wd, T } from './core/timing.js';
import * as K from './core/kit.js';
const { P, GROUND, FLOOR } = K;

// ── the street set (flat, same all video) ──────────────────────────────────────
export function street(o = {}) {
  ctx.fillStyle = P.sky; ctx.fillRect(-300, -300, W + 600, FLOOR + 300);
  if (o.sun) o.sun();                                   // the sun goes BEHIND the skyline
  const bl = [[-50, 700, 340, 650, '#E6DAC5'], [290, 840, 300, 510, '#DCCDB4'], [590, 640, 310, 710, '#E9DECB'], [890, 880, 300, 470, '#D9C9AF']];
  for (const [x, y, w, h, c] of bl) {
    ctx.fillStyle = c; ctx.fillRect(x, y, w, h);
    ctx.strokeStyle = 'rgba(28,28,34,0.30)'; ctx.lineWidth = 6; ctx.strokeRect(x, y, w, h);
    for (let r = 0; r < 3; r++) for (let k = 0; k < 3; k++) {
      const cw = (w - 70) / 3, ch = (h - 90) / 3;
      rr(x + 35 + k * cw, y + 45 + r * ch, cw - 30, ch - 34, 6); ctx.fillStyle = '#9EC2D8'; ctx.fill();
    }
  }
  ctx.fillStyle = '#DBD3C3'; ctx.fillRect(-300, FLOOR, W + 600, 430);            // sidewalk
  ctx.strokeStyle = '#C4BAA7'; ctx.lineWidth = 6;
  for (let y = FLOOR + 130; y < FLOOR + 430; y += 140) { ctx.beginPath(); ctx.moveTo(-300, y); ctx.lineTo(W + 300, y); ctx.stroke(); }
  for (let x = -120; x < W + 300; x += 250) { ctx.beginPath(); ctx.moveTo(x, FLOOR); ctx.lineTo(x, FLOOR + 430); ctx.stroke(); }
  ctx.fillStyle = '#C7BCA8'; ctx.fillRect(-300, FLOOR + 430, W + 600, 34);       // curb
  ctx.fillStyle = '#6E6A72'; ctx.fillRect(-300, FLOOR + 464, W + 600, H + 300);  // road
  ctx.fillStyle = '#E8E2D2';
  for (let x = -60; x < W + 300; x += 260) ctx.fillRect(x, 1846, 150, 16);
}
/** a dark doorway (the "dark room" alternative) */
export function darkDoor(x, y) {
  rr(x - 150, y - 560, 300, 560, [16, 16, 0, 0]); ctx.fillStyle = '#12141C'; ctx.fill();
  rr(x - 166, y - 586, 332, 600, [18, 18, 0, 0]); ctx.fillStyle = '#7A5236'; ctx.fill();
  rr(x - 142, y - 556, 284, 556, [12, 12, 0, 0]); ctx.fillStyle = '#12141C'; ctx.fill();
  rr(x + 40, y - 540, 88, 540, [10, 10, 0, 0]); ctx.fillStyle = '#A8754E'; ctx.fill();
  circle(x + 66, y - 280, 13, P.gold);
}
/** the sun: rays rotate slowly, pulse on the beat */
export function sunDisc(x, y, r, o = {}) {
  const warm = !!o.warm, a = o.a ?? 1;
  ctx.save(); ctx.globalAlpha = a; ctx.translate(x, y);
  const core = warm ? P.gold : '#FFD43B', ray = warm ? '#F2B23E' : '#FFE07A';
  for (let i = 0; i < 12; i++) {
    ctx.save(); ctx.rotate((o.rot || 0) + i * TAU / 12);
    const r0 = r * 1.34 + (o.pulse || 0) * 16;
    line([[0, r0], [0, r0 + r * 0.55]], ray, Math.max(7, r * 0.17));
    ctx.restore();
  }
  circle(0, 0, r, core); circle(0, 0, r * 0.76, warm ? '#FFD27A' : '#FFECA8');
  ctx.restore();
}
function cloud(x, y, s = 1, a = 1) {
  if (a <= 0.01) return;
  ctx.save(); ctx.globalAlpha = a; ctx.translate(x, y); ctx.scale(s, s);
  circle(-86, 8, 58, '#E9E6EE'); circle(-6, -30, 82, '#E9E6EE'); circle(84, 10, 56, '#E9E6EE');
  rr(-146, 6, 250, 62, 31); ctx.fillStyle = '#E9E6EE'; ctx.fill();
  ctx.fillStyle = '#CFCBD9'; ctx.beginPath(); ctx.ellipse(-10, 52, 120, 26, 0, 0, TAU); ctx.fill();
  ctx.restore();
}
/** the shadow the hero casts: a long dark bar + the head blob at the far end */
export function castShadow(x, y, len, dir, a = 1) {
  if (a <= 0.01 || len < 10) return;
  const far = x + dir * len;
  ctx.save(); ctx.globalAlpha = a; ctx.fillStyle = 'rgba(24,24,30,0.55)';
  ctx.beginPath();
  ctx.moveTo(x, y - 36); ctx.lineTo(far, y - 26); ctx.lineTo(far, y + 28); ctx.lineTo(x, y + 36);
  ctx.closePath(); ctx.fill();
  ctx.beginPath(); ctx.ellipse(far + dir * 16, y + 2, 58, 42, 0, 0, TAU); ctx.fill();
  ctx.beginPath(); ctx.ellipse(x + dir * 40, y + 2, 74, 46, 0, 0, TAU); ctx.fill();
  ctx.restore();
}
/** a small shadow sitting straight beneath the shoes (noon) */
export function blobShadow(x, y, rx, a = 1) {
  if (a <= 0.01) return;
  ctx.save(); ctx.globalAlpha = a; ell(x, y, rx, rx * 0.3, 'rgba(24,24,30,0.55)');
  ell(x, y + 6, rx * 0.62, rx * 0.2, 'rgba(24,24,30,0.5)'); ctx.restore();
}
function ankleCuffs(x, y, s = 1, a = 1) {
  if (a <= 0.01) return;
  ctx.save(); ctx.globalAlpha = a; ctx.translate(x, y); ctx.scale(s, s);
  for (const dx of [-40, 40]) { rr(dx - 44, -34, 88, 62, 24); ctx.fillStyle = P.ink; ctx.fill(); rr(dx - 28, -20, 56, 34, 14); ctx.fillStyle = P.gold; ctx.fill(); }
  ctx.restore();
}
export function umbrella(x, y, s = 1, open = 1, color = P.red) {
  if (open <= 0.03) return;
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  line([[0, 14], [0, -296]], P.ink, 13);
  const w = 214 * open;
  ctx.beginPath(); ctx.moveTo(-w, -296); ctx.quadraticCurveTo(0, -296 - 196 * open, w, -296);
  for (let i = 0; i < 4; i++) { const a = w - 2 * w * (i / 4), b = w - 2 * w * ((i + 1) / 4); ctx.quadraticCurveTo((a + b) / 2, -296 + 48 * open, b, -296); }
  ctx.closePath(); ctx.fillStyle = color; ctx.fill(); ctx.strokeStyle = P.ink; ctx.lineWidth = 9; ctx.stroke();
  for (let i = 1; i < 4; i++) line([[0, -296 - 168 * open], [w - 2 * w * (i / 4), -296]], 'rgba(28,28,34,0.45)', 6);
  circle(0, -296 - 190 * open, 13, P.ink);
  ctx.restore();
}
/** gold measure line with a label ("10 FEET") */
function measure(x0, x1, y, label, a = 1) {
  if (a <= 0.01) return;
  const mid = (x0 + x1) / 2;
  ctx.save(); ctx.globalAlpha = a;
  line([[x0, y], [x1, y]], P.gold, 10);
  for (const x of [x0, x1]) { line([[x - 26, y - 26], [x + 26, y + 26]], P.gold, 10); line([[x - 26, y + 26], [x + 26, y - 26]], P.gold, 10); }
  ctx.font = '900 54px Inter'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  const tw = ctx.measureText(label).width;
  rr(mid - tw / 2 - 34, y - 110, tw + 68, 84, 26); ctx.fillStyle = P.navy; ctx.fill();
  ctx.fillStyle = P.gold; ctx.fillText(label, mid, y - 67);
  ctx.restore();
}
function downArrow(x, y, s, a) { if (a <= 0) return; ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.globalAlpha = a; ctx.beginPath(); ctx.moveTo(0, -90); ctx.lineTo(-64, 20); ctx.lineTo(-22, 20); ctx.lineTo(-22, 110); ctx.lineTo(22, 110); ctx.lineTo(22, 20); ctx.lineTo(64, 20); ctx.closePath(); ctx.fillStyle = P.gold; ctx.fill(); ctx.lineWidth = 9; ctx.strokeStyle = P.ink; ctx.stroke(); ctx.restore(); }

export function buildShots() {
  const S = [], CUES = [], add = (o) => (S.push(o), o), cue = (t, type, o = {}) => CUES.push({ t: +t.toFixed(3), type, ...o });
  const cut = (i) => (i === 0 ? 0 : L(i) - 0.08);
  const blink = (t) => ((t % 3.1) < 0.12 ? 1 : 0);

  // 1 · HOOK (0–5 s): step outside at noon, 50 kg locks onto the ankles
  { const st = 0, fifty = Wd('fifty', 0), locks = Wd('locks', 0);
    add({ id: 'S01', at: st, cam: [540, 1100], note: 'street at noon, hero strides out, 50 KG lands on the ankles', draw(lt, d, t) {
      street({ sun: () => sunDisc(820, 250, 92, { rot: t * 0.05 }) });
      const landed = lt > locks, loaded = lt > fifty;
      const hx = lerp(300, 470, eio(clamp(lt / Math.max(0.6, locks))));
      const sink = landed ? 30 * eob(seg(lt, locks, locks + 0.4)) : 0;
      K.person({ x: hx, y: GROUND + sink, h: 840, dir: 1, mood: landed ? 'scared' : loaded ? 'worried' : 'calm',
        look: landed ? [0.7, 0.8] : loaded ? [0.5, 0.7] : [0.9, 0.1], blink: landed ? 0 : blink(t),
        walk: landed ? undefined : lt * 3.4, legs: landed ? { L: [30, 40], R: [-24, 46] } : undefined,
        arms: landed ? { L: [-52, 44], R: [62, 36] } : undefined });
      const g = loaded ? eio(seg(lt, fifty, fifty + 0.5)) : 0;
      blobShadow(hx, GROUND + 16, 140 + 34 * g, 0.34 + 0.36 * g);
      if (landed) { ankleCuffs(hx, GROUND - 46, 1, eob(seg(lt, locks, locks + 0.25))); for (let i = 0; i < 3; i++) line([[hx - 70 + i * 70, GROUND - 150], [hx - 90 + i * 70, GROUND - 210]], P.gold, 9); }
      K.counterPill('SHADOW: 50 KG', 540, 300, loaded ? eob(seg(lt, fifty, fifty + 0.3)) : 0);
      if (landed) downArrow(hx, GROUND - 430, 0.8, eob(seg(lt, locks, locks + 0.3)) * 0.9);
      darkDoor(120, FLOOR + 30);
    } });
    cue(0.2, 'pop', { gain: 0.5 }); cue(fifty, 'pop', { gain: 0.7 }); cue(locks, 'thud', { gain: 1.0 }); }

  // 2 · NOON ANGLE (5–12 s): the sun hangs straight overhead
  { const st = cut(1), sunW = Wd('sun', 1) - st, above = Wd('above', 1) - st;
    add({ id: 'S02', at: st, cam: [540, 1050], zoom: 0.08, note: 'sun straight overhead, dashed drop line onto the hero, noon pill', draw(lt, d, t) {
      const hx = 470;
      street({ sun: () => sunDisc(hx, 250, 104, { rot: t * 0.06, pulse: lt > sunW ? 0.6 * Math.exp(-(lt - sunW) * 1.4) * (0.6 + 0.4 * Math.sin(lt * 9)) : 0 }) });
      K.person({ x: hx, y: GROUND, h: 640, mood: 'calm', look: [0.15, -1], blink: blink(t), arms: { L: [-6, 14], R: [14, 18] } });
      if (lt > sunW) { const p = eo(seg(lt, sunW, sunW + 0.5)); ctx.save(); ctx.setLineDash([26, 22]); ctx.strokeStyle = 'rgba(28,28,34,0.55)'; ctx.lineWidth = 9; ctx.beginPath(); ctx.moveTo(hx, 380); ctx.lineTo(hx, lerp(380, 930, p)); ctx.stroke(); ctx.restore(); }
      blobShadow(hx, GROUND + 16, 132, 0.5);
      K.counterPill('12:00 NOON', 830, 560, eob(seg(lt, 0.05, 0.32)));
      if (lt > above) measure(hx + 170, hx + 430, GROUND + 30, 'TINY', eob(seg(lt, above, above + 0.3)) * 0.95);
    } });
    cue(st, 'whoosh'); cue(st + sunW, 'tock', { gain: 0.6 }); cue(st + above, 'pop', { gain: 0.6 }); }

  // 3 · NOON ANGLE (9–13.6 s): close-up — a small dark puddle under the shoes
  { const st = cut(2), puddle = Wd('puddle', 2) - st, shoes = Wd('shoes', 2) - st;
    add({ id: 'S03', at: st, cam: [540, 1100], zoom: 0.06, note: 'close-up: boots + tiny shadow puddle straight below, 50 KG pressing down', draw(lt, d, t) {
      ctx.save(); ctx.translate(540, 1833); ctx.scale(2.2, 2.2); ctx.translate(-540, -1833);
      street();
      const tremble = Math.sin(lt * 26) * 5;
      line([[452 + tremble, 1430], [410 + tremble, 940]], P.ink, 46);
      line([[648 - tremble, 1430], [694 - tremble, 940]], P.ink, 46);
      for (const [bx, rot] of [[430, -0.06], [664, 0.05]]) { ctx.save(); ctx.translate(bx, 1546); ctx.rotate(rot); rr(-118, -120, 236, 132, 40); ctx.fillStyle = P.ink; ctx.fill(); rr(-118, -6, 236, 30, 14); ctx.fillStyle = '#F4EEDC'; ctx.fill(); ctx.restore(); }
      const gp = eio(seg(lt, 0.15, 0.9));
      blobShadow(548, 1614, 150 + 34 * gp, 0.5 + 0.2 * gp);
      ctx.restore();
      downArrow(540, 760, 1.05, eob(seg(lt, 0.1, 0.4)) * (0.9 + 0.1 * Math.sin(lt * 7)));
      K.counterPill('50 KG · STRAIGHT DOWN', 540, 480, eob(seg(lt, 0.15, 0.42)));
      if (lt > puddle) K.counterPill('SHADOW: TINY', 540, 640, eob(seg(lt, puddle, puddle + 0.3)) * 0.86);
      if (lt > shoes) { for (let i = 0; i < 4; i++) line([[360 + i * 130, 1280], [340 + i * 130, 1230]], P.gold, 9); }
    } });
    cue(st, 'whoosh'); cue(st + puddle, 'tock', { gain: 0.5 }); cue(st + shoes, 'pop', { gain: 0.6 }); }

  // 4 · 4:00 PM DRAG (13.6–19 s): low sun, the shadow stretches ten feet
  { const st = cut(3), drops = Wd('drops', 3) - st, stretches = Wd('stretches', 3) - st, feet = Wd('feet', 3) - st;
    add({ id: 'S04', at: st, cam: [540, 1100], zoom: 0.1, note: 'low sun right, hero walks, shadow grows to 10 FEET behind him', draw(lt, d, t) {
      const sink = lt > drops ? 44 * eio(seg(lt, drops, drops + 0.9)) : 0;
      street({ sun: () => sunDisc(966, 1150 + sink, 88, { warm: 1, rot: t * 0.04, pulse: lt > drops ? 0.4 * Math.exp(-(lt - drops) * 1.6) : 0 }) });
      const hx = lerp(470, 700, eio(clamp(lt / Math.max(0.6, feet))));
      const grow = lt > stretches ? eio(seg(lt, stretches, stretches + 1.1)) : 0;
      const len = 210 + 370 * grow;
      castShadow(hx, GROUND + 18, len, -1, 0.5 + 0.14 * grow);
      K.person({ x: hx, y: GROUND, h: 840, dir: 1, mood: 'worried', look: [-0.7, 0.3], blink: blink(t),
        walk: lt < feet ? lt * 3.0 : undefined, lean: lt > feet ? -12 : 0,
        legs: lt > feet ? { L: [22, 26], R: [-16, 30] } : undefined, arms: lt > feet ? { L: [-30, 30], R: [40, 26] } : undefined });
      K.counterPill('4:00 PM', 300, 300, eob(seg(lt, 0.05, 0.32)));
      if (lt > feet) measure(hx - len, hx - 40, GROUND + 46, '10 FEET', eob(seg(lt, feet, feet + 0.35)));
      if (lt > stretches) { const a = 0.5 + 0.5 * Math.sin(lt * 5); ctx.save(); ctx.globalAlpha = a * 0.5; line([[hx + 60, GROUND - 250], [hx + 150, GROUND - 290]], P.gold, 8); line([[hx + 60, GROUND - 160], [hx + 150, GROUND - 150]], P.gold, 8); ctx.restore(); }
    } });
    cue(st, 'whoosh'); cue(st + drops, 'rumble', { gain: 0.7, dur: 1.6 }); cue(st + stretches, 'slide', { gain: 0.85, dur: 1.6 }); cue(st + feet, 'pop', { gain: 0.6 }); }

  // 5 · 4:00 PM DRAG (19–22.4 s): the shadow yanks him flat onto the sidewalk
  { const st = cut(4), yanks = Wd('yanks', 4) - st, flat = Wd('flat', 4) - st, walkway = Wd('sidewalk', 4) - st;
    add({ id: 'S05', at: st, cam: [540, 1150], zoom: 0.12, note: 'shadow jerks, hero is pulled backward and lands flat, cinema bars', draw(lt, d, t) {
      street({ sun: () => sunDisc(966, 1194, 88, { warm: 1, rot: t * 0.04 }) });
      const p = lt > yanks ? eio(seg(lt, yanks, yanks + 0.55)) : 0;
      const hx = lerp(730, 640, p);
      const hipY = lerp(GROUND - 0.46 * 760, 1490, eio(clamp((p - 0.3) / 0.7)));
      castShadow(hx + 40, GROUND + 18, 560, -1, 0.64);
      K.person({ x: hx, y: hipY + 0.46 * 760, h: 760, dir: 1, mood: p > 0.5 ? 'scared' : 'worried', look: p > 0.5 ? [0.8, -0.4] : [-0.8, 0.2], blink: 0,
        lean: -80 * p, legs: p > 0.2 ? { L: [26 - 20 * p, 30], R: [-18, 34 - 18 * p] } : { L: [22, 26], R: [-16, 30] },
        arms: p > 0.2 ? { L: [-74, 46], R: [78, 40] } : { L: [-30, 30], R: [40, 26] } });
      if (lt > yanks) { const tag = eob(seg(lt, yanks, yanks + 0.5)); K.counterPill('50 KG', lerp(360, 250, p), GROUND - 180, tag); }
      if (p > 0.05 && p < 0.95) for (let i = 0; i < 4; i++) { const a = (1 - Math.abs(p - 0.5) * 2) * 0.7; ctx.save(); ctx.globalAlpha = a * (0.4 + rnd(i) * 0.6); circle(hx + 150 + i * 66, GROUND + 6 - rnd(i + 3) * 40, 26 + rnd(i + 7) * 22, '#CFC6B4'); ctx.restore(); }
      if (lt > walkway && lt < walkway + 0.4 && Math.floor(lt * 20) % 2 === 0) { ctx.fillStyle = 'rgba(255,255,255,0.20)'; ctx.fillRect(-300, -300, W + 600, H + 600); }
      if (lt > walkway) { ctx.strokeStyle = 'rgba(28,28,34,0.5)'; ctx.lineWidth = 9; for (let i = 0; i < 3; i++) { ctx.beginPath(); ctx.moveTo(hx - 120 + i * 120, GROUND + 70); ctx.lineTo(hx - 60 + i * 120, GROUND + 130); ctx.stroke(); } }
      K.cinemaBars(eo(seg(lt, yanks, yanks + 0.35)) * 0.55);
    } });
    cue(st, 'whoosh'); cue(st + yanks, 'slide', { gain: 0.9, dur: 1.2 }); cue(st + walkway - 0.15, 'rumble', { gain: 0.5, dur: 1.0 }); cue(st + walkway, 'crash', { gain: 1.0 }); }

  // 6 · SHADOW-DELETE TRICK (22.4–27.8 s): umbrella / dark room → 0 kg
  { const st = cut(5), umb = Wd('umbrella', 5) - st, drops = Wd('drops', 5) - st, zero = Wd('zero', 5) - st;
    add({ id: 'S06', at: st, cam: [540, 1100], zoom: 0.08, note: 'umbrella opens, shadow + cuffs vanish, SHADOW: 0 KG + check', draw(lt, d, t) {
      street({ sun: () => sunDisc(966, 1194, 88, { warm: 1, rot: t * 0.04 }) });
      darkDoor(170, FLOOR + 30);
      const open = lt > umb ? eob(seg(lt, umb, umb + 0.45)) : 0;
      const gone = lt > umb ? 1 - eio(seg(lt, umb, umb + 0.7)) : 1;
      const rel = lt > zero;
      K.person({ x: 520, y: GROUND - (rel ? 14 * Math.sin(lt * 2.4) : 0), h: 840, dir: 1, mood: rel ? 'happy' : 'determined', look: [0.4, -0.5], blink: rel ? 0 : blink(t),
        lean: rel ? 4 : 0, arms: { L: [-8, 16], R: [96, 34] }, hold: (x, y) => umbrella(x + 6, y - 30, 1.0, open) });
      castShadow(520, GROUND + 18, 470, -1, 0.62 * gone);
      if (lt > drops) { const fall = eio(seg(lt, drops, drops + 0.8)); ankleCuffs(520 + 150 * fall, GROUND - 46 + 46 * fall, 1 - 0.35 * fall, 1 - fall); }
      K.counterPill(rel ? 'SHADOW: 0 KG' : 'SHADOW: 50 KG', 540, 300, rel ? eob(seg(lt, zero, zero + 0.3)) : eob(seg(lt, 0.05, 0.3)));
      if (rel) { K.check(880, 620, eob(seg(lt, zero + 0.1, zero + 0.4)) * 0.95); for (let i = 0; i < 5; i++) circle(300 + i * 130, GROUND - 120 - rnd(i) * 160, 12 + rnd(i + 2) * 10, 'rgba(242,178,62,0.75)'); }
      if (lt > umb && lt < umb + 0.6) { ctx.save(); ctx.globalAlpha = (1 - seg(lt, umb, umb + 0.6)) * 0.5; for (let i = 0; i < 3; i++) line([[240 + i * 300, 900], [240 + i * 300, 780]], P.white, 10); ctx.restore(); }
    } });
    cue(st, 'whoosh'); cue(st + umb, 'pop', { gain: 0.6 }); cue(st + drops, 'tock', { gain: 0.5 }); cue(st + zero, 'sparkle', { gain: 0.9, dur: 1.0 }); }

  // 7 · CLOUD TWIST (27.8–32.9 s): the cloud covers the sun, 50 kg slams back
  { const st = cut(6), cloudW = Wd('cloud', 6) - st, slam = Wd('slam', 6) - st, heels = Wd('heels', 6) - st;
    add({ id: 'S07', at: st, cam: [540, 1120], zoom: 0.1, note: 'cloud slides over the sun, shadow snaps back, weight slams onto the heels', draw(lt, d, t) {
      const covered = lt > slam;
      street({ sun: () => sunDisc(966, 1194, 88, { warm: 1, rot: t * 0.04, a: covered ? 0.4 : 1 }) });
      const cp = lt > cloudW ? eio(seg(lt, cloudW, cloudW + 1.1)) : 0;
      if (cp > 0) cloud(lerp(1420, 966, cp), 1150, 1.5, 1);
      const open = 1;
      const back = covered ? eob(seg(lt, slam, slam + 0.3)) : 0;
      const jolt = covered ? 26 * Math.exp(-(lt - slam) * 3.4) * Math.sin((lt - slam) * 22) : 0;
      K.person({ x: 520, y: GROUND + Math.max(0, jolt), h: 840, dir: 1, mood: covered ? 'scared' : 'worried', look: covered ? [0.8, -0.5] : [0.5, -0.7], blink: 0,
        lean: covered ? -26 * back : 0, legs: covered ? { L: [34 * back, 36], R: [-26 * back, 40] } : { L: [18, 22], R: [-14, 26] },
        arms: covered ? { L: [-64 * back - 10, 40], R: [70 * back + 16, 36] } : { L: [-8, 16], R: [96, 34] }, hold: (x, y) => umbrella(x + 6, y - 30, 1.0, open) });
      castShadow(520, GROUND + 18, 210 + 370 * back, -1, 0.64 * Math.min(1, back * 1.5));
      if (covered) { ankleCuffs(520, GROUND - 46, 1, Math.min(1, back * 1.4)); downArrow(520, GROUND - 430, 0.8, Math.min(1, back) * 0.9); }
      K.counterPill('50 KG', 540, 300, covered ? eob(seg(lt, slam, slam + 0.3)) : eob(seg(lt, 0.05, 0.3)));
      if (covered && lt < slam + 0.35 && Math.floor(lt * 20) % 2 === 0) { ctx.fillStyle = 'rgba(255,255,255,0.22)'; ctx.fillRect(-300, -300, W + 600, H + 600); }
      if (lt > heels) { ctx.save(); ctx.globalAlpha = 0.6; for (let i = 0; i < 3; i++) line([[640 + i * 60, GROUND - 300 + i * 60], [740 + i * 60, GROUND - 340 + i * 60]], P.gold, 9); ctx.restore(); }
    } });
    cue(st, 'whoosh'); cue(st + cloudW, 'boing', { gain: 0.7 }); cue(st + slam, 'slam', { gain: 1.0 }); cue(st + heels, 'thud', { gain: 0.7 }); }

  // 8 · end card: flat on the sidewalk, the 50 KG tag, loop line
  { const st = Math.max(Le(6) + 0.1, T.dur - 2.6);
    add({ id: 'S08', at: st, cam: [540, 1150], zoom: 0.1, note: 'hero flat under the long shadow, 50 KG pill, resigned', draw(lt, d, t) {
      street({ sun: () => sunDisc(966, 1194, 88, { warm: 1, rot: t * 0.04, a: 0.4 }) });
      cloud(966, 1150, 1.5, 1);
      castShadow(760, GROUND + 18, 640, -1, 0.64);
      K.person({ x: 700, y: 1840, h: 760, dir: 1, mood: 'worried', look: [0.6, -0.8], blink: blink(t), lean: -88,
        legs: { L: [24, 34], R: [-16, 36] }, arms: { L: [-70, 46], R: [74, 42] } });
      ankleCuffs(986, 1490, 1, 0.9);
      K.counterPill('HEAVY SHADOWS: 50 KG', 540, 640, eob(seg(lt, 0.3, 0.6)) * 1.12);
    } });
    cue(st, 'whoosh'); cue(st + 0.35, 'pop', { gain: 0.6 }); cue(st + 0.9, 'gulp', { gain: 0.7 }); }

  return { shots: S, cues: CUES };
}
