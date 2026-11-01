// 3D modeli plinskih ražnjeva za odojka. Sve mjere u mm; Y gore, X uzduž ražnja, Z dubina (straga = -Z).
import * as THREE from 'three';
const V = (x, y, z) => new THREE.Vector3(x, y, z);

export function materials() {
  const std = (c, o = {}) => new THREE.MeshStandardMaterial({ color: c, metalness: .55, roughness: .5, ...o });
  return {
    steel: std(0x45484c),
    frame: std(0x2a2b2d, { metalness: .4, roughness: .6 }),
    inox: std(0xc8ccd1, { metalness: .85, roughness: .28 }),
    wall: std(0x55585c, { side: THREE.DoubleSide, transparent: true, opacity: 1 }),
    pig: std(0xd09468, { metalness: 0, roughness: .75 }),
    flame: new THREE.MeshStandardMaterial({ color: 0xff7a1a, emissive: 0xff5a00, emissiveIntensity: 1.2, transparent: true, opacity: .85 }),
    ceramic: new THREE.MeshStandardMaterial({ color: 0xff6a1a, emissive: 0xff4800, emissiveIntensity: 1.1, roughness: .9 }),
    ceramicGrid: new THREE.MeshBasicMaterial({ color: 0x7a1e00, wireframe: true, transparent: true, opacity: .55 }),
    copper: std(0xb8733a, { metalness: .8, roughness: .35 }),
    bottle: std(0xb8322a, { metalness: .3, roughness: .45 }),
    black: std(0x111111, { metalness: .2, roughness: .6 }),
  };
}

function box(w, h, d, mat, x = 0, y = 0, z = 0) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat);
  m.position.set(x, y, z); return m;
}
function bar(a, b, s, mat) {
  const d = new THREE.Vector3().subVectors(b, a); const len = d.length();
  const m = new THREE.Mesh(new THREE.BoxGeometry(s, len, s), mat);
  m.position.copy(a).add(b).multiplyScalar(.5);
  m.quaternion.setFromUnitVectors(V(0, 1, 0), d.normalize()); return m;
}
function cylX(r, len, mat, x, y, z, seg = 24) {
  const g = new THREE.CylinderGeometry(r, r, len, seg); g.rotateZ(Math.PI / 2);
  const m = new THREE.Mesh(g, mat); m.position.set(x, y, z); return m;
}
function cylY(r, h, mat, x, y, z, seg = 24) {
  const m = new THREE.Mesh(new THREE.CylinderGeometry(r, r, h, seg), mat); m.position.set(x, y, z); return m;
}

export function pig(M) {
  const g = new THREE.Group(); g.userData.pig = true;
  const body = new THREE.Mesh(new THREE.SphereGeometry(1, 40, 24), M.pig); body.scale.set(400, 135, 150); g.add(body);
  const head = new THREE.Mesh(new THREE.SphereGeometry(1, 32, 20), M.pig); head.scale.set(120, 95, 100); head.position.set(420, 10, 0); g.add(head);
  g.add(cylX(45, 70, M.pig, 545, 0, 0));
  const ear = (z) => { const e = new THREE.Mesh(new THREE.ConeGeometry(35, 70, 12), M.pig); e.position.set(400, 95, z); e.rotation.z = -0.5; return e; };
  g.add(ear(55), ear(-55));
  for (const z of [-70, 70]) {
    g.add(bar(V(250, -60, z), V(560, -90, z * 0.6), 45, M.pig));   // prednje noge naprijed
    g.add(bar(V(-250, -60, z), V(-580, -90, z * 0.6), 50, M.pig)); // stražnje noge natrag
  }
  return g;
}

function spit(M, y, z, motorSide = 1) {
  const g = new THREE.Group();
  g.add(box(1500, 16, 16, M.inox, 0, y, z));
  g.add(cylX(14, 90, M.black, -760, y, z));                     // ručka
  for (const s of [-1, 1]) {                                     // vilice
    const x = s * 470;
    g.add(box(10, 60, 60, M.inox, x, y, z));
    for (const dz of [-20, 20]) g.add(cylX(4, 200, M.inox, x - s * 100, y, z + dz, 10));
  }
  const mot = box(120, 100, 85, M.black, motorSide * 790, y, z); g.add(mot);
  g.add(box(14, 160, 14, M.black, motorSide * 790, y - 110, z));  // krak protiv okretanja
  return g;
}

