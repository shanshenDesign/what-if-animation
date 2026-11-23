import React from 'react';
import {
  Hero, LOOKS, Pose, poseAt, kf, clamp, lerp, easeOut, easeIn, joints, toWorld, reachAngle, LEG_LEN, faceAt,
  Study, Rooftop, Schematic, Desk, Glow, Sparkle, Arrow, DrawOn, SchLabel, CountUp, PlantIcon, SCH,
  ShotProps, Foreground, camT, TitleCard,
} from '../../engine';

/** Pip in the dark hoodie (look B). */
const PIP = LOOKS.pipHood;

// ---------- SH1: wide, study - Day 1: The Disconnect ----------
// Screens and lights flicker out in a sudden digital silence.
export const Sh1: React.FC<ShotProps> = ({ t }) => {
  const flicker = Math.sin(t * 2.5) > 0.3 ? 1 : 0.15;
  const pose = poseAt(t, [
    { f: 0, p: { x: 960, y: 712, yaw: 0.3, armL: { a: 20, b: -6 }, armR: { a: 10, b: -8 }, look: 0.5 } },
    { f: 30, p: { armL: { a: 60, b: 10 }, armR: { a: 50, b: 0 }, look: 1 }, ease: easeOut },
    { f: 90, p: { armL: { a: 20, b: -6 }, armR: { a: 10, b: -8 }, look: 0.2 } },
  ]);
  const face = faceAt(t, [[0, 'neutral'], [10, 'shock'], [80, 'worried']]);
  return (
    <g transform={camT(960, 540, kf(t, [[0, 1.0], [180, 1.05]]))}>
      <Study t={t} id="sh1" veil={0.28} />
      <Hero look={PIP} pose={{ ...pose, ...face }} shadow={0} rimId="rimR" />
      <Desk x0={560} x1={1360} y={700} laptop={true} lamp={flicker > 0.5} />
      {/* Screen flicker overlay */}
      <rect x={700} y={520} width={520} height={300} fill="#24222E" opacity={flicker} />
      <g opacity={flicker * 0.8}>
        <path d="M 720 540 L 1180 540" stroke="#9FC0FF" strokeWidth={2} opacity={0.7} />
        <path d="M 720 580 L 1080 580" stroke="#9FC0FF" strokeWidth={2} opacity={0.5} />
        <path d="M 720 620 L 1000 620" stroke="#9FC0FF" strokeWidth={2} opacity={0.4} />
        <path d="M 720 660 L 1140 660" stroke="#9FC0FF" strokeWidth={2} opacity={0.6} />
      </g>
      <Glow x={960} y={596} r={600} kind="cool" o={0.3 * flicker} />
      <Foreground blur={10}>
        <path d="M -140 1220 L -140 860 Q -128 786 -30 786 L 236 786 Q 322 786 334 862 L 344 1220 Z" fill="#140F1A" />
        <path d="M 222 856 Q 368 846 388 932 L 398 1220 L 222 1220 Z" fill="#0F0B14" />
      </Foreground>
    </g>
  );
};

