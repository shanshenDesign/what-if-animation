// The Stick Story style sheet for HEAVY SHADOWS: 50 KG, drawn with the style's own kit.
import { ctx } from './core/lib.js';
import { startBoard, panel, frame, cell, small, swatches, rules } from './core/board.js';
import * as K from './core/kit.js';
import { street, sunDisc, castShadow, blobShadow, umbrella, darkDoor } from './shots.js';
const { P } = K;

const cv = document.getElementById('cv');
await document.fonts.load('900 40px Inter'); await document.fonts.load('800 40px Inter');
startBoard(cv, { title: 'HEAVY SHADOWS: 50 KG', accent: P.gold });

// 1 · hero frame
let b = panel(20, 80, 560, 520, 1, 'HERO FRAME');
frame(b.x + 6, b.y, 240, () => {
  street({ sun: () => sunDisc(820, 250, 92, {}) });
  K.person({ x: 470, y: K.GROUND, h: 840, dir: 1, mood: 'worried', look: [0.6, 0.6], legs: { L: [30, 40], R: [-24, 46] } });
  castShadow(470, K.GROUND + 18, 520, -1, 0.6);
  K.counterPill('SHADOW: 50 KG', 540, 300, 1);
  K.captionBar([{ txt: 'Fifty' }, { txt: 'kilograms', hi: 1 }, { txt: 'on you.' }], 540, K.CAPLOOK.y, 1.05);
});
small('ONE HERO, ONE STREET, ALL VIDEO.', b.x + 270, b.y + 40, 'left', 17);
small('THE SHADOW ACTS: TINY AT NOON,\nTEN FEET AT 4 PM, GONE AT 0 KG.', b.x + 270, b.y + 130, 'left', 17);
small('GOLD PILLS CARRY THE CLOCK\nAND THE WEIGHT.', b.x + 270, b.y + 240, 'left', 17);
small('UMBRELLA = ZERO KG.\nA CLOUD PUTS IT ALL BACK.', b.x + 270, b.y + 340, 'left', 17);

// 2 · palette
b = panel(590, 80, 660, 520, 2, 'PALETTE');
const yy = swatches(b, [['WALL', P.wall], ['FLOOR', P.floor], ['INK', P.ink], ['GOLD', P.gold], ['NAVY', P.navy], ['DANGER', P.red], ['SAFE', P.green], ['SKY', P.sky]]);
['PEOPLE ARE ALWAYS INK BLACK. COLOUR LIVES IN THE STREET.',
 'GOLD IS ONLY FOR WEIGHT, TIME AND KEY WORDS.',
 'NO NIGHT SET: THE CLOUD IS THE DARK.']
  .forEach((t, i) => small(t, b.x + 4, yy + 20 + i * 40, 'left', 16, '#E6E7EA'));
// expressions strip (the eyes are the style's signature)
ctx.fillStyle = P.wall; ctx.beginPath(); ctx.roundRect(b.x, yy + 140, b.w, 150, 14); ctx.fill();
['calm', 'happy', 'worried', 'scared', 'determined', 'sleepy'].forEach((m, i) => cell(b.x + 55 + i * 104, yy + 195, 0.36, () => K.bigHead(0, 0, 100, { mood: m }), m.toUpperCase(), 72));

