import * as THREE from 'three';
import {
  createToonGradient,
  createPaintedTexture,
  addInkOutline,
  createFacade,
  createElevatedDeck,
  createStoneArch,
  createLampPost,
  createCrate,
  createPlankSidewalk,
  createBarrel,
  createWorldSign,
} from './kit';
import { createCharacter } from './char3';
import sentenceTimes from './sentence_times.json';

const CUTS = sentenceTimes.cuts || [0, 4.399, 8.798, 13.496, 17.895, 22.593, 27.29, 31.988, 36.387, 41.085, 45.186];

// 0..1 progress inside one shot (shot index must match the sentence index)
function u(t, shot) {
  const start = CUTS[shot] ?? shot * 4.5;
  const end = CUTS[shot + 1] ?? start + 4.5;
  return THREE.MathUtils.clamp((t - start) / Math.max(0.001, end - start), 0, 1);
}

function toonBox(w, h, d, color, gradientMap) {
  const mesh = new THREE.Mesh(
    new THREE.BoxGeometry(w, h, d),
    new THREE.MeshToonMaterial({ map: createPaintedTexture(color), gradientMap })
  );
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  return addInkOutline(mesh, 0.03);
}

function postedSign(text, gradientMap, width = 2.6, height = 0.72, postHeight = 1.5) {
  const group = new THREE.Group();
  const sign = createWorldSign(text, width, height);
  sign.position.y = postHeight + height / 2;
  group.add(sign);

  const postMat = new THREE.MeshToonMaterial({
    map: createPaintedTexture('#7d5a3c'),
    gradientMap,
  });
  for (const px of [-width / 2 + 0.32, width / 2 - 0.32]) {
    const post = new THREE.Mesh(new THREE.BoxGeometry(0.11, postHeight, 0.11), postMat);
    post.position.set(px, postHeight / 2, -0.05);
    post.castShadow = true;
    addInkOutline(post, 0.05);
    group.add(post);
  }
  return group;
}

// Flat painted river/lake block with drifting ink ripple bars.
function createWater({ width, depth, color = '#7f9aa4', gradientMap, bars = 6 }) {
  const group = new THREE.Group();
  const body = toonBox(width, 0.12, depth, color, gradientMap);
  body.position.y = 0.06;
  group.add(body);

  const rippleMat = new THREE.MeshToonMaterial({ color: '#e4ece4', gradientMap });
  const ripples = [];
  for (let i = 0; i < bars; i++) {
    const bar = new THREE.Mesh(
      new THREE.BoxGeometry(1.4 + (i % 3) * 0.6, 0.05, 0.16),
      rippleMat
    );
    addInkOutline(bar, 0.07);
    bar.position.y = 0.15;
    bar.position.z = -depth / 2 + 0.5 + (i * (depth - 1.0)) / Math.max(1, bars - 1);
    group.add(bar);
    ripples.push(bar);
  }

  group.userData.ripples = ripples;
  group.userData.span = width + 4;
  group.userData.baseY = 0.06;
  return group;
}

function rippleFlow(water, direction = 1, speed = 1.3) {
  const ripples = water.userData.ripples;
  const span = water.userData.span;
  return (t) => {
    ripples.forEach((bar, i) => {
      const x0 = i * (span / ripples.length) + t * speed * direction * (1 + i * 0.07);
      bar.position.x = -span / 2 + (((x0 % span) + span) % span);
      bar.position.y = 0.15 + Math.sin(t * 2.1 + i) * 0.025;
    });
  };
}

function createKeelboat(gradientMap) {
  const group = new THREE.Group();

  const hull = toonBox(2.7, 0.42, 0.85, '#8a623c', gradientMap);
  hull.position.y = 0.28;
  group.add(hull);

  const deck = toonBox(2.2, 0.14, 0.66, '#a88259', gradientMap);
  deck.position.y = 0.52;
  group.add(deck);

  const mast = new THREE.Mesh(
    new THREE.CylinderGeometry(0.06, 0.08, 1.9, 8),
    new THREE.MeshToonMaterial({ map: createPaintedTexture('#9c7349'), gradientMap })
  );
  mast.position.y = 1.4;
  mast.castShadow = true;
  addInkOutline(mast, 0.06);
  group.add(mast);

  const sail = new THREE.Mesh(
    new THREE.PlaneGeometry(1.2, 1.15),
    new THREE.MeshToonMaterial({
      map: createPaintedTexture('#efe4cf'),
      side: THREE.DoubleSide,
      gradientMap,
    })
  );
  sail.position.set(0.5, 1.45, 0);
  addInkOutline(sail, 0.02);
  group.add(sail);

  return group;
}