// ---------- SH2: medium, rooftop - Day 2: Digital Detox ----------
// Looking up at stars with dead phones.
export const Sh2: React.FC<ShotProps> = ({ t }) => {
  const pose = poseAt(t, [
    { f: 0, p: { x: 960, y: 780, scale: 1.1, yaw: -0.2, armL: { a: 10, b: -8 }, armR: { a: 170, b: 30 }, headTilt: 20 } },
    { f: 60, p: { armR: { a: 160, b: 20 } } },
    { f: 120, p: { armR: { a: 170, b: 30 }, headTilt: 25 } },
  ]);
  const face = faceAt(t, [[0, 'worried'], [30, 'neutral'], [100, 'happy']]);
  const phoneY = 780 - 100;
  const phoneDead = t > 10 ? 1 : 0;
  return (
    <g transform={camT(960, 580, kf(t, [[0, 1.1], [180, 1.15]]))}>
      <Rooftop t={t} clock={false} low={200} />
      <Hero look={PIP} pose={{ ...pose, ...face }} shadow={0} rimId="rimR" />
      {/* Dead phone in hand */}
      <g transform={`translate(${960 + 80} ${phoneY})`}>
        <rect x={-40} y={-80} width={80} height={160} rx={12} fill="#1A1822" stroke={PIP.line} strokeWidth={3} />
        <rect x={-30} y={-70} width={60} height={140} fill="#0A0810" />
        {phoneDead && <path d="M -20 0 L 20 0 M 0 -20 L 0 20" stroke="#444" strokeWidth={3} strokeLinecap="round" />}
      </g>
      <Sparkle x={600} y={200} t={t} s={1.2} />
      <Sparkle x={1300} y={180} t={t - 10} s={1.0} />
      <Sparkle x={400} y={300} t={t - 20} s={0.8} />
    </g>
  );
};

// ---------- SH3: schematic, schematic - Day 6: Systems Stall ----------
// Frozen bank terminals and offline server racks.
export const Sh3: React.FC<ShotProps> = ({ t }) => {
  const serverDraw = clamp(t / 40);
  const bankDraw = clamp((t - 30) / 40);
  const chainDraw = clamp((t - 60) / 40);
  const count = t > 90 ? easeOut(clamp((t - 90) / 50)) : 0;
  return (
    <g>
      <Schematic t={t} id="sh3" />
      {/* Server rack */}
      <DrawOn d="M 400 300 L 400 700 M 500 300 L 500 700 M 400 300 L 500 300 M 400 700 L 500 700" t={t} dur={40} color={SCH.line} width={3} />
      {[420, 440, 460, 480].map((x) =>
        <DrawOn key={x} d={`M ${x} 320 L ${x} 680`} t={t - 5} dur={35} color={SCH.dim} width={1} />
      )}
      <SchLabel x={450} y={260} t={t - 10} text="SERVER RACK" size={28} color={SCH.dim} />
      {/* Offline indicator */}
      <circle cx={450} cy={500} r={30} fill={SCH.ground} stroke={t > 80 ? SCH.live : SCH.dim} strokeWidth={3} />
      <text x={450} y={510} textAnchor="middle" fontFamily="monospace" fontSize={20} fill={t > 80 ? SCH.live : SCH.dim}>OFF</text>
      {/* Bank terminal */}
      <DrawOn d="M 1000 350 L 1000 600 M 1200 350 L 1200 600 M 1000 350 L 1200 350 M 1000 600 L 1200 600" t={t - 30} dur={40} color={SCH.line} width={3} />
      <DrawOn d="M 1020 380 L 1180 380 M 1020 420 L 1180 420 M 1020 460 L 1100 460" t={t - 35} dur={35} color={SCH.dim} width={2} />
      <SchLabel x={1100} y={320} t={t - 40} text="BANK TERMINAL" size={28} color={SCH.dim} />
      <rect x={1030} y={490} width={140} height={40} rx={4} fill={SCH.ground} stroke={SCH.dim} strokeWidth={2} />
      <text x={1100} y={518} textAnchor="middle" fontFamily="monospace" fontSize={18} fill={SCH.dim}>FROZEN</text>
      {/* Supply chain */}
      <Arrow x0={700} y0={800} x1={1000} y1={800} t={t - 60} dur={40} color={SCH.dim} bend={-0.1} />
      <Arrow x0={1000} y0={800} x1={1300} y1={800} t={t - 70} dur={40} color={SCH.dim} bend={0.1} />
      <SchLabel x={850} y={840} t={t - 65} text="SUPPLY" size={24} color={SCH.dim} />
      <SchLabel x={1150} y={840} t={t - 75} text="CHAIN" size={24} color={SCH.dim} />
      {/* Counter */}
      <CountUp x={960} y={960} t={t - 90} to={847000} dur={60} size={48} color={SCH.live} suffix=" OFFLINE" format={(v) => Math.round(v).toLocaleString()} />
      <SchLabel x={960} y={1020} t={t - 90} text="NODES DISCONNECTED" size={24} color={SCH.dim} />
    </g>
  );
};