// 3 · components
b = panel(1260, 80, 640, 520, 3, 'COMPONENTS');
ctx.fillStyle = P.wall; ctx.beginPath(); ctx.roundRect(b.x, b.y, b.w, b.h, 14); ctx.fill();
const gx = (i) => b.x + 75 + i * 150, gy = (r) => b.y + 140 + r * 195;
cell(gx(0), gy(0) + 80, 0.38, () => K.person({ x: 0, y: 0, h: 520, mood: 'happy', arms: { L: [-30, 40], R: [150, 20] } }), 'HERO', 30);
cell(gx(1), gy(0) + 80, 0.38, () => K.person({ x: 0, y: 0, h: 520, mood: 'scared', walk: 1.2, dir: -1 }), 'WALKING', 30);
cell(gx(2), gy(0), 0.55, () => K.bigHead(0, -20, 120, { mood: 'determined' }), 'CLOSE-UP', 90);
cell(gx(3), gy(0), 0.5, () => K.thought(0, -40, 0.8, () => K.bottle(0, -20, 0.6), 60, 120), 'THOUGHT', 90);
cell(gx(0), gy(1) + 20, 0.5, () => castShadow(150, 40, 420, -1, 0.6), 'CAST SHADOW', 70);
cell(gx(1), gy(1) + 10, 0.4, () => umbrella(0, 140, 1, 1), 'UMBRELLA', 70);
cell(gx(2), gy(1) - 10, 0.55, () => { K.check(-55, 0, 0.8); K.cross(55, 0, 0.8); }, 'YES / NO', 80);
cell(gx(3), gy(1), 0.5, () => K.counterPill('50 KG', 0, 0, 1), 'WEIGHT TAG', 70);

// 4 · scenes
b = panel(20, 610, 760, 456, 4, 'SCENES');
const sw = 200, sx = (i) => b.x + 20 + i * (sw + 45);
frame(sx(0), b.y, sw, () => { street({ sun: () => sunDisc(470, 250, 100, {}) }); K.person({ x: 470, y: K.GROUND, h: 700, mood: 'calm', look: [0.15, -1] }); blobShadow(470, K.GROUND + 16, 132, 0.5); });
frame(sx(1), b.y, sw, () => { street({ sun: () => sunDisc(966, 1180, 88, { warm: 1 }) }); K.person({ x: 560, y: K.GROUND, h: 700, mood: 'worried', look: [-0.7, 0.3] }); castShadow(560, K.GROUND + 18, 520, -1, 0.6); });
frame(sx(2), b.y, sw, () => { street({ sun: () => sunDisc(966, 1180, 88, { warm: 1 }) }); darkDoor(170, K.FLOOR + 30); K.person({ x: 620, y: K.GROUND, h: 700, mood: 'happy', look: [0.4, -0.5], arms: { L: [-8, 16], R: [96, 34] }, hold: (x, y) => umbrella(x + 6, y - 30, 0.9, 1) }); });
['(A) STREET · NOON', '(B) STREET · 4:00 PM', '(C) UNDER THE UMBRELLA'].forEach((t, i) => small(t, sx(i) + sw / 2, b.y + sw * 16 / 9 + 26, 'center', 15));

// 5 · captions
b = panel(790, 610, 520, 456, 5, 'CAPTIONS');
ctx.fillStyle = P.wall; ctx.fillRect(b.x, b.y, b.w, b.h - 10);
[[[{ txt: 'Fifty' }, { txt: 'kilograms', hi: 1 }], 70], [[{ txt: 'Ten feet' }, { txt: 'behind' }, { txt: 'you.', hi: 1 }], 175], [[{ txt: 'Shadow:' }, { txt: 'zero.', hi: 1 }], 280]]
  .forEach(([w, y]) => cell(b.x + b.w / 2, b.y + y, 0.42, () => K.captionBar(w, 0, 0), null));
small('SENTENCE CASE · 2-4 WORDS · ONE GOLD WORD', b.x + b.w / 2, b.y + b.h - 26, 'center', 14, '#5A5560');

// 6 · rules
b = panel(1320, 610, 580, 456, 6, 'RULES');
rules(b, ['ONE STREET ALL VIDEO: NOON, 4 PM, CLOUD.', 'THE SHADOW IS THE CHARACTER: TINY, 10 FT, GONE.', 'GOLD PILLS CARRY TIME AND KILOGRAMS.', 'EYES ACT FIRST: LOOK, THEN REACT.', 'CINEMA BARS ONLY ON THE YANK.', 'SOFT CARTOON SOUND: POP, THUD, SLIDE, SLAM.', 'MOOD: TENSE, CLEVER, A LITTLE FUNNY.'], b.y + 26, 16, 52);
window.SHEET_READY = true;
