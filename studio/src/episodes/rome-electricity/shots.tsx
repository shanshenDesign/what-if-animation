import React from 'react';
import {
  Hero,
  LOOKS,
  Study,
  Kitchen,
  Classroom,
  Rooftop,
  Schematic,
  Sparkle,
  Tag,
  FloatLabel,
  FocusRings,
  DizzyStars,
  FONT,
  ShotProps,
  poseAt,
  faceAt,
  clamp,
  easeOut,
} from '../../engine';
import { rnd } from '../../engine/anim';

const Domus: React.FC<{ t: number; veil?: number }> = ({ t, veil = 0.25 }) => (
  <Study t={t} id="rome-domus" veil={veil} />
);
const Thermae: React.FC<{ t: number; veil?: number }> = ({ t, veil = 0.25 }) => (
  <Kitchen t={t} veil={veil} />
);
const Forum: React.FC<{ t: number; veil?: number }> = ({ t, veil = 0.25 }) => (
  <Classroom t={t} veil={veil} />
);

const VoltaicJar: React.FC<{ x: number; y: number; t: number; s?: number; active?: boolean }> = ({
  x,
  y,
  t,
  s = 1,
  active = true,
}) => {
  const pulse = active ? 0.7 + 0.3 * Math.sin(t * 0.45) : 0.25;
  return (
    <g transform={`translate(${x} ${y}) scale(${s})`}>
      <rect x={-34} y={-68} width={68} height={84} rx={10} fill="#5C381E" stroke="#F4B851" strokeWidth={4} />
      <rect x={-26} y={-32} width={52} height={42} rx={4} fill="#C87D32" opacity={0.85} />
      <line x1={-14} y1={-84} x2={-14} y2={-18} stroke="#E88D4F" strokeWidth={6} strokeLinecap="round" />
      <line x1={14} y1={-84} x2={14} y2={-18} stroke="#B8C4D0" strokeWidth={6} strokeLinecap="round" />
      {active ? (
        <>
          <circle cx={0} cy={-86} r={34} fill="#FFD37A" opacity={0.28 * pulse} />
          <Sparkle x={0} y={-88} t={Math.max(1, (t % 18) + 1)} s={0.9} />
        </>
      ) : null}
    </g>
  );
};

const ArcBolt: React.FC<{ x1: number; y1: number; x2: number; y2: number; t: number; color?: string }> = ({
  x1,
  y1,
  x2,
  y2,
  t,
  color = '#FFD37A',
}) => {
  const mx = (x1 + x2) / 2 + (rnd(t * 1.7) - 0.5) * 44;
  const my = (y1 + y2) / 2 - 28 + (rnd(t * 2.3) - 0.5) * 32;
  const op = 0.55 + 0.45 * Math.abs(Math.sin(t * 0.7));
  return (
    <g opacity={op}>
      <polyline
        points={`${x1},${y1} ${mx},${my} ${x2},${y2}`}
        fill="none"
        stroke={color}
        strokeWidth={6}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <circle cx={mx} cy={my} r={14} fill={color} opacity={0.45} />
    </g>
  );
};

const SceneBadge: React.FC<{ title: string; subtitle?: string }> = ({ title, subtitle }) => (
  <g>
    <rect x={96} y={76} width={760} height={116} rx={22} fill="#0B0816" opacity={0.78} />
    <text x={128} y={126} fontFamily={FONT.title} fontSize={44} fill="#F6EFE3" letterSpacing={3}>
      {title}
    </text>
    {subtitle ? (
      <text x={128} y={168} fontFamily={FONT.ui} fontSize={28} fill="#FFB15A" letterSpacing={2}>
        {subtitle}
      </text>
    ) : null}
  </g>
);

