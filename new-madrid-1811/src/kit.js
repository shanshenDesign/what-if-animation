import * as THREE from 'three';

export const INK_COLOR = 0x351f22;
export const INK_HEX = '#351f22';

export function createToonGradient() {
  const colors = new Uint8Array([92, 174, 255]);
  const tex = new THREE.DataTexture(colors, 3, 1, THREE.RedFormat);
  tex.minFilter = THREE.NearestFilter;
  tex.magFilter = THREE.NearestFilter;
  tex.needsUpdate = true;
  return tex;
}

export function createPaintedTexture(baseHex, wearAlpha = 0.14) {
  const canvas = document.createElement('canvas');
  canvas.width = 256;
  canvas.height = 256;
  const ctx = canvas.getContext('2d');

  ctx.fillStyle = baseHex;
  ctx.fillRect(0, 0, 256, 256);

  for (let i = 0; i < 56; i++) {
    ctx.fillStyle =
      i % 2 === 0
        ? `rgba(53,31,34,${wearAlpha})`
        : `rgba(255,248,235,${wearAlpha})`;
    ctx.fillRect(
      (i * 53) % 244,
      (i * 97) % 244,
      3 + (i % 15),
      1 + (i % 4)
    );
  }

  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

export function addInkOutline(mesh, thickness = 0.03) {
  const hullMat = new THREE.MeshBasicMaterial({
    color: INK_COLOR,
    side: THREE.BackSide,
  });
  const hull = new THREE.Mesh(mesh.geometry, hullMat);
  hull.scale.setScalar(1 + thickness);
  mesh.add(hull);

  const edges = new THREE.EdgesGeometry(mesh.geometry, 28);
  const line = new THREE.LineSegments(
    edges,
    new THREE.LineBasicMaterial({ color: INK_COLOR })
  );
  mesh.add(line);
  return mesh;
}

export function createFacade({
  width = 8,
  height = 6.5,
  depth = 0.48,
  color = '#b86b52',
  gradientMap,
}) {
  const group = new THREE.Group();
  const shape = new THREE.Shape();
  const halfW = width / 2;
  const doorW = 1.15;
  const doorH = 2.25;

  shape.moveTo(-halfW, 0);
  shape.lineTo(-doorW / 2, 0);
  shape.lineTo(-doorW / 2, doorH);
  shape.lineTo(doorW / 2, doorH);
  shape.lineTo(doorW / 2, 0);
  shape.lineTo(halfW, 0);
  shape.lineTo(halfW, height);
  shape.lineTo(-halfW, height);
  shape.closePath();

  const winPositions = [
    [-2.4, 3.6],
    [0, 3.6],
    [2.4, 3.6],
    [-2.4, 1.1],
    [2.4, 1.1],
  ];
  for (const [wx, wy] of winPositions) {
    const hole = new THREE.Path();
    hole.moveTo(wx - 0.55, wy);
    hole.lineTo(wx + 0.55, wy);
    hole.lineTo(wx + 0.55, wy + 1.35);
    hole.lineTo(wx - 0.55, wy + 1.35);
    hole.closePath();
    shape.holes.push(hole);
  }

  const geo = new THREE.ExtrudeGeometry(shape, { depth, bevelEnabled: false });
  const mat = new THREE.MeshToonMaterial({
    map: createPaintedTexture(color),
    gradientMap,
  });

  const wall = new THREE.Mesh(geo, mat);
  wall.castShadow = true;
  wall.receiveShadow = true;
  addInkOutline(wall, 0.014);
  group.add(wall);

  const backing = new THREE.Mesh(
    new THREE.BoxGeometry(width - 0.2, height - 0.2, 0.08),
    new THREE.MeshBasicMaterial({ color: 0x3f2d2b })
  );
  backing.position.set(0, height / 2, -0.04);
  group.add(backing);

  const corniceMat = new THREE.MeshToonMaterial({
    map: createPaintedTexture('#8b6248'),
    gradientMap,
  });
  const cornice = new THREE.Mesh(
    new THREE.BoxGeometry(width + 0.4, 0.32, depth + 0.35),
    corniceMat
  );
  cornice.position.set(0, height + 0.14, depth / 2);
  addInkOutline(cornice, 0.025);
  group.add(cornice);

  return group;
}

export function createCribJack(gradientMap, tiers = 5) {
  const group = new THREE.Group();
  const woodMat = new THREE.MeshToonMaterial({
    map: createPaintedTexture('#9c7349'),
    gradientMap,
  });

  for (let tier = 0; tier < tiers; tier++) {
    const isEven = tier % 2 === 0;
    for (const offset of [-0.36, 0.36]) {
      const beam = new THREE.Mesh(
        new THREE.BoxGeometry(isEven ? 1.15 : 0.22, 0.18, isEven ? 0.22 : 1.15),
        woodMat
      );
      beam.position.set(
        isEven ? 0 : offset,
        0.09 + tier * 0.18,
        isEven ? offset : 0
      );
      beam.castShadow = true;
      addInkOutline(beam, 0.035);
      group.add(beam);
    }
  }

  const ironMat = new THREE.MeshToonMaterial({
    map: createPaintedTexture('#4a4a4e'),
    gradientMap,
  });
  const screw = new THREE.Mesh(
    new THREE.CylinderGeometry(0.09, 0.09, 0.68, 10),
    ironMat
  );
  screw.position.y = tiers * 0.18 + 0.34;
  addInkOutline(screw, 0.05);
  group.add(screw);

  return group;
}

export function createElevatedDeck({
  length = 10,
  width = 2.6,
  height = 1.2,
  surfaceColor = '#a66249',
  gradientMap,
}) {
  const group = new THREE.Group();
  const deckMat = new THREE.MeshToonMaterial({
    map: createPaintedTexture(surfaceColor),
    gradientMap,
  });
  const deck = new THREE.Mesh(
    new THREE.BoxGeometry(length, 0.24, width),
    deckMat
  );
  deck.position.y = height;
  deck.castShadow = true;
  deck.receiveShadow = true;
  addInkOutline(deck, 0.02);
  group.add(deck);

  const postMat = new THREE.MeshToonMaterial({
    map: createPaintedTexture('#7d5a3c'),
    gradientMap,
  });
  const bays = Math.max(2, Math.floor(length / 2.2));
  for (let i = 0; i <= bays; i++) {
    const px = -length / 2 + 0.3 + (i * (length - 0.6)) / bays;
    for (const pz of [-width / 2 + 0.22, width / 2 - 0.22]) {
      const post = new THREE.Mesh(
        new THREE.BoxGeometry(0.18, height, 0.18),
        postMat
      );
      post.position.set(px, height / 2, pz);
      post.castShadow = true;
      addInkOutline(post, 0.04);
      group.add(post);
    }
  }
  return group;
}

export function createStoneArch({
  width = 5.4,
  height = 4.2,
  depth = 1.6,
  color = '#8d8173',
  gradientMap,
}) {
  const shape = new THREE.Shape();
  const hw = width / 2;
  const archR = width * 0.31;

  shape.moveTo(-hw, 0);
  shape.lineTo(-archR, 0);
  shape.absarc(0, height * 0.35, archR, Math.PI, 0, true);
  shape.lineTo(archR, 0);
  shape.lineTo(hw, 0);
  shape.lineTo(hw, height);
  shape.lineTo(-hw, height);
  shape.closePath();

  const geo = new THREE.ExtrudeGeometry(shape, { depth, bevelEnabled: false });
  const mat = new THREE.MeshToonMaterial({
    map: createPaintedTexture(color),
    gradientMap,
  });
  const mesh = new THREE.Mesh(geo, mat);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  return addInkOutline(mesh, 0.018);
}

export function createLampPost(gradientMap, height = 3.4) {
  const group = new THREE.Group();
  const ironMat = new THREE.MeshToonMaterial({
    map: createPaintedTexture('#3d383a'),
    gradientMap,
  });
  const pole = new THREE.Mesh(
    new THREE.CylinderGeometry(0.06, 0.11, height, 10),
    ironMat
  );
  pole.position.y = height / 2;
  pole.castShadow = true;
  addInkOutline(pole, 0.05);
  group.add(pole);

  const lantern = new THREE.Mesh(
    new THREE.BoxGeometry(0.32, 0.42, 0.32),
    new THREE.MeshBasicMaterial({ color: 0xffe6a3 })
  );
  lantern.position.y = height + 0.18;
  addInkOutline(lantern, 0.04);
  group.add(lantern);

  return group;
}

export function createCrate(gradientMap, size = 0.85) {
  const mat = new THREE.MeshToonMaterial({
    map: createPaintedTexture('#b08554'),
    gradientMap,
  });
  const crate = new THREE.Mesh(
    new THREE.BoxGeometry(size, size, size),
    mat
  );
  crate.position.y = size / 2;
  crate.castShadow = true;
  crate.receiveShadow = true;
  return addInkOutline(crate, 0.035);
}

export function createPlankSidewalk(length = 10, width = 1.6, gradientMap) {
  const group = new THREE.Group();
  const plankMat = new THREE.MeshToonMaterial({
    map: createPaintedTexture('#a88259'),
    gradientMap,
  });
  const count = Math.floor(length / 0.35);
  for (let i = 0; i < count; i++) {
    const plank = new THREE.Mesh(
      new THREE.BoxGeometry(0.31, 0.08, width),
      plankMat
    );
    plank.position.set(-length / 2 + i * 0.35 + 0.17, 0.08, 0);
    plank.receiveShadow = true;
    addInkOutline(plank, 0.03);
    group.add(plank);
  }
  return group;
}

export function createBarrel(gradientMap) {
  const mat = new THREE.MeshToonMaterial({
    map: createPaintedTexture('#8a623c'),
    gradientMap,
  });
  const barrel = new THREE.Mesh(
    new THREE.CylinderGeometry(0.34, 0.3, 0.85, 14),
    mat
  );
  barrel.position.y = 0.425;
  barrel.castShadow = true;
  return addInkOutline(barrel, 0.04);
}

export function createWorldSign(text, width = 2.6, height = 0.72) {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 144;
  const ctx = canvas.getContext('2d');

  ctx.fillStyle = '#f3e8d2';
  ctx.fillRect(0, 0, 512, 144);
  ctx.strokeStyle = INK_HEX;
  ctx.lineWidth = 10;
  ctx.strokeRect(5, 5, 502, 134);

  ctx.fillStyle = INK_HEX;
  ctx.font = 'bold 50px Georgia, serif';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(text, 256, 74);

  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  const sign = new THREE.Mesh(
    new THREE.BoxGeometry(width, height, 0.08),
    new THREE.MeshBasicMaterial({ map: tex })
  );
  return addInkOutline(sign, 0.03);
}
