// Boot: fonts → script + timing → captions → shots. Then draw(t) renders film time t (pure function of t).
// window.OP is the API tools/capture.mjs drives: ready, bootError, duration(), draw(t), frame(t, q), cues(), shots().
// Heavy-shadows-35s: the light tells the story — a white noon wash from straight above, a warm low-sun wash
// from the right for the 4:00 PM beat, a gold relief glow while the shadow reads 0 kg, and a grey dim the
// moment the cloud covers the sun. Four short camera shakes land on the impacts (locks / yanks / sidewalk / slam).
import { W, H, setCtx, ctx, clamp, eo, eio, seg } from './core/lib.js';
import { T, Wd, loadTiming } from './core/timing.js';
import { buildCaptions, drawCaption, captionList } from './core/captions.js';
import { buildShots } from './shots.js';

const cv = document.getElementById('cv');
setCtx(cv.getContext('2d'));
const OP = (window.OP = { ready: false });

let IMPACTS = [], ZERO = 0, CLOUD = 0;              // filled once in boot (Wd throws early if a word went missing)
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

  // ── the light washes ──
  const noon = clamp(seg(t, at(1) - 0.1, at(1) + 0.7)) * (1 - clamp(seg(t, at(3) - 0.7, at(3) - 0.1)));
  const warm = clamp(seg(t, at(3) - 0.2, at(3) + 0.9)) * (1 - clamp(seg(t, at(5) - 0.8, at(5) - 0.1)));
  const relief = clamp(seg(t, ZERO, ZERO + 0.6)) * (1 - clamp(seg(t, CLOUD, CLOUD + 0.5)));
  const dim = clamp(seg(t, CLOUD, CLOUD + 1.1));
  if (noon > 0) {                                          // high noon: light straight down
    const g = ctx.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, `rgba(255,255,255,${0.22 * noon})`);
    g.addColorStop(0.55, `rgba(255,244,214,${0.10 * noon})`);
    g.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  }
  if (warm > 0) {                                          // 4 PM: low sun from the right
    const g = ctx.createLinearGradient(W, 0, 0, H);
    g.addColorStop(0, `rgba(255,186,88,${0.26 * warm})`);
    g.addColorStop(0.6, `rgba(242,178,62,${0.12 * warm})`);
    g.addColorStop(1, 'rgba(242,178,62,0)');
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  }
  if (relief > 0) {                                        // weight gone: a soft gold lift
    const g = ctx.createRadialGradient(540, 1320, 60, 540, 1320, 1150);
    g.addColorStop(0, `rgba(255,231,170,${0.30 * relief})`);
    g.addColorStop(1, 'rgba(255,231,170,0)');
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    for (let k = 0; k < 7; k++) {
      const y = H - ((t * 46 + k * 270) % (H + 80));
      ctx.globalAlpha = 0.4 * relief; ctx.fillStyle = '#FFE7AA';
      ctx.beginPath(); ctx.arc(140 + k * 140, y, 6 + (k % 3) * 3, 0, 6.283); ctx.fill();
    }
    ctx.globalAlpha = 1;
  }
  if (dim > 0) {                                           // the cloud: the whole street cools off
    ctx.fillStyle = `rgba(34,40,58,${0.20 * dim})`; ctx.fillRect(0, 0, W, H);
    const g = ctx.createLinearGradient(0, 0, 0, 620);
    g.addColorStop(0, `rgba(120,128,150,${0.22 * dim})`);
    g.addColorStop(1, 'rgba(120,128,150,0)');
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, 620);
  }
  ctx.globalAlpha = 1; ctx.letterSpacing = '0px';

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
    IMPACTS = [
      { t: Wd('locks', 0), amp: 16, dur: 0.45 },
      { t: Wd('yanks', 4), amp: 12, dur: 0.40 },
      { t: Wd('sidewalk', 4), amp: 20, dur: 0.50 },
      { t: Wd('slam', 6), amp: 22, dur: 0.55 },
    ];
    ZERO = Wd('zero', 5); CLOUD = Wd('cloud', 6);
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