// ---------- SH4: medium, study - Day 12: Analog Revival ----------
// Emergency red lamps, paper maps, handwritten ledgers, vacuum-tube radio.
export const Sh4: React.FC<ShotProps> = ({ t }) => {
  const pose = poseAt(t, [
    { f: 0, p: { x: 880, y: 712, yaw: 0.4, armL: { a: 170, b: 30 }, armR: { a: 30, b: -10 }, look: -0.5 } },
    { f: 40, p: { armL: { a: 150, b: 20 }, armR: { a: 60, b: 10 } }, ease: easeOut },
    { f: 100, p: { armL: { a: 170, b: 30 }, armR: { a: 30, b: -10 } } },
  ]);
  const face = faceAt(t, [[0, 'worried'], [30, 'neutral'], [80, 'smug']]);
  const radioGlow = Math.sin(t * 1.5) * 0.3 + 0.5;
  return (
    <g transform={camT(900, 560, kf(t, [[0, 1.2], [180, 1.25]]))}>
      <Study t={t} id="sh4" veil={0.35} night={true} />
      <Hero look={PIP} pose={{ ...pose, ...face }} shadow={0} rimId="rimL" />
      <Desk x0={500} x1={1260} y={700} laptop={false} lamp={false} />
      {/* Paper map on desk */}
      <rect x={700} y={580} width={320} height={240} fill="#E8DCC8" stroke="#8A7A6A" strokeWidth={2} />
      <path d="M 720 600 Q 820 580 900 620 Q 850 700 780 740 Q 700 700 720 600" fill="none" stroke="#4A3A2A" strokeWidth={2} />
      <path d="M 800 650 Q 840 680 860 710" stroke="#C0392B" strokeWidth={3} strokeDasharray="8 4" />
      {/* Handwritten ledger */}
      <rect x={1000} y={600} width={200} height={180} fill="#F6EFE3" stroke="#8A7A6A" strokeWidth={2} />
      {Array.from({ length: 10 }).map((_, i) =>
        <path key={i} d={`M 1020 ${620 + i * 16} L 1170 ${620 + i * 16}`} stroke="#2A2020" strokeWidth={1.5} opacity={0.7} />
      )}
      {/* Vacuum tube radio */}
      <rect x={580} y={580} width={160} height={140} rx={8} fill="#2A2028" />
      <rect x={600} y={600} width={120} height={60} rx={4} fill="#1A141C" />
      <circle cx={660} cy={630} r={25} fill="#0A080C" stroke="#3A2A3C" strokeWidth={3} />
      <Glow x={660} y={630} r={80} kind="red" o={radioGlow * 0.6} />
      <rect x={610} y={680} width={100} height={20} rx={4} fill="#3A2A2A" />
      <circle cx={620} cy={690} r={6} fill="#FF4A4A" opacity={radioGlow} />
      <circle cx={660} cy={690} r={6} fill="#FFD06A" opacity={0.7} />
      <circle cx={700} cy={690} r={6} fill="#6AFF6A" opacity={0.5} />
      {/* Emergency red lamp */}
      <Glow x={960} y={400} r={400} kind="red" o={0.3} />
      <rect x={930} y={380} width={60} height={80} rx={4} fill="#3A1A1A" />
      <circle cx={960} cy={400} r={20} fill="#FF3333" opacity={0.8 + Math.sin(t * 3) * 0.2} />
      <Foreground blur={10}>
        <rect x={400} y={800} width={220} height={40} rx={6} fill="#120D16" />
        <rect x={412} y={762} width={200} height={40} rx={6} fill="#17111C" />
      </Foreground>
    </g>
  );
};

