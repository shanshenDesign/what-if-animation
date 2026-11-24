// LOCKED DOORS: 45S : the shot list (Stick Story, locked-doors-45s).
// One picture per clause. A shot: { id, at, cam: [cx, cy], zoom, note, draw(lt, d, t) }. cut(i) = just before line i,
// Wd('word', i) = when the word is said. Sound: cue(t, type, { gain, dur }).
// Set: one street with ground-floor shop doors, all video; cutaways to an elevator shaft, a kitchen, a clock,
// and one stuck bathroom latch. Every door gets a gold padlock that pops on "clicks" and falls off on "open".
import { ctx, W, H, TAU, clamp, lerp, seg, eo, eio, eob, rnd, rr, circle, ell, line } from './core/lib.js';
import { L, Le, Wd, T } from './core/timing.js';
import * as K from './core/kit.js';
const { P, GROUND, FLOOR } = K;

const mmss = (s) => `${String(Math.floor(Math.max(0, s) / 60)).padStart(2, '0')}:${String(Math.floor(Math.max(0, s) % 60)).padStart(2, '0')}`;

// ── the street set (flat, same all video) ──────────────────────────────────────
const FRONT = [[-50, 340], [290, 300], [590, 310], [890, 300]];
export const DOORS = FRONT.map(([x, w]) => ({ x: x + Math.round(w * 0.72), w: 140, h: 400 }));
const BAND_Y = 906;

