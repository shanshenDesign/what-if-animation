// METAL COINS ONLY: 40S : the shot list (Stick Story, metal-coins-40s).
// One picture per clause. A shot: { id, at, cam: [cx, cy], zoom, note, draw(lt, d, t) }. cut(i) = just before line i,
// Wd('word', i) = when the word is said. Sound: cue(t, type, { gain, dur }).
// Set: one street with shopfronts, all video; cutaways to a café counter, a belt close-up, a bank counter and
// a floor that tears open. Every payment is metal: gold/silver/copper coins, cloth pouches, a brass balance.
import { ctx, W, H, TAU, clamp, lerp, seg, eo, eio, eob, rnd, rr, circle, ell, line } from './core/lib.js';
import { L, Le, Wd, T } from './core/timing.js';
import * as K from './core/kit.js';
const { P, GROUND, FLOOR } = K;

// ── metal: three coin colours, all flat with an ink-free rim ───────────────────
const METAL = {
  bronze: ['#F2C063', '#C98A1C'],
  silver: ['#E4E9EF', '#A9B2BD'],
  copper: ['#EE9A5C', '#B0653A'],
};
/** one stamped coin at (x, y); rot in radians */
export function coin(x, y, r = 34, o = {}) {
  const [f, rim] = METAL[o.metal || 'bronze'];
  ctx.save(); ctx.translate(x, y); ctx.rotate(o.rot || 0);
  circle(0, 0, r, rim);
  circle(0, 0, r * 0.78, f);
  line([[-r * 0.36, 0], [r * 0.36, 0]], rim, Math.max(4, r * 0.14));
  line([[0, -r * 0.36], [0, r * 0.36]], rim, Math.max(4, r * 0.14));
  circle(0, 0, r * 0.15, rim);
  ctx.restore();
}
/** a heap of loose coins sitting on (x, y) (y = the surface) */
export function coinPile(x, y, n = 8, s = 1) {
  for (let i = 0; i < n; i++) {
    const k = rnd(i * 3.7), m = ['bronze', 'silver', 'copper'][i % 3];
    coin(x + (k - 0.5) * 190 * s, y - 26 * s * Math.floor(i / 3) - rnd(i + 9) * 14 * s, 32 * s, { metal: m, rot: (rnd(i + 4) - 0.5) * 0.9 });
  }
}
/** a drawstring coin pouch centred at (x, y); o.squash = landing squash 0..1, o.rot = sway */
export function pouch(x, y, s = 1, o = {}) {
  const sq = o.squash || 0;
  ctx.save(); ctx.translate(x, y); ctx.rotate(o.rot || 0); ctx.scale(s * (1 + sq * 0.16), s * (1 - sq * 0.16));
  rr(-92, -132, 184, 152, [70, 70, 44, 44]); ctx.fillStyle = o.color || '#9C6B48'; ctx.fill();
  ctx.strokeStyle = P.ink; ctx.lineWidth = 9; ctx.stroke();
  rr(-44, -176, 88, 58, 16); ctx.fillStyle = '#B4803F'; ctx.fill(); ctx.stroke();
  line([[-54, -150], [54, -150]], '#6B4A31', 11);
  coin(0, -172, 30, { metal: 'bronze' });
  ell(-34, -64, 24, 32, 'rgba(255,255,255,0.22)', -0.45);
  ctx.restore();
}
/** a big haul sack (tied neck, coin stamps on the belly) centred at (x, y) */
export function sack(x, y, s = 1, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(o.rot || 0); ctx.scale(s, s);
  ctx.beginPath(); ctx.moveTo(-142, 118); ctx.quadraticCurveTo(-196, -36, -74, -112);
  ctx.quadraticCurveTo(0, -166, 74, -112); ctx.quadraticCurveTo(196, -36, 142, 118);
  ctx.quadraticCurveTo(0, 176, -142, 118); ctx.closePath();
  ctx.fillStyle = o.color || '#C9A06A'; ctx.fill(); ctx.strokeStyle = P.ink; ctx.lineWidth = 10; ctx.stroke();
  rr(-36, -154, 72, 50, 14); ctx.fillStyle = '#9C6B48'; ctx.fill(); ctx.stroke();
  coin(-46, 24, 32, { metal: 'bronze' }); coin(52, 62, 28, { metal: 'silver' }); coin(34, -42, 24, { metal: 'copper' });
  ctx.restore();
}
/** side-view metal handcart facing right, wheels at (±) y-10; o.spin rotates the spokes, o.tilt rocks it */
export function handcart(x, y, s = 1, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.rotate(o.tilt || 0);
  rr(-206, -124, 348, 36, 10); ctx.fillStyle = '#8F959E'; ctx.fill();
  ctx.strokeStyle = P.ink; ctx.lineWidth = 8; ctx.stroke();
  for (const rx of [-196, -70, 56, 128]) line([[rx, -124], [rx, -306]], '#A6ADB8', 14);
  line([[-206, -306], [136, -306]], '#A6ADB8', 16);
  line([[-206, -116], [-322, -300]], '#8F959E', 16);
  line([[-322, -300], [-362, -300]], P.ink, 20);   // grip: (x-362, y-300)
  for (const wx of [-124, 106]) {
    circle(wx, -8, 86, P.ink); circle(wx, -8, 60, '#C9CDD4');
    ctx.save(); ctx.translate(wx, -8); ctx.rotate(o.spin || 0);
    for (let i = 0; i < 2; i++) { ctx.rotate(Math.PI / 4); line([[-56, 0], [56, 0]], '#8F959E', 9); }
    ctx.restore();
    circle(wx, -8, 13, P.ink);
  }
  ctx.restore();
}
/** brass balance scale, baseline at (x, y). o.tilt (rad) rocks the beam; o.leftDraw / o.rightDraw fill the pans */
export function brassScale(x, y, s = 1, o = {}) {
  const tilt = o.tilt || 0;
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  rr(-116, -34, 232, 44, 14); ctx.fillStyle = '#C9932E'; ctx.fill();
  ctx.strokeStyle = P.ink; ctx.lineWidth = 8; ctx.stroke();
  line([[0, -34], [0, -268]], '#C9932E', 24);
  circle(0, -268, 20, '#E8B24A');
  ctx.save(); ctx.translate(0, -268); ctx.rotate(tilt);
  line([[-196, 0], [196, 0]], '#E8B24A', 18);
  circle(0, 0, 17, P.ink);
  for (const side of [-1, 1]) {
    const px = side * 196;
    line([[px, 0], [px, 74]], '#8F959E', 6);
    ctx.beginPath(); ctx.moveTo(px - 74, 74); ctx.quadraticCurveTo(px, 140, px + 74, 74); ctx.closePath();
    ctx.fillStyle = '#D9A93F'; ctx.fill(); ctx.strokeStyle = P.ink; ctx.lineWidth = 8; ctx.stroke();
    const cb = side < 0 ? o.leftDraw : o.rightDraw;
    if (cb) cb(px, 74);
  }
  ctx.restore();
  ctx.restore();
}
/** a to-go coffee cup, base at (x, y) */
export function cup(x, y, s = 1) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  rr(-54, -118, 108, 118, [8, 8, 26, 26]); ctx.fillStyle = P.white; ctx.fill();
  ctx.strokeStyle = P.ink; ctx.lineWidth = 8; ctx.stroke();
  rr(-58, -142, 116, 32, 12); ctx.fillStyle = '#8F959E'; ctx.fill(); ctx.stroke();
  rr(-54, -84, 108, 46, 6); ctx.fillStyle = '#C9A06A'; ctx.fill();
  ctx.restore();
}