// ---------- SH5: wide, rooftop - Day 18: Local Mesh ----------
// Rooftop antennas spring to life, beaming short-range peer-to-peer radio and laser links.
export const Sh5: React.FC<ShotProps> = ({ t }) => {
  const meshPhase = t / 15;
  const antenna1On = t > 20;
  const antenna2On = t > 50;
  const antenna3On = t > 80;
  const laserPhase = (t % 30) / 30;
  return (
    <g transform={camT(960, 540, kf(t, [[0, 0.9], [180, 0.95]]))}>
      <Rooftop t={t} clock={false} low={0} cityLit={0.5} />
      {/* Antenna 1 - left rooftop */}
      <g transform="translate(200 760)">
        <path d="M 0 0 L 0 -120" stroke="#3A3444" strokeWidth={6} strokeLinecap="round" />
        <circle cx={0} cy={-120} r={8} fill={antenna1On ? "#00F0FF" : "#3A3444"} />
        {antenna1On && <Glow x={0} y={-120} r={60} o={0.7} kind="cool" />}
        {/* Radio waves */}
        {antenna1On && [0, 1, 2].map((i) => (
          <path key={i} d="M -40 0 Q 0 -40 40 0 M -60 0 Q 0 -80 60 0 M -80 0 Q 0 -120 80 0"
            stroke="#00F0FF" strokeWidth={2} fill="none" opacity={0.6 - i * 0.15}
            transform={`translate(0 ${-120 + i * 20}) scale(${1 + (meshPhase + i) % 1})`} />
        ))}
        {/* Laser to center */}
        {antenna1On && antenna2On && (
          <path d="M 0 -120 L 760 0" stroke="#00FFFF" strokeWidth={3} strokeDasharray={laserPhase * 1000} strokeDashoffset={laserPhase * 1000 - 1000} opacity={0.8} />
        )}
      </g>
      {/* Antenna 2 - center (our roof) */}
      <g transform="translate(960 760)">
        <path d="M 0 0 L 0 -140" stroke="#3A3444" strokeWidth={8} strokeLinecap="round" />
        <circle cx={0} cy={-140} r={10} fill={antenna2On ? "#00F0FF" : "#3A3444"} />
        {antenna2On && <Glow x={0} y={-140} r={80} o={0.8} kind="cool" />}
        {antenna2On && [0, 1, 2, 3].map((i) => (
          <path key={i} d="M -50 0 Q 0 -50 50 0 M -70 0 Q 0 -100 70 0 M -90 0 Q 0 -150 90 0"
            stroke="#00F0FF" strokeWidth={2.5} fill="none" opacity={0.7 - i * 0.12}
            transform={`translate(0 ${-140 + i * 20}) scale(${1 + (meshPhase + i * 0.5) % 1})`} />
        ))}
      </g>
      {/* Antenna 3 - right rooftop */}
      <g transform="translate(1720 760)">
        <path d="M 0 0 L 0 -120" stroke="#3A3444" strokeWidth={6} strokeLinecap="round" />
        <circle cx={0} cy={-120} r={8} fill={antenna3On ? "#00F0FF" : "#3A3444"} />
        {antenna3On && <Glow x={0} y={-120} r={60} o={0.7} kind="cool" />}
        {antenna3On && [0, 1, 2].map((i) => (
          <path key={i} d="M -40 0 Q 0 -40 40 0 M -60 0 Q 0 -80 60 0 M -80 0 Q 0 -120 80 0"
            stroke="#00F0FF" strokeWidth={2} fill="none" opacity={0.6 - i * 0.15}
            transform={`translate(0 ${-120 + i * 20}) scale(${1 + (meshPhase + i) % 1})`} />
        ))}
        {/* Laser from center */}
        {antenna2On && antenna3On && (
          <path d="M -760 0 L 0 -120" stroke="#00FFFF" strokeWidth={3} strokeDasharray={laserPhase * 1000} strokeDashoffset={laserPhase * 1000 - 1000} opacity={0.8} />
        )}
      </g>
      {/* Peer-to-peer labels */}
      <SchLabel x={580} y={600} t={t - 30} text="P2P RADIO" size={28} color={SCH.live} />
      <SchLabel x={960} y={560} t={t - 50} text="MESH NODE" size={32} color={SCH.live} />
      <SchLabel x={1340} y={600} t={t - 80} text="LASER LINK" size={28} color={SCH.live} />
    </g>
  );
};

