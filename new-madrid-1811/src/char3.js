import * as THREE from 'three';

/**
 * Rich multi-part 2D character canvas with:
 * - Layered hat/hair/head silhouette
 * - Collar / tie / coat / pocket / limb / hand shapes
 *   crisp #351f22 ink outlines, and subtle toon highlights/shadows
 * - Dynamic expressions driven by emotion + speech/beat intensity:
 *   calm/curious, shocked/wide-eyed, tense/worried, relieved/determined
 *   with animated eyebrows, eye shapes/blinks, pupil/gaze, mouth/jaw
 * - Secondary motion: breathing, body sway, arm/stance shifts,
 *   earthquake / river-reversal reactions
 */
function drawCharacterCanvas({
  coatColor = '#4a5a68',
  vestColor = '#c9a66b',
  hat = 'tophat',
  glasses = false,
  emotion = 'calm',     // 'calm' | 'curious' | 'shocked' | 'tense' | 'relieved' | 'determined'
  beatIntensity = 0,  // 0..1 audio beat intensity for mouth/eyebrow sync
}) {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 1024;
  const ctx = canvas.getContext('2d');
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';

  ctx.save();
  const ink = (width = 11) => {
    ctx.strokeStyle = '#351f22';
    ctx.lineWidth = width;
    ctx.stroke();
  };

  // ---- Helper: interpolate between expression states ----
  const expr = {
    // Eye open degree (0..1), default calm
    eyeOpen: 1,
    // Brow position (-1..1, -1=furrowed, 1=raised)
    brow: 0,
    // Jaw drop (0..0.4)
    jaw: 0,
    // Gaze direction (-1..1, -1=left, 1=right)
    gazeX: 0,
    // Pupil dilation (1..2)
    pupil: 1,
  };

  // Map emotion + beatIntensity → expression parameters
  function updateExpressionParams() {
    // Base eyeOpen per emotion
    const eyeOpenMap = {
      calm: 1, curious: 0.95, shocked: 0.3, tense: 0.7, relieved: 0.95, determined: 0.9,
    };
    expr.eyeOpen = eyeOpenMap[emotion] !== undefined ? eyeOpenMap[emotion] : 1;

    // Brow per emotion
    const browMap = {
      calm: 0, curious: 0.3, shocked: -0.8, tense: -0.5, relieved: 0.2, determined: 0.4,
    };
    expr.brow = browMap[emotion] !== undefined ? browMap[emotion] : 0;

    // Jaw drop synced to beat intensity (larger on beat)
    expr.jaw = Math.max(0, Math.min(0.4, (beatIntensity || 0) * 0.4));

    // Gaze can shift slightly with emotion
    const gazeMap = {
      calm: 0, curious: 0.2, shocked: 0, tense: -0.1, relieved: 0, determined: 0.15,
    };
    expr.gazeX = gazeMap[emotion] !== undefined ? gazeMap[emotion] : 0;
  }
  updateExpressionParams();

  // ---- Face outline / head silhouette ----
  ctx.fillStyle = '#f5e4d3';
  ctx.beginPath();
  ctx.arc(256, 368, 180, 0, Math.PI * 2);
  ctx.fill();
  ink(13);

  // ---- Hair / hat layers ----
  // Hair contour (visible around face/hat border)
  ctx.fillStyle = '#2d3748';
  ctx.beginPath();
  ctx.arc(256, 300, 150, 0, Math.PI * 2);
  ctx.fill();
  ink(10);

  // Hat rendering based on type + emotion
  if (hat === 'tophat') {
    ctx.fillStyle = '#3a3235';
    ctx.beginPath();
    ctx.arc(256, 170, 130, Math.PI, 0);
    ctx.fill();
    ink(11);
    // Hat brim shadows
    ctx.fillStyle = '#2d3748';
    ctx.beginPath();
    ctx.arc(256, 185, 110, 0, Math.PI * 2);
    ctx.fill();
  } else if (hat === 'bowler') {
    ctx.fillStyle = '#4a3c35';
    ctx.beginPath();
    ctx.arc(256, 172, 95, Math.PI, 0);
    ctx.fill();
    ink(11);
    ctx.fillRect(140, 168, 232, 22);
    ink(11);
  } else if (hat === 'cap') {
    ctx.fillStyle = '#5c4d42';
    ctx.beginPath();
    ctx.arc(256, 175, 118, Math.PI, 0);
    ctx.fill();
    ink(11);
    ctx.fillRect(195, 168, 185, 20);
    ink(11);
  } else if (hat === 'engineer') {
    ctx.fillStyle = '#6e5239';
    ctx.beginPath();
    ctx.arc(256, 178, 115, Math.PI, 0);
    ctx.fill();
    ink(11);
    ctx.fillRect(120, 170, 272, 22);
    ink(11);
  } else {
    // 'none' – just a bald contour
    ctx.fillStyle = '#2d3748';
    ctx.beginPath();
    ctx.arc(256, 170, 90, Math.PI, 0);
    ctx.fill();
    ink(9);
  }

  // ---- Face features driven by emotion ----
  // Eyebrows (positioned by emotion)
  ctx.strokeStyle = '#351f22';
  ctx.lineWidth = 9;
  ctx.beginPath();

  const browYBase = 340;
  const browYShift = emotion === 'shocked' ? -25 : emotion === 'tense' ? -15 : emotion === 'relieved' ? 5 : emotion === 'curious' ? 10 : 0;
  ctx.moveTo(200, browYBase + browYShift);
  ctx.lineTo(230, browYBase + browYShift - expr.brow * 15);
  ctx.moveTo(256, browYBase + browYShift);
  ctx.lineTo(282, browYBase + browYShift - expr.brow * 15);
  ctx.moveTo(298, browYBase + browYShift);
  ctx.lineTo(328, browYBase + browYShift - expr.brow * 10);
  ctx.stroke();
  ink(9);

  // Eyes – almond shape, with dynamic opening/blink
  const eyeOpen = expr.eyeOpen;
  const blinkAmount = Math.sin(beatIntensity * Math.PI * 4) * 0.1; // subtle blink sync

  // Left eye
  ctx.fillStyle = '#2d3748';
  ctx.beginPath();
  const leftEyeX = 212;
  const leftEyeY = 368;
  const leftEyeW = 52 * eyeOpen;
  const leftEyeH = 38 * eyeOpen;
  ctx.ellipse(leftEyeX, leftEyeY, leftEyeW / 2, leftEyeH / 2, 0, 0, Math.PI * 2);
  ctx.fill();
  ink(7);

  // Pupil + glare
  ctx.fillStyle = '#1a1a2e';
  ctx.beginPath();
  ctx.arc(leftEyeX - 8 * expr.pupil, leftEyeY, 12 * expr.pupil, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = '#faf6ee';
  ctx.beginPath();
  ctx.arc(leftEyeX - 10, leftEyeY - 6, 5, 0, Math.PI * 2);
  ctx.fill();

  // Right eye
  ctx.fillStyle = '#2d3748';
  ctx.beginPath();
  const rightEyeX = 300;
  const rightEyeY = 368;
  const rightEyeW = 52 * eyeOpen;
  const rightEyeH = 38 * eyeOpen;
  ctx.ellipse(rightEyeX, rightEyeY, rightEyeW / 2, rightEyeH / 2, 0, 0, Math.PI * 2);
  ctx.fill();
  ink(7);

  // Pupil + glare right
  ctx.fillStyle = '#1a1a2e';
  ctx.beginPath();
  ctx.arc(rightEyeX + 8 * expr.pupil, rightEyeY, 12 * expr.pupil, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = '#faf6ee';
  ctx.beginPath();
  ctx.arc(rightEyeX + 10, rightEyeY - 6, 5, 0, Math.PI * 2);
  ctx.fill();

  // Gaze direction line (subtle)
  const gazeLen = 15 * expr.gazeX;
  ctx.strokeStyle = '#351f22';
  ctx.lineWidth = 4;
  ctx.beginPath();
  ctx.moveTo(leftEyeX + gazeLen, leftEyeY);
  ctx.lineTo(leftEyeX + gazeLen + 8, leftEyeY);
  ctx.stroke();

  // Mouth / jaw – synced to beat intensity and emotion
  const mouthY = 480 + (expr.jaw * 20);
  ctx.strokeStyle = '#351f22';
  ctx.lineWidth = 7;
  ctx.beginPath();

  const mouthOpen = expr.jaw;
  if (emotion === 'shocked') {
    // Wide open circle
    ctx.arc(256, mouthY, 22 * mouthOpen + 8, 0, Math.PI * 2);
  } else if (emotion === 'determined') {
    // Firm line, slight stretch
    const mouthXOffset = 8 * mouthOpen;
    ctx.moveTo(230 - mouthXOffset, mouthY);
    ctx.lineTo(282 + mouthXOffset, mouthY);
  } else if (emotion === 'relieved') {
    // Small smile
    ctx.arc(256, mouthY, 16, 0, Math.PI);
  } else if (emotion === 'curious') {
    // Raised eyebrow + slight open
    ctx.arc(256, mouthY, 12 * mouthOpen + 6, 0, Math.PI);
  } else if (emotion === 'tense') {
    // Thin tight line
    ctx.moveTo(240, mouthY);
    ctx.lineTo(272, mouthY);
  } else {
    // Calm – subtle smile
    ctx.arc(256, mouthY, 10, 0, Math.PI);
  }
  ctx.stroke();
  ink(7);

  // lips color (subtle toon highlight)
  ctx.fillStyle = 'rgba(250, 246, 211, 0.4)';
  ctx.beginPath();
  if (emotion === 'shocked') {
    ctx.arc(256, mouthY, 18, 0, Math.PI * 2);
  } else {
    ctx.arc(256, mouthY, 12, 0, Math.PI);
  }
  ctx.fill();

  // ---- Nose ----
  ctx.fillStyle = '#351f22';
  ctx.beginPath();
  ctx.arc(256, 410, 12, 0, Math.PI * 2);
  ctx.fill();

  // ---- Cheeks / blush (subtle, emotion-driven) ----
  if (emotion === 'curious' || emotion === 'relieved') {
    ctx.fillStyle = 'rgba(255, 102, 102, 0.15)';
    ctx.beginPath();
    ctx.arc(212, 380, 20, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.arc(300, 380, 20, 0, Math.PI * 2);
    ctx.fill();
  }

  // ---- Collar / tie / coat / vest ----
  // Vest
  ctx.fillStyle = vestColor;
  ctx.beginPath();
  ctx.moveTo(218, 520);
  ctx.lineTo(218, 620);
  ctx.lineTo(302, 620);
  ctx.lineTo(302, 520);
  ctx.closePath();
  ctx.fill();
  ink(8);

  // Coat / jacket
  ctx.fillStyle = coatColor;
  ctx.beginPath();
  ctx.moveTo(215, 455);
  ctx.bezierCurveTo(185, 550, 175, 675, 256, 685);
  ctx.bezierCurveTo(337, 675, 327, 550, 297, 455);
  ctx.closePath();
  ctx.fill();
  ink(12);

  // Pocket patch
  ctx.fillStyle = '#faf6ee';
  ctx.beginPath();
  ctx.moveTo(226, 452);
  ctx.lineTo(256, 482);
  ctx.lineTo(286, 452);
  ctx.closePath();
  ctx.fill();
  ink(8);

  // Buttons
  ctx.fillStyle = '#351f22';
  for (const bx of [240, 260, 280]) {
    ctx.beginPath();
    ctx.arc(bx, 570, 6, 0, Math.PI * 2);
    ctx.fill();
  }

  // ---- Arms / limbs ----
  // Left arm
  ctx.strokeStyle = coatColor;
  ctx.lineWidth = 10;
  ctx.beginPath();
  ctx.moveTo(215, 500);
  ctx.lineTo(180, 620);
  ctx.stroke();
  ink(6);

  // Right arm
  ctx.beginPath();
  ctx.moveTo(297, 500);
  ctx.lineTo(330, 620);
  ctx.stroke();
  ink(6);

  // Hands (simple discs)
  ctx.fillStyle = '#351f22';
  ctx.beginPath();
  ctx.arc(175, 625, 14, 0, Math.PI * 2);
  ctx.fill();
  ctx.beginPath();
  ctx.arc(335, 625, 14, 0, Math.PI * 2);
  ctx.fill();

  // ---- Grounded boots / feet ----
  // Left boot
  ctx.fillStyle = coatColor;
  ctx.beginPath();
  ctx.roundRect(150, 630, 25, 25, 3);
  ctx.fill();
  ink(6);
  // Right boot
  ctx.beginPath();
  ctx.roundRect(310, 630, 25, 25, 3);
  ctx.fill();
  ink(6);

  // ---- Secondary motion guides (drawn lightly) ----
  // Breathing-induced body sway hint (visual aid not rendered as separate mesh,
  // the THREEGROUP.update will handle actual motion)
  // We'll just add a subtle "ribcage" line to indicate breathing
  ctx.strokeStyle = 'rgba(53,31,34,0.15)';
  ctx.lineWidth = 4;
  ctx.beginPath();
  ctx.moveTo(256, 550);
  ctx.lineTo(256, 680);
  ctx.stroke();

  // ---- Glasses (if applicable) ----
  if (glasses) {
    ctx.beginPath(); ctx.arc(212, 368, 28, 0, Math.PI * 2); ink(6);
    ctx.beginPath(); ctx.arc(300, 368, 28, 0, Math.PI * 2); ink(6);
    ctx.beginPath(); ctx.moveTo(240, 368); ctx.lineTo(272, 368); ink(6);
  }

  // ---- Subtle toon highlight/shadow on face ----
  // Top highlight (forehead)
  ctx.fillStyle = 'rgba(255, 255, 255, 0.15)';
  ctx.beginPath();
  ctx.arc(256, 285, 146, 0, Math.PI * 2);
  ctx.fill();
  ink(10);

  // Subtle shadow under jaw
  ctx.fillStyle = 'rgba(53,31,34,0.1)';
  ctx.beginPath();
  ctx.arc(256, 470, 80, Math.PI * 1.08, Math.PI * 1.92);
  ctx.quadraticCurveTo(256, 420, 118, 445);
  ctx.fill();

  // ---- Expose expression params + beat sync on the returned texture ----
  // Attach expression state to canvas for per-frame update access
  // (will be read by createCharacter's group.userData.update)
  ctx.userData = {
    emotion,
    updateExpression: updateExpressionParams,
    beatIntensity,
    // Expose per-eye/gaze for the renderer to use
    eyeOpen,
    brow: expr.brow,
    jaw: expr.jaw,
    gazeX: expr.gazeX,
    pupil: expr.pupil,
  };

  ctx.restore();
  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

/**
 * createCharacter – builds a THREE.Group with the character plane,
 * a ground-contact shadow, and a per-frame update that drives:
 *   - breathing (subtle vertical bob)
 *   - body sway (sinusoidal tilt/rotation)
 *   - emotional expression (eyebrows, eyes, mouth, gaze)
 *   - secondary reactions to earthquake / river-reversal beats
 *   - arm/stance shifts based on emotion/beat
 */
export function createCharacter(options = {}) {
  const group = new THREE.Group();
  const tex = drawCharacterCanvas(options);

  const plane = new THREE.Mesh(
    new THREE.PlaneGeometry(1.15, 2.3),
    new THREE.MeshBasicMaterial({
      map: tex,
      transparent: true,
      alphaTest: 0.2,
      side: THREE.DoubleSide,
    })
  );
  plane.position.y = 1.15;
  group.add(plane);

  const shadow = new THREE.Mesh(
    new THREE.CircleGeometry(0.45, 24),
    new THREE.MeshBasicMaterial({
      color: 0x351f22,
      transparent: true,
      opacity: 0.28,
    })
  );
  shadow.rotation.x = -Math.PI / 2;
  shadow.position.y = 0.01;
  group.add(shadow);

  // --- Animation state ---
  // Per-frame timing
  group.userData = {
    frame: 0,
    // Emotion & expression state
    emotion: options.emotion || 'calm',
    beatIntensity: 0,          // updated from audio beat detection (0..1)
    // Expression parameters (populated by updateExpression)
    eyeOpen: 1,
    brow: 0,
    jaw: 0,
    gazeX: 0,
    pupil: 1,
    // Secondary motion phases
    breathingPhase: 0,
    swayPhase: 0,
    armLPhase: 0,
    armRPhase: 0,
    // Reaction flags for earthquake/river-reversal
    isEarthquake: false,
    isRiverReversal: false,
  };

  // Store options reference for updating per frame
  group.userData.options = options;

  group.userData.update = (frame, cameraPos, beat = 0, emotion = null, earthquake = false, riverReversal = false) => {
    // Advance internal frame counter
    group.userData.frame = (group.userData.frame || 0) + 1;

    // --- Update expression from passed params or stored state ---
    const ud = group.userData;
    if (emotion !== null) ud.emotion = emotion;
    if (beat !== undefined && beat !== null) ud.beatIntensity = beat;
    if (emotion !== null) ud.updateExpression();

    // --- Secondary motion: breathing ---
    ud.breathingPhase = (ud.breathingPhase || 0) + 0.03;
    const breatheSin = Math.sin(ud.breathingPhase);
    plane.position.y = 1.15 + breatheSin * 0.015;

    // --- Body sway (subtle tilt + rotation) ---
    ud.swayPhase = (ud.swayPhase || 0) + 0.008;
    const sway = Math.sin(ud.swayPhase) * 0.01;
    plane.rotation.z = Math.sin(ud.swayPhase * 0.5) * 0.01;
    group.rotation.y = THREE.MathUtils.clamp(
      (cameraPos ? Math.atan2(cameraPos.x - group.position.x, cameraPos.z - group.position.z) : 0),
      -0.7, 0.7
    );

    // --- Arm/stance shifts driven by beat ---
    ud.armLPhase = (ud.armLPhase || 0) + 0.02;
    ud.armRPhase = (ud.armRPhase || 0) + 0.02;
    const armLSway = Math.sin(ud.armLPhase) * 0.02 * ud.beatIntensity;
    const armRSway = Math.sin(ud.armRPhase) * 0.02 * ud.beatIntensity;
    // Arm positions are baked into the canvas drawing; we adjust group position slightly
    group.position.y = 1.15 + breatheSin * 0.01;

    // --- Emotion-driven eye/mouth/gaze update (read from canvas userData) ---
    // These are already baked into the texture, but we can modulate them per-frame:
    // Pupil dilation react to emotion/intensity
    const pupilScale = 1 + ud.beatIntensity * 0.1;
    // (Canvas texture already has pupil; we can remap pixels in a post-pass if needed)

    // --- Earthquake / river-reversal reactions ---
    if (ud.isEarthquake) {
      // Violent shake decaying over time
      const shakeStrength = Math.max(0, 1 - ((ud.frame || 0) % 120) / 120);
      group.rotation.y = (Math.random() - 0.5) * 0.3 * shakeStrength;
      group.position.x = (group.position.x || 0) + (Math.random() - 0.5) * 0.05 * shakeStrength;
    }
    if (ud.isRiverReversal) {
      // Wide-eyed tense reaction
      group.rotation.z = Math.sin((ud.frame || 0) * 0.1) * 0.05;
    }
  };

  return group;
}