// keramički infracrveni plamenik (tip gyros): kućište + užarena keramička ploča, okrenut prema +Z
function irBurner(M, x, y, zBack) {
  const g = new THREE.Group();
  g.add(box(200, 150, 50, M.inox, x, y, zBack + 25));                     // kućište
  const face = box(170, 125, 4, M.ceramic, x, y, zBack + 52); g.add(face); // užarena keramika
  const grid = new THREE.Mesh(new THREE.PlaneGeometry(170, 125, 17, 12), M.ceramicGrid);
  grid.position.set(x, y, zBack + 54.5); g.add(grid);
  g.add(cylX(10, 60, M.inox, x - 130, y - 40, zBack + 25));               // venturi / dovod
  const tc = new THREE.Mesh(new THREE.CylinderGeometry(3, 3, 60, 8), M.inox); // termoelement
  tc.rotation.x = Math.PI / 2; tc.position.set(x + 92, y - 45, zBack + 40); g.add(tc);
  return g;
}
function bottle(M, x, z) {
  const g = new THREE.Group();
  g.add(cylY(150, 520, M.bottle, x, 300, z, 32));
  const top = new THREE.Mesh(new THREE.SphereGeometry(150, 32, 12, 0, Math.PI * 2, 0, Math.PI / 2), M.bottle); top.position.set(x, 560, z); g.add(top);
  const bot = new THREE.Mesh(new THREE.SphereGeometry(150, 32, 12, 0, Math.PI * 2, Math.PI / 2, Math.PI / 2), M.bottle); bot.position.set(x, 40, z); g.add(bot);
  g.add(cylY(150, 40, M.bottle, x, 20, z, 32));
  g.add(cylY(25, 60, M.inox, x, 735, z)); g.add(cylY(40, 35, M.black, x, 770, z));
  return g;
}
function knobs(M, x0, y, z, n = 4) {
  const g = new THREE.Group();
  for (let i = 0; i < n; i++) { const k = new THREE.Mesh(new THREE.CylinderGeometry(22, 22, 25, 20), M.black); k.rotation.x = Math.PI / 2; k.position.set(x0 + i * 60, y, z); g.add(k); }
  const p = new THREE.Mesh(new THREE.CylinderGeometry(9, 9, 18, 12), M.flame); p.rotation.x = Math.PI / 2; p.position.set(x0 + n * 60 + 10, y, z); g.add(p);
  return g;
}