// ---------- SH6: medium, study - Day 25: Rebuilding the Core ----------
// Engineers in rooftop labs wire up decentralized battery arrays and glowing holographic nodes.
export const Sh6: React.FC<ShotProps> = ({ t }) => {
  const pose = poseAt(t, [
    { f: 0, p: { x: 1000, y: 712, yaw: -0.3, armL: { a: 160, b: 20 }, armR: { a: 40, b: -10 }, look: -0.4 } },
    { f: 50, p: { armL: { a: 140, b: 30 }, armR: { a: 80, b: 0 } }, ease: easeOut },
    { f: 120, p: { armL: { a: 160, b: 20 }, armR: { a: 40, b: -10 } } },
  ]);
  const face = faceAt(t, [[0, 'neutral'], [20, 'happy'], [100, 'smug']]);
  const hologramPulse = Math.sin(t * 2) * 0.3 + 0.7;
  const batteryFill = clamp(t / 180);
  return (
    <g transform={camT(960, 560, kf(t, [[0, 1.15], [180, 1.2]]))}>
      <Study t={t} id="sh6" veil={0.3} night={true} shelf={0.3} />
      <Hero look={PIP} pose={{ ...pose, ...face }} shadow={0} rimId="rimL" />
      <Desk x0={540} x1={1340} y={700} laptop={false} lamp={false} />
      {/* Holographic network node */}
      <g transform="translate(860 420)">
        <circle cx={0} cy={0} r={80 * hologramPulse} fill="none" stroke="#00F0FF" strokeWidth={3} opacity={0.5 * hologramPulse} />
        <circle cx={0} cy={0} r={50} fill="none" stroke="#00FFFF" strokeWidth={2} opacity={0.8} />
        <circle cx={0} cy={0} r={20} fill="#00F0FF" opacity={0.6 * hologramPulse} />
        {[0, 45, 90, 135, 180, 225, 270, 315].map((deg) => {
          const rad = (deg * Math.PI) / 180;
          return (
            <g key={deg} transform={`rotate(${deg + t * 0.5})`}>
              <path d="M 60 0 L 120 0" stroke="#00F0FF" strokeWidth={2} opacity={0.7} />
              <circle cx={120} cy={0} r={6} fill="#00FFFF" opacity={0.9} />
            </g>
          );
        })}
      </g>
      <SchLabel x={860} y={520} t={t - 20} text="HOLOGRAPHIC NODE" size={24} color={SCH.live} />
      {/* Battery array */}
      <g transform="translate(1100 580)">
        {Array.from({ length: 6 }).map((_, i) => (
          <g key={i} transform={`translate(${(i - 2.5) * 50} 0)`}>
            <rect x={-20} y={-80} width={40} height={160} rx={4} fill="#1A1822" stroke="#3A3444" strokeWidth={2} />
            <rect x={-16} y={76 - 150 * batteryFill} width={32} height={150 * batteryFill} rx={2} fill="#00F0FF" opacity={0.8} />
            <rect x={-16} y={-76} width={32} height={152} rx={2} fill="none" stroke="#00F0FF" strokeWidth={1.5} opacity={0.5} />
            <text x={0} y={100} textAnchor="middle" fontFamily="monospace" fontSize={14} fill={SCH.dim}>BAT {i + 1}</text>
          </g>
        ))}
      </g>
      <SchLabel x={1100} y={780} t={t - 40} text="DECENTRALIZED BATTERY ARRAY" size={24} color={SCH.live} />
      {/* Wiring */}
      <path d="M 940 420 Q 1000 500 1050 580" stroke="#00F0FF" strokeWidth={3} strokeDasharray="10 5" opacity={0.6} fill="none" />
      <path d="M 940 420 Q 900 500 850 580" stroke="#00F0FF" strokeWidth={3} strokeDasharray="10 5" opacity={0.6} fill="none" />
      <Foreground blur={10}>
        <rect x={440} y={800} width={220} height={40} rx={6} fill="#120D16" />
        <rect x={452} y={762} width={200} height={40} rx={6} fill="#17111C" />
      </Foreground>
    </g>
  );
};

