// The Stick Story style sheet for LOCKED DOORS: 45S, drawn with the style's own kit.
import { ctx, rr, line } from './core/lib.js';
import { startBoard, panel, frame, cell, small, swatches, rules } from './core/board.js';
import * as K from './core/kit.js';
import { street, shopDoor, padlock, kettle, van, DOORS } from './shots.js';
const { P } = K;

const cv = document.getElementById('cv');
await document.fonts.load('900 40px Inter'); await document.fonts.load('800 40px Inter');
startBoard(cv, { title: 'LOCKED DOORS: 45S', accent: P.gold });

// 1 · hero frame
let b = panel(20, 80, 560, 520, 1, 'HERO FRAME');
frame(b.x + 6, b.y, 240, () => {
  street({ locks: true });
  for (const d of DOORS) padlock(d.x, K.FLOOR - 186, 0.85, 1);
  K.person({ x: 470, y: K.GROUND, h: 840, dir: 1, mood: 'worried', look: [0.6, 0.6], legs: { L: [30, 40], R: [-24, 46] } });
  K.counterPill('DOORS: LOCKED', 540, 300, 1);
  K.captionBar([{ txt: 'Every' }, { txt: 'door', hi: 1 }, { txt: 'shut.' }], 540, K.CAPLOOK.y, 1.05);
});
small('ONE STREET, ONE HERO, ALL VIDEO.', b.x + 270, b.y + 40, 'left', 17);
small('EVERY DOOR GETS A GOLD PADLOCK\nTHAT POPS ON "CLICKS".', b.x + 270, b.y + 130, 'left', 17);
small('GOLD PILLS CARRY THE STATE:\nLOCKED, STUCK, OPEN.', b.x + 270, b.y + 240, 'left', 17);
small('THE COUNTDOWN PILL RUNS\n59:59 → 00:00 ACROSS SHOTS.', b.x + 270, b.y + 340, 'left', 17);

// 2 · palette
b = panel(590, 80, 660, 520, 2, 'PALETTE');
const yy = swatches(b, [['WALL', P.wall], ['FLOOR', P.floor], ['INK', P.ink], ['GOLD', P.gold], ['NAVY', P.navy], ['DANGER', P.red], ['SAFE', P.green], ['SKY', P.sky]]);
['PEOPLE ARE ALWAYS INK BLACK. COLOUR LIVES IN THE STREET.',
 'GOLD IS ONLY FOR LOCKS, TIME AND KEY WORDS.',
 'STEEL GREY = SEALED. RED = THE COUNTDOWN.']
  .forEach((t, i) => small(t, b.x + 4, yy + 20 + i * 40, 'left', 16, '#E6E7EA'));
// expressions strip (the eyes are the style's signature)
ctx.fillStyle = P.wall; ctx.beginPath(); ctx.roundRect(b.x, yy + 140, b.w, 150, 14); ctx.fill();
['calm', 'happy', 'worried', 'scared', 'determined', 'sleepy'].forEach((m, i) => cell(b.x + 55 + i * 104, yy + 195, 0.36, () => K.bigHead(0, 0, 100, { mood: m }), m.toUpperCase(), 72));

// 3 · components
b = panel(1260, 80, 640, 520, 3, 'COMPONENTS');
ctx.fillStyle = P.wall; ctx.beginPath(); ctx.roundRect(b.x, b.y, b.w, b.h, 14); ctx.fill();
const gx = (i) => b.x + 75 + i * 150, gy = (r) => b.y + 140 + r * 195;
cell(gx(0), gy(0) + 80, 0.38, () => K.person({ x: 0, y: 0, h: 520, mood: 'scared', arms: { L: [-56, 40], R: [64, 34] } }), 'HERO', 30);
cell(gx(1), gy(0) + 80, 0.38, () => K.person({ x: 0, y: 0, h: 520, mood: 'worried', walk: 1.2, dir: -1 }), 'WALKING', 30);
cell(gx(2), gy(0), 0.55, () => K.bigHead(0, -20, 120, { mood: 'scared' }), 'CLOSE-UP', 90);
cell(gx(3), gy(0), 0.5, () => K.thought(0, -40, 0.8, () => K.phone(0, -20, 0.5), 60, 120), 'THOUGHT', 90);
cell(gx(0), gy(1) + 60, 0.4, () => shopDoor(0, 320, 140, 400), 'SHOP DOOR', 30);
cell(gx(1), gy(1) + 40, 0.62, () => padlock(0, 0, 1), 'PADLOCK', 30);
cell(gx(2), gy(1) + 70, 0.3, () => van(0, 60, 1), 'VAN', 30);
cell(gx(3), gy(1) + 60, 0.5, () => { K.check(-55, 0, 0.8); K.cross(55, 0, 0.8); }, 'YES / NO', 80);

