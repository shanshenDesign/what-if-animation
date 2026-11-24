// WHAT IF GRAVITY TURNED OFF FOR 35 SECONDS? : the shot list (Stick Story, gravity-35s).
// One picture per clause. A shot: { id, at, cam: [cx, cy], zoom, note, draw(lt, d, t) }. cut(i) = just before line i,
// Wd('word', i) = when the word is said. Sound: cue(t, type, { gain, dur }).
import { ctx, W, H, clamp, lerp, seg, eo, eio, eob, rnd, rr, circle, ell, line } from './core/lib.js';
import { L, Le, Wd, T } from './core/timing.js';
import * as K from './core/kit.js';
const { P, GROUND } = K;

// small set pieces for this story
function mug(x, y, s = 1, rot = 0) { ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s); rr(-46, -70, 92, 84, 14); ctx.fillStyle = '#F4EEDC'; ctx.fill(); ctx.strokeStyle = P.ink; ctx.lineWidth = 7; ctx.stroke(); ctx.beginPath(); ctx.arc(58, -28, 30, -1.2, 1.2); ctx.stroke(); rr(-46, -70, 92, 26, 12); ctx.fillStyle = '#6B4A34'; ctx.fill(); ctx.restore(); }
function book(x, y, s = 1, rot = 0) { ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s); rr(-90, -60, 180, 120, 8); ctx.fillStyle = P.red; ctx.fill(); ctx.strokeStyle = P.ink; ctx.lineWidth = 7; ctx.stroke(); line([[-60, -60], [-60, 60]], P.ink, 6); ctx.restore(); }
function cushion(x, y, s = 1, rot = 0) { ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s); rr(-130, -90, 260, 180, 46); ctx.fillStyle = '#8FA8C8'; ctx.fill(); ctx.strokeStyle = P.ink; ctx.lineWidth = 8; ctx.stroke(); ctx.restore(); }
function dog(x, y, s = 1, rot = 0) { ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s); ell(0, 0, 120, 66, P.wood); circle(120, -60, 52, P.wood); ell(150, -90, 18, 34, '#6B4A34', 0.5); circle(138, -66, 7, P.ink); line([[-110, -20], [-150, -70]], P.ink, 14); line([[-60, 50], [-60, 96]], P.ink, 14); line([[40, 50], [40, 96]], P.ink, 14); ctx.restore(); }
function ceilingLamp(x, y) { line([[x, -300], [x, y - 60]], P.ink, 10); ell(x, y, 120, 46, P.ink); ell(x, y + 26, 70, 26, P.lamp); }
function downArrow(x, y, s, a) { if (a <= 0) return; ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.globalAlpha = a; ctx.beginPath(); ctx.moveTo(0, -90); ctx.lineTo(-64, 20); ctx.lineTo(-22, 20); ctx.lineTo(-22, 110); ctx.lineTo(22, 110); ctx.lineTo(22, 20); ctx.lineTo(64, 20); ctx.closePath(); ctx.fillStyle = P.gold; ctx.fill(); ctx.lineWidth = 9; ctx.strokeStyle = P.ink; ctx.stroke(); ctx.restore(); }