// ---------- SH7: wide, rooftop - Day 30: Signal Restored ----------
// A dramatic cyan wave sweeps across the skyline as clean optical beams reconnect every tower in a global sync.
export const Sh7: React.FC<ShotProps> = ({ t }) => {
  const waveProgress = clamp((t - 20) / 140);
  const sunRise = easeOut(clamp(t / 60));
  const beamsOn = t > 80;
  const flashIntensity = t === 1080 ? 1 : (t > 1080 && t < 1085 ? 1 - (t - 1080) / 5 : 0);
  return (
    <g transform={camT(960, 540 - sunRise * 100, kf(t, [[0, 0.85], [180, 0.95]]))}>
      <Rooftop t={t} clock={false} low={0} cityLit={sunRise} blackout={1 - waveProgress} red={0} />
      {/* Cyan wave sweeping across city */}
      <path
        d="M -400 760 Q 960 ${760 - waveProgress * 400} 2320 760 L 2320 1080 L -400 1080 Z"
        fill="#00FFFF"
        opacity={0.15 * waveProgress}
        style={{ mixBlendMode: 'screen' }}
      />
      {/* Optical beams from rooftops */}
      {beamsOn && [
        { x: 200, y: 760, target: { x: 960, y: 400 } },
        { x: 960, y: 760, target: { x: 960, y: 300 } },
        { x: 1720, y: 760, target: { x: 960, y: 400 } },
        { x: 400, y: 680, target: { x: 960, y: 400 } },
        { x: 1520, y: 680, target: { x: 960, y: 400 } },
      ].map((beam, i) => (
        <g key={i}>
          <path
            d={`M ${beam.x} ${beam.y} L ${beam.target.x} ${beam.target.y}`}
            stroke="#00FFFF"
            strokeWidth={4}
            strokeDasharray={20}
            strokeDashoffset={-t * 10}
            opacity={0.9}
            style={{ filter: 'drop-shadow(0 0 10px #00FFFF)' }}
          />
          <circle cx={beam.x} cy={beam.y} r={8} fill="#00FFFF" />
          <Glow x={beam.x} y={beam.y} r={50} kind="cool" o={0.8} />
        </g>
      ))}
      {/* Central beam to sky */}
      {beamsOn && (
        <g>
          <path d="M 960 760 L 960 100" stroke="#00FFFF" strokeWidth={6} strokeDasharray={30} strokeDashoffset={-t * 15} opacity={1} style={{ filter: 'drop-shadow(0 0 20px #00FFFF)' }} />
          <circle cx={960} cy={760} r={12} fill="#00FFFF" />
          <Glow x={960} y={760} r={100} kind="cool" o={1} />
          <Glow x={960} y={200} r={150} kind="cool" o={0.6} />
        </g>
      )}
      {/* Flash at f:1080 (frame 1080 is at t=1080 in global, but this shot starts at 1080) */}
      {t > 0 && t < 10 && flashIntensity > 0 && (
        <rect x={-400} y={-400} width={2720} height={1880} fill="#00FFFF" opacity={flashIntensity * 0.6} style={{ mixBlendMode: 'screen' }} />
      )}
      <SchLabel x={960} y={300} t={t - 50} text="GLOBAL SYNC" size={48} color={SCH.live} />
      <SchLabel x={960} y={360} t={t - 50} text="DAY 30 — SIGNAL RESTORED" size={28} color={SCH.dim} />
    </g>
  );
};