// 4 · scenes
b = panel(20, 610, 760, 456, 4, 'SCENES');
const sw = 200, sx = (i) => b.x + 20 + i * (sw + 45);
frame(sx(0), b.y, sw, () => { street({ locks: true }); for (const d of DOORS) padlock(d.x, K.FLOOR - 186, 0.85, 1); K.person({ x: 470, y: K.GROUND, h: 700, mood: 'worried', look: [0.15, -1] }); });
frame(sx(1), b.y, sw, () => {
  ctx.fillStyle = P.wall; ctx.fillRect(-300, -300, 1680, K.FLOOR + 300);
  ctx.fillStyle = P.floor; ctx.fillRect(-300, K.FLOOR, 1680, 900);
  K.door(240, K.FLOOR + 40, null, 0); padlock(240, 1130, 1, 1);
  K.counter(620, K.FLOOR + 60, 420); kettle(760, 1078, 1.4);
  K.person({ x: 520, y: K.GROUND, h: 700, dir: -1, mood: 'worried', look: [-0.7, 0.2], arms: { L: [64, 18], R: [74, 12] } });
});
frame(sx(2), b.y, sw, () => {
  ctx.fillStyle = P.wall; ctx.fillRect(-300, -300, 1680, K.FLOOR + 300);
  ctx.fillStyle = P.floor; ctx.fillRect(-300, K.FLOOR, 1680, 900);
  K.door(770, K.FLOOR + 40, null, 0);
  rr(560, 1040, 150, 100, 16); ctx.fillStyle = '#8E6142'; ctx.fill();
  rr(590, 1062, 300, 56, 28); ctx.fillStyle = P.gold; ctx.fill();
  K.person({ x: 400, y: K.GROUND, h: 760, dir: 1, mood: 'scared', look: [0.7, 0.1], lean: 7, arms: { L: [74, 10], R: [84, 6] } });
  K.cross(930, 940, 0.8);
});
['(A) STREET · ALL LOCKED', '(B) KITCHEN · KETTLE', '(C) LATCH · STUCK'].forEach((t, i) => small(t, sx(i) + sw / 2, b.y + sw * 16 / 9 + 26, 'center', 15));

// 5 · captions
b = panel(790, 610, 520, 456, 5, 'CAPTIONS');
ctx.fillStyle = P.wall; ctx.fillRect(b.x, b.y, b.w, b.h - 10);
[[[{ txt: 'Every' }, { txt: 'door', hi: 1 }, { txt: 'shut.' }], 70],
 [[{ txt: 'Wrong' }, { txt: 'side', hi: 1 }, { txt: 'of glass.' }], 175],
 [[{ txt: 'One' }, { txt: 'stuck', hi: 1 }, { txt: 'latch.' }], 280]]
  .forEach(([w, y]) => cell(b.x + b.w / 2, b.y + y, 0.42, () => K.captionBar(w, 0, 0), null));
small('SENTENCE CASE · 2-4 WORDS · ONE GOLD WORD', b.x + b.w / 2, b.y + b.h - 26, 'center', 14, '#5A5560');

// 6 · rules
b = panel(1320, 610, 580, 456, 6, 'RULES');
rules(b, ['ONE STREET ALL VIDEO: DOORS, GLASS, SCREENS.', 'CUTAWAYS ONLY FOR LIFT, KITCHEN, CLOCK, LATCH.', 'GOLD PILLS CARRY LOCKED / STUCK / OPEN.', 'EYES ACT FIRST: LOOK, THEN REACT.', 'CINEMA BARS ONLY ON THE QUIET + THE CLOCK.', 'SOFT CARTOON SOUND: TOCK, THUD, BOING, SLAM.', 'MOOD: CREEPING, THEN GLEEFUL.'], b.y + 26, 16, 52);
window.SHEET_READY = true;
