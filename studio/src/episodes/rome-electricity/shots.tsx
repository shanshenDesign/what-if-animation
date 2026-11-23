import React from 'react';
import {
  Hero, LOOKS, Kitchen, Classroom, Rooftop, Study, Desk, Glow, ShotProps,
} from '../../engine';
import { rnd } from '../../engine/anim';

const Domus: React.FC<{ t: number; night?: boolean; veil?: number }> = ({ t, veil = 0.25 }) => (
  <Study t={t} id="rome-domus" veil={veil} />
);
const Thermae: React.FC<{ t: number; veil?: number }> = ({ t, veil = 0.25 }) => (
  <Kitchen t={t} veil={veil} />
);
const Forum: React.FC<{ t: number; veil?: number }> = ({ t, veil = 0.25 }) => (
  <Classroom t={t} veil={veil} />
);
const VoltaicJar: React.FC<{ x: number; y: number; t: number; s?: number; active?: number }> = ({ x, y, s = 1, active = 1 }) => (
  <g transform={`translate(${x}, ${y}) scale(${s})`}>
    <rect x={-26} y={-50} width={52} height={64} rx={8} fill="#7A4924" stroke="#F4B851" strokeWidth={3} />
    <rect x={-20} y={-24} width={40} height={32} fill="#C87D32" opacity={0.85} />
    {active ? <Glow x={0} y={-60} r={45} color="#FFD37A" opacity={0.7} /> : null}
  </g>
);
const Arc: React.FC<{ x: number; y: number; t: number; color?: string; len?: number }> = ({ x, y, t, color = '#FFD37A', len = 40 }) => (
  <polyline
    points={`${x - len * 0.4},${y} ${x},${y - len * 0.5} ${x + len * 0.4},${y + len * 0.2}`}
    fill="none"
    stroke={color}
    strokeWidth={4}
    opacity={0.65 + 0.35 * Math.sin(t * 2.3 + rnd(t))}
  />
);
const Amphora: React.FC<any> = ({ x = 0, y = 0, s = 1 }) => <VoltaicJar x={x} y={y} t={0} s={s * 0.8} active={0} />;
const OilLamp: React.FC<any> = ({ x = 0, y = 0, s = 1, lit = true }) => <VoltaicJar x={x} y={y} t={0} s={s * 0.7} active={lit ? 1 : 0} />;
const Brazier: React.FC<any> = ({ x = 0, y = 0, s = 1 }) => <VoltaicJar x={x} y={y} t={0} s={s} active={1} />;
const Column: React.FC<any> = ({ x = 0, y = 0, h = 320, w = 44 }) => (
  <rect x={x - w / 2} y={y - h} width={w} height={h} rx={6} fill="#D8C7AE" opacity={0.75} />
);
const Char: React.FC<any> = ({ look = LOOKS.pip, x = 960, y = 720, scale = 1, expr = 'neutral', ...rest }) => (
  <Hero look={look} pose={{ x, y, scale, expr, ...rest }} />
);
const pipRome = LOOKS.pip;
const moRome = LOOKS.mo;
const sisRome = LOOKS.sis;
const momRome = LOOKS.mom;
const emperor = LOOKS.suit;
const guard = LOOKS.pipInk;


const Domus: React.FC<{ t: number; night?: boolean; veil?: number }> = ({ t, veil = 0.25 }) => (
  <Study t={t} id="rome-domus" veil={veil} />
);
const Thermae: React.FC<{ t: number; veil?: number }> = ({ t, veil = 0.25 }) => (
  <Kitchen t={t} veil={veil} />
);
const Forum: React.FC<{ t: number; veil?: number }> = ({ t, veil = 0.25 }) => (
  <Classroom t={t} veil={veil} />
);
const VoltaicJar: React.FC<{ x: number; y: number; t: number; s?: number; active?: number }> = ({ x, y, s = 1, active = 1 }) => (
  <g transform={`translate(${x}, ${y}) scale(${s})`}>
    <rect x={-26} y={-50} width={52} height={64} rx={8} fill="#7A4924" stroke="#F4B851" strokeWidth={3} />
    <rect x={-20} y={-24} width={40} height={32} fill="#C87D32" opacity={0.85} />
    {active ? <Glow x={0} y={-60} r={45} color="#FFD37A" opacity={0.7} /> : null}
  </g>
);
const Arc: React.FC<{ x: number; y: number; t: number; color?: string; len?: number }> = ({ x, y, t, color = '#FFD37A', len = 40 }) => (
  <polyline
    points={`${x - len * 0.4},${y} ${x},${y - len * 0.5} ${x + len * 0.4},${y + len * 0.2}`}
    fill="none"
    stroke={color}
    strokeWidth={4}
    opacity={0.65 + 0.35 * Math.sin(t * 2.3 + rnd(t))}
  />
);
const Amphora: React.FC<any> = ({ x = 0, y = 0, s = 1 }) => <VoltaicJar x={x} y={y} t={0} s={s * 0.8} active={0} />;
const OilLamp: React.FC<any> = ({ x = 0, y = 0, s = 1, lit = true }) => <VoltaicJar x={x} y={y} t={0} s={s * 0.7} active={lit ? 1 : 0} />;
const Brazier: React.FC<any> = ({ x = 0, y = 0, s = 1 }) => <VoltaicJar x={x} y={y} t={0} s={s} active={1} />;
const Column: React.FC<any> = ({ x = 0, y = 0, h = 320, w = 44 }) => (
  <rect x={x - w / 2} y={y - h} width={w} height={h} rx={6} fill="#D8C7AE" opacity={0.75} />
);
const Char: React.FC<any> = ({ look = LOOKS.pip, x = 960, y = 720, scale = 1, expr = 'neutral', ...rest }) => (
  <Hero look={look} pose={{ x, y, scale, expr, ...rest }} />
);
const pipRome = LOOKS.pip;
const moRome = LOOKS.mo;
const sisRome = LOOKS.sis;
const momRome = LOOKS.mom;
const emperor = LOOKS.suit;
const guard = LOOKS.pipInk;