function createCypress(gradientMap, scale = 1) {
  const group = new THREE.Group();
  const trunk = new THREE.Mesh(
    new THREE.CylinderGeometry(0.14, 0.22, 1.7, 8),
    new THREE.MeshToonMaterial({ map: createPaintedTexture('#6b4f36'), gradientMap })
  );
  trunk.position.y = 0.85;
  trunk.castShadow = true;
  addInkOutline(trunk, 0.05);
  group.add(trunk);

  const crown = new THREE.Mesh(
    new THREE.ConeGeometry(0.95, 2.0, 9),
    new THREE.MeshToonMaterial({ map: createPaintedTexture('#5f6f4a'), gradientMap })
  );
  crown.position.y = 2.4;
  crown.castShadow = true;
  addInkOutline(crown, 0.04);
  group.add(crown);

  group.scale.setScalar(scale);
  return group;
}

function createChimney(gradientMap) {
  const stack = toonBox(0.5, 1.5, 0.5, '#9b6a52', gradientMap);
  const cap = toonBox(0.66, 0.16, 0.66, '#7d5a3c', gradientMap);
  const group = new THREE.Group();
  cap.position.y = 0.8;
  stack.position.y = 0.75;
  group.add(stack, cap);
  return group;
}

function createFenceRow(gradientMap, posts = 7) {
  const group = new THREE.Group();
  const rail = toonBox(posts * 0.72, 0.1, 0.1, '#9c7349', gradientMap);
  rail.position.set(0, 0.72, 0);
  group.add(rail);
  for (let i = 0; i < posts; i++) {
    const post = toonBox(0.11, 1.0, 0.11, '#8a623c', gradientMap);
    post.position.set(-posts * 0.36 + 0.36 + i * 0.72, 0.5, 0);
    group.add(post);
  }
  return group;
}

