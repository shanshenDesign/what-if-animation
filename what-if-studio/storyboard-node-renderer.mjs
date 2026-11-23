// Custom stills renderer for this Android studio: the Remotion headless Chrome is unavailable
// (chrome-for-testing has no Android build; glibc builds can't run on bionic). The shots are pure
// functions of their clock, so we render each shot to SVG with react-dom/server and rasterize with
// rsvg-convert, reproducing what stills.mjs writes to out/<slug>/board/.
import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { ShotFrame } from './src/engine/episode.tsx';
import * as shots from './src/episodes/pause-everyone/shots.tsx';
import timeline from './src/episodes/pause-everyone/timeline.json';

const RSVG = '/data/data/com.termux/files/usr/bin/rsvg-convert';
const root = process.cwd();
const slug = 'pause-everyone';

// Font registration in fonts.ts touches document; this render is static, so stub it.
globalThis.document ??= { fonts: { add() {}, insertRule() {}, status: 'loaded' }, createElement: () => ({ style: {} }), head: { appendChild() {} } };
globalThis.FontFace ??= class {
  constructor(family, src) { this.family = family; this.status = 'loaded'; }
};

const board = path.join(root, 'out', slug, 'board');
fs.mkdirSync(board, { recursive: true });
for (const s of timeline.shots) {
  const Shot = shots[s.id];
  const svg = renderToStaticMarkup(
    React.createElement(ShotFrame, null, React.createElement(Shot, { t: s.key, len: s.len, f: s.first + s.key })),
  );
  fs.writeFileSync(path.join(board, `${s.id}.svg`), svg);
  execFileSync(RSVG, ['-o', path.join(board, `${s.id}.png`), path.join(board, `${s.id}.svg`)]);
  console.log(`wrote ${s.id}.png`);
}
console.log('done');
