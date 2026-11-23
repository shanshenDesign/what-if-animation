import React from 'react';
import { ShotFrame, SparkFX, TitleCard, SchematicCard } from '../../engine/episode';
import { Domus } from '../../engine/sets/domus';
import { Thermae } from '../../engine/sets/thermae';
import { Forum } from '../../engine/sets/forum';
import { VoltaicJar, Arc, Amphora, OilLamp, Brazier, Column } from '../../engine/props-rome';
import { Char, pipRome, moRome, sisRome, momRome, emperor, guard } from '../../engine/rig';
import { rnd } from '../../engine/anim';

// S1: CU - First spark: coin, vinegar jar, copper plate arc
export const S1: React.FC<{ t: number; len: number; f: number }> = ({ t, len, f }) => {
  const arcOn = (f % 18) < 9;
  return (
    <svg viewBox="0 0 1920 1080" style={{ width: '100%', height: '100%', background: '#110C0A' }}>
      <Domus t={t} night={true} veil={0.2} />
      {/* Close-up table with vinegar jar and copper coin/plates */}
      <g transform="translate(960, 720) scale(1.6)">
        <VoltaicJar x={0} y={0} t={t} s={1.8} active={1} />
        {arcOn && <Arc x={0} y={-80} t={t} color="#FFD37A" len={40} />}
      </g>
    </svg>
  );
};

// S2: MCU - Domus kitchen: oil lamp dies, spark relights lamp
export const S2: React.FC<{ t: number; len: number; f: number }> = ({ t, len, f }) => {
  const lit = t > 1.5 ? 1 : 0.2;
  return (
    <svg viewBox="0 0 1920 1080" style={{ width: '100%', height: '100%', background: '#110C0A' }}>
      <Domus t={t} night={true} />
      <Char def={pipRome} pose="work" x={750} y={640} s={0.9} />
      <OilLamp x={900} y={620} s={1.2} lit={lit} t={t} />
      {t > 1.2 && t < 1.6 && <SparkFX x={900} y={600} color="#FFD37A" />}
    </svg>
  );
};

// S3: MS - Cold bath pool: spark fires electrode, steam rolls off
export const S3: React.FC<{ t: number; len: number; f: number }> = ({ t, len, f }) => (
  <svg viewBox="0 0 1920 1080" style={{ width: '100%', height: '100%', background: '#110C0A' }}>
    <Thermae t={t} pool={true} steam={1} />
    <Char def={moRome} pose="stand" x={960} y={660} s={0.95} />
    <Arc x={960} y={740} t={t} color="#6EEDFF" len={60} />
  </svg>
);

// S4: WS - Senator villa: ring spark, lamps flare in unison
export const S4: React.FC<{ t: number; len: number; f: number }> = ({ t, len, f }) => (
  <svg viewBox="0 0 1920 1080" style={{ width: '100%', height: '100%', background: '#110C0A' }}>
    <Domus t={t} grand={true} night={true} />
    <Char def={emperor} pose="grand" x={960} y={620} s={1.05} />
    <SparkFX x={960} y={540} color="#FFD37A" />
  </svg>
);

// S5: CU - Macro spark arc across dark frame
export const S5: React.FC<{ t: number; len: number; f: number }> = ({ t, len, f }) => (
  <svg viewBox="0 0 1920 1080" style={{ width: '100%', height: '100%', background: '#080504' }}>
    <Arc x={960} y={540} t={t} color="#FFD37A" len={220} />
    <SparkFX x={960} y={540} color="#6EEDFF" />
  </svg>
);

// S6: TITLE - Title Card: WHAT IF ANCIENT ROME DISCOVERED ELECTRICITY?
export const S6: React.FC<{ t: number; len: number; f: number }> = ({ t, len, f }) => (
  <svg viewBox="0 0 1920 1080" style={{ width: '100%', height: '100%', background: '#110C0A' }}>
    <TitleCard title={["WHAT IF ANCIENT ROME", "FOUND ELECTRICITY?"]} accent="ELECTRICITY?" />
  </svg>
);

// S7: EWS - Forum at night glowing with electric lamps & wires
export const S7: React.FC<{ t: number; len: number; f: number }> = ({ t, len, f }) => (
  <svg viewBox="0 0 1920 1080" style={{ width: '100%', height: '100%', background: '#110C0A' }}>
    <Forum t={t} night={true} electric={true} />
  </svg>
);

// S8: MS - Thermae hot baths at midnight: steaming warm water
export const S8: React.FC<{ t: number; len: number; f: number }> = ({ t, len, f }) => (
  <svg viewBox="0 0 1920 1080" style={{ width: '100%', height: '100%', background: '#110C0A' }}>
    <Thermae t={t} hot={true} steam={1.5} />
  </svg>
);