// ---------- SH8: wide, rooftop - The Future Payoff ----------
// A solar-punk metropolis hums beneath an unbreakable, decentralized peer-to-peer orbital and rooftop mesh network.
export const Sh8: React.FC<ShotProps> = ({ t }) => {
  const orbitPhase = t / 50;
  const meshPulse = Math.sin(t * 1.5) * 0.2 + 0.8;
  const pose = poseAt(t, [
    { f: 0, p: { x: 960, y: 780, scale: 1.3, yaw: 0, armL: { a: 150, b: 30 }, armR: { a: 150, b: 30 }, headTilt: 10 } },
    { f: 90, p: { headTilt: -5 } },
  ]);
  const face = faceAt(t, [[0, 'happy'], [60, 'cool']]);
  return (
    <g transform={camT(960, 520, kf(t, [[0, 0.8], [180, 0.88]]))}>
      <Rooftop t={t} clock={false} low={0} cityLit={2.5} blackout={0} red={0} />
      {/* Orbital mesh - satellites */}
      {[0, 1, 2, 3, 4, 5].map((i) => {
        const angle = orbitPhase + i * Math.PI / 3;
        const r = 400;
        const x = 960 + Math.cos(angle) * r;
        const y = 400 + Math.sin(angle) * r * 0.5;
        return (
          <g key={i} transform={`translate(${x} ${y})`}>
            <circle cx={0} cy={0} r={12} fill="#FFD06A" />
            <Glow x={0} y={0} r={60} o={0.6 * meshPulse} kind="warm" />
            {/* Laser links between satellites */}
            <path
              d={`M 0 0 L ${960 + Math.cos(angle + Math.PI / 3) * r - x} ${400 + Math.sin(angle + Math.PI / 3) * r * 0.5 - y}`}
              stroke="#FFD06A"
              strokeWidth={2}
              strokeDasharray="15 10"
              strokeDashoffset={-t * 5}
              opacity={0.6 * meshPulse}
            />
            {/* Downlink to rooftops */}
            <path
              d={`M 0 0 L ${960 - x} ${760 - y}`}
              stroke="#00F0FF"
              strokeWidth={1.5}
              strokeDasharray="10 5"
              strokeDashoffset={-t * 8}
              opacity={0.5 * meshPulse}
            />
          </g>
        );
      })}
      {/* Rooftop mesh nodes pulsing */}
      {[200, 500, 960, 1420, 1720].map((x, i) => (
        <g key={i} transform={`translate(${x} 760)`}>
          <circle cx={0} cy={0} r={8 * meshPulse} fill="#00F0FF" opacity={0.9} />
          <Glow x={0} y={0} r={40 * meshPulse} kind="cool" o={0.5 * meshPulse} />
          {[0, 1, 2, 3].map((j) => (
            <circle key={j} cx={0} cy={0} r={20 + j * 25 + (t * 2) % 100} fill="none" stroke="#00F0FF" strokeWidth={1.5} opacity={0.3 * (1 - j * 0.2) * meshPulse} />
          ))}
        </g>
      ))}
      {/* Title card */}
      <TitleCard t={t - 20} lines={['THE FUTURE PAYOFF', 'AN UNBREAKABLE MESH']} accent="MESH" accentT={60} />
      <Hero look={PIP} pose={{ ...pose, ...face }} shadow={0.4} rimId="rimR" />
      <Sparkle x={600} y={300} t={t} s={1.5} />
      <Sparkle x={1300} y={250} t={t - 15} s={1.2} />
      <Sparkle x={400} y={400} t={t - 30} s={1.0} />
    </g>
  );
};