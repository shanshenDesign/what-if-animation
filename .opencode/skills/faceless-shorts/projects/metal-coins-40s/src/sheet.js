// The Stick Story style sheet for METAL COINS ONLY: 40S, drawn with the style's own kit.
import { ctx, rr, line } from './core/lib.js';
import { startBoard, panel, frame, cell, small, swatches, rules } from './core/board.js';
import * as K from './core/kit.js';
import { street, pouch, coin, coinPile, sack, handcart, brassScale, cup } from './shots.js';
const { P } = K;

const cv = document.getElementById('cv');
await document.fonts.load('900 40px Inter'); await document.fonts.load('800 40px Inter');
startBoard(cv, { title: 'METAL COINS ONLY: 40S', accent: P.gold });

// 1 · hero frame
let b = panel(20, 80, 560, 520, 1, 'HERO FRAME');
frame(b.x + 6, b.y, 240, () => {
  street();
  K.person({ x: 470, y: K.GROUND, h: 840, dir: 1, mood: 'happy', look: [0.3, -0.3],
    arms: { L: [18, -4], R: [28, -8] }, legs: { L: [7, 6], R: [-7, 8] } });
  pouch(470, 1120, 0.95);
  coinPile(760, 1560, 5, 0.8);
  K.counterPill('FRIDAY: PAID', 540, 300, 1);
  K.captionBar([{ txt: 'Every' }, { txt: 'payment', hi: 1 }, { txt: 'metal.' }], 540, K.CAPLOOK.y, 1.05);
});
small('ONE STREET, ONE HERO, ALL VIDEO.', b.x + 270, b.y + 40, 'left', 17);
small('EVERY PAYMENT IS A COIN: BRONZE,\\nSILVER, COPPER — FLAT, WITH A STAMP.', b.x + 270, b.y + 130, 'left', 17);
small('GOLD PILLS CARRY THE STATE:\\nNO WALLETS, RENT DAY, POCKET FAIL.', b.x + 270, b.y + 240, 'left', 17);
small('CUTAWAYS: COUNTER, BELT, BANK,\\nAND THE FLOOR THAT TEARS OPEN.', b.x + 270, b.y + 340, 'left', 17);

// 2 · palette
b = panel(590, 80, 660, 520, 2, 'PALETTE');
const yy = swatches(b, [['WALL', P.wall], ['FLOOR', P.floor], ['INK', P.ink], ['GOLD', P.gold],
  ['BRONZE', '#F2C063'], ['SILVER', '#E4E9EF'], ['COPPER', '#EE9A5C'], ['SKY', P.sky]]);
['PEOPLE ARE ALWAYS INK BLACK. COLOUR LIVES IN THE SET.',
 'METAL TONES ARE ONLY FOR MONEY AND BELT BUCKLES.',
 'NAVY = THE OLD CARD WORLD. RED = THE RIP.']
  .forEach((t, i) => small(t, b.x + 4, yy + 20 + i * 40, 'left', 16, '#E6E7EA'));
// expressions strip (the eyes are the style's signature)
ctx.fillStyle = P.wall; ctx.beginPath(); ctx.roundRect(b.x, yy + 140, b.w, 150, 14); ctx.fill();
['calm', 'happy', 'worried', 'scared', 'determined', 'sleepy'].forEach((m, i) => cell(b.x + 55 + i * 104, yy + 195, 0.36, () => K.bigHead(0, 0, 100, { mood: m }), m.toUpperCase(), 72));

// 3 · components
b = panel(1260, 80, 640, 520, 3, 'COMPONENTS');
ctx.fillStyle = P.wall; ctx.beginPath(); ctx.roundRect(b.x, b.y, b.w, b.h, 14); ctx.fill();
const gx = (i) => b.x + 75 + i * 150, gy = (r) => b.y + 140 + r * 195;
cell(gx(0), gy(0) + 80, 0.38, () => K.person({ x: 0, y: 0, h: 520, mood: 'worried', arms: { L: [-6, 14], R: [10, 16] } }), 'HERO', 30);
cell(gx(1), gy(0) + 80, 0.38, () => K.person({ x: 0, y: 0, h: 520, mood: 'determined', walk: 1.2, dir: -1 }), 'WALKING', 30);
cell(gx(2), gy(0) + 40, 0.6, () => coin(0, 0, 60, { metal: 'bronze' }), 'COIN', 70);
cell(gx(3), gy(0) + 50, 0.6, () => pouch(0, 0, 0.8), 'POUCH', 70);
cell(gx(0), gy(1) + 60, 0.4, () => sack(0, 0, 0.6), 'SACK', 60);
cell(gx(1), gy(1) + 70, 0.32, () => handcart(0, 0, 1), 'HANDCART', 50);
cell(gx(2), gy(1) + 60, 0.42, () => brassScale(0, 0, 0.9, { tilt: 0.08 }), 'BRASS SCALE', 60);
cell(gx(3), gy(1) + 70, 0.62, () => { K.check(-46, -20, 0.7); K.cross(54, -20, 0.7); }, 'YES / NO', 60);