export const S1: React.FC<ShotProps> = ({ t }) => {
  const pose = poseAt(t, [
    { f: 0, p: { x: 860, y: 760, armR: { a: 45, b: -30 } } },
    { f: 30, p: { armR: { a: 72, b: -12 } }, ease: easeOut },
  ]);
  return (
    <g>
      <Domus t={t} veil={0.35} />
      <Hero look={LOOKS.pip} pose={poseAt(t, [{ f: 0, p: { ...pose, ...faceAt(t, [[0, 'neutral'], [25, 'happy']]) } }])} />
      <VoltaicJar x={1120} y={760} t={t} s={1.35} active={true} />
      <ArcBolt x1={1106} y1={676} x2={1134} y2={676} t={t} color="#FFD37A" />
      <Tag x={1560} y={240} t={t - 8} text="0.7 V" />
      <SceneBadge title="40 BC · FIRST SPARK" subtitle="COIN · VINEGAR JAR · COPPER ARC" />
    </g>
  );
};

export const S2: React.FC<ShotProps> = ({ t }) => {
  const relit = t >= 24;
  return (
    <g>
      <Thermae t={t} veil={relit ? 0.2 : 0.55} />
      <Hero look={LOOKS.mo} pose={poseAt(t, [{ f: 0, p: { x: 780, y: 750, ...faceAt(t, [[0, 'worried'], [24, 'shock']]) } }])} />
      <VoltaicJar x={1180} y={760} t={t} s={1.1} active={relit} />
      {relit ? (
        <>
          <ArcBolt x1={1166} y1={676} x2={1260} y2={580} t={t} color="#FFE27A" />
          <FocusRings x={1260} y={580} t={t - 24} color="#FFD37A" />
        </>
      ) : null}
      <SceneBadge title="SLAVE KITCHEN" subtitle={relit ? 'SPARK RELIGHTS LAMP' : 'WICK DIES IN DARK'} />
    </g>
  );
};

export const S3: React.FC<ShotProps> = ({ t }) => {
  const steamRise = clamp(t / 60) * 180;
  return (
    <g>
      <Thermae t={t} veil={0.22} />
      <rect x={540} y={640} width={840} height={240} rx={24} fill="#2A6F97" stroke="#A9D6E5" strokeWidth={5} />
      <VoltaicJar x={960} y={650} t={t} s={1.05} active={true} />
      <ArcBolt x1={946} y1={566} x2={974} y2={566} t={t} color="#6EEDFF" />
      {[0, 1, 2, 3].map((i) => (
        <ellipse
          key={i}
          cx={720 + i * 160}
          cy={600 - steamRise * (0.7 + i * 0.1)}
          rx={70}
          ry={26}
          fill="#F6EFE3"
          opacity={0.32 * (1 - clamp(t / 80))}
        />
      ))}
      <SceneBadge title="COLD BATH" subtitle="ELECTRODE FIRES · STEAM RISES" />
    </g>
  );
};

export const S4: React.FC<ShotProps> = ({ t }) => {
  const pulse = t >= 20;
  return (
    <g>
      <Domus t={t} veil={pulse ? 0.12 : 0.4} />
      <Hero look={LOOKS.suit} pose={poseAt(t, [{ f: 0, p: { x: 960, y: 740, ...faceAt(t, [[0, 'smug'], [20, 'happy']]) } }])} />
      {[420, 690, 1230, 1500].map((lx, idx) => (
        <VoltaicJar key={idx} x={lx} y={420} t={t + idx * 5} s={0.85} active={pulse} />
      ))}
      {pulse ? <FocusRings x={960} y={560} t={t - 20} r0={90} color="#FFD37A" /> : null}
      <SceneBadge title="SENATOR VILLA" subtitle="RING SPARK · LAMPS FLARE" />
    </g>
  );
};

export const S5: React.FC<ShotProps> = ({ t }) => (
  <g>
    <rect x={0} y={0} width={1920} height={1080} fill="#090712" />
    <ArcBolt x1={520} y1={540} x2={1400} y2={540} t={t} color="#FFD37A" />
    <ArcBolt x1={640} y1={420} x2={1280} y2={660} t={t + 3} color="#6EEDFF" />
    <FloatLabel x={960} y={320} t={t} text="SPARK" color="#FFD37A" size={88} />
  </g>
);

