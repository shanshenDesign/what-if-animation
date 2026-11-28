import * as THREE from 'three';

function drawCharacterCanvas({
  coatColor = '#4a5a68',
  vestColor = '#c9a66b',
  hat = 'tophat',
  glasses = false,
}) {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 1024;
  const ctx = canvas.getContext('2d');
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';

  const ink = (width = 11) => {
    ctx.strokeStyle = '#351f22';
    ctx.lineWidth = width;
    ctx.stroke();
  };

  ctx.fillStyle = '#351f22';
  ctx.beginPath();
  ctx.moveTo(222, 680); ctx.lineTo(234, 680); ctx.lineTo(228, 935); ctx.lineTo(220, 935); ctx.closePath();
  ctx.moveTo(278, 680); ctx.lineTo(290, 680); ctx.lineTo(292, 935); ctx.lineTo(284, 935); ctx.closePath();
  ctx.fill();

  ctx.fillStyle = coatColor;
  ctx.beginPath();
  ctx.moveTo(215, 455);
  ctx.bezierCurveTo(185, 550, 175, 675, 256, 685);
  ctx.bezierCurveTo(337, 675, 327, 550, 297, 455);
  ctx.closePath();
  ctx.fill();
  ink(12);

  ctx.fillStyle = vestColor;
  ctx.fillRect(218, 520, 76, 95);
  ink(8);
  ctx.strokeRect(264, 545, 22, 26);

  ctx.fillStyle = '#faf6ee';
  ctx.beginPath();
  ctx.moveTo(226, 452); ctx.lineTo(256, 482); ctx.lineTo(286, 452); ctx.closePath();
  ctx.fill();
  ink(8);

  ctx.fillStyle = '#8b3a3a';
  ctx.beginPath();
  ctx.moveTo(250, 468); ctx.lineTo(262, 468); ctx.lineTo(266, 535); ctx.lineTo(256, 548); ctx.lineTo(246, 535); ctx.closePath();
  ctx.fill();
  ink(7);

  ctx.strokeStyle = '#351f22';
  ctx.lineWidth = 10;
  ctx.beginPath(); ctx.moveTo(205, 475); ctx.lineTo(165, 615); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(307, 475); ctx.lineTo(347, 615); ctx.stroke();

  ctx.fillStyle = '#351f22';
  ctx.beginPath(); ctx.arc(163, 622, 16, 0, Math.PI * 2); ctx.fill();
  ctx.beginPath(); ctx.arc(349, 622, 16, 0, Math.PI * 2); ctx.fill();

  ctx.fillStyle = '#f5e4d3';
  ctx.beginPath();
  ctx.arc(256, 305, 148, 0, Math.PI * 2);
  ctx.fill();
  ink(13);

  ctx.fillStyle = '#5a4337';
  ctx.beginPath();
  ctx.arc(256, 285, 146, Math.PI * 1.08, Math.PI * 1.92);
  ctx.quadraticCurveTo(256, 225, 118, 265);
  ctx.fill();
  ink(10);

  for (const ex of [212, 300]) {
    ctx.fillStyle = '#ffffff';
    ctx.beginPath(); ctx.arc(ex, 312, 22, 0, Math.PI * 2); ctx.fill();
    ink(7);
    ctx.fillStyle = '#351f22';
    ctx.beginPath(); ctx.arc(ex, 316, 8, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = '#f5e4d3';
    ctx.fillRect(ex - 23, 288, 46, 22);
    ctx.beginPath(); ctx.moveTo(ex - 22, 310); ctx.lineTo(ex + 22, 310); ink(7);
  }

  if (glasses) {
    ctx.beginPath(); ctx.arc(212, 312, 28, 0, Math.PI * 2); ink(6);
    ctx.beginPath(); ctx.arc(300, 312, 28, 0, Math.PI * 2); ink(6);
    ctx.beginPath(); ctx.moveTo(240, 312); ctx.lineTo(272, 312); ink(6);
  }

  ctx.beginPath();
  ctx.arc(256, 368, 22, 0.15 * Math.PI, 0.85 * Math.PI);
  ink(8);

  if (hat === 'tophat') {
    ctx.fillStyle = '#3a3235';
    ctx.fillRect(175, 65, 162, 105); ink(11);
    ctx.fillRect(130, 162, 252, 24); ink(11);
  } else if (hat === 'bowler') {
    ctx.fillStyle = '#4a3c35';
    ctx.beginPath(); ctx.arc(256, 175, 95, Math.PI, 0); ctx.fill(); ink(11);
    ctx.fillRect(140, 168, 232, 22); ink(11);
  } else if (hat === 'cap') {
    ctx.fillStyle = '#5c4d42';
    ctx.beginPath(); ctx.arc(256, 178, 118, Math.PI, 0); ctx.fill(); ink(11);
    ctx.fillRect(195, 168, 185, 20); ink(11);
  } else if (hat === 'engineer') {
    ctx.fillStyle = '#6e5239';
    ctx.beginPath(); ctx.arc(256, 180, 115, Math.PI, 0); ctx.fill(); ink(11);
    ctx.fillRect(120, 170, 272, 22); ink(11);
  }

  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

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

  group.userData.update = (frame, cameraPos) => {
    plane.position.y = 1.15 + Math.sin(frame * 0.12) * 0.025;
    plane.rotation.z = Math.sin(frame * 0.08) * 0.02;

    const dx = cameraPos.x - group.position.x;
    const dz = cameraPos.z - group.position.z;
    const rawYaw = Math.atan2(dx, dz);
    group.rotation.y = THREE.MathUtils.clamp(rawYaw, -0.7, 0.7);
  };

  return group;
}