// ── the street set (flat, same all video): sky, shopfronts, sidewalk, road ─────
const FRONT = [[-50, 340], [290, 300], [590, 310], [890, 300]];
const BAND_Y = 906;
function cloud(x, y, s = 1, a = 1) {
  if (a <= 0.01) return;
  ctx.save(); ctx.globalAlpha = a; ctx.translate(x, y); ctx.scale(s, s);
  circle(-86, 8, 58, '#E9E6EE'); circle(-6, -30, 82, '#E9E6EE'); circle(84, 10, 56, '#E9E6EE');
  rr(-146, 6, 250, 62, 31); ctx.fillStyle = '#E9E6EE'; ctx.fill();
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
  for (const [x, w] of FRONT) {
    ctx.fillStyle = '#DCCDB4'; ctx.fillRect(x, BAND_Y, w, FLOOR - BAND_Y);
    ctx.strokeStyle = 'rgba(28,28,34,0.30)'; ctx.lineWidth = 6; ctx.strokeRect(x, BAND_Y, w, FLOOR - BAND_Y);
    // shop window + striped awning
    rr(x + 30, 960, w - 60, 330, 8); ctx.fillStyle = '#9EC2D8'; ctx.fill();
    ctx.strokeStyle = 'rgba(28,28,34,0.35)'; ctx.strokeRect(x + 30, 960, w - 60, 330);
    line([[x + 48, 1270], [x + w - 36, 1000]], 'rgba(255,255,255,0.45)', 12);
    ctx.fillStyle = P.navy; ctx.beginPath(); ctx.moveTo(x - 6, 946); ctx.lineTo(x + w + 6, 946);
    ctx.lineTo(x + w - 16, 1016); ctx.lineTo(x + 10, 1016); ctx.closePath(); ctx.fill();
    for (let k = 0; k < 4; k++) { ctx.fillStyle = P.white; ctx.beginPath(); ctx.moveTo(x + 6 + k * (w / 4), 946); ctx.lineTo(x + 6 + (k + 0.5) * (w / 4), 946); ctx.lineTo(x - 4 + (k + 0.5) * (w / 4), 1016); ctx.lineTo(x + 4 + k * (w / 4), 1016); ctx.closePath(); ctx.fill(); }
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
/** the flat interior shell (wall + floor) used by the cutaways */
function shell() {
  ctx.fillStyle = P.wall; ctx.fillRect(-300, -300, W + 600, FLOOR + 300);
  ctx.fillStyle = P.wallShade; ctx.fillRect(-300, FLOOR - 70, W + 600, 70);
  ctx.fillStyle = P.base; ctx.fillRect(-300, FLOOR - 20, W + 600, 20);
  ctx.fillStyle = P.floor; ctx.fillRect(-300, FLOOR, W + 600, H - FLOOR + 300);
  ctx.strokeStyle = P.floorDark; ctx.lineWidth = 6;
  for (let y = FLOOR + 90; y < H + 300; y += 110) { ctx.beginPath(); ctx.moveTo(-300, y); ctx.lineTo(W + 300, y); ctx.stroke(); }
}
/** three little gold clink marks flashing around (x, y) */
function clink(x, y, a) {
  if (a <= 0.01) return;
  ctx.save(); ctx.globalAlpha = a;
  for (let i = 0; i < 3; i++) line([[x + i * 34 - 34, y - i * 30], [x + i * 34 - 6, y - i * 30 - 26]], P.gold, 10);
  ctx.restore();
}

export function buildShots() {
  const S = [], CUES = [], add = (o) => (S.push(o), o), cue = (t, type, o = {}) => CUES.push({ t: +t.toFixed(3), type, ...o });
  const cut = (i) => (i === 0 ? 0 : L(i) - 0.08);
  const blink = (t) => ((t % 3.1) < 0.12 ? 1 : 0);

  // 1 · HOOK (0–5.2 s): coffee, then a clinking pouch of bronze coins hits the counter
  { const st = 0, clinkW = Wd('clinking', 0), land = Wd('counter', 0);
    add({ id: 'S01', at: st, cam: [540, 1100], zoom: 0.07, note: 'café counter: hero drops a bronze coin pouch, it lands + coins bounce, PAYMENT: COINS', draw(lt, d, t) {
      shell();
      K.windowPane(770, 340, 300, 330);
      K.counter(560, FLOOR + 40, 460);
      cup(610, 1060, 1);
      // the pouch: held up, then dropped between "clinking" and "counter"
      let px, py, rot = 0, sq = 0;
      if (lt <= clinkW) { px = 549; py = 938; rot = Math.sin(lt * 2.4) * 0.05; }
      else if (lt < land) { const p = seg(lt, clinkW, land); px = lerp(549, 760, p); py = lerp(938, 1046, p * p); rot = p * 0.4; }
      else { px = 760; py = 1046; sq = Math.exp(-(lt - land) * 7) * Math.max(0, Math.sin((lt - land) * 26)); }
      K.person({ x: 320, y: GROUND, h: 820, dir: 1, mood: lt > land ? 'happy' : 'calm', look: lt > land ? [0.7, 0.4] : [0.9, 0.1],
        blink: blink(t), arms: lt <= clinkW ? { L: [40, 26], R: [135, -40] } : { L: [64, 22], R: [86, 10] },
        legs: { L: [7, 6], R: [-7, 8] } });
      pouch(px, py, 0.7, { rot, squash: sq });
      // coins bounce out as it lands, then settle on the counter
      if (lt > land) for (let i = 0; i < 3; i++) {
        const a = lt - land - i * 0.07, rest = [700, 862, 944][i];
        if (a <= 0) continue;
        const p = clamp(a / 0.55), hop = Math.sin(Math.min(1, p) * Math.PI) * 120;
        coin(rest + (1 - p) * 40 * (i % 2 ? 1 : -1), (p < 1 ? 1046 - hop : 0) + (p < 1 ? 0 : 1030), 30, { metal: ['bronze', 'silver', 'copper'][i], rot: p < 1 ? p * 6 : (i - 1) * 0.4 });
      }
      clink(760, 980, lt > land && lt < land + 0.4 ? 1 - (lt - land) / 0.4 : 0);
      K.counterPill('PAYMENT: COINS', 540, 330, lt > land + 0.1 ? eob(seg(lt, land + 0.1, land + 0.4)) : 0);
    } });
    cue(st, 'whoosh'); cue(clinkW, 'tock', { gain: 0.9 }); cue(land, 'thud', { gain: 1.0 }); }

  // 2 · POCKET PHYSICS (5.2–9.9 s): no bills — a thick belt, bulging pockets, the wallet falls away
  { const st = cut(1), bills = Wd('bills', 1) - st, beltW = Wd('belt', 1) - st, sag = Wd('sag', 1) - st;
    add({ id: 'S02', at: st, cam: [540, 1060], zoom: 0.12, note: 'waist close-up: slim wallet flutters away, thick belt cinches, pockets bulge, NO WALLETS', draw(lt, d, t) {
      ctx.fillStyle = P.wall; ctx.fillRect(-300, -300, W + 600, H + 600);
      ctx.fillStyle = P.wallShade; ctx.fillRect(-300, 1660, W + 600, 400);
      // the torso (flat ink)
      rr(300, 380, 480, 420, 130); ctx.fillStyle = P.ink; ctx.fill();
      rr(348, 700, 384, 900, 110); ctx.fill();
      // the belt: cinches tight on "belt"
      const tight = lt > beltW ? eob(seg(lt, beltW, beltW + 0.3)) : 0, bw = 430 - 34 * tight;
      rr(540 - bw / 2, 1096, bw, 116, 22); ctx.fillStyle = '#6B4A31'; ctx.fill();
      ctx.strokeStyle = P.ink; ctx.lineWidth = 9; ctx.stroke();
      line([[540 - bw / 2 + 20, 1154], [540 + bw / 2 - 20, 1154]], '#8E6142', 7);
      const bk = 1 + 0.18 * Math.max(0, tight - 0.4) * (1 - tight);
      rr(540 - 52 * bk, 1082 + 14 * (1 - bk), 104 * bk, 144 * bk, 18); ctx.fillStyle = P.gold; ctx.fill();
      ctx.strokeStyle = P.ink; ctx.lineWidth = 9; ctx.stroke();
      // the pockets: sag and bulge on "sag"
      const sg = lt > sag ? eio(seg(lt, sag, sag + 0.5)) : 0;
      for (const sgn of [-1, 1]) {
        const cx = 540 + sgn * 250, ph = 190 + 130 * sg;
        rr(cx - 108, 1226, 216, ph, 46); ctx.fillStyle = '#8E6142'; ctx.fill();
        ctx.strokeStyle = P.ink; ctx.lineWidth = 9; ctx.stroke();
        coin(cx - sgn * 30, 1240 + 30 * sg, 40 + 12 * sg, { metal: sgn < 0 ? 'bronze' : 'silver', rot: sgn * 0.3 });
        ell(cx + sgn * 40, 1300 + 60 * sg, 34, 44, 'rgba(255,255,255,0.16)', sgn * 0.3);
      }
      // the paper world leaves: wallet + bills flutter down and out of frame
      if (lt < bills + 1.9) {
        const p = clamp(lt / 1.9), fade = p > 0.75 ? 1 - (p - 0.75) / 0.25 : 1;
        ctx.save(); ctx.globalAlpha = fade;
        rr(806, lerp(560, 2100, p * p), 150, 104, 16); ctx.fillStyle = P.navy; ctx.fill();
        ctx.strokeStyle = P.ink; ctx.lineWidth = 8; ctx.stroke();
        ctx.translate(880, lerp(560, 2100, p * p)); ctx.rotate(p * 3.2); rr(-44, -26, 88, 52, 6); ctx.fillStyle = P.white; ctx.fill(); ctx.stroke();
        ctx.restore();
        for (let i = 0; i < 2; i++) {
          const q = clamp((lt - 0.25 - i * 0.3) / 1.9); if (q <= 0 || q >= 1) continue;
          ctx.save(); ctx.globalAlpha = 1 - Math.max(0, (q - 0.8) / 0.2);
          ctx.translate(160 + i * 80, lerp(360, 2100, q * q)); ctx.rotate(-q * 4 + i);
          rr(-52, -30, 104, 60, 6); ctx.fillStyle = P.white; ctx.fill(); ctx.strokeStyle = P.ink; ctx.lineWidth = 7; ctx.stroke();
          line([[-30, 0], [30, 0]], '#9AA6B2', 6);
          ctx.restore();
        }
      }
      K.counterPill('NO WALLETS', 540, 300, eob(seg(lt, 0.12, 0.42)));
    } });
    cue(st, 'whoosh'); cue(st + beltW, 'plop', { gain: 0.9 }); }

  // 3 · POCKET PHYSICS (9.9–14.1 s): every step drags, the pockets sag
  { const st = cut(2), drags = Wd('drags', 2) - st;
    add({ id: 'S03', at: st, cam: [540, 1180], zoom: 0.08, note: 'street: hero walks with heavy sagging pockets dragging, SAGGING POCKETS', draw(lt, d, t) {
      street();
      const swing = (lt > drags ? 1.5 : 1) * Math.sin(lt * 5.2);
      K.person({ x: 520, y: GROUND, h: 840, dir: 1, mood: 'worried', look: [0.3, 0.7], blink: blink(t),
        lean: 4, walk: lt * 4.4, arms: { L: [-30, 20], R: [34, 18] } });
      // the sagging pockets hang off the hips and lag behind the stride
      for (const sgn of [-1, 1]) {
        const hx = 520 + sgn * 66, hy = GROUND - 840 * 0.46 + 40, drop = 200 + 60 * Math.min(1, (lt > drags ? 1.4 : 0.8));
        ctx.save(); ctx.translate(hx + swing * 14 * sgn, hy); ctx.rotate(swing * 0.07 * sgn);
        rr(-74, 0, 148, drop, 40); ctx.fillStyle = '#8E6142'; ctx.fill();
        ctx.strokeStyle = P.ink; ctx.lineWidth = 9; ctx.stroke();
        coin(sgn * 10, drop - 46, 40, { metal: sgn < 0 ? 'bronze' : 'silver', rot: sgn * 0.4 });
        ctx.restore();
      }
      // drag lines behind the pockets
      if (lt > drags) for (let i = 0; i < 3; i++) line([[250, 1240 + i * 60], [370 + Math.sin(lt * 9 + i) * 16, 1240 + i * 60]], 'rgba(28,28,34,0.35)', 9);
      K.counterPill('SAGGING POCKETS', 540, 330, eob(seg(lt, 0.15, 0.45)));
    } });
    cue(st, 'whoosh'); cue(st + drags, 'slide', { gain: 0.9, dur: 1.1 }); }

  // 4 · BIG PURCHASES (14.1–18.1 s): groceries in a clinking sack over one shoulder
  { const st = cut(3), clinkW = Wd('clinking', 3) - st, haul = Wd('haul', 3) - st;
    add({ id: 'S04', at: st, cam: [540, 1140], zoom: 0.09, note: 'street: hero hauls a clinking coin sack over one shoulder with groceries poking out', draw(lt, d, t) {
      street();
      const heave = lt > haul ? Math.sin((lt - haul) * 16) * 10 * Math.exp(-(lt - haul) * 2.4) : 0;
      K.person({ x: 440, y: GROUND, h: 840, dir: 1, mood: 'determined', look: [0.4, -0.3], blink: blink(t),
        lean: 9, walk: lt * 3.6, arms: { L: [58, 46], R: [126, -34] }, legs: undefined });
      ctx.save(); ctx.translate(0, heave);
      sack(680, 810, 1.05, { rot: 0.16 });
      // groceries poking out of the neck
      ctx.save(); ctx.translate(700, 640); ctx.rotate(0.5); ell(0, -70, 26, 96, '#D9A96A'); ctx.restore();
      K.can(636, 668, 0.9); K.bottle(766, 664, 0.9);
      line([[648, 700], [566, 796]], '#9C7848', 14);   // the shoulder strap
      ctx.restore();
      // a grocery bag in the free hand
      rr(268, 1160, 150, 170, 14); ctx.fillStyle = '#C9A06A'; ctx.fill(); ctx.strokeStyle = '#9C7848'; ctx.lineWidth = 8; ctx.stroke();
      ctx.beginPath(); ctx.arc(343, 1166, 44, Math.PI, TAU); ctx.strokeStyle = '#9C7848'; ctx.lineWidth = 10; ctx.stroke();
      clink(700, 760, lt > clinkW && lt < clinkW + 0.5 ? 1 - (lt - clinkW) / 0.5 : 0);
      K.counterPill('CLINKING SACKS', 540, 330, eob(seg(lt, 0.15, 0.45)));
    } });
    cue(st, 'whoosh'); cue(st + haul, 'rumble', { gain: 0.7, dur: 1.6 }); }

  // 5 · BIG PURCHASES (18.1–22.1 s): rent day — a metal handcart of coins hits the curb
  { const st = cut(4), bump = Wd('sidewalk', 4) - st;
    add({ id: 'S05', at: st, cam: [540, 1240], zoom: 0.08, note: 'street: hero pushes a metal handcart loaded with coin sacks, it bumps the curb, RENT DAY', draw(lt, d, t) {
      street();
      const hit = lt > bump ? Math.exp(-(lt - bump) * 4) : 0;
      const jitter = Math.sin(lt * 26) * 3;
      handcart(660, 1476 + jitter, 1, { spin: -lt * 5, tilt: -0.07 * hit });
      ctx.save(); ctx.translate(0, jitter - hit * 12);
      sack(560, 1230, 0.72, { rot: -0.08 }); sack(742, 1252, 0.6, { rot: 0.12 });
      coinPile(660, 1180, 4, 0.7);
      ctx.restore();
      // grip lands exactly in the front hand: hand ≈ (338, 1182) for x=269, h=840, R=[10,10]
      K.person({ x: 269, y: GROUND, h: 840, dir: 1, mood: 'determined', look: [0.5, -0.1], blink: blink(t),
        lean: 8, walk: lt * 3.2, arms: { L: [-44, 22], R: [10, 10] } });
      if (hit > 0.02) { ctx.save(); ctx.globalAlpha = hit;
        for (let i = 0; i < 4; i++) { const a = i * TAU / 4 + 0.4; line([[790 + Math.cos(a) * 60, 1520 + Math.sin(a) * 60], [790 + Math.cos(a) * 110, 1520 + Math.sin(a) * 110]], P.gold, 11); }
        ctx.restore(); }
      K.counterPill('RENT DAY', 540, 330, eob(seg(lt, 0.15, 0.45)));
    } });
    cue(st, 'whoosh'); cue(st + bump, 'crash', { gain: 0.9 }); }

  // 6 · BANK (22.1–26.5 s): cashiers weigh stamped silver and copper on brass scales
  { const st = cut(5), weigh = Wd('weigh', 5) - st;
    add({ id: 'S06', at: st, cam: [540, 1060], zoom: 0.08, note: 'bank counter: cashier levels a brass balance with a bucket of coins, hero waits with a sack, WEIGHED OUT', draw(lt, d, t) {
      shell();
      rr(430, 300, 300, 110, 18); ctx.fillStyle = P.navy; ctx.fill();
      ctx.font = '900 64px Inter'; ctx.fillStyle = P.gold; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      ctx.fillText('BANK', 580, 358);
      // cashier behind the counter (clipped to above the counter top)
      ctx.save(); ctx.beginPath(); ctx.rect(-300, -300, W + 600, 1390); ctx.clip();
      K.person({ x: 780, y: 1560, h: 780, dir: -1, mood: 'calm', look: [-0.6, 0.3], blink: blink(t),
        arms: { L: [64, 26], R: [78, 14] } });
      ctx.restore();
      K.counter(140, FLOOR + 40, 780);
      // the balance: levels out on "weigh"
      const tilt = 0.14 * Math.sin(lt * 2.1) * (lt > weigh ? Math.exp(-(lt - weigh) * 1.8) : 1) + (lt > weigh ? 0.015 : 0);
      brassScale(470, 1056, 1, {
        tilt,
        leftDraw: (px, py) => { rr(px - 58, py - 86, 116, 92, 14); ctx.fillStyle = '#8F959E'; ctx.fill(); ctx.strokeStyle = P.ink; ctx.lineWidth = 7; ctx.stroke(); coinPile(px, py - 8, 5, 0.62); },
        rightDraw: (px, py) => { for (let i = 0; i < 3; i++) { rr(px - 40 + i * 6, py - 6 - i * 30, 74, 28, 8); ctx.fillStyle = '#596075'; ctx.fill(); ctx.strokeStyle = P.ink; ctx.lineWidth = 6; ctx.stroke(); } },
      });
      // hero waits in front with a sack
      K.person({ x: 1010, y: GROUND, h: 780, dir: -1, mood: 'worried', look: [-0.6, -0.1], blink: blink(t),
        arms: { L: [58, 40], R: [70, 30] }, hold: (x, y) => sack(x, y - 40, 0.42) });
      K.counterPill('WEIGHED OUT', 540, 330, eob(seg(lt, 0.15, 0.45)));
    } });
    cue(st, 'whoosh'); cue(st + weigh, 'zip', { gain: 0.8 }); }

  // 7 · BANK (26.5–30.3 s): no card — your change gets weighed out, coin by coin
  { const st = cut(6), change = Wd('change', 6) - st;
    add({ id: 'S07', at: st, cam: [540, 1020], zoom: 0.13, note: 'brass scale close-up: coin drops on the pan, credit card crossed out, NO CARD SWIPES', draw(lt, d, t) {
      ctx.fillStyle = P.wall; ctx.fillRect(-300, -300, W + 600, H + 600);
      ctx.fillStyle = P.wallShade; ctx.fillRect(-300, FLOOR - 70, W + 600, 70);
      ctx.fillStyle = P.floor; ctx.fillRect(-300, FLOOR, W + 600, H - FLOOR + 300);
      const tilt = 0.1 * Math.sin(lt * 2.4);
      brassScale(420, 1420, 1.75, {
        tilt,
        leftDraw: (px, py) => {
          coinPile(px, py + 34, 4, 0.7);
          // the coin landing on "change"
          if (lt > change) { const p = eob(seg(lt, change, change + 0.4)); coin(px + 40, lerp(300, py - 34, p), 44, { metal: 'copper', rot: p * 5 }); }
        },
        rightDraw: (px, py) => { for (let i = 0; i < 4; i++) { rr(px - 44 + i * 7, py - 4 - i * 34, 84, 32, 9); ctx.fillStyle = '#596075'; ctx.fill(); ctx.strokeStyle = P.ink; ctx.lineWidth = 6; ctx.stroke(); } },
      });
      // the card world: a credit card flutters away, crossed out
      const cp = clamp(lt / 1.4);
      ctx.save(); ctx.translate(870, lerp(560, 1500, cp * cp)); ctx.rotate(cp * 2.4);
      rr(-120, -76, 240, 152, 18); ctx.fillStyle = P.navy; ctx.fill(); ctx.strokeStyle = P.ink; ctx.lineWidth = 9; ctx.stroke();
      rr(-104, -40, 90, 62, 8); ctx.fillStyle = P.gold; ctx.fill();
      line([[-104, 44], [104, 44]], '#8FA3C4', 10);
      ctx.restore();
      if (lt > 0.3 && lt < 1.6) K.cross(870, 560, eob(seg(lt, 0.3, 0.6)) * 0.9 * (1 - clamp(seg(lt, 1.2, 1.6))));
      K.counterPill('NO CARD SWIPES', 540, 330, eob(seg(lt, 0.15, 0.45)));
    } });
    cue(st, 'whoosh'); cue(st + change, 'pop', { gain: 0.8 }); }

  // 8 · TWIST A (30.6–34.8 s): Friday pays — the week's wages land in both hands
  { const st = cut(7), pays = Wd('pays', 7) - st;
    add({ id: 'S08', at: st, cam: [540, 1120], zoom: 0.09, note: 'street: happy hero holds a bulging pay pouch, pockets heavy with coins, gold sparkle, FRIDAY: PAID', draw(lt, d, t) {
      street();
      K.person({ x: 540, y: GROUND, h: 840, dir: 1, mood: 'happy', look: [0.2, -0.3], blink: 0,
        arms: { L: [18, -4], R: [28, -8] }, legs: { L: [7, 6], R: [-7, 8] } });
      pouch(540, 1120, 0.95, { squash: lt > pays ? Math.exp(-(lt - pays) * 6) * Math.max(0, Math.sin((lt - pays) * 22)) : 0 });
      // heavy pockets
      for (const sgn of [-1, 1]) { rr(540 + sgn * 150 - 74, 1210, 148, 210, 44); ctx.fillStyle = '#8E6142'; ctx.fill(); ctx.strokeStyle = P.ink; ctx.lineWidth = 9; ctx.stroke(); coin(540 + sgn * 150, 1250, 44, { metal: sgn < 0 ? 'bronze' : 'copper', rot: sgn * 0.3 }); }
      // payday sparkle burst
      if (lt > pays && lt < pays + 1.1) { const a = 1 - (lt - pays) / 1.1; ctx.save(); ctx.globalAlpha = a;
        for (let i = 0; i < 8; i++) { const ang = i * TAU / 8, r0 = 180 + 140 * (lt - pays); line([[540 + Math.cos(ang) * r0, 900 + Math.sin(ang) * r0 * 0.8], [540 + Math.cos(ang) * (r0 + 70), 900 + Math.sin(ang) * (r0 + 70) * 0.8]], P.gold, 12); }
        ctx.restore(); }
      if (lt > pays) for (let i = 0; i < 3; i++) { const q = ((lt - pays) * 0.7 + i * 0.33) % 1; coin(300 + i * 240, 700 - Math.sin(q * Math.PI) * 160, 30, { metal: ['bronze', 'silver', 'copper'][i], rot: q * 6 }); }
      K.counterPill('FRIDAY: PAID', 540, 330, eob(seg(lt, 0.15, 0.45)));
    } });
    cue(st, 'whoosh'); cue(st + pays, 'sparkle', { gain: 0.9, dur: 1.2 }); }

  // 9 · TWIST B (34.8–37.5 s): the pockets rip straight through the floor
  { const st = cut(8), rip = Wd('rip', 8) - st, through = Wd('floor', 8) - st;
    add({ id: 'S09', at: st, cam: [540, 1060], zoom: 0.1, note: 'floor close-up: pockets tear open, the floor gives way, hero drops through with coins, POCKET FAIL', draw(lt, d, t) {
      ctx.fillStyle = P.wall; ctx.fillRect(-300, -300, W + 600, 1450);
      ctx.fillStyle = P.wallShade; ctx.fillRect(-300, 1380, W + 600, 70);
      ctx.fillStyle = P.floor; ctx.fillRect(-300, 1450, W + 600, H - 1450 + 300);
      ctx.strokeStyle = P.floorDark; ctx.lineWidth = 6;
      for (let y = 1540; y < H + 300; y += 110) { ctx.beginPath(); ctx.moveTo(-300, y); ctx.lineTo(W + 300, y); ctx.stroke(); }
      const drop = lt > through ? eob(seg(lt, through, through + 0.6)) * 660 : 0;
      // everything above the floor line: the floor itself hides the legs on the way down
      ctx.save(); ctx.beginPath(); ctx.rect(-300, -300, W + 600, 1750); ctx.clip();
      const feet = 1450 + drop;
      K.person({ x: 540, y: feet, h: 840, dir: 1, mood: lt > rip ? 'scared' : 'worried', look: [0.1, 0.8], blink: 0,
        lean: lt > through ? -6 : 3, arms: lt > rip ? { L: [-70, 34], R: [78, 30] } : { L: [-8, 20], R: [12, 18] } });
      // torn pocket flaps once it rips
      if (lt > rip) for (const sgn of [-1, 1]) {
        ctx.save(); ctx.translate(540 + sgn * 150, 1160); ctx.rotate(sgn * 0.5);
        ctx.beginPath(); ctx.moveTo(-70, 0); ctx.lineTo(70, 0); ctx.lineTo(sgn * 20, 190); ctx.closePath();
        ctx.fillStyle = '#8E6142'; ctx.fill(); ctx.strokeStyle = P.ink; ctx.lineWidth = 9; ctx.stroke();
        ctx.restore();
      }
      // coins tumbling through with the hero
      if (lt > rip) for (let i = 0; i < 6; i++) {
        const a = lt - rip - i * 0.12; if (a <= 0) continue;
        const p = clamp(a / 0.9);
        coin(540 + (rnd(i) - 0.5) * 420, 1200 + p * p * 900, 32, { metal: ['bronze', 'silver', 'copper'][i % 3], rot: a * 7 });
      }
      ctx.restore();
      // the hole: opens on "rip"; the lip is drawn over the clipped body so it sinks through
      if (lt > rip) {
        const g = eob(seg(lt, rip, rip + 0.45)), rx = 240 * g, ry = 70 * g;
        ctx.save(); ctx.translate(540, 1462);
        ell(0, 0, rx, ry, '#23202A');
        ctx.beginPath(); ctx.ellipse(0, 0, rx, ry, 0, 0.15 * Math.PI, 0.85 * Math.PI);
        ctx.strokeStyle = '#8A6238'; ctx.lineWidth = 22; ctx.stroke();
        ctx.restore();
      }
      if (lt > through && lt < through + 0.4 && Math.floor(lt * 20) % 2 === 0) { ctx.fillStyle = 'rgba(255,255,255,0.22)'; ctx.fillRect(-300, -300, W + 600, H + 600); }
      K.counterPill('POCKET FAIL', 540, 330, lt > rip ? eob(seg(lt, rip, rip + 0.3)) : 0);
    } });
    cue(st, 'whoosh'); cue(st + rip, 'boing', { gain: 0.9 }); cue(st + through, 'slam', { gain: 1.0 }); }

  // 10 · end card: the hole, the spilled week, the title pill
  { const st = Math.max(Le(8) + 0.1, T.dur - 2.6);
    add({ id: 'S10', at: st, cam: [540, 1120], zoom: 0.08, note: 'hero beside the floor hole and a spill of coins, METAL COINS ONLY: 40S pill', draw(lt, d, t) {
      ctx.fillStyle = P.wall; ctx.fillRect(-300, -300, W + 600, 1450);
      ctx.fillStyle = P.wallShade; ctx.fillRect(-300, 1380, W + 600, 70);
      ctx.fillStyle = P.floor; ctx.fillRect(-300, 1450, W + 600, H - 1450 + 300);
      ctx.strokeStyle = P.floorDark; ctx.lineWidth = 6;
      for (let y = 1540; y < H + 300; y += 110) { ctx.beginPath(); ctx.moveTo(-300, y); ctx.lineTo(W + 300, y); ctx.stroke(); }
      ell(330, 1500, 230, 64, '#23202A');
      ctx.beginPath(); ctx.ellipse(330, 1500, 230, 64, 0, 0.15 * Math.PI, 0.85 * Math.PI);
      ctx.strokeStyle = '#8A6238'; ctx.lineWidth = 22; ctx.stroke();
      coinPile(350, 1580, 9, 0.9); coinPile(760, 1620, 6, 0.8);
      K.person({ x: 700, y: 1660, h: 780, dir: -1, mood: 'happy', look: [-0.2, 0.5], blink: 0,
        arms: { L: [-56, 30], R: [62, 26] }, legs: { L: [6, 5], R: [-6, 7] } });
      K.counterPill('METAL COINS ONLY: 40S', 540, 640, eob(seg(lt, 0.3, 0.6)) * 1.1);
    } });
    cue(st, 'whoosh'); cue(st + 0.35, 'pop', { gain: 0.6 }); cue(st + 0.9, 'gulp', { gain: 0.7 }); }

  return { shots: S, cues: CUES };
}