export const S6: React.FC<ShotProps> = ({ t }) => (
  <g>
    <Rooftop t={t} veil={0.35} />
    <rect x={160} y={280} width={1600} height={460} rx={36} fill="#0B0816" opacity={0.84} />
    <text x={960} y={430} textAnchor="middle" fontFamily={FONT.title} fontSize={78} fill="#F6EFE3" letterSpacing={4}>
      WHAT IF ANCIENT ROME
    </text>
    <text x={960} y={540} textAnchor="middle" fontFamily={FONT.title} fontSize={84} fill="#FFB15A" letterSpacing={5}>
      FOUND ELECTRICITY?
    </text>
    <text x={960} y={640} textAnchor="middle" fontFamily={FONT.ui} fontSize={38} fill="#6EEDFF" letterSpacing={6}>
      0.7 VOLTS · ONE SPARK
    </text>
  </g>
);

export const S7: React.FC<ShotProps> = ({ t }) => (
  <g>
    <Forum t={t} veil={0.18} />
    {[340, 650, 960, 1270, 1580].map((x, i) => (
      <VoltaicJar key={i} x={x} y={680} t={t + i * 4} s={0.95} active={true} />
    ))}
    <line x1={340} y1={596} x2={1580} y2={596} stroke="#FFD37A" strokeWidth={5} opacity={0.85} />
    <SceneBadge title="FORUM AT NIGHT" subtitle="NO OIL · NO SMOKE · WIRES AGLOW" />
  </g>
);

export const S8: React.FC<ShotProps> = ({ t }) => (
  <g>
    <Thermae t={t} veil={0.2} />
    <rect x={420} y={620} width={1080} height={260} rx={28} fill="#E07A5F" opacity={0.45} />
    <Hero look={LOOKS.sis} pose={poseAt(t, [{ f: 0, p: { x: 760, y: 730, ...faceAt(t, [[0, 'happy']]) } }])} />
    <Hero look={LOOKS.pip} pose={poseAt(t, [{ f: 0, p: { x: 1160, y: 730, ...faceAt(t, [[0, 'cool']]) } }])} />
    <SceneBadge title="MIDNIGHT THERMAE" subtitle="HOT BATHS · COLD WINE" />
  </g>
);

export const S9: React.FC<ShotProps> = ({ t }) => (
  <g>
    <Forum t={t} veil={0.25} />
    <Hero look={LOOKS.suit} pose={poseAt(t, [{ f: 0, p: { x: 960, y: 720, scale: 1.15, ...faceAt(t, [[0, 'smug'], [12, 'shock']]) } }])} />
    <FloatLabel x={960} y={260} t={t} text="MORE POWER!" color="#FF8A3D" size={76} />
    <SceneBadge title="THE EMPEROR" subtitle="DEMANDS INFINITE JARS" />
  </g>
);

export const S10: React.FC<ShotProps> = ({ t }) => (
  <g>
    <Forum t={t} veil={0.25} />
    {[300, 630, 960, 1290, 1620].map((x, i) => (
      <VoltaicJar key={i} x={x} y={740} t={t + i * 3} s={0.9} active={true} />
    ))}
    <line x1={180} y1={480} x2={1740} y2={480} stroke="#FF8A3D" strokeWidth={6} strokeDasharray="18 10" />
    <SceneBadge title="IMPERIAL DECREE" subtitle="A JAR IN EVERY HOUSE · A WIRE ON EVERY STREET" />
  </g>
);

export const S11: React.FC<ShotProps> = ({ t }) => (
  <g>
    <Schematic t={t} />
    <VoltaicJar x={620} y={620} t={t} s={1.6} active={true} />
    <Tag x={1260} y={420} t={t - 4} text="0.7 V" w={190} />
    <Tag x={1260} y={560} t={t - 10} text="0.02 W" w={210} />
    <SceneBadge title="SCHEMATIC 1 · ONE VOLTAIC JAR" subtitle="1/50TH OF A WATT · TONGUE TINGLE" />
  </g>
);