export function buildShots() {
  const S = [], CUES = [], add = (o) => (S.push(o), o), cue = (t, type, o = {}) => CUES.push({ t: +t.toFixed(3), type, ...o });
  const cut = (i) => (i === 0 ? 0 : L(i) - 0.08);
  const blink = (t) => ((t % 3.1) < 0.12 ? 1 : 0);
  // how far up the hero is floating at local time lt inside a float shot (px above GROUND)
  const floatY = (lt) => 60 + 260 * eio(clamp(lt / 2.2)) + 26 * Math.sin(lt * 1.7);

  // 1 · hook: hero in the living room, the question lands
  add({ id: 'S01', at: 0, cam: [540, 1100], note: 'hero on the rug, GRAVITY: ON pill, looks up', draw(lt, d, t) {
    K.livingRoom({});
    K.person({ x: 520, y: GROUND, h: 840, mood: lt > d * 0.55 ? 'worried' : 'calm', look: lt > d * 0.55 ? [0, -1] : [0.5, 0.3], blink: blink(t), arms: { L: [-6, 14], R: [12, 16] } });
    K.counterPill('GRAVITY: ON', 540, 300, eob(seg(lt, 0.1, 0.35)));
    if (lt > d * 0.7) downArrow(860, 620, 0.9, eob(seg(lt, d * 0.7, d * 0.7 + 0.3)) * 0.9);
  } });
  cue(0.2, 'pop', { gain: 0.5 });

  // 2 · "your feet leave the floor" — lift-off on the word
  { const st = cut(1), lift = Wd('feet', 1) - st, fl = Wd('floats', 1) - st;
    add({ id: 'S02', at: st, cam: [540, 1100], note: 'hero lifts off the rug, mug + cushion rise', draw(lt, d, t) {
      K.livingRoom({});
      const up = lt > lift;
      K.person({ x: 520, y: GROUND - (up ? floatY(lt - lift) : 0), h: 840, mood: up ? 'scared' : 'happy', look: up ? [Math.sin(lt * 3), -0.6] : [0.6, 0.3], blink: up ? 0 : blink(t), legs: up ? { L: [18, 22], R: [-14, 26] } : undefined, arms: up ? { L: [-40, 34], R: [46, 30] } : { L: [-6, 14], R: [12, 16] } });
      const r = up ? eio(seg(lt, lift, lift + 0.9)) : 0;
      if (r > 0) { mug(260, 1250 - 420 * r, 1.1, 0.5 * r); cushion(840, 1180 - 300 * r, 1, -0.35 * r); }
      K.counterPill(up ? 'GRAVITY: OFF' : 'GRAVITY: ON', 540, 300, eob(seg(lt, 0.05, 0.3)));
      if (lt > fl) K.cinemaBars(eo(seg(lt, fl, fl + 0.4)) * 0.5);
    } });
    cue(st, 'whoosh'); cue(st + lift, 'slide', { gain: 0.7, dur: 1.4 }); cue(st + fl, 'sparkle', { dur: 0.7 }); }

  // 3 · STEP ONE: grab something solid (gold step card)
  { const st = cut(2), grab = Wd('grab', 2) - st, solid = Wd('solid', 2) - st;
    add({ id: 'S03', at: st, cam: [540, 1100], note: 'step card 1 HOLD ON, hero grabs the couch', draw(lt, d, t) {
      K.livingRoom({});
      const g = eio(seg(lt, grab, grab + 0.5));
      const y = GROUND - 200 * (1 - g) - 40 * Math.sin(lt * 1.7) * (1 - g);
      K.person({ x: 430, y, h: 840, mood: g > 0.6 ? 'determined' : 'scared', look: [1, 0.4], blink: 0, lean: g > 0.6 ? -10 : 0, legs: { L: [14, 18], R: [-10, 22] }, arms: g > 0.4 ? { L: [-6, 14], R: [95, 30] } : { L: [-40, 34], R: [46, 30] } });
      K.stepCard(1, 'HOLD ON', 540, 300, eob(seg(lt, 0.05, 0.3)));
      if (lt > solid) K.check(880, 640, eob(seg(lt, solid, solid + 0.3)) * 0.9);
    } });
    cue(st, 'whoosh'); cue(st + 0.05, 'pop'); cue(st + solid, 'tock'); }

  // 4 · STEP TWO: windows and shelves will come down
  { const st = cut(3), win = Wd('windows', 3) - st, down = Wd('come', 3) - st;
    add({ id: 'S04', at: st, cam: [540, 1050], note: 'step card 2 STAY CLEAR, window + shelf get red X', draw(lt, d, t) {
      K.livingRoom({}); ctx.fillStyle = 'rgba(5,8,18,0.10)'; ctx.fillRect(-300, -300, W + 600, H + 600);
      K.person({ x: 300, y: GROUND - 340, h: 780, mood: 'worried', look: [1, -0.5], blink: 0, legs: { L: [16, 20], R: [-12, 24] }, arms: { L: [-34, 30], R: [40, 30] } });
      K.stepCard(2, 'STAY CLEAR', 540, 300, eob(seg(lt, 0.05, 0.3)));
      if (lt > win) K.cross(780, 560, eob(seg(lt, win, win + 0.3)));
      if (lt > down) { const w = Math.sin((lt - down) * 26) * 8 * Math.exp(-(lt - down) * 2); ctx.save(); ctx.translate(w, 0); K.windowPane(600, 360, 360, 420, false); ctx.restore(); downArrow(860, 900, 0.8, eob(seg(lt, down, down + 0.3)) * 0.85); }
    } });
    cue(st, 'whoosh'); cue(st + 0.05, 'pop'); cue(st + win, 'alarm', { dur: 1.0, gain: 0.5 }); cue(st + down, 'rumble', { gain: 0.55, dur: 1.2 }); }

  // 5 · STEP THREE: get under something sturdy
  { const st = cut(4), sturdy = Wd('sturdy', 4) - st, danger = Wd('danger', 4) - st;
    add({ id: 'S05', at: st, cam: [540, 1150], note: 'step card 3 TAKE COVER, hero crouches under the table', draw(lt, d, t) {
      K.livingRoom({});
      rr(280, 1050, 620, 44, 14); ctx.fillStyle = P.wood; ctx.fill(); ctx.strokeStyle = P.ink; ctx.lineWidth = 9; ctx.stroke();
      ctx.fillStyle = P.ink; ctx.fillRect(310, 1094, 40, 466); ctx.fillRect(830, 1094, 40, 466);
      const g = eio(seg(lt, sturdy - 0.6, sturdy + 0.3));
      K.person({ x: lerp(980, 560, g), y: GROUND, h: lerp(780, 460, g), mood: g > 0.6 ? 'determined' : 'worried', look: [0, -1], blink: 0, arms: { L: [-20, 60], R: [30, 60] } });
      K.stepCard(3, 'TAKE COVER', 540, 300, eob(seg(lt, 0.05, 0.3)));
      if (lt > sturdy) K.check(190, 700, eob(seg(lt, sturdy, sturdy + 0.3)));
      if (lt > danger) { book(760, 700, 0.9, 0.5 + 0.3 * Math.sin(lt * 2)); cushion(300, 640, 0.8, -0.4); }
    } });
    cue(st, 'whoosh'); cue(st + 0.05, 'pop'); cue(st + sturdy, 'gulp', { gain: 0.6 }); cue(st + danger, 'rumble', { gain: 0.6, dur: 1.4 }); }

  // 6 · everything you own floats above your head
  { const st = cut(5), dogW = Wd('dog', 5) - st, couchW = Wd('couch', 5) - st, head = Wd('head', 5) - st;
    add({ id: 'S06', at: st, cam: [540, 1000], note: 'dog, mug, books, couch all drifting near the ceiling', draw(lt, d, t) {
      K.livingRoom({}); ceilingLamp(540, 330);
      const b = Math.sin(lt * 1.4);
      K.person({ x: 540, y: GROUND - 430 - 30 * b, h: 760, mood: 'scared', look: [0, -1], blink: 0, legs: { L: [18, 24], R: [-14, 28] }, arms: { L: [-56, 40], R: [56, 40] } });
      if (lt > dogW) dog(250, 620 + 40 * b, 1, 0.18 * b);
      if (lt > dogW) mug(340, 470 + 50 * b, 1, 0.6 * b);
      if (lt > couchW) { ctx.save(); ctx.translate(0, 20 * b); K.couch(820, 1150, 0.7, false); ctx.restore(); }
      if (lt > couchW) cushion(760, 760 + 60 * b, 0.9, -0.5 * b);
      if (lt > head) K.counterPill('LOOSE THINGS', 540, 300, eob(seg(lt, head, head + 0.3)));
    } });
    cue(st, 'whoosh'); cue(st + dogW, 'boing', { gain: 0.5 }); cue(st + couchW, 'thud', { gain: 0.4 }); cue(st + head, 'pop'); }

  // 7 · gravity snaps back — everything crashes down
  { const st = cut(6), snap = Wd('snaps', 6) - st, crash = Wd('crashes', 6) - st;
    add({ id: 'S07', at: st, cam: [540, 1100], zoom: 0.08, note: '35.0s pill, everything SLAMS down on "crashes"', draw(lt, d, t) {
      K.livingRoom({});
      const fall = lt > snap;
      const p = fall ? eio(seg(lt, snap, snap + 0.55)) : 0;
      const b = fall ? 0 : Math.sin(lt * 1.4);
      K.person({ x: 540, y: GROUND - (fall ? 430 * (1 - p) : 430 + 30 * b), h: 760, mood: 'scared', look: [0, fall ? 0.6 : -1], blink: 0, legs: fall && p > 0.9 ? { L: [10, 8], R: [-8, 10] } : { L: [18, 24], R: [-14, 28] }, arms: fall ? { L: [-70, 50], R: [70, 50] } : { L: [-56, 40], R: [56, 40] } });
      if (fall) { dog(250, lerp(620, GROUND - 60, p), 1, 0.2 * (1 - p)); mug(340, lerp(470, GROUND - 60, p), 1, 1.4 * p); cushion(800, lerp(760, GROUND - 80, p), 0.9, 0.6 * p); if (p > 0.92) { for (let i = 0; i < 5; i++) circle(300 + i * 130, GROUND + 10, 26 + rnd(i) * 18, 'rgba(242,178,62,0.5)'); } }
      K.counterPill(lt > snap ? 'GRAVITY: ON' : '35.0 SECONDS', 540, 300, eob(seg(lt, 0.05, 0.3)));
      if (lt > crash && lt < crash + 0.45 && Math.floor(lt * 20) % 2 === 0) { ctx.fillStyle = 'rgba(255,255,255,0.22)'; ctx.fillRect(-300, -300, W + 600, H + 600); }
      K.cinemaBars(0.5 * (1 - eo(seg(lt, crash, crash + 0.6))));
    } });
    cue(st, 'whoosh'); cue(st + snap, 'rumble', { gain: 0.8, dur: 1.6 }); cue(st + crash, 'slam', { gain: 1.0 }); cue(st + crash + 0.1, 'crash', { gain: 0.8 }); }

  // 8 · end card: big check, daylight, hero is fine
  { const st = Math.max(Le(6) + 0.1, T.dur - 2.6);
    add({ id: 'S08', at: st, cam: [540, 1050], zoom: 0.1, note: 'daylight room, hero safe, big green check, loop line', draw(lt, d, t) {
      K.livingRoom({});
      K.person({ x: 460, y: GROUND, h: 860, mood: 'happy', look: [0.4, 0], blink: blink(t), arms: { L: [-20, 30], R: [130, 60] } });
      K.check(830, 620, eob(seg(lt, 0.2, 0.5)) * 1.3);
      K.counterPill('SAFE!', 540, 300, eob(seg(lt, 0.35, 0.6)));
    } });
    cue(st, 'whoosh'); cue(st + 0.3, 'sparkle', { dur: 1.0 }); }

  return { shots: S, cues: CUES };
}
