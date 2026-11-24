// Boot: fonts → script + timing → captions → shots. Then draw(t) renders film time t (pure function of t).
// window.OP is the API tools/capture.mjs drives: ready, bootError, duration(), draw(t), frame(t, q), cues(), shots().
// Locked-doors-45s: the light tells the story — a steel wash when the lifts stop, kettle-warm in the kitchen,
// diesel grey at the curb, a red alarm under the countdown, dusk when the street goes quiet, and gold the
// second every lock opens. Nine word-timed camera shakes land on the impacts.
import { W, H, setCtx, ctx, clamp, eo, eio, seg } from './core/lib.js';
import { T, Wd, Le, loadTiming } from './core/timing.js';
import { buildCaptions, drawCaption, captionList } from './core/captions.js';
import { buildShots } from './shots.js';

const cv = document.getElementById('cv');
setCtx(cv.getContext('2d'));
const OP = (window.OP = { ready: false });

let IMPACTS = [], WASHES = [], ENDCARD = 0;   // filled once in boot (Wd throws early if a word went missing)
const at = (i) => T.lines[i].start;

function draw(t) {
  t = clamp(t, 0, T.dur - 1e-4);
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.letterSpacing = '0px';
  ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);

  // camera: a short shake on each impact, then the usual punch-in + slow push
  let sx = 0, sy = 0;
  for (const s of IMPACTS) if (t > s.t && t < s.t + s.dur) {
    const p = (t - s.t) / s.dur, a = s.amp * (1 - p);
    sx += Math.sin((t - s.t) * 66) * a; sy += Math.cos((t - s.t) * 52) * a * 0.6;
  }
  ctx.save(); ctx.translate(sx, sy);

  const S = OP._shots; let i = S.length - 1; while (i > 0 && S[i].at > t) i--;
  const sh = S[i], end = i < S.length - 1 ? S[i + 1].at : T.dur, d = end - sh.at, lt = t - sh.at;
  const punch = 1 + 0.06 * (1 - eo(clamp(lt / 0.25)));
  const drift = 1 + (sh.zoom ?? 0.06) * eio(clamp(lt / d));
  const [cx, cy] = sh.cam || [540, 900];
  ctx.save(); ctx.translate(cx, cy); ctx.scale(punch * drift, punch * drift); ctx.translate(-cx, -cy);
  sh.draw(lt, d, t);
  ctx.restore();
  ctx.restore();

  // ── the light washes: one per beat, crossfading over 0.5 s so no cut ever hard-flashes ──
  for (const w of WASHES) {
    const a = clamp(seg(t, w.t0, w.t0 + 0.5)) * (1 - clamp(seg(t, w.t1 - 0.5, w.t1)));
    if (a <= 0.004) continue;
    ctx.fillStyle = `rgba(${w.c},${(w.a * a).toFixed(3)})`;
    ctx.fillRect(-300, -300, W + 600, H + 600);
  }
  ctx.globalAlpha = 1;

  // fade from / to black on the first and last 0.25 s
  const fade = Math.min(clamp(t / 0.25), clamp((T.dur - t) / 0.35));
  if (fade < 1) { ctx.fillStyle = '#000'; ctx.globalAlpha = 1 - fade; ctx.fillRect(0, 0, W, H); ctx.globalAlpha = 1; }
  drawCaption(t);
}

(async () => {
  try {
    await document.fonts.load('900 100px Inter');
    const script = await (await fetch('script.json', { cache: 'no-store' })).json();
    await loadTiming();
    buildCaptions(script);
    const { shots, cues } = buildShots();
    shots.sort((a, b) => a.at - b.at);
    ENDCARD = Math.max(Le(9) + 0.1, T.dur - 2.6);
    IMPACTS = [
      { t: Wd('once', 0), amp: 18, dur: 0.50 },     // every door clicks shut at once
      { t: Wd('sealed', 1), amp: 12, dur: 0.40 },   // the lift doors seal
      { t: Wd('glass', 2), amp: 10, dur: 0.35 },    // palms on the glass
      { t: Wd('door', 3), amp: 10, dur: 0.40 },     // the kitchen door, locked
      { t: Wd('holds', 5), amp: 12, dur: 0.40 },    // every window holds
      { t: Wd('ticks', 6), amp: 14, dur: 0.45 },    // the countdown ticks
      { t: Wd('quiet', 7), amp: 16, dur: 0.50 },    // the street goes quiet
      { t: Wd('together', 8), amp: 22, dur: 0.55 }, // every lock opens together
      { t: Wd('budge', 9), amp: 18, dur: 0.50 },    // the latch won't budge
      { t: ENDCARD + 0.3, amp: 10, dur: 0.40 },     // the end card lands
    ];
    WASHES = [
      { t0: Wd('freeze', 1) - 0.3, t1: Wd('simmers', 3) - 0.3, c: '124,136,160', a: 0.22 },  // steel: the lift stops
      { t0: Wd('simmers', 3) - 0.3, t1: Wd('idling', 4) - 0.3, c: '242,178,62', a: 0.16 },   // kettle-warm
      { t0: Wd('idling', 4) - 0.3, t1: Wd('checks', 5) - 0.3, c: '110,120,142', a: 0.18 },   // diesel grey
      { t0: Wd('ticks', 6) - 0.3, t1: Wd('quiet', 7) - 0.3, c: '200,70,60', a: 0.20 },       // red alarm
      { t0: Wd('quiet', 7) - 0.3, t1: Wd('open', 8) - 0.3, c: '30,36,66', a: 0.36 },         // dusk: the street waits
      { t0: Wd('open', 8) - 0.2, t1: Wd('stuck', 9) - 0.3, c: '242,178,62', a: 0.20 },       // gold: every lock opens
      { t0: Wd('stuck', 9) - 0.3, t1: ENDCARD - 0.3, c: '124,136,160', a: 0.20 },            // steel: the one stuck latch
      { t0: ENDCARD - 0.2, t1: T.dur, c: '242,178,62', a: 0.14 },                            // the end card
    ];
    OP._shots = shots; OP.script = script;
    OP.duration = () => T.dur;
    OP.draw = draw;
    OP.frame = (t, q = 0.92) => { draw(t); return cv.toDataURL('image/jpeg', q); };
    OP.shots = () => shots.map((s, i) => ({ id: s.id, at: +s.at.toFixed(3), end: +(i < shots.length - 1 ? shots[i + 1].at : T.dur).toFixed(3), note: s.note || '' }));
    OP.captions = () => captionList().map((c) => ({ s: +c.s.toFixed(3), e: +c.e.toFixed(3), text: c.words.map((w) => (w.hi ? '*' : '') + w.txt).join(' ') }));
    OP.cues = () => cues.slice().sort((a, b) => a.t - b.t);
    OP.ready = true;
    // preview mode (not capture): play in real time, ?t=12.3 to hold a frame
    const q = new URLSearchParams(location.search);
    if (!q.has('capture')) {
      if (q.has('t')) draw(+q.get('t'));
      else {
        const audio = new Audio('data/mix.wav'); let t0 = null;
        const btn = document.getElementById('play'); btn.hidden = false;
        btn.onclick = () => { btn.hidden = true; t0 = performance.now(); audio.currentTime = 0; audio.play().catch(() => {}); };
        const loop = (now) => { const t = t0 == null ? 0 : (now - t0) / 1000; draw(t0 == null ? 0 : t); if (t0 != null && t > T.dur) { t0 = null; btn.hidden = false; } requestAnimationFrame(loop); };
        requestAnimationFrame(loop);
      }
    }
  } catch (e) { OP.bootError = String(e && e.stack || e); console.error(e); }
})();