export const S12: React.FC<ShotProps> = ({ t }) => (
  <g>
    <Schematic t={t} />
    <Tag x={960} y={430} t={t - 4} text="605,000 JARS" w={380} />
    <SceneBadge title="SCHEMATIC 2 · ONE SMALL BATH" subtitle="10 M³ + 25°C OVER 24 HOURS" />
  </g>
);

export const S13: React.FC<ShotProps> = ({ t }) => (
  <g>
    <Schematic t={t} />
    <Tag x={960} y={430} t={t - 4} text="544,500,000 JARS" w={440} />
    <SceneBadge title="SCHEMATIC 3 · 900 BATHS IN ROME" subtitle="HALF A BILLION JARS · REAL MATH" />
  </g>
);

export const S14: React.FC<ShotProps> = ({ t }) => (
  <g>
    <Rooftop t={t} veil={0.3} />
    <Hero look={LOOKS.pipInk} pose={poseAt(t, [{ f: 0, p: { x: 960, y: 740, ...faceAt(t, [[0, 'neutral']]) } }])} />
    <FloatLabel x={960} y={280} t={t} text="COPPER TAX!" color="#FF5A4A" size={76} />
    <SceneBadge title="ROOFTOP RAID" subtitle="STRIPPING COPPER TILES" />
  </g>
);

export const S15: React.FC<ShotProps> = ({ t }) => (
  <g>
    <Forum t={t} veil={0.35} />
    <Hero look={LOOKS.mom} pose={poseAt(t, [{ f: 0, p: { x: 760, y: 750, ...faceAt(t, [[0, 'worried']]) } }])} />
    <Hero look={LOOKS.pipInk} pose={poseAt(t, [{ f: 0, p: { x: 1180, y: 750, ...faceAt(t, [[0, 'neutral']]) } }])} />
    <SceneBadge title="CONFISCATION" subtitle="TEMPLES · STATUES · COINS" />
  </g>
);

export const S16: React.FC<ShotProps> = ({ t }) => (
  <g>
    <Domus t={t} veil={0.45} />
    <Hero look={LOOKS.sis} pose={poseAt(t, [{ f: 0, p: { x: 780, y: 750, ...faceAt(t, [[0, 'worried']]) } }])} />
    <VoltaicJar x={980} y={760} t={t} s={1.15} active={true} />
    <Hero look={LOOKS.pipInk} pose={poseAt(t, [{ f: 0, p: { x: 1240, y: 750, ...faceAt(t, [[0, 'neutral']]) } }])} />
    <SceneBadge title="AT THE DOOR" subtitle="YOUR SISTER'S LAMP IS NEXT" />
  </g>
);

export const S17: React.FC<ShotProps> = ({ t }) => {
  const blackout = clamp(t / 20);
  return (
    <g>
      <Forum t={t} veil={0.85} />
      <rect x={0} y={0} width={1920} height={1080} fill="#040308" opacity={0.5 + 0.48 * blackout} />
      <DizzyStars x={960} y={540} t={t} rx={160} ry={70} />
      <SceneBadge title="BLACKOUT" subtitle="THE CITY GOES DARK" />
    </g>
  );
};

export const S18: React.FC<ShotProps> = ({ t }) => (
  <g>
    <rect x={0} y={0} width={1920} height={1080} fill="#090712" />
    <ArcBolt x1={960} y1={220} x2={960} y2={860} t={t} color="#FF5533" />
    <text x={960} y={460} textAnchor="middle" fontFamily={FONT.title} fontSize={74} fill="#F6EFE3" letterSpacing={4}>
      IT FALLS TO A FUSE.
    </text>
    <text x={960} y={580} textAnchor="middle" fontFamily={FONT.title} fontSize={88} fill="#FF5533" letterSpacing={6}>
      PART ONE.
    </text>
  </g>
);