// 4 · scenes
b = panel(20, 610, 760, 456, 4, 'SCENES');
const sw = 200, sx = (i) => b.x + 20 + i * (sw + 45);
frame(sx(0), b.y, sw, () => {
  ctx.fillStyle = P.wall; ctx.fillRect(-300, -300, 1680, K.FLOOR + 300);
  ctx.fillStyle = P.floor; ctx.fillRect(-300, K.FLOOR, 1680, 900);
  K.windowPane(770, 340, 300, 330);
  K.counter(560, K.FLOOR + 40, 460);
  cup(610, 1060, 1);
  pouch(760, 1046, 0.7, {});
  K.person({ x: 320, y: K.GROUND, h: 820, dir: 1, mood: 'happy', look: [0.7, 0.4],
    arms: { L: [64, 22], R: [86, 10] }, legs: { L: [7, 6], R: [-7, 8] } });
});
frame(sx(1), b.y, sw, () => {
  ctx.fillStyle = P.wall; ctx.fillRect(-300, -300, 1680, K.FLOOR + 300);
  ctx.fillStyle = P.floor; ctx.fillRect(-300, K.FLOOR, 1680, 900);
  rr(430, 300, 300, 110, 18); ctx.fillStyle = P.navy; ctx.fill();
  ctx.font = '900 64px Inter'; ctx.fillStyle = P.gold; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText('BANK', 580, 358);
  ctx.save(); ctx.beginPath(); ctx.rect(-300, -300, 1680, 1390); ctx.clip();
  K.person({ x: 780, y: 1560, h: 780, dir: -1, mood: 'calm', look: [-0.6, 0.3], arms: { L: [64, 26], R: [78, 14] } });
  ctx.restore();
  K.counter(140, K.FLOOR + 40, 780);
  brassScale(470, 1056, 1, {
    tilt: 0.05,
    leftDraw: (px, py) => { rr(px - 56, py - 84, 112, 96, 14); ctx.fillStyle = '#8F959E'; ctx.fill(); ctx.strokeStyle = P.ink; ctx.lineWidth = 7; ctx.stroke(); coinPile(px, py - 8, 5, 0.62); },
    rightDraw: (px, py) => { for (let i = 0; i < 3; i++) { rr(px - 40 + i * 6, py - 6 - i * 30, 74, 28, 8); ctx.fillStyle = '#596075'; ctx.fill(); ctx.strokeStyle = P.ink; ctx.lineWidth = 6; ctx.stroke(); } },
  });
  K.person({ x: 1010, y: K.GROUND, h: 780, dir: -1, mood: 'worried', look: [-0.6, -0.1],
    arms: { L: [58, 40], R: [70, 30] }, hold: (x, y) => sack(x, y - 40, 0.42) });
});
frame(sx(2), b.y, sw, () => {
  ctx.fillStyle = P.wall; ctx.fillRect(-300, -300, 1680, 1450);
  ctx.fillStyle = P.floor; ctx.fillRect(-300, 1450, 1680, 900);
  K.person({ x: 540, y: 1450, h: 840, dir: 1, mood: 'scared', look: [0.1, 0.8],
    lean: -6, arms: { L: [-70, 34], R: [78, 30] } });
  ell(540, 1462, 240, 70, '#23202A');
  ctx.beginPath(); ctx.ellipse(540, 1462, 240, 70, 0, 0.15 * Math.PI, 0.85 * Math.PI);
  ctx.strokeStyle = '#8A6238'; ctx.lineWidth = 22; ctx.stroke();
  coinPile(540, 1640, 6, 0.8);
});
['(A) CAFÉ · THE DROP', '(B) BANK · THE SCALES', '(C) THE RIP'].forEach((t, i) => small(t, sx(i) + sw / 2, b.y + sw * 16 / 9 + 26, 'center', 15));

// 5 · captions
b = panel(790, 610, 520, 456, 5, 'CAPTIONS');
ctx.fillStyle = P.wall; ctx.fillRect(b.x, b.y, b.w, b.h - 10);
[[[{ txt: 'You grab a' }, { txt: 'coffee,', hi: 1 }, { txt: 'drop' }], 70],
 [[{ txt: 'metal' }, { txt: 'handcart', hi: 1 }, { txt: 'of' }], 175],
 [[{ txt: 'Then your' }, { txt: 'pockets', hi: 1 }, { txt: 'rip' }], 280]]
  .forEach(([w, y]) => cell(b.x + b.w / 2, b.y + y, 0.42, () => K.captionBar(w, 0, 0), null));
small('SENTENCE CASE · 2-4 WORDS · ONE GOLD WORD', b.x + b.w / 2, b.y + b.h - 26, 'center', 14, '#5A5560');

// 6 · rules
b = panel(1320, 610, 580, 456, 6, 'RULES');
rules(b, ['ONE STREET ALL VIDEO: SHOPFRONTS AND SIDEWALK.',
  'CUTAWAYS ONLY FOR COUNTER, BELT, SCALE, FLOOR.',
  'METAL TONES ARE ONLY FOR MONEY.',
  'GOLD PILLS CARRY STATE: PAID, RENT DAY, FAIL.',
  'EYES ACT FIRST: LOOK, THEN REACT.',
  'SOFT ROUND SOUND: TOCK, PLOP, ZIP, BOING.',
  'MOOD: HEAVY AT FIRST, THEN GLEEFUL.'], b.y + 26, 16, 52);
window.SHEET_READY = true;