export function buildStoryScene() {
  const gradientMap = createToonGradient();
  const staticObjects = [];
  const dynamicActors = [];
  const characters = [];

  // LOCATION 1 (x = 0): Mississippi levee — 16 December 1811
  const facade1 = createFacade({ color: '#b86b52', gradientMap, width: 7, height: 5.2 });
  facade1.position.set(0, 0, -4.2);
  const walk1 = createPlankSidewalk(10, 1.4, gradientMap);
  walk1.position.set(0, 0, 0.05);
  const sign1 = postedSign('DEC 16 1811', gradientMap, 2.7, 0.74, 1.55);
  sign1.position.set(-2.6, 0, -1.5);
  const sign1b = createWorldSign('MISSISSIPPI 1811', 3.2, 0.8);
  sign1b.position.set(0, 5.9, -3.6);
  const lamp1 = createLampPost(gradientMap, 3.2);
  lamp1.position.set(3.6, 0, -1.4);
  const barrel1 = createBarrel(gradientMap);
  barrel1.position.set(3.1, 0.425, 0.6);
  staticObjects.push(facade1, walk1, sign1, sign1b, lamp1, barrel1);

  const water1 = createWater({ width: 11, depth: 3.0, gradientMap, bars: 7 });
  water1.position.set(0, 0, 2.1);
  const boat1 = createKeelboat(gradientMap);
  boat1.position.set(-3.0, 0.1, 2.2);
  boat1.rotation.y = 0.25;
  staticObjects.push(boat1);

  dynamicActors.push({
    mesh: water1,
    update: (t) => {
      rippleFlow(water1, 1, 1.35)(t);
      boat1.position.y = 0.1 + Math.sin(t * 1.5) * 0.05;
      boat1.rotation.z = Math.sin(t * 1.2) * 0.045;
    },
  });

  const char1 = createCharacter({
    coatColor: '#4a5a68',
    vestColor: '#c9a66b',
    hat: 'tophat',
    glasses: true,
  });
  char1.position.set(1.4, 0.16, 0.45);
  characters.push(char1);

  // LOCATION 2 (x = 40): New Madrid fissure & sand blows
  const facade2 = createFacade({ color: '#a85f48', gradientMap, width: 7.5, height: 5.0 });
  facade2.position.set(40, 0, -4.4);
  const sign2 = postedSign('NEW MADRID', gradientMap, 2.6, 0.72, 1.5);
  sign2.position.set(42.4, 0, -1.7);
  const lamp2 = createLampPost(gradientMap, 3.0);
  lamp2.position.set(36.6, 0, -1.9);
  const crate2 = createCrate(gradientMap, 0.9);
  crate2.position.set(37.2, 0.45, -0.4);
  staticObjects.push(sign2, lamp2, crate2);

  const crackLeft = toonBox(4.6, 0.5, 5.2, '#7a5c41', gradientMap);
  crackLeft.position.set(37.4, 0.12, 1.4);
  crackLeft.rotation.z = 0.07;
  const crackRight = toonBox(4.6, 0.5, 5.2, '#7a5c41', gradientMap);
  crackRight.position.set(42.7, 0.12, 1.4);
  crackRight.rotation.z = -0.07;
  staticObjects.push(crackLeft, crackRight);

  const sandBlow = new THREE.Mesh(
    new THREE.ConeGeometry(0.75, 1.15, 12),
    new THREE.MeshToonMaterial({ map: createPaintedTexture('#d9c39a'), gradientMap })
  );
  sandBlow.position.set(40.1, 0.5, 1.6);
  sandBlow.castShadow = true;
  addInkOutline(sandBlow, 0.04);
  dynamicActors.push({
    mesh: sandBlow,
    update: (t) => {
      const p = u(t, 1);
      const grow = THREE.MathUtils.clamp((p - 0.25) / 0.5, 0, 1);
      sandBlow.scale.set(
        1 + grow * 0.35,
        0.35 + grow * 0.9 + Math.sin(t * 9) * 0.06,
        1 + grow * 0.35
      );
      sandBlow.rotation.y = t * 0.6;
    },
  });

  dynamicActors.push({
    mesh: facade2,
    update: (t) => {
      const p = u(t, 1);
      const shake = Math.sin(t * 34) * 0.04 * (1 - THREE.MathUtils.clamp(p * 1.8, 0, 1));
      facade2.position.y = shake;
      facade2.rotation.z = shake * 0.03;
      crackLeft.rotation.z = 0.07 + shake * 0.35;
      crackRight.rotation.z = -0.07 - shake * 0.35;
      crate2.position.y = 0.45 + Math.abs(shake) * 0.5;
      crate2.rotation.z = shake * 0.25;
    },
  });

  const char2 = createCharacter({
    coatColor: '#5c4d3c',
    vestColor: '#d4b475',
    hat: 'cap',
    glasses: false,
  });
  char2.position.set(41.2, 0, 0.2);
  characters.push(char2);

  // LOCATION 3 (x = 80): cabins and toppling chimneys
  const cabin3 = createFacade({ color: '#c0805d', gradientMap, width: 6.4, height: 4.4 });
  cabin3.position.set(79, 0, -3.9);
  const cabin3b = createFacade({ color: '#a8674c', gradientMap, width: 5.0, height: 3.8 });
  cabin3b.position.set(84.2, 0, -4.6);
  const walk3 = createPlankSidewalk(9, 1.3, gradientMap);
  walk3.position.set(80, 0, -0.2);
  const sign3 = postedSign('CHIMNEYS FALL', gradientMap, 3.0, 0.74, 1.6);
  sign3.position.set(82.6, 0, -1.4);
  const barrel3 = createBarrel(gradientMap);
  barrel3.position.set(77.4, 0.425, 0.7);
  staticObjects.push(cabin3, cabin3b, walk3, sign3, barrel3);

  const chimney3 = createChimney(gradientMap);
  chimney3.position.set(77.6, 4.4, -3.7);
  dynamicActors.push({
    mesh: chimney3,
    update: (t) => {
      const p = u(t, 2);
      const topple = THREE.MathUtils.smoothstep(THREE.MathUtils.clamp((p - 0.3) / 0.45, 0, 1), 0, 1);
      chimney3.rotation.z = -topple * 1.25;
      chimney3.position.y = 4.4 - topple * 0.55;
    },
  });

  const char3 = createCharacter({
    coatColor: '#3f5248',
    vestColor: '#c29b61',
    hat: 'bowler',
    glasses: false,
  });
  char3.position.set(81.4, 0.16, 0.3);
  characters.push(char3);

  // LOCATION 4 (x = 120): church, swinging bell — felt as far as Boston
  const church4 = createFacade({ color: '#b3714f', gradientMap, width: 6.8, height: 5.6 });
  church4.position.set(120, 0, -4.4);
  const arch4 = createStoneArch({ width: 3.6, height: 3.6, depth: 1.2, gradientMap });
  arch4.position.set(123.9, 0, -3.2);
  const sign4 = postedSign('BELLS RING ALONE', gradientMap, 3.3, 0.74, 1.55);
  sign4.position.set(117.6, 0, -1.6);
  const lamp4 = createLampPost(gradientMap, 3.3);
  lamp4.position.set(123.4, 0, -1.2);
  staticObjects.push(church4, arch4, sign4, lamp4);

  const bell4 = new THREE.Group();
  const bellBody = new THREE.Mesh(
    new THREE.ConeGeometry(0.5, 0.8, 14, 1, true),
    new THREE.MeshToonMaterial({
      map: createPaintedTexture('#b98b45'),
      gradientMap,
      side: THREE.DoubleSide,
    })
  );
  bellBody.position.y = -0.4;
  addInkOutline(bellBody, 0.045);
  bell4.add(bellBody);
  const yoke4 = toonBox(1.4, 0.16, 0.3, '#7d5a3c', gradientMap);
  bell4.add(yoke4);
  bell4.position.set(120, 4.3, -3.0);

  const frame4 = new THREE.Group();
  for (const px of [-1.25, 1.25]) {
    const post = toonBox(0.24, 4.9, 0.24, '#8a623c', gradientMap);
    post.position.set(px, 2.45, 0);
    frame4.add(post);
  }
  const beam4 = toonBox(3.2, 0.26, 0.3, '#7d5a3c', gradientMap);
  beam4.position.y = 4.82;
  frame4.add(beam4);
  frame4.position.set(120, 0, -3.0);
  dynamicActors.push({
    mesh: bell4,
    update: (t) => {
      const p = u(t, 3);
      const swing = Math.sin(p * Math.PI) * Math.sin(t * 7.5) * 0.42;
      bell4.rotation.z = swing;
    },
  });
  staticObjects.push(frame4);

  const char4 = createCharacter({
    coatColor: '#6b4a55',
    vestColor: '#cba86f',
    hat: 'engineer',
    glasses: true,
  });
  char4.position.set(121.4, 0, 0.6);
  characters.push(char4);

  // LOCATION 5 (x = 160): 7 February 1812 — the river runs backwards
  const facade5 = createFacade({ color: '#b06a51', gradientMap, width: 6.6, height: 4.6 });
  facade5.position.set(160, 0, -4.6);
  const walk5 = createPlankSidewalk(9, 1.4, gradientMap);
  walk5.position.set(160, 0, -0.1);
  const sign5 = postedSign('FEB 7 1812', gradientMap, 2.7, 0.74, 1.5);
  sign5.position.set(157.4, 0, -1.5);
  const sign5b = createWorldSign('RIVER RUNS BACK', 3.1, 0.78);
  sign5b.position.set(160, 5.3, -3.95);
  const barrel5 = createBarrel(gradientMap);
  barrel5.position.set(163.2, 0.425, 0.5);
  staticObjects.push(facade5, walk5, sign5, sign5b, barrel5);

  const water5 = createWater({ width: 12, depth: 3.4, gradientMap, bars: 8 });
  water5.position.set(160, 0, 2.3);
  const boat5 = createKeelboat(gradientMap);
  boat5.position.set(162.6, 0.1, 2.4);
  boat5.rotation.y = Math.PI - 0.35;
  staticObjects.push(boat5);

  dynamicActors.push({
    mesh: water5,
    update: (t) => {
      rippleFlow(water5, -1, 1.9)(t);
      const p = u(t, 4);
      boat5.position.y = 0.1 + Math.sin(t * 2.4) * 0.12 * (0.4 + p);
      boat5.rotation.z = Math.sin(t * 3.1) * 0.16 * (0.35 + p);
      facade5.position.y = Math.sin(t * 31) * 0.02 * (1 - THREE.MathUtils.clamp(p * 2, 0, 1));
    },
  });

  const char5 = createCharacter({
    coatColor: '#41525f',
    vestColor: '#d0a86c',
    hat: 'cap',
    glasses: false,
  });
  char5.position.set(161.4, 0.16, 0.4);
  characters.push(char5);

  // LOCATION 6 (x = 200): settlers abandon New Madrid
  const house6 = createFacade({ color: '#bd7a58', gradientMap, width: 6.2, height: 4.4 });
  house6.position.set(199.2, 0, -4.2);
  const house6b = createFacade({ color: '#a46349', gradientMap, width: 4.8, height: 3.6 });
  house6b.position.set(204.6, 0, -4.8);
  const sign6 = postedSign('NEW MADRID FLEES', gradientMap, 3.3, 0.74, 1.55);
  sign6.position.set(202.2, 0, -1.5);
  const walk6 = createPlankSidewalk(8, 1.3, gradientMap);
  walk6.position.set(200, 0, -0.2);
  staticObjects.push(house6, house6b, sign6, walk6);

  const crate6a = createCrate(gradientMap, 0.95);
  crate6a.position.set(197.4, 0.475, 0.3);
  const crate6b = createCrate(gradientMap, 0.75);
  crate6b.position.set(197.5, 1.325, 0.3);
  const barrel6 = createBarrel(gradientMap);
  barrel6.position.set(205.4, 0.425, 0.4);
  const barrel6b = createBarrel(gradientMap);
  barrel6b.position.set(206.1, 0.425, 1.2);
  staticObjects.push(crate6a, barrel6, barrel6b);

  dynamicActors.push({
    mesh: crate6b,
    update: (t) => {
      const p = u(t, 5);
      crate6b.position.x = 197.5 + p * 2.6;
      crate6b.position.y = 1.325 + Math.abs(Math.sin(p * Math.PI * 3)) * 0.18;
      crate6b.rotation.z = -p * 0.4;
      barrel6b.position.x = 206.1 - p * 3.4;
      barrel6b.rotation.z = p * 1.15;
    },
  });

  const char6 = createCharacter({
    coatColor: '#5b4a3a',
    vestColor: '#c9a66b',
    hat: 'tophat',
    glasses: true,
  });
  char6.position.set(201.6, 0.16, 0.3);
  characters.push(char6);

  // LOCATION 7 (x = 240): the pivot — the land sinks instead of splitting
  const ground7 = toonBox(9.5, 1.0, 5.4, '#8d6b4a', gradientMap);
  ground7.position.set(240, 0.5, 1.6);
  const field7 = toonBox(6.6, 0.34, 3.6, '#8a7a45', gradientMap);
  field7.position.set(240, 1.17, 1.6);
  const sign7 = postedSign('THE LAND SINKS', gradientMap, 3.1, 0.74, 1.55);
  sign7.position.set(236.4, 0, -1.9);
  const facade7 = createFacade({ color: '#b06a51', gradientMap, width: 6.4, height: 4.4 });
  facade7.position.set(240, 0, -4.4);
  const fence7 = createFenceRow(gradientMap, 6);
  fence7.position.set(241.0, 1.34, 0.4);
  const barrel7 = createBarrel(gradientMap);
  barrel7.position.set(236.2, 1.425, 2.2);
  staticObjects.push(ground7, sign7, facade7, fence7, barrel7);

  dynamicActors.push({
    mesh: field7,
    update: (t) => {
      const p = THREE.MathUtils.smoothstep(u(t, 6), 0, 1);
      field7.position.y = 1.17 - p * 1.5;
      fence7.position.y = 1.34 - p * 1.5;
      barrel7.position.y = 1.425 - p * 1.5;
      ground7.rotation.z = Math.sin(t * 26) * 0.012 * p;
      sign7.rotation.z = Math.sin(t * 21) * 0.01 * p;
    },
  });

  const char7 = createCharacter({
    coatColor: '#4a5a68',
    vestColor: '#c29b61',
    hat: 'bowler',
    glasses: false,
  });
  char7.position.set(239.6, 1.0, 3.4);
  characters.push(char7);

  // LOCATION 8 (x = 280): Reelfoot Lake is born
  const sign8 = postedSign('REELFOOT LAKE', gradientMap, 3.1, 0.74, 1.5);
  sign8.position.set(277.6, 0, -1.6);
  const sign8b = createWorldSign('15,000 ACRES', 2.7, 0.68);
  sign8b.position.set(283.4, 2.94, -2.6);
  const post8a = toonBox(0.16, 2.6, 0.16, '#7d5a3c', gradientMap);
  post8a.position.set(283.4, 1.3, -2.68);
  const dock8 = createPlankSidewalk(7, 1.2, gradientMap);
  dock8.position.set(278.4, 0.42, 2.4);
  const facade8 = createFacade({ color: '#a8674c', gradientMap, width: 5.4, height: 3.8 });
  facade8.position.set(280, -0.6, -4.8);
  staticObjects.push(sign8, sign8b, post8a, dock8, facade8);

  const water8 = createWater({ width: 13, depth: 4.6, gradientMap, bars: 8 });
  water8.position.set(280, -0.3, 1.6);
  dynamicActors.push({
    mesh: water8,
    update: (t) => {
      rippleFlow(water8, 1, 0.75)(t);
      const p = THREE.MathUtils.smoothstep(u(t, 7), 0, 1);
      water8.position.y = -0.45 + p * 0.5;
    },
  });

  const tree8a = createCypress(gradientMap, 1.05);
  tree8a.position.set(284.6, -0.1, 0.6);
  const tree8b = createCypress(gradientMap, 0.85);
  tree8b.position.set(275.4, -0.2, 1.4);
  staticObjects.push(tree8a, tree8b);

  const char8 = createCharacter({
    coatColor: '#3f5248',
    vestColor: '#d4b475',
    hat: 'cap',
    glasses: false,
  });
  char8.position.set(281.0, 0.54, 2.4);
  characters.push(char8);

  // LOCATION 9 (x = 320): the depth gauge — five to eighteen feet
  const sign9 = postedSign('DEPTH 5-18 FT', gradientMap, 3.1, 0.74, 1.55);
  sign9.position.set(317.4, 0, -1.7);
  const deck9 = createElevatedDeck({
    length: 9.5,
    width: 2.4,
    height: 1.2,
    surfaceColor: '#a66249',
    gradientMap,
  });
  deck9.position.set(320, 0, -1.4);
  const facade9 = createFacade({ color: '#b3714f', gradientMap, width: 6.2, height: 4.2 });
  facade9.position.set(320, 0, -4.6);
  const barrel9 = createBarrel(gradientMap);
  barrel9.position.set(324.6, 0.425, 1.0);
  staticObjects.push(sign9, deck9, facade9, barrel9);

  const gauge9 = new THREE.Group();
  for (let i = 0; i < 6; i++) {
    const tick = toonBox(0.9, 0.1, 0.16, i % 2 === 0 ? '#351f22' : '#f3e8d2', gradientMap);
    tick.position.set(0, i * 0.42, 0);
    gauge9.add(tick);
  }
  const pole9 = toonBox(0.16, 2.6, 0.16, '#7d5a3c', gradientMap);
  pole9.position.y = 1.1;
  gauge9.add(pole9);
  gauge9.position.set(317.9, 0, 1.9);
  staticObjects.push(gauge9);

  const water9 = createWater({ width: 12, depth: 4.4, gradientMap, bars: 7 });
  water9.position.set(320, 0, 2.4);
  dynamicActors.push({
    mesh: water9,
    update: (t) => {
      rippleFlow(water9, 1, 0.9)(t);
      water9.position.y = 0.02 + Math.sin(t * 1.4) * 0.06;
      gauge9.rotation.z = Math.sin(t * 1.4) * 0.03;
    },
  });

  const char9 = createCharacter({
    coatColor: '#54485c',
    vestColor: '#cbb075',
    hat: 'engineer',
    glasses: true,
  });
  char9.position.set(321.4, 1.27, -1.4);
  characters.push(char9);

  // LOCATION 10 (x = 360): the lake, two centuries on
  const sign10 = postedSign('200 YEARS LATER', gradientMap, 3.2, 0.74, 1.55);
  sign10.position.set(357.4, 0, -1.6);
  const walk10 = createPlankSidewalk(8, 1.3, gradientMap);
  walk10.position.set(360, 0.35, 1.9);
  const lamp10 = createLampPost(gradientMap, 3.0);
  lamp10.position.set(363.4, 0, -0.4);
  const facade10 = createFacade({ color: '#b86b52', gradientMap, width: 5.6, height: 4.0 });
  facade10.position.set(360, 0, -4.8);
  staticObjects.push(sign10, walk10, lamp10, facade10);

  const water10 = createWater({ width: 13, depth: 4.2, gradientMap, bars: 8 });
  water10.position.set(360, 0, 3.0);
  dynamicActors.push({
    mesh: water10,
    update: (t) => rippleFlow(water10, 1, 0.5)(t),
  });

  const tree10a = createCypress(gradientMap, 1.15);
  tree10a.position.set(356.2, 0, 0.6);
  const tree10b = createCypress(gradientMap, 0.9);
  tree10b.position.set(365.0, 0, 1.2);
  const tree10c = createCypress(gradientMap, 0.7);
  tree10c.position.set(362.0, -0.2, 3.4);
  staticObjects.push(tree10b, tree10c);

  dynamicActors.push({
    mesh: tree10a,
    update: (t) => {
      tree10a.rotation.z = Math.sin(t * 0.8) * 0.035;
      tree10b.rotation.z = Math.sin(t * 0.7 + 1.2) * 0.03;
    },
  });

  const char10 = createCharacter({
    coatColor: '#4a5a68',
    vestColor: '#c9a66b',
    hat: 'none',
    glasses: false,
  });
  char10.position.set(361.6, 0.47, 1.9);
  characters.push(char10);

  // One camera move per cut / sentence (10 shots, 10 locations at x = 0, 40 ... 360)
  const shots = [
    { camStart: [-1.4, 1.95, 5.2], camEnd: [1.0, 2.25, 4.0], lookAt: [0.2, 1.8, -2.0] },
    { camStart: [38.6, 1.7, 4.8], camEnd: [41.0, 2.1, 3.6], lookAt: [40.2, 1.5, -1.6] },
    { camStart: [78.4, 2.1, 5.0], camEnd: [81.4, 2.4, 3.9], lookAt: [80.4, 2.0, -2.4] },
    { camStart: [118.6, 2.0, 5.4], camEnd: [121.0, 2.4, 4.2], lookAt: [120.4, 2.3, -3.0] },
    { camStart: [158.6, 1.9, 5.4], camEnd: [161.0, 2.3, 4.2], lookAt: [160.2, 1.7, -1.8] },
    { camStart: [198.6, 1.85, 4.9], camEnd: [201.6, 2.2, 3.7], lookAt: [200.4, 1.7, -2.4] },
    { camStart: [237.8, 3.1, 7.6], camEnd: [240.4, 2.4, 6.3], lookAt: [240.3, 1.1, 1.0] },
    { camStart: [278.6, 2.2, 6.0], camEnd: [281.2, 2.5, 5.4], lookAt: [280.4, 1.5, -1.6] },
    { camStart: [318.6, 2.3, 4.6], camEnd: [321.8, 2.15, 2.8], lookAt: [320.6, 1.5, -2.0] },
    { camStart: [358.6, 2.1, 5.6], camEnd: [361.6, 2.45, 4.4], lookAt: [360.4, 1.7, -1.8] },
  ];

  return { staticObjects, dynamicActors, characters, shots };
}
