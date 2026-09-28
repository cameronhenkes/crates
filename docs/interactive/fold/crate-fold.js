/**
 * The crate fold, as a plain module. No framework, one dependency (three).
 *
 *   const fold = createCrateFold({ THREE, mount, textures, size, onState });
 *   fold.toggle();   fold.dispose();
 *
 * textures: { "front.png": url, "back.png": url, "side.png": url, "floor.png": url }
 * onState:  called with "closed" | "folding" | "folded" | "unfolding"
 *
 * Generated from docs/explorations/fold-three.html by
 * styles/crate/build-component.py. Edit the exploration, then rebuild.
 */
export function createCrateFold({ THREE, mount, textures, size = 460, onState = () => {}, onReady = () => {} }) {
const W = 900, H = 684, D = 950;   // the front face is the icon, tab and all
// The icon is a FOLDER: its tab rises 96 above the body. The crate box is the
// body only, so the other three walls are shorter and the tab overhangs them,
// exactly as a folder tab overhangs. Sizing every wall to the full height was
// what pushed the sides proud of the front at the corners.
const BODY_TOP = 96, HB = H - BODY_TOP;
// sides stop below the front's top-corner curve so they are not
// left exposed as a nub where the silhouette rounds in
// sides top out below where the front's top-right corner starts to curve,
// measured from the highest side hinge, so neither shows past that corner
const SIDE_H = 468;
const TH = 13;   // wall thickness, ~1.4% of the crate width
// ONE footprint, W wide, and the icon is its front elevation. Read that way:
//   - the icon's bottom band (80 high, the rail with the feet) is the BASE.
//     It never moves. The end wall hinges behind it and folds away from it.
//   - the outer wall-thickness of the icon at each side is a SIDE WALL seen
//     end-on. The end walls are narrower than the icon by that much and fold
//     between the sides, as on the real crate.
// Earlier the sides sat outboard of a full-width front, which made the base
// wider than the icon; the base then had to be hidden at rest and faded in,
// and its rim rose in front of the front's lower edge. Nothing fades now.
// Every part is opaque and present from the first frame to the last.
const RIM = 80;          // height of the base: the icon's bottom band
const FASCIA = 6;        // thickness of the base's front and back faces
const FLOOR_Y = 26;      // floor height: clear of the rounded lower edges
const INSET = TH + 0.8;  // an end wall stops this far short of the icon's edge
const PANEL_W = W - INSET * 2;
const R = 62;
const SIDE_W = D - TH;                 // flush with the end walls' outer faces
const SIDE_X = W/2 - 0.5 - TH/2;       // outer face just inside the silhouette
const END_Z = D/2 - FASCIA - 0.5 - TH/2;   // end wall centre, behind the fascia
const HINGE = {front: FLOOR_Y + TH*0.5, back: FLOOR_Y + TH*1.5,
               left:  FLOOR_Y + TH*2.5, right: FLOOR_Y + TH*3.5};
// the end walls are full width only ABOVE the side walls' tops
const EAR_L = HINGE.left + SIDE_H + 0.5, EAR_R = HINGE.right + SIDE_H + 0.5;
const SIZE = size;

const scene = new THREE.Scene();
const renderer = new THREE.WebGLRenderer({antialias:true, alpha:true});
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(SIZE, SIZE);
mount.appendChild(renderer.domElement);
renderer.domElement.style.cssText = "display:block;width:100%;height:auto";

// Low FOV from far away reads as near-orthographic, so the resting frame is
// the icon rather than a photograph of it.
const camera = new THREE.PerspectiveCamera(17, 1, 10, 12000);
scene.add(new THREE.AmbientLight(0xffffff, 1.05));
const key = new THREE.DirectionalLight(0xffffff, 0.45);
key.position.set(-500, 900, 1200); scene.add(key);

// Textures load async. Rendering once at startup paints an empty canvas,
// so the manager re-renders the moment they are all in.
const TEX = textures;
const manager = new THREE.LoadingManager();
const loader = new THREE.TextureLoader(manager);
// Interior faces sit inside a crate, so they are in shade. Without this the
// back wall is as bright as the front, you see two identical grids stacked,
// and it reads as confusion rather than depth.
function mat(url, shade, flipX){
  const t = loader.load(url);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 8;
  // A box's -z face carries mirrored UVs, so rotating the mesh to correct a
  // mirrored back just cancels out. Flipping the texture itself is the only
  // thing that actually moves the folder tab back to the correct side.
  if (flipX) { t.wrapS = THREE.RepeatWrapping; t.repeat.x = -1; t.offset.x = 1; }
  // alphaTest rather than blending: the fragment shader discards transparent
  // pixels, so the depth buffer stays authoritative and the perforations are
  // genuinely see-through at every angle. This is the thing CSS could not do.
  return new THREE.MeshLambertMaterial({
    map:t, transparent:false, alphaTest:0.5, alphaToCoverage:true, side:THREE.DoubleSide,
    color: shade ? 0xcfcfcf : 0xffffff,
    // Folded walls end up almost coplanar with the floor and each other.
    // Without a depth bias the fragments tie and flicker frame to frame --
    // that is the jitter. polygonOffset breaks the tie in the depth test.
    polygonOffset:true, polygonOffsetFactor:-1, polygonOffsetUnits:-1 });
}

/** A wall hinged on a base edge. The pivot sits ON the hinge; the plane is
 *  offset so it stands up from it, so rotating the pivot IS the fold. */
// Walls are boxes, not planes. A zero-thickness plane reads as paper at
// every angle except dead-on, and the folded stack has no layers to it --
// which is what made the crate look nothing like the moulded original.
// Each wall is a SOLID slab extruded from its own outline.
//
// Two earlier attempts both failed at the edges. A box has solid rectangular
// edge faces, which wrapped the folder silhouette in a bar. Two textured
// sheets a thickness apart kept the silhouette but had nothing joining them,
// so at any grazing angle a wall read as two blades with a gap. Extruding the
// outline gives real edges that follow the shape, and the faces still carry
// the artwork with its perforations cut through.
function faceMat(url, shade, w, h){
  const t = loader.load(url);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 8;
  // extruded faces get their UVs in shape units, so scale them back to 0..1
  t.repeat.set(1 / w, 1 / h);
  return new THREE.MeshLambertMaterial({
    map: t, transparent: false, alphaTest: 0.5, alphaToCoverage: true, side: THREE.DoubleSide,
    color: shade ? 0xcfcfcf : 0xffffff,
    polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1 });
}
function wall(shape, w, h, url, hinge, rot, shade, x0 = w / 2, y0 = 0){
  const pivot = new THREE.Group();
  pivot.position.copy(hinge);
  pivot.userData.lift = 0;
  pivot.userData.baseY = pivot.position.y;
  const geo = new THREE.ExtrudeGeometry(shape,
    {depth: TH, bevelEnabled: false, curveSegments: 20});
  const edge = new THREE.MeshLambertMaterial(
    {color: shade ? 0x9C4B38 : 0xB2543F});
  // ExtrudeGeometry groups: 0 = the two faces, 1 = the edge all the way round
  const slab = new THREE.Mesh(geo, [faceMat(url, shade, w, h), edge]);
  slab.position.set(-x0, -y0, -TH / 2);
  const mesh = new THREE.Group();
  mesh.add(slab);
  if (rot) mesh.rotation.y = rot;
  pivot.add(mesh);
  scene.add(pivot);
  return pivot;
}

// Outlines, origin bottom-left, y up. Arcs are true arcs (absarc), because a
// quadratic approximation drifts a few units off the artwork's own corners.
const PI = Math.PI;
// The end walls, in the icon's own coordinates so the artwork maps 1:1. They
// start on their hinge line, behind the base's fascia, so artwork height
// equals world height and the icon lines up. They are inset by a wall
// thickness up to the side walls' tops; above that they are the icon's
// silhouette, which is what keeps the resting outline exact.
function frontShape(){
  const bt = BODY_TOP, tl = 44, tr = 54, te = 330, ce = 437;
  const top = H - bt, sh = new THREE.Shape();
  sh.moveTo(INSET, HINGE.front);
  sh.lineTo(W - INSET, HINGE.front);
  sh.lineTo(W - INSET, EAR_R);
  const a0 = Math.asin((EAR_R - (top - tr)) / tr);
  sh.lineTo(W - tr + tr * Math.cos(a0), EAR_R);
  sh.absarc(W - tr, top - tr, tr, a0, PI/2, false);
  sh.lineTo(ce, top);
  sh.bezierCurveTo(ce - 42, top, te + 42, H, te, H);
  sh.lineTo(tl, H);          sh.absarc(tl, H - tl, tl, PI/2, PI, false);
  sh.lineTo(0, EAR_L);
  sh.lineTo(INSET, EAR_L);
  sh.lineTo(INSET, HINGE.front);
  return sh;
}
function backShape(){        // the front's body: no tab, and no ears
  const tr = 54, sh = new THREE.Shape(), xr = W - INSET;
  const a0 = Math.acos((xr - (W - tr)) / tr);
  sh.moveTo(INSET, HINGE.back);
  sh.lineTo(xr, HINGE.back);
  sh.lineTo(xr, HB - tr + tr * Math.sin(a0));
  sh.absarc(W - tr, HB - tr, tr, a0, PI/2, false);
  sh.lineTo(INSET, HB);
  sh.lineTo(INSET, HINGE.back);
  return sh;
}
// the icon's bottom band, rounded lower corners and all
function fasciaShape(){
  const sh = new THREE.Shape();
  sh.moveTo(R, 0);
  sh.lineTo(W - R, 0);       sh.absarc(W - R, R, R, -PI/2, 0, false);
  sh.lineTo(W, RIM);
  sh.lineTo(0, RIM);
  sh.lineTo(0, R);           sh.absarc(R, R, R, PI, 1.5*PI, false);
  return sh;
}
// the base in section: the same outline, hollowed into a tray
function trayShape(){
  const sh = new THREE.Shape(), xi = INSET - 0.5;
  sh.moveTo(R, 0);
  sh.lineTo(W - R, 0);       sh.absarc(W - R, R, R, -PI/2, 0, false);
  sh.lineTo(W, RIM);
  sh.lineTo(W - xi, RIM);
  sh.lineTo(W - xi, FLOOR_Y);
  sh.lineTo(xi, FLOOR_Y);
  sh.lineTo(xi, RIM);
  sh.lineTo(0, RIM);
  sh.lineTo(0, R);           sh.absarc(R, R, R, PI, 1.5*PI, false);
  return sh;
}
function rectShape(w, h, r){
  const sh = new THREE.Shape();
  sh.moveTo(r, 0);
  sh.lineTo(w - r, 0);       sh.absarc(w - r, r, r, -PI/2, 0, false);
  sh.lineTo(w, h - r);       sh.absarc(w - r, h - r, r, 0, PI/2, false);
  sh.lineTo(r, h);           sh.absarc(r, h - r, r, PI/2, PI, false);
  sh.lineTo(0, r);           sh.absarc(r, r, r, PI, 1.5*PI, false);
  return sh;
}

// THE BASE. A tray extruded front to back from the icon's own lower outline,
// so from the front its silhouette IS the icon's bottom band, rounded corners
// included. Its front face carries that band's artwork. Because the band
// belongs to the base, nothing rises in front of the end wall when the crate
// opens and nothing is left behind when it closes.
const plain = c => new THREE.MeshLambertMaterial({color: c});
{
  const tray = new THREE.Mesh(
    new THREE.ExtrudeGeometry(trayShape(),
      {depth: D - FASCIA * 2, bevelEnabled: false, curveSegments: 20}),
    plain(0xB2543F));
  tray.position.set(-W/2, 0, -(D/2 - FASCIA));
  scene.add(tray);
  const geo = () => new THREE.ExtrudeGeometry(fasciaShape(),
    {depth: FASCIA, bevelEnabled: false, curveSegments: 20});
  const fascia = new THREE.Mesh(geo(),
    [faceMat(TEX["front.png"], false, W, H), plain(0xB2543F)]);
  fascia.position.set(-W/2, 0, D/2 - FASCIA);
  scene.add(fascia);
  const rear = new THREE.Mesh(geo(), plain(0x9C4B38));
  rear.position.set(-W/2, 0, -D/2);
  scene.add(rear);
  const floor = new THREE.Mesh(
    new THREE.PlaneGeometry(W - INSET * 2 + 1, D - FASCIA * 2),
    mat(TEX["floor.png"], false));
  floor.rotation.x = -Math.PI/2;
  floor.position.y = FLOOR_Y + 0.3;
  scene.add(floor);
  floor.userData.interior = true;
}

// Walls have thickness, so a folded crate is a stack. Each wall hinges a
// wall-thickness higher than the one that folds before it, all of them
// inside the tray, which is 80 deep and houses the four of them.
const front = wall(frontShape(), W, H, TEX["front.png"],
  new THREE.Vector3(0, HINGE.front,  END_Z), 0, false, W/2, HINGE.front);
// same moulding as the front, cropped to the body -- no second tab
const back  = wall(backShape(), W, HB, TEX["back.png"],
  new THREE.Vector3(0, HINGE.back,  -END_Z), 0, true,  W/2, HINGE.back);
const left  = wall(rectShape(SIDE_W, SIDE_H, 6), SIDE_W, SIDE_H, TEX["side.png"],
  new THREE.Vector3(-SIDE_X, HINGE.left,  0), Math.PI/2, true);
const right = wall(rectShape(SIDE_W, SIDE_H, 6), SIDE_W, SIDE_H, TEX["side.png"],
  new THREE.Vector3( SIDE_X, HINGE.right, 0), Math.PI/2, true);

// A side wall's front end is part of the icon: the strip of artwork at the
// icon's edge. It rides on the wall, so it folds away with it.
for (const [p, hy] of [[left, HINGE.left], [right, HINGE.right]]) {
  const h = hy + SIDE_H - RIM, x0 = W/2 + p.position.x - TH/2;
  const t = loader.load(TEX["front.png"]);
  t.colorSpace = THREE.SRGBColorSpace;
  t.repeat.set(TH / W, h / H);
  t.offset.set(x0 / W, RIM / H);
  const end = new THREE.Mesh(new THREE.PlaneGeometry(TH, h),
    new THREE.MeshLambertMaterial({map: t}));
  end.userData.exterior = true;
  end.position.set(0, RIM - hy + h / 2, SIDE_W / 2 + 0.15);
  p.add(end);
}

// LATCHES. Studied off the reference panel: at each end of an end wall, in
// its upper third, a spring tongue is moulded into the wall -- a stepped slot
// around it lets it flex -- carrying a round catch that clicks into the side
// wall, with grip ridges on its outer edge. You squeeze the tongues in, the
// catch clears, and the wall is free. The end walls carry them; the sides
// carry none, which is why they fold freely once the ends are down.
const LATCH_OUT = 9, LATCH_W = 30, LATCH_H = 62, LATCH_Y = 408 - HINGE.front;
function addLatches(pivot, w){
  const group = pivot.children[0];
  pivot.userData.latches = [];
  for (const side of [-1, 1]) {
    const tongue = new THREE.Group();
    const body = new THREE.Mesh(
      new THREE.ExtrudeGeometry(rectShape(LATCH_W, LATCH_H, 10),
        {depth: TH + 3, bevelEnabled: false, curveSegments: 10}),
      new THREE.MeshLambertMaterial({color: 0xCE7560}));
    body.position.set(0, 0, -(TH + 3) / 2);
    tongue.add(body);
    // grip ridges on the outer edge, where a thumb pushes
    for (let i = 0; i < 4; i++) {
      const ridge = new THREE.Mesh(new THREE.BoxGeometry(4, 8, TH + 6),
        new THREE.MeshLambertMaterial({color: 0x9C4B38}));
      ridge.position.set(side < 0 ? 4 : LATCH_W - 4, 10 + i * 14, 0);
      tongue.add(ridge);
    }
    // the round catch that seats in the side wall
    const boss = new THREE.Mesh(new THREE.CylinderGeometry(5, 5, TH + 7, 18),
      new THREE.MeshLambertMaterial({color: 0xE0907C}));
    boss.rotation.x = Math.PI / 2;
    boss.position.set(side < 0 ? LATCH_W - 9 : 9, LATCH_H / 2, 0);
    tongue.add(boss);
    const baseX = side < 0 ? -w/2 - LATCH_OUT : w/2 + LATCH_OUT - LATCH_W;
    tongue.position.set(baseX, LATCH_Y, 0);
    group.add(tongue);
    pivot.userData.latches.push({tongue, baseX, dir: -side});
  }
}
addLatches(front, PANEL_W);
addLatches(back, PANEL_W);

// Folding the way a hand does it, in milliseconds.
//   end wall: PRESS  -- squeeze the tongues in; the wall barely moves, it is
//                       still held
//             SNAP   -- the catch clears and the wall pops free, fast
//             LOWER  -- then it is placed down, gently, slowing as it lands
//   side:     one easy motion; nothing holds it once the ends are down
const PRESS = 130, SNAP = 110, LOWER = 520, SIDE = 420;
const HELD = 0.020, FREE = 0.150;        // fraction of 90 degrees
const START = {front: 0, back: 640, left: 1300, right: 1470};
const TOTAL = START.right + SIDE;

const outQuad  = x => 1 - (1 - x) * (1 - x);
const outCubic = x => 1 - Math.pow(1 - x, 3);
const inOutSine = x => -(Math.cos(Math.PI * x) - 1) / 2;

function endWall(ms){
  if (ms <= 0) return {a: 0, press: 0};
  if (ms < PRESS) { const k = outQuad(ms / PRESS); return {a: HELD * k, press: k}; }
  if (ms < PRESS + SNAP) {
    const k = outCubic((ms - PRESS) / SNAP);
    return {a: HELD + (FREE - HELD) * k, press: 1};
  }
  const k = Math.min(1, (ms - PRESS - SNAP) / LOWER);
  // the tongues spring back out as soon as the wall is clear
  return {a: FREE + (1 - FREE) * inOutSine(k),
          press: 1 - Math.min(1, (ms - PRESS - SNAP) / 140)};
}
function sideWall(ms){
  if (ms <= 0) return {a: 0, press: 0};
  return {a: inOutSine(Math.min(1, ms / SIDE)), press: 0};
}

const BEATS = [
  {o:front, axis:"x", to:-Math.PI/2, start:START.front, fn:endWall},
  {o:back,  axis:"x", to: Math.PI/2, start:START.back,  fn:endWall},
  {o:left,  axis:"z", to:-Math.PI/2, start:START.left,  fn:sideWall},
  {o:right, axis:"z", to: Math.PI/2, start:START.right, fn:sideWall},
];
// ease-out cubic is heavily front-loaded: 90% done at 54% through. On a
// four-beat sequence that makes each wall snap and then wait, which reads
// as a jump rather than a fold. ease-in-out spends the time in the middle,
// where the motion actually is.
const ease = x => x < 0.5 ? 4*x*x*x : 1 - Math.pow(-2*x + 2, 3) / 2;
const clamp01 = x => x < 0 ? 0 : x > 1 ? 1 : x;

// The inside of a closed crate is in its own shadow: seen through the slots
// it is dark, which is also why the resting frame still reads as the icon.
// Light comes in as the front wall opens. This is shading on opaque
// surfaces, tied to the wall's angle -- not opacity, and not a timer.
const INTERIOR = [];
scene.traverse(o => {
  if (!o.isMesh || o.userData.exterior) return;
  let inside = o.userData.interior;
  for (let n = o; n && !inside; n = n.parent) inside = (n === back || n === left || n === right);
  if (inside) for (const m of [].concat(o.material)) INTERIOR.push({m, base: m.color.clone()});
});
const CLOSED_LIGHT = 0.38;

function apply(t){
  const ms = t * TOTAL;
  const open = clamp01(endWall(ms - START.front).a / 0.45);
  const light = CLOSED_LIGHT + (1 - CLOSED_LIGHT) * open * open * (3 - 2 * open);
  for (const {m, base} of INTERIOR) m.color.copy(base).multiplyScalar(light);
  for (const b of BEATS){
    const {a, press} = b.fn(ms - b.start);
    b.o.rotation[b.axis] = b.to * a;
    for (const l of (b.o.userData.latches || []))
      l.tongue.position.x = l.baseX + l.dir * LATCH_OUT * press;
  }
  // The camera lifts across the WHOLE fold, not the first half. Reaching
  // its final angle by 55% meant the viewpoint had stopped moving while
  // three of the four walls were still folding, so the back half of the
  // animation happened in a static frame.
  // Nothing is faded or switched on. Every part is opaque at every instant.

  const c = ease(t);
  const dist = 3400 + 500*c;
  // Dead-on at rest. At 5 degrees the floor and rim behind the front showed
// as a strip beneath it, wider than the front and square at the corners --
// which read as the bottom corners not lining up. Face-on, the front
// occludes everything behind it and the resting frame is the icon alone.
  const el = (0 + 49*c) * Math.PI/180;
  camera.position.set(0, H*0.42 + Math.sin(el)*dist, Math.cos(el)*dist + D/2);
  camera.lookAt(0, H*0.40*(1-c), c*(-D*0.10));
  renderer.render(scene, camera);
}


let t = 0, target = 0, raf = null, last = 0, dead = false;
const DUR = TOTAL;
const still = window.matchMedia("(prefers-reduced-motion: reduce)");
const settled = () => onState(t > 0.5 ? "folded" : "closed");
function run(now){
  if (dead) return;
  if (!last) last = now;
  const dt = Math.min(now - last, 50); last = now;
  const dir = target > t ? 1 : -1;
  t = clamp01(t + dir * dt / DUR);
  apply(t);
  if ((dir > 0 && t < target) || (dir < 0 && t > target)) raf = requestAnimationFrame(run);
  else { raf = null; last = 0; settled(); }
}
function toggle(){
  const open = target < 0.5; target = open ? 1 : 0;
  // reduced motion: the state still changes, it just does not travel
  if (still.matches) { t = target; apply(t); settled(); return open; }
  onState(open ? "folding" : "unfolding");
  if (!raf) { last = 0; raf = requestAnimationFrame(run); }
  return open;
}
function set(v){ t = target = clamp01(v); apply(t); settled(); }
function dispose(){
  dead = true;
  if (raf) cancelAnimationFrame(raf);
  scene.traverse(o => {
    if (!o.isMesh) return;
    o.geometry.dispose();
    for (const m of [].concat(o.material)) { if (m.map) m.map.dispose(); m.dispose(); }
  });
  renderer.dispose();
  renderer.domElement.remove();
}
manager.onLoad = () => { if (!dead) { apply(t); onReady(); } };
apply(t);
return { toggle, set, dispose, duration: TOTAL };
}