function cloud(x, y, s = 1, a = 1) {
  if (a <= 0.01) return;
  ctx.save(); ctx.globalAlpha = a; ctx.translate(x, y); ctx.scale(s, s);
  circle(-86, 8, 58, '#E9E6EE'); circle(-6, -30, 82, '#E9E6EE'); circle(84, 10, 56, '#E9E6EE');
  rr(-146, 6, 250, 62, 31); ctx.fillStyle = '#E9E6EE'; ctx.fill();
  ctx.restore();
}
/** a flat street door: frame + panel + knob; open = 0..1 swings the panel away */
export function shopDoor(x, y, w, h, o = {}) {
  const open = o.open || 0;
  rr(x - w / 2 - 16, y - h - 16, w + 32, h + 16, [14, 14, 0, 0]); ctx.fillStyle = '#6B4A31'; ctx.fill();
  rr(x - w / 2, y - h, w, h, [8, 8, 0, 0]); ctx.fillStyle = open > 0.04 ? '#12141C' : '#A8754E'; ctx.fill();
  if (open > 0.04) {
    ctx.save(); ctx.translate(x - w / 2, 0); ctx.scale(Math.max(0.1, 1 - 0.8 * open), 1);
    rr(0, y - h, w, h, [8, 8, 0, 0]); ctx.fillStyle = '#A8754E'; ctx.fill();
    rr(w * 0.12, y - h + 34, w * 0.76, h * 0.36, 6); ctx.strokeStyle = '#8E6142'; ctx.lineWidth = 7; ctx.stroke();
    ctx.restore();
  } else {
    rr(x - w / 2 + 22, y - h + 30, w - 44, h * 0.36, 6); ctx.strokeStyle = '#8E6142'; ctx.lineWidth = 7; ctx.stroke();
    rr(x - w / 2 + 22, y - h * 0.54, w - 44, h * 0.36, 6); ctx.stroke();
    circle(x + w / 2 - 24, y - h * 0.46, 11, P.gold);
  }
}
/** gold padlock (shackle + body + keyhole) */
export function padlock(x, y, s = 1, a = 1) {
  if (a <= 0.01 || s <= 0.01) return;
  ctx.save(); ctx.globalAlpha = clamp(a); ctx.translate(x, y); ctx.scale(s, s);
  ctx.strokeStyle = P.gold; ctx.lineWidth = 15; ctx.beginPath(); ctx.arc(0, -36, 30, Math.PI, 0); ctx.stroke();
  rr(-48, -32, 96, 80, 16); ctx.fillStyle = P.gold; ctx.fill();
  circle(0, 4, 13, P.navy); rr(-5, 4, 10, 24, 4); ctx.fillStyle = P.navy; ctx.fill();
  ctx.restore();
}
export function street(o = {}) {
  ctx.fillStyle = P.sky; ctx.fillRect(-300, -300, W + 600, FLOOR + 300);
  cloud(250, 280, 1.1, 0.9); cloud(870, 200, 0.85, 0.8);
  const bl = [[-50, 700, 340, 650], [290, 840, 300, 510], [590, 640, 310, 710], [890, 880, 300, 470]];
  for (const [x, y, w, h] of bl) {
    ctx.fillStyle = '#E6DAC5'; ctx.fillRect(x, y, w, h);
    ctx.strokeStyle = 'rgba(28,28,34,0.30)'; ctx.lineWidth = 6; ctx.strokeRect(x, y, w, h);
    const rows = Math.max(1, Math.floor((BAND_Y - y - 60) / 190));
    for (let r = 0; r < rows; r++) for (let k = 0; k < 3; k++) {
      const cw = (w - 70) / 3, ch = Math.min(140, BAND_Y - y - 70 - r * 190);
      if (ch < 50) continue;
      rr(x + 35 + k * cw, y + 45 + r * 190, cw - 30, ch, 6); ctx.fillStyle = '#9EC2D8'; ctx.fill();
    }
  }
  for (let i = 0; i < FRONT.length; i++) {
    const [x, w] = FRONT[i], d = DOORS[i];
    ctx.fillStyle = '#DCCDB4'; ctx.fillRect(x, BAND_Y, w, FLOOR - BAND_Y);
    ctx.strokeStyle = 'rgba(28,28,34,0.30)'; ctx.lineWidth = 6; ctx.strokeRect(x, BAND_Y, w, FLOOR - BAND_Y);
    const wx = x + 26, ww = (d.x - d.w / 2 - 16) - wx;
    if (ww > 40) {
      rr(wx, 950, ww, 330, 8); ctx.fillStyle = '#9EC2D8'; ctx.fill();
      ctx.strokeStyle = 'rgba(28,28,34,0.35)'; ctx.strokeRect(wx, 950, ww, 330);
      line([[wx + 18, 1250], [wx + ww - 24, 990]], 'rgba(255,255,255,0.45)', 12);
    }
    shopDoor(d.x, FLOOR, d.w, d.h, { open: o.open || 0 });
    if ((o.locks ?? true) && (o.lockA ?? 1) > 0.01) padlock(d.x, FLOOR - 186, 0.85, o.lockA ?? 1);
  }
  ctx.fillStyle = '#DBD3C3'; ctx.fillRect(-300, FLOOR, W + 600, 430);
  ctx.strokeStyle = '#C4BAA7'; ctx.lineWidth = 6;
  for (let y = FLOOR + 130; y < FLOOR + 430; y += 140) { ctx.beginPath(); ctx.moveTo(-300, y); ctx.lineTo(W + 300, y); ctx.stroke(); }
  for (let x = -120; x < W + 300; x += 250) { ctx.beginPath(); ctx.moveTo(x, FLOOR); ctx.lineTo(x, FLOOR + 430); ctx.stroke(); }
  ctx.fillStyle = '#C7BCA8'; ctx.fillRect(-300, FLOOR + 430, W + 600, 34);
  ctx.fillStyle = '#6E6A72'; ctx.fillRect(-300, FLOOR + 464, W + 600, H + 300);
  ctx.fillStyle = '#E8E2D2';
  for (let x = -60; x < W + 300; x += 260) ctx.fillRect(x, 1846, 150, 16);
}
/** steam wisps above a kettle (phase-animated) */
function steam(x, y, t, a = 1) {
  if (a <= 0.01) return;
  ctx.save(); ctx.globalAlpha = a; ctx.strokeStyle = 'rgba(255,255,255,0.9)'; ctx.lineWidth = 14; ctx.lineCap = 'round';
  for (let i = 0; i < 3; i++) {
    const p = ((t * 0.5 + i * 0.33) % 1), yy = y - p * 330, wob = Math.sin(t * 3 + i * 2) * 26 * p;
    ctx.globalAlpha = a * (1 - p) * 0.9;
    ctx.beginPath(); ctx.moveTo(x + i * 44 - 44 + wob, yy + 60);
    ctx.quadraticCurveTo(x + i * 44 - 44 - 30 + wob, yy + 20, x + i * 44 - 44 + wob, yy - 20);
    ctx.stroke();
  }
  ctx.restore();
}
/** a kettle on the counter */
export function kettle(x, y, s = 1) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  rr(-78, -120, 156, 120, 30); ctx.fillStyle = '#B8BEC6'; ctx.fill();
  rr(-78, -58, 156, 34, 8); ctx.fillStyle = '#8F959E'; ctx.fill();
  line([[-70, -100], [-132, -150]], '#8F959E', 26);                       // spout
  ctx.strokeStyle = P.ink; ctx.lineWidth = 16; ctx.beginPath(); ctx.arc(0, -134, 62, Math.PI, 0); ctx.stroke(); // handle
  rr(-34, -152, 68, 34, 12); ctx.fillStyle = '#8F959E'; ctx.fill();       // lid
  circle(0, -160, 13, P.ink);
  ctx.restore();
}
/** delivery van (side view, facing right); exhaust puffs drawn separately */
export function van(x, y, s = 1) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  rr(-300, -300, 400, 236, 22); ctx.fillStyle = '#E9EEF2'; ctx.fill();
  rr(-300, -300, 400, 236, 22); ctx.strokeStyle = P.ink; ctx.lineWidth = 9; ctx.stroke();
  rr(100, -244, 196, 180, 20); ctx.fillStyle = '#D9E2EA'; ctx.fill();
  rr(100, -244, 196, 180, 20); ctx.stroke();
  rr(150, -228, 120, 84, 12); ctx.fillStyle = '#9EC2D8'; ctx.fill();      // windshield
  rr(-276, -262, 150, 84, 12); ctx.fillStyle = P.gold; ctx.fill();        // parcel logo
  circle(-170, -62, 62, P.ink); circle(-170, -62, 26, '#C9CDD4');
  circle(212, -62, 62, P.ink); circle(212, -62, 26, '#C9CDD4');
  ctx.restore();
}
/** cardboard box (held at a hand) */
function boxAt(x, y, s = 1) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  rr(-74, -60, 148, 120, 10); ctx.fillStyle = '#C9A06A'; ctx.fill();
  ctx.strokeStyle = '#9C7848'; ctx.lineWidth = 7; ctx.strokeRect(-74, -60, 148, 120);
  line([[-74, -8], [74, -8]], '#9C7848', 9);
  ctx.restore();
}
/** wall clock racing toward 1:00 (left = seconds remaining) */
function clockFace(x, y, r, left) {
  const minsPast = (3600 - left) / 60;
  circle(x, y, r + 16, P.ink); circle(x, y, r, P.white);
  for (let i = 0; i < 12; i++) {
    const a = -Math.PI / 2 + i * TAU / 12;
    line([[x + Math.cos(a) * r * 0.86, y + Math.sin(a) * r * 0.86], [x + Math.cos(a) * r * 0.96, y + Math.sin(a) * r * 0.96]], P.ink, i % 3 ? 8 : 16);
  }
  const hA = -Math.PI / 2 + TAU * (minsPast / 60) / 12, mA = -Math.PI / 2 + TAU * (minsPast % 60) / 60;
  line([[x, y], [x + Math.cos(hA) * r * 0.5, y + Math.sin(hA) * r * 0.5]], P.ink, 22);
  line([[x, y], [x + Math.cos(mA) * r * 0.78, y + Math.sin(mA) * r * 0.78]], P.ink, 14);
  line([[x, y], [x + Math.cos(mA) * r * 0.82, y + Math.sin(mA) * r * 0.82]], P.red, 7);
  circle(x, y, 18, P.red);
}