/* ---------- B: kutija sa stražnjim zidom plamenika (preporuka) ---------- */
function sidePanel(M, x) {
  // ploča 500 × 700 u ravnini ZY, s vodoravnim utorom za ražanj kao u DXF-u (z 10..160, širina 30, zaobljeni krajevi)
  const s = new THREE.Shape();
  s.moveTo(-250, 600); s.lineTo(250, 600); s.lineTo(250, 1300); s.lineTo(-250, 1300); s.closePath();
  const h = new THREE.Path();
  h.moveTo(25, 935); h.lineTo(145, 935); h.absarc(145, 950, 15, -Math.PI / 2, Math.PI / 2, false);
  h.lineTo(25, 965); h.absarc(25, 950, 15, Math.PI / 2, 3 * Math.PI / 2, false);
  s.holes.push(h);
  const geo = new THREE.ExtrudeGeometry(s, { depth: 2, bevelEnabled: false });
  geo.rotateY(-Math.PI / 2);         // shape x → z
  const m = new THREE.Mesh(geo, M.wall); m.position.x = x; m.userData.wall = true; return m;
}
function spitBracket(M, x) {
  // vanjski nosač 3 mm s 3 U-utora (z = 35 / 85 / 135)
  const s = new THREE.Shape();
  s.moveTo(-20, 880);
  const pts = [35, 85, 135]; s.lineTo(-20, 960);
  for (const z of pts) { s.lineTo(z - 10, 960); s.lineTo(z - 10, 942); s.lineTo(z + 10, 942); s.lineTo(z + 10, 960); }
  s.lineTo(190, 960); s.lineTo(190, 880); s.closePath();
  const geo = new THREE.ExtrudeGeometry(s, { depth: 3, bevelEnabled: false }); geo.rotateY(-Math.PI / 2);
  const m = new THREE.Mesh(geo, M.steel); m.position.x = x; return m;
}
export function roaster(M) {
  const g = new THREE.Group(); const T = 30, SZ = 85, SY = 950;
  for (const x of [-535, 535]) for (const z of [-235, 235]) g.add(box(T, 1300, T, M.frame, x, 650, z));
  for (const y of [600, 1300]) {
    for (const z of [-235, 235]) g.add(box(1100, T, T, M.frame, 0, y, z));
    for (const x of [-535, 535]) g.add(box(T, T, 500, M.frame, x, y, 0));
  }
  g.add(box(1100, T, T, M.frame, 0, 150, -235)); g.add(box(1100, T, T, M.frame, 0, 150, 235));
  g.add(box(1040, 6, 440, M.steel, 0, 168, 0));                  // polica
  const back = box(1100, 700, 2, M.wall, 0, 950, -251); back.userData.wall = true; g.add(back);
  // unutarnji zid s 4 izreza 175 × 130 za plamenike (osi na x = -375, -125, 125, 375)
  const BX = [-375, -125, 125, 375];
  const sh = new THREE.Shape(); sh.moveTo(-530, 620); sh.lineTo(530, 620); sh.lineTo(530, 1280); sh.lineTo(-530, 1280); sh.closePath();
  for (const x of BX) { const h = new THREE.Path(); h.moveTo(x - 88, SY - 65); h.lineTo(x + 88, SY - 65); h.lineTo(x + 88, SY + 65); h.lineTo(x - 88, SY + 65); h.closePath(); sh.holes.push(h); }
  const inner = new THREE.Mesh(new THREE.ExtrudeGeometry(sh, { depth: 2, bevelEnabled: false }), M.wall);
  inner.position.z = -224; inner.userData.wall = true; g.add(inner);
  g.add(sidePanel(M, -552)); g.add(sidePanel(M, 554));
  g.add(spitBracket(M, -556)); g.add(spitBracket(M, 561));
  const roof = new THREE.Group(); roof.userData.wall = true;
  const r1 = box(1160, 2, 570, M.wall, 0, 1318, 15); r1.userData.wall = true;
  const r2 = box(1160, 100, 2, M.wall, 0, 1268, 300); r2.userData.wall = true;
  g.add(r1, r2);
  for (const x of BX) g.add(irBurner(M, x, SY, -250));
  // bakrene cijevi Ø8: od ventila ispod kutije, straga izvan stražnjeg zida, do svakog plamenika
  for (let i = 0; i < 4; i++) {
    const kx = -420 + i * 60, bx = BX[i] - 130, zz = -268 - i * 12, yy = 580 - i * 12;
    const pts = [V(kx, 545, 235), V(kx, yy, 235), V(kx, yy, zz), V(bx, yy, zz), V(bx, SY - 40, zz), V(bx, SY - 40, -235)];
    for (let j = 0; j < pts.length - 1; j++) g.add(bar(pts[j], pts[j + 1], 8, M.copper));
  }
  g.add(box(380, 12, 12, M.inox, -330, 545, 225));                // razdjelnik iza letve
  g.add(box(1050, 40, 450, M.inox, 0, 640, 10));                 // tava
  g.add(box(400, 120, 3, M.steel, -330, 545, 252)); g.add(knobs(M, -420, 545, 262, 4));
  g.add(spit(M, SY, SZ));
  const p = pig(M); p.position.set(0, SY, SZ); g.add(p);
  g.add(bottle(M, -880, 0));
  return g;
}