// S9: MS - Emperor on throne demanding more power
export const S9: React.FC<{ t: number; len: number; f: number }> = ({ t, len, f }) => (
  <svg viewBox="0 0 1920 1080" style={{ width: '100%', height: '100%', background: '#110C0A' }}>
    <Forum t={t} throne={true} />
    <Char def={emperor} pose="command" x={960} y={620} s={1.1} />
  </svg>
);

// S10: WS - Decree: wiring every street, jars in houses
export const S10: React.FC<{ t: number; len: number; f: number }> = ({ t, len, f }) => (
  <svg viewBox="0 0 1920 1080" style={{ width: '100%', height: '100%', background: '#110C0A' }}>
    <Forum t={t} decree={true} />
    <Char def={guard} pose="point" x={800} y={640} s={1.0} />
  </svg>
);

// S11: SCH - Schematic 1: Voltaic Jar (0.7 V, 0.02 W)
export const S11: React.FC<{ t: number; len: number; f: number }> = ({ t, len, f }) => (
  <svg viewBox="0 0 1920 1080" style={{ width: '100%', height: '100%', background: '#110C0A' }}>
    <SchematicCard title="VOLTAIC JAR" subtitle="0.7 Volts • 0.02 Watts" stat="1/50 W" note="Copper plate + iron rod in vinegar" />
    <VoltaicJar x={960} y={580} t={t} s={2.2} active={1} />
  </svg>
);

// S12: SCH - Schematic 2: Bath heating math (605,000 jars)
export const S12: React.FC<{ t: number; len: number; f: number }> = ({ t, len, f }) => (
  <svg viewBox="0 0 1920 1080" style={{ width: '100%', height: '100%', background: '#110C0A' }}>
    <SchematicCard title="BATH THERMODYNAMICS" subtitle="10 m³ water • +25°C = 290 kWh" stat="605,000 JARS" note="Required to heat one small Roman bath pool for 24 hours" />
  </svg>
);

// S13: SCH - Schematic 3: City scale math (544,500,000 jars)
export const S13: React.FC<{ t: number; len: number; f: number }> = ({ t, len, f }) => (
  <svg viewBox="0 0 1920 1080" style={{ width: '100%', height: '100%', background: '#110C0A' }}>
    <SchematicCard title="IMPERIAL METROPOLIS" subtitle="900 public baths across Rome" stat="544,500,000 JARS" note="Half a billion chemical cells to sustain public luxury" />
  </svg>
);

// S14: CU - Roof close: Legionaries stripping copper tiles
export const S14: React.FC<{ t: number; len: number; f: number }> = ({ t, len, f }) => (
  <svg viewBox="0 0 1920 1080" style={{ width: '100%', height: '100%', background: '#110C0A' }}>
    <Forum t={t} roof={true} />
    <Char def={guard} pose="work" x={960} y={640} s={1.0} />
  </svg>
);

// S15: MS - Statues and coin stacks being confiscated
export const S15: React.FC<{ t: number; len: number; f: number }> = ({ t, len, f }) => (
  <svg viewBox="0 0 1920 1080" style={{ width: '100%', height: '100%', background: '#110C0A' }}>
    <Forum t={t} tribute={true} />
    <Char def={guard} pose="stand" x={800} y={640} s={1.0} />
    <Char def={momRome} pose="sad" x={1120} y={640} s={0.95} />
  </svg>
);

// S16: MCU - Domus interior: Sister with spark jar, Legionary at door
export const S16: React.FC<{ t: number; len: number; f: number }> = ({ t, len, f }) => (
  <svg viewBox="0 0 1920 1080" style={{ width: '100%', height: '100%', background: '#110C0A' }}>
    <Domus t={t} night={true} />
    <Char def={sisRome} pose="scared" x={750} y={640} s={0.95} />
    <Char def={guard} pose="point" x={1180} y={640} s={1.0} />
    <VoltaicJar x={880} y={660} t={t} s={1.0} active={1} />
  </svg>
);

// S17: EWS - Forum plunges into blackout darkness
export const S17: React.FC<{ t: number; len: number; f: number }> = ({ t, len, f }) => (
  <svg viewBox="0 0 1920 1080" style={{ width: '100%', height: '100%', background: '#050302' }}>
    <Forum t={t} night={true} blackout={true} />
  </svg>
);

// S18: TITLE - Cliffhanger: Roman fuse blows, PART ONE
export const S18: React.FC<{ t: number; len: number; f: number }> = ({ t, len, f }) => {
  const blown = (f % 12) < 6;
  return (
    <svg viewBox="0 0 1920 1080" style={{ width: '100%', height: '100%', background: '#050302' }}>
      <TitleCard title={["ROME FALLS TO A FUSE.", "PART ONE"]} accent="PART ONE" />
      {blown && <SparkFX x={960} y={540} color="#FF5533" />}
    </svg>
  );
};