export function buildShots() {
  const S = [], CUES = [], add = (o) => (S.push(o), o), cue = (t, type, o = {}) => CUES.push({ t: +t.toFixed(3), type, ...o });
  const cut = (i) => (i === 0 ? 0 : L(i) - 0.08);
  const blink = (t) => ((t % 3.1) < 0.12 ? 1 : 0);

  // 1 · HOOK (0–5 s): step outside, every door clicks shut at once
  { const st = 0, clicks = Wd('clicks', 0), once = Wd('once', 0);
    add({ id: 'S01', at: st, cam: [540, 1100], note: 'street, hero strides out, every door slams + gold padlocks pop, DOORS: LOCKED', draw(lt, d, t) {
      const shut = lt > clicks ? eob(seg(lt, clicks, clicks + 0.22)) : 0;
      street({ open: 0.3 * (1 - shut), locks: false });
      if (lt > clicks) for (let i = 0; i < DOORS.length; i++) {
        const p = eob(seg(lt, clicks + i * 0.05, clicks + i * 0.05 + 0.3));
        padlock(DOORS[i].x, FLOOR - 186, 0.85 * (0.5 + 0.5 * p), p);
      }
      const hx = lerp(240, 520, eio(clamp(lt / Math.max(0.8, clicks))));
      K.person({ x: hx, y: GROUND, h: 820, dir: 1, mood: lt > clicks ? 'scared' : 'calm',
        look: lt > clicks ? [0.7, 0.6] : [0.9, 0.1], blink: blink(t), walk: lt < clicks ? lt * 3.4 : undefined,
        legs: lt > clicks ? { L: [24, 30], R: [-18, 34] } : undefined, arms: lt > clicks ? { L: [-56, 40], R: [64, 34] } : undefined });
      K.counterPill('DOORS: LOCKED', 540, 330, lt > clicks ? eob(seg(lt, clicks + 0.1, clicks + 0.4)) : 0);
      if (lt > clicks && lt < clicks + 0.5 && Math.floor(lt * 20) % 2 === 0) { ctx.fillStyle = 'rgba(255,255,255,0.18)'; ctx.fillRect(-300, -300, W + 600, H + 600); }
    } });
    cue(st, 'whoosh'); cue(clicks, 'tock', { gain: 0.9 }); cue(once, 'thud', { gain: 1.0 }); }

  // 2 · BOTTLENECK (5–8.7 s): elevator frozen between floors, doors sealed
  { const st = cut(1), freeze = Wd('freeze', 1), sealed = Wd('sealed', 1) - st;
    add({ id: 'S02', at: st, cam: [540, 980], zoom: 0.07, note: 'elevator shaft cutaway, car stuck between floors, doors slide shut, BETWEEN FLOORS', draw(lt, d, t) {
      ctx.fillStyle = P.nWall; ctx.fillRect(-300, -300, W + 600, H + 600);
      ctx.fillStyle = P.nWallShade;
      for (const fy of [560, 980, 1400]) ctx.fillRect(-300, fy - 14, W + 600, 28);
      ctx.font = '900 40px Inter'; ctx.fillStyle = '#8A93AC'; ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
      ctx.fillText('FLOOR 3', 60, 500); ctx.fillText('FLOOR 2', 60, 920); ctx.fillText('FLOOR 1', 60, 1340);
      const jolt = lt > freeze - st ? 16 * Math.exp(-(lt - (freeze - st)) * 3.6) * Math.sin((lt - (freeze - st)) * 24) : 0;
      ctx.save(); ctx.translate(0, jolt);
      rr(300, 700, 480, 340, 16); ctx.fillStyle = '#EFE6D6'; ctx.fill();
      rr(300, 700, 480, 340, 16); ctx.strokeStyle = P.ink; ctx.lineWidth = 14; ctx.stroke();
      K.person({ x: 540, y: 1030, h: 300, mood: 'worried', look: [0, 0.5], blink: blink(t), arms: { L: [40, 20], R: [52, 16] } });
      const p = lt > sealed - 0.7 ? eio(seg(lt, sealed - 0.7, sealed)) : 0;
      if (p > 0) {
        rr(300, 700, 240 * p, 340, [10, 0, 0, 10]); ctx.fillStyle = '#8F959E'; ctx.fill();
        rr(780 - 240 * p, 700, 240 * p, 340, [0, 10, 10, 0]); ctx.fillStyle = '#A6ADB8'; ctx.fill();
        line([[540, 700], [540, 1040]], P.ink, 8);
      }
      ctx.restore();
      K.counterPill('BETWEEN FLOORS', 540, 330, lt > freeze - st ? eob(seg(lt, freeze - st, freeze - st + 0.3)) : 0);
    } });
    cue(st, 'whoosh'); cue(freeze, 'thud', { gain: 0.8 }); cue(st + sealed, 'tock', { gain: 0.7 }); }

  // 3 · BOTTLENECK (8.7–13.3 s): shoppers + commuter on the wrong side of the glass
  { const st = cut(2), commuters = Wd('commuters', 2) - st, glass = Wd('glass', 2) - st;
    add({ id: 'S03', at: st, cam: [540, 1050], zoom: 0.08, note: 'shopfront close-up: two shoppers palms-on inside the glass, commuter outside, WRONG SIDE', draw(lt, d, t) {
      ctx.fillStyle = '#DCCDB4'; ctx.fillRect(-300, -300, W + 600, H + 600);
      rr(110, 430, 860, 1010, 22); ctx.fillStyle = '#6B4A31'; ctx.fill();          // frame
      rr(140, 460, 800, 950, 12); ctx.fillStyle = '#EFE6D6'; ctx.fill();            // inside
      K.person({ x: 380, y: 1400, h: 560, dir: 1, mood: 'worried', look: [0.6, 0.2], blink: blink(t), arms: { L: [78, 8], R: [86, 6] } });
      K.person({ x: 680, y: 1400, h: 560, dir: -1, mood: 'scared', look: [-0.6, 0.1], blink: blink(t), arms: { L: [80, 6], R: [88, 4] } });
      ctx.fillStyle = 'rgba(158,194,216,0.5)'; ctx.fillRect(140, 460, 800, 950);   // glass
      line([[170, 1330], [430, 560]], 'rgba(255,255,255,0.5)', 22);
      line([[520, 1330], [780, 560]], 'rgba(255,255,255,0.35)', 18);
      for (const [px, py] of [[350, 980], [430, 1030], [640, 960], [716, 1010]]) ell(px, py, 34, 44, 'rgba(255,255,255,0.75)'); // palms
      rr(140, 460, 800, 950, 12); ctx.strokeStyle = P.ink; ctx.lineWidth = 16; ctx.stroke();
      K.person({ x: 850, y: GROUND, h: 780, dir: -1, mood: 'worried', look: [-0.7, -0.1], blink: blink(t),
        arms: { L: [70, 14], R: [80, 8] }, legs: { L: [8, 6], R: [-8, 8] } });
      if (lt > glass && lt < glass + 0.45) for (let i = 0; i < 3; i++) line([[760 + i * 26, 900 + i * 40], [790 + i * 26, 870 + i * 40]], P.gold, 9);
      K.counterPill('WRONG SIDE', 540, 300, lt > commuters ? eob(seg(lt, commuters, commuters + 0.3)) : 0);
    } });
    cue(st, 'whoosh'); cue(st + commuters, 'pop', { gain: 0.6 }); cue(st + glass, 'tock', { gain: 0.8 }); }

  // 4 · BOTTLENECK (13.3–17.6 s): kettle simmers behind a locked kitchen door
  { const st = cut(3), simmers = Wd('simmers', 3) - st, doorW = Wd('door', 3) - st;
    add({ id: 'S04', at: st, cam: [540, 1080], zoom: 0.07, note: 'kitchen: kettle steaming on the counter, locked door on the left, DOOR: LOCKED', draw(lt, d, t) {
      ctx.fillStyle = P.wall; ctx.fillRect(-300, -300, W + 600, FLOOR + 300);
      ctx.fillStyle = P.wallShade; ctx.fillRect(-300, FLOOR - 70, W + 600, 70);
      ctx.fillStyle = P.base; ctx.fillRect(-300, FLOOR - 20, W + 600, 20);
      ctx.fillStyle = P.floor; ctx.fillRect(-300, FLOOR, W + 600, H - FLOOR + 300);
      ctx.strokeStyle = P.floorDark; ctx.lineWidth = 6;
      for (let y = FLOOR + 90; y < H + 300; y += 110) { ctx.beginPath(); ctx.moveTo(-300, y); ctx.lineTo(W + 300, y); ctx.stroke(); }
      K.windowPane(770, 360, 300, 340);
      K.door(240, FLOOR + 40, null, 0);
      padlock(240, 1130, 1.0, eob(seg(lt, 0.1, 0.4)));
      K.counter(620, FLOOR + 60, 420);
      kettle(760, 1078, 1.4);
      if (lt > simmers - 0.3) steam(760, 900, t, eob(seg(lt, simmers - 0.3, simmers + 0.4)));
      K.person({ x: 520, y: GROUND, h: 760, dir: -1, mood: 'worried', look: [-0.7, 0.2], blink: blink(t),
        lean: 5, arms: { L: [64, 18], R: [74, 12] }, legs: { L: [8, 6], R: [-8, 8] } });
      if (lt > doorW && lt < doorW + 0.5) for (let i = 0; i < 3; i++) line([[330 + i * 30, 1110 + i * 36], [364 + i * 30, 1084 + i * 36]], P.gold, 9);
      K.counterPill('DOOR: LOCKED', 540, 320, eob(seg(lt, 0.15, 0.45)));
    } });
    cue(st, 'whoosh'); cue(st + simmers, 'sizzle', { gain: 0.7, dur: 2.2 }); cue(st + doorW, 'tock', { gain: 0.6 }); }

  // 5 · ESCALATION (17.6–21.6 s): drivers wait beside idling vans
  { const st = cut(4), idling = Wd('idling', 4) - st, packages = Wd('packages', 4) - st;
    add({ id: 'S05', at: st, cam: [540, 1180], zoom: 0.08, note: 'van idling at the curb with exhaust puffs, two drivers waiting with boxes, WAITING', draw(lt, d, t) {
      street();
      van(560, 1876, 1.0);
      for (let i = 0; i < 4; i++) {
        const p = ((t * 0.6 + i * 0.25) % 1);
        ctx.save(); ctx.globalAlpha = (1 - p) * 0.5; circle(240 - p * 130, 1830 - p * 70, 26 + p * 40, '#C9CDD4'); ctx.restore();
      }
      K.person({ x: 880, y: GROUND, h: 760, dir: -1, mood: 'worried', look: [-0.6, 0.3], blink: blink(t),
        arms: { L: [56, 46], R: [66, 40] }, legs: { L: [6, 5], R: [-6, 7] }, hold: (x, y) => boxAt(x, y, 0.9) });
      K.person({ x: 300, y: GROUND, h: 660, dir: 1, mood: 'calm', look: [0.6, 0.2], blink: blink(t),
        arms: { L: [58, 44], R: [68, 38] }, hold: (x, y) => boxAt(x, y, 0.8) });
      if (lt > idling && lt < idling + 1.6) { const b = Math.sin(lt * 9) * 4; ctx.save(); ctx.translate(0, b); ctx.restore(); }
      K.counterPill('WAITING...', 540, 330, lt > idling ? eob(seg(lt, idling, idling + 0.3)) : 0);
      if (lt > packages) for (let i = 0; i < 3; i++) line([[820 + i * 30, 1270 + i * 34], [852 + i * 30, 1244 + i * 34]], P.gold, 9);
    } });
    cue(st, 'whoosh'); cue(st + idling, 'rumble', { gain: 0.6, dur: 1.8 }); cue(st + packages, 'pop', { gain: 0.6 }); }

  // 6 · ESCALATION (21.6–25.8 s): everybody checks the ground-floor windows
  { const st = cut(5), checks = Wd('checks', 5) - st, holds = Wd('holds', 5) - st;
    add({ id: 'S06', at: st, cam: [540, 1120], zoom: 0.13, note: 'two people rattling ground-floor windows that will not budge, red crosses, ALL LOCKED', draw(lt, d, t) {
      street();
      const rattle = lt > checks ? Math.sin(lt * 42) * 5 * Math.exp(-(lt - checks) * 1.4) : 0;
      ctx.save(); ctx.translate(rattle, 0);
      K.person({ x: 368, y: GROUND, h: 780, dir: 1, mood: 'worried', look: [0.4, -0.4], blink: blink(t),
        lean: 6, arms: { L: [72, 10], R: [82, 6] }, legs: { L: [8, 6], R: [-8, 8] } });
      K.person({ x: 666, y: GROUND, h: 720, dir: 1, mood: 'scared', look: [0.4, -0.4], blink: blink(t),
        lean: 5, arms: { L: [70, 12], R: [80, 8] }, legs: { L: [7, 5], R: [-7, 7] } });
      ctx.restore();
      if (lt > holds) { K.cross(368, 1115, eob(seg(lt, holds, holds + 0.3)) * 0.75); K.cross(666, 1115, eob(seg(lt, holds + 0.15, holds + 0.45)) * 0.75); }
      K.counterPill('ALL LOCKED', 540, 330, lt > holds ? eob(seg(lt, holds, holds + 0.3)) : 0);
    } });
    cue(st, 'whoosh'); cue(st + checks, 'tock', { gain: 0.7 }); cue(st + holds, 'thud', { gain: 0.7 }); }

  // 7 · ESCALATION (25.8–29.7 s): the sixty-minute countdown on every screen
  { const st = cut(6), countdown = Wd('countdown', 6) - st, ticks = Wd('ticks', 6) - st;
    add({ id: 'S07', at: st, cam: [540, 1080], zoom: 0.06, note: 'countdown pill 59:59 ticking, every shop screen shows it, TICKING', draw(lt, d, t) {
      street();
      const txt = mmss(3599 - Math.floor(lt));
      for (const [sx, sw] of [[-24, 110], [316, 104], [616, 104], [916, 104]]) {
        rr(sx, 1000, sw, 180, 10); ctx.fillStyle = P.navy; ctx.fill();
        ctx.font = '900 46px Inter'; ctx.fillStyle = P.gold; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
        ctx.fillText(txt, sx + sw / 2, 1092);
      }
      K.counterPill(txt, 540, 420, 1.5 * eob(seg(lt, 0.1, 0.45)));
      if (lt > ticks && Math.floor(lt * 2) % 2 === 0) { ctx.save(); ctx.globalAlpha = 0.5; circle(540, 420, 210, 'rgba(242,178,62,0.25)'); ctx.restore(); }
    } });
    cue(st, 'whoosh'); cue(st + countdown, 'alarm', { gain: 0.5, dur: 2.6 }); cue(st + ticks, 'tock', { gain: 0.8 }); }

  // 8 · FINAL MINUTES (29.7–~32.5 s): the street goes quiet, everyone waits
  { const quietW = Wd('quiet', 7), st = cut(7), quiet = quietW - st;
    add({ id: 'S08', at: st, cam: [540, 1120], zoom: 0.06, note: 'everybody frozen on the sidewalk waiting, countdown 09:5x, cinema bars creep in', draw(lt, d, t) {
      street();
      K.person({ x: 300, y: GROUND, h: 760, dir: 1, mood: 'worried', look: [0.5, -0.5], blink: blink(t), arms: { L: [-6, 14], R: [10, 16] } });
      K.person({ x: 560, y: GROUND, h: 820, dir: -1, mood: 'scared', look: [-0.3, -0.6], blink: 0, arms: { L: [-4, 16], R: [8, 18] } });
      K.person({ x: 830, y: GROUND, h: 720, dir: 1, mood: 'worried', look: [0.2, -0.5], blink: blink(t), arms: { L: [-6, 14], R: [10, 16] } });
      K.counterPill(mmss(599 - Math.floor(lt)), 540, 380, 1.35);
      K.cinemaBars(eo(seg(lt, 0.2, 1.6)) * 0.35);
    } });
    cue(st, 'whoosh'); cue(quietW, 'heartbeat', { gain: 0.7 }); }

  // 9 · FINAL MINUTES (~32.5–34.7 s): the clock races to 1:00:00
  { const st = Wd('quiet', 7), everybody = Wd('everybody', 7), waits = Wd('waits', 7);
    add({ id: 'S09', at: st, cam: [540, 900], zoom: 0.05, note: 'clock close-up racing to 1:00, countdown 00:0x, heartbeat', draw(lt, d, t) {
      ctx.fillStyle = '#DCCDB4'; ctx.fillRect(-300, -300, W + 600, H + 600);
      const left = Math.max(0, 600 * (1 - lt / Math.max(0.6, d)));
      clockFace(540, 760, 330, left);
      K.counterPill(mmss(left), 540, 1300, 1.6 * eob(seg(lt, 0.05, 0.35)));
      if (left < 60 && Math.floor(lt * 6) % 2 === 0) { ctx.save(); ctx.globalAlpha = 0.35; circle(540, 760, 400, 'rgba(226,87,76,0.35)'); ctx.restore(); }
      K.cinemaBars(0.35 + 0.25 * eo(seg(lt, 0, d)));
    } });
    cue(st, 'whoosh'); cue(everybody, 'tock', { gain: 0.6 }); cue(waits, 'heartbeat', { gain: 0.8 }); }

  // 10 · TWIST (34.7–38.8 s): one hour — every lock clicks open together
  { const st = cut(8), openW = Wd('open', 8) - st, together = Wd('together', 8) - st;
    add({ id: 'S10', at: st, cam: [540, 1100], zoom: 0.09, note: 'all doors fling open, padlocks fall off, gold sparkle, EVERY DOOR: OPEN', draw(lt, d, t) {
      const p = lt > openW ? eob(seg(lt, openW, openW + 0.55)) : 0;
      street({ open: p, locks: false });
      for (let i = 0; i < DOORS.length; i++) {
        const dp = clamp((p - i * 0.06) / 0.9);
        if (dp <= 0) padlock(DOORS[i].x, FLOOR - 186, 0.85, 1);
        else if (dp < 1) padlock(DOORS[i].x + dp * 40 * (i % 2 ? 1 : -1), FLOOR - 186 + dp * dp * 300, 0.85 * (1 - 0.4 * dp), 1 - dp);
      }
      if (p > 0.4) for (let i = 0; i < DOORS.length; i++) {
        const a = clamp((p - 0.4 - i * 0.05) / 0.4);
        if (a <= 0) continue;
        ctx.save(); ctx.globalAlpha = (1 - a) * 0.9;
        for (let k = 0; k < 6; k++) { const ang = k * TAU / 6; line([[DOORS[i].x + Math.cos(ang) * 60, FLOOR - 186 + Math.sin(ang) * 60], [DOORS[i].x + Math.cos(ang) * (60 + 90 * a), FLOOR - 186 + Math.sin(ang) * (60 + 90 * a)]], P.gold, 10); }
        ctx.restore();
      }
      const happy = p > 0.5;
      K.person({ x: 540, y: GROUND, h: 820, dir: 1, mood: happy ? 'happy' : 'calm', look: [0.3, -0.5], blink: happy ? 0 : blink(t),
        arms: happy ? { L: [-64, 26], R: [70, 24] } : { L: [-8, 14], R: [12, 16] }, legs: { L: [6, 5], R: [-6, 7] } });
      K.person({ x: 880, y: GROUND, h: 700, dir: -1, mood: happy ? 'happy' : 'worried', look: [-0.3, -0.5], blink: blink(t),
        arms: happy ? { L: [-60, 28], R: [66, 26] } : { L: [-6, 14], R: [10, 16] } });
      K.counterPill('EVERY DOOR: OPEN', 540, 330, p > 0 ? eob(seg(lt, openW, openW + 0.3)) : 0);
      if (lt > together && lt < together + 0.3 && Math.floor(lt * 20) % 2 === 0) { ctx.fillStyle = 'rgba(255,255,255,0.25)'; ctx.fillRect(-300, -300, W + 600, H + 600); }
    } });
    cue(st, 'whoosh'); cue(st + openW, 'sparkle', { gain: 0.9, dur: 1.4 }); cue(st + together, 'pop', { gain: 0.8 }); }

  // 11 · TWIST (38.8–42.4 s): one stuck bathroom latch that won't budge
  { const st = cut(9), stuck = Wd('stuck', 9) - st, budge = Wd('budge', 9) - st;
    add({ id: 'S11', at: st, cam: [540, 1080], zoom: 0.1, note: 'bathroom door close-up, gold slide bolt shivering and refusing, STUCK + red cross', draw(lt, d, t) {
      ctx.fillStyle = P.wall; ctx.fillRect(-300, -300, W + 600, FLOOR + 300);
      ctx.fillStyle = P.wallShade; ctx.fillRect(-300, FLOOR - 70, W + 600, 70);
      ctx.fillStyle = P.floor; ctx.fillRect(-300, FLOOR, W + 600, H - FLOOR + 300);
      ctx.strokeStyle = P.floorDark; ctx.lineWidth = 6;
      for (let y = FLOOR + 90; y < H + 300; y += 110) { ctx.beginPath(); ctx.moveTo(-300, y); ctx.lineTo(W + 300, y); ctx.stroke(); }
      K.door(770, FLOOR + 40, null, 0);
      const shake = (lt > stuck ? 1 : 0.35) * (lt > budge ? 1.6 : 1) * Math.sin(lt * 46) * 7;
      ctx.save(); ctx.translate(shake, 0);
      rr(560, 1040, 150, 100, 16); ctx.fillStyle = '#8E6142'; ctx.fill();         // keeper plate
      rr(590, 1062, 300, 56, 28); ctx.fillStyle = P.gold; ctx.fill();             // the bolt
      circle(880, 1090, 34, P.gold); rr(846, 1056, 68, 68, 16); ctx.fillStyle = P.gold; ctx.fill();
      ctx.restore();
      K.person({ x: 400, y: GROUND, h: 820, dir: 1, mood: lt > budge ? 'scared' : 'worried', look: [0.7, 0.1], blink: 0,
        lean: 7 + 5 * (lt > budge ? 1 : 0), arms: { L: [74, 10], R: [84, 6] }, legs: { L: [10, 8], R: [-8, 10] } });
      if (lt > budge) for (let i = 0; i < 3; i++) ell(470 + i * 44, 760 - (lt - budge) * 160 - i * 40, 14, 20, '#9EC2D8');
      if (lt > stuck) K.cross(930, 940, eob(seg(lt, stuck, stuck + 0.3)) * 0.8);
      K.counterPill('STUCK', 300, 380, lt > stuck ? eob(seg(lt, stuck, stuck + 0.3)) : 0);
      if (lt > budge && lt < budge + 0.4 && Math.floor(lt * 20) % 2 === 0) { ctx.fillStyle = 'rgba(255,255,255,0.2)'; ctx.fillRect(-300, -300, W + 600, H + 600); }
    } });
    cue(st, 'whoosh'); cue(st + stuck, 'boing', { gain: 0.8 }); cue(st + budge, 'slam', { gain: 1.0 }); }

  // 12 · end card: doors open, the title pill, loop line
  { const st = Math.max(Le(9) + 0.1, T.dur - 2.6);
    add({ id: 'S12', at: st, cam: [540, 1120], zoom: 0.08, note: 'hero happy among open doors, LOCKED DOORS: 45S pill', draw(lt, d, t) {
      street({ open: 1, locks: false });
      K.person({ x: 540, y: GROUND, h: 820, dir: 1, mood: 'happy', look: [0.3, -0.4], blink: 0,
        arms: { L: [-58, 30], R: [64, 28] }, legs: { L: [6, 5], R: [-6, 7] } });
      K.counterPill('LOCKED DOORS: 45S', 540, 620, eob(seg(lt, 0.3, 0.6)) * 1.12);
    } });
    cue(st, 'whoosh'); cue(st + 0.35, 'pop', { gain: 0.6 }); cue(st + 0.9, 'gulp', { gain: 0.7 }); }

  return { shots: S, cues: CUES };
}
