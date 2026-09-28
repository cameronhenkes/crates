/**
 * The crate fold, as a plain module. No framework, one dependency (three).
 *
 *   const fold = createCrateFold({ THREE, mount, textures, size, onState });
 *   fold.toggle();   fold.dispose();
 *
 * textures: { "front.png": url, "back.png": url, "side.png": url, "floor.png": url }
 * onState:  called with "closed" | "folding" | "folded" | "unfolding"
 *
 * THIS FILE IS THE SOURCE. It began as a lift of the reviewed exploration
 * (docs/explorations/fold-three.html) and has since grown the portfolio's
 * camera work and the record crate; the exploration is now history.
 * Review it with docs/interactive/fold/demo.html served over http.
 */
export function createCrateFold({ THREE, mount, textures, size = 460, onState = () => {}, onReady = () => {},
  palette: P = [0xB2543F, 0x9C4B38, 0xCE7560, 0xE0907C], view = "front",
  recordEdge = 0xE8E2D6, recordRadius = 30, recordLit = true, recordsAspect = 0.72,
  front: frontWall = "up" }) {
// front: what the display crate does with its front wall. "up" keeps it standing, so the crate is
// still the icon and the chosen record slides up out of it. "down" folds it away and shows the
// records through the open front.
const UP = frontWall !== "down";
// "records" is "above" with the camera already brought down to look into the open front, so a
// crate that flew there and a crate painted there are the same picture.
const lifted = view !== "front";
// The records view is a portrait frame: the crate at its foot and room above for a folder drawn
// right out of it. Width over height. Every other view is square.
const ASPECT = view === "records" ? recordsAspect : 1;
const FOV = 17;                          // across the frame; the same in every view
// palette: the untextured parts -- edges and tray, the shaded rear, the latch, its catch -- so a
// crate in another colour matches its textures all the way round.
// view: "front" is the icon, face-on at rest, and the camera lifts as it folds. "above" keeps the
// camera lifted the whole way, so a crate that rests folded opens up in front of you rather than
// swinging round to face you -- and is already looking down into itself for the dolly.
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
renderer.setSize(SIZE, Math.round(SIZE / ASPECT));
mount.appendChild(renderer.domElement);
renderer.domElement.style.cssText = "display:block;width:100%;height:auto";

// Low FOV from far away reads as near-orthographic, so the resting frame is
// the icon rather than a photograph of it.
const camera = new THREE.PerspectiveCamera(FOV, ASPECT, 10, 12000);
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
    {color: shade ? P[1] : P[0]});
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
    plain(P[0]));
  tray.position.set(-W/2, 0, -(D/2 - FASCIA));
  scene.add(tray);
  const geo = () => new THREE.ExtrudeGeometry(fasciaShape(),
    {depth: FASCIA, bevelEnabled: false, curveSegments: 20});
  const fascia = new THREE.Mesh(geo(),
    [faceMat(TEX["front.png"], false, W, H), plain(P[0])]);
  fascia.position.set(-W/2, 0, D/2 - FASCIA);
  scene.add(fascia);
  const rear = new THREE.Mesh(geo(), plain(P[1]));
  rear.position.set(-W/2, 0, -D/2);
  scene.add(rear);
  const floor = new THREE.Mesh(
    new THREE.PlaneGeometry(W - INSET * 2 + 1, D - FASCIA * 2),
    mat(TEX["floor.png"], false));
  // Seen from above, the floor is where the light falls into the open crate, and it is what the
  // dolly lands on: drawn in its own colours, unlit, so the ground around the prints is the colour
  // of the page the crate opens into.
  if (lifted) {
    const lit = floor.material;
    floor.material = new THREE.MeshBasicMaterial({
      map: lit.map, alphaTest: lit.alphaTest, side: lit.side, toneMapped: false,
      polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1 });
    lit.dispose();
  }
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
      new THREE.MeshLambertMaterial({color: P[2]}));
    body.position.set(0, 0, -(TH + 3) / 2);
    tongue.add(body);
    // grip ridges on the outer edge, where a thumb pushes
    for (let i = 0; i < 4; i++) {
      const ridge = new THREE.Mesh(new THREE.BoxGeometry(4, 8, TH + 6),
        new THREE.MeshLambertMaterial({color: P[1]}));
      ridge.position.set(side < 0 ? 4 : LATCH_W - 4, 10 + i * 14, 0);
      tongue.add(ridge);
    }
    // the round catch that seats in the side wall
    const boss = new THREE.Mesh(new THREE.CylinderGeometry(5, 5, TH + 7, 18),
      new THREE.MeshLambertMaterial({color: P[3]}));
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
  {o:front, axis:"x", to:-Math.PI/2, start:START.front, fn:endWall,  name:"front", len:PRESS+SNAP+LOWER},
  {o:back,  axis:"x", to: Math.PI/2, start:START.back,  fn:endWall,  name:"back",  len:PRESS+SNAP+LOWER},
  {o:left,  axis:"z", to:-Math.PI/2, start:START.left,  fn:sideWall, name:"left",  len:SIDE},
  {o:right, axis:"z", to: Math.PI/2, start:START.right, fn:sideWall, name:"right", len:SIDE},
];
// PRESENTING. From folded flat to a display crate: the walls come up in the reverse of the order
// they went down -- right, left, back -- and the front stays where it lies. Each wall is its own
// fold played backwards, so the back is lifted, meets its latches and clicks home.
const P_START = {right: 0, left: 170, back: 530};
const P_TOTAL = P_START.back + PRESS + SNAP + LOWER;
const DOWN = {a: 1, press: 0};
const rising = (b, ms) => b.fn(b.len - Math.max(0, Math.min(b.len, ms)));
// cubic-bezier(0.2, 0, 0, 1), the house curve: solved for x by bisection
const house = x => {
  if (x <= 0) return 0; if (x >= 1) return 1;
  const bx = u => 3*(1-u)*(1-u)*u*0.2 + u*u*u;         // x1 = 0.2, x2 = 0
  const by = u => 3*(1-u)*u*u + u*u*u;                  // y1 = 0,   y2 = 1
  let lo = 0, hi = 1;
  for (let i = 0; i < 30; i++) { const m = (lo + hi) / 2; if (bx(m) < x) lo = m; else hi = m; }
  return by((lo + hi) / 2);
};
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
  // Seen from above the crate is open to the sky, so its inside is never in its own shadow.
  const light = lifted ? 1
    : CLOSED_LIGHT + (1 - CLOSED_LIGHT) * open * open * (3 - 2 * open);
  for (const {m, base} of INTERIOR) m.color.copy(base).multiplyScalar(light);
  for (const b of BEATS){
    const {a, press} = pq > 0
      ? (b.name === "front" ? DOWN : rising(b, pq * P_TOTAL - P_START[b.name]))
      : b.fn(ms - b.start);
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
  // From above, the camera holds still while the crate opens and closes under it: one distance,
  // one point, framed for the open crate, which is the taller of the two.
  // Dead-on at rest in "front": face-on, the front occludes everything behind it and the resting
  // frame is the icon alone.
  // camMix brings any of that down to the records view: low enough to look in through the open
  // front at the faces of the records, high enough to see that they stand in a crate.
  const m = house(camMix);
  // A crate flown here is drawn in a square that grows to the portrait frame's height, so its
  // angle of view opens as it travels; one painted here has the portrait frame from the start.
  // Once taken over, a crate painted in the records view is drawn in a square too, so it can
  // close its angle of view again on the way back to the shelf.
  const shape = (ASPECT !== 1 && !box) ? ASPECT : 1 + (recordsAspect - 1) * m;
  camera.fov = 2 * Math.atan(Math.tan(FOV * Math.PI / 360) / shape) * 180 / Math.PI;
  camera.updateProjectionMatrix();
  const mix = (a, b) => a + (b - a) * m;
  const dist = mix(lifted ? 4300 : 3400 + 500*c, REC.dist);
  const el = mix(lifted ? 49 : 49*c, REC.el) * Math.PI/180;
  const lx = 0;
  const ly = mix(lifted ? HB*0.32 : H*0.40*(1-c), REC.ly);
  const lz = mix(lifted ? -D*0.06 : c*(-D*0.10), REC.lz);
  if (!dz) {
    camera.up.set(0, 1, 0);
    camera.position.set(0, H*0.42 + Math.sin(el)*dist, Math.cos(el)*dist + D/2);
    camera.lookAt(lx, ly, lz);
    // After takeover the crate is drawn in a square somewhere on the screen; flyTo moves it.
    if (box) camera.setViewOffset(box.s, box.s, -box.x, -box.y, box.vw, box.vh);
  } else {
    // The dolly: into the open crate and down onto its floor. The camera swings from its lifted
    // angle to straight down while it closes in, and distance shrinks geometrically so the zoom
    // reads at one rate rather than crawling and then lunging. Screen-up stays the crate's back
    // the whole way, so nothing rolls as the view comes over the top.
    const k = ease(dz);
    const e2 = el + (Math.PI/2 - el) * k;
    const d2 = dist * Math.pow(dollyEnd / dist, k);
    const fy = FLOOR_Y + PRINT_Y;
    // Both the point the camera circles and the point it looks at slide onto the floor's centre.
    const cy = H*0.42 + (fy - H*0.42) * k, cz = D/2 * (1 - k);
    camera.up.set(0, 0, -1);
    camera.position.set(0, cy + Math.sin(e2)*d2, cz + Math.cos(e2)*d2 + 0.001);
    camera.lookAt(lx, ly + (fy - ly) * k, lz * (1 - k));
    // The frame slides with it: from where the crate sat on the page to where it lands.
    if (view0 && view1) {
      camera.setViewOffset(view0.s, view0.s,
        -(view0.x + (view1.x - view0.x) * k), -(view0.y + (view1.y - view0.y) * k),
        view0.vw, view0.vh);
    }
  }
  if (spy === "side") {
    camera.clearViewOffset();
    camera.up.set(0, 1, 0);
    camera.position.set(9000, 330, 120); camera.lookAt(0, 330, 120);
  }
  renderer.render(scene, camera);
}
// spy: a review camera, never used by a page. "side" looks square across the crate.
let spy = null;


let t = 0, target = 0, raf = null, last = 0, dead = false;
// pq: how far through presenting, 0 (not presenting) to 1 (open front). Only meaningful folded.
let pq = view === "records" && !UP ? 1 : 0;
// camMix: how far the camera has come down to the records view.
let camMix = view === "records" ? 1 : 0;
// Front up, the camera sits higher: it has to see over the front wall into the crate, and
// leave room above for a record drawn right out of it.
const REC = UP ? {dist: 4450, el: 27, ly: 690, lz: 60} : {dist: 3750, el: 17, ly: 318, lz: 190};
// box: the square the crate is drawn into after takeover, in screen pixels.
let box = null;
if (view === "records") t = target = UP ? 0 : 1;
// dz: how far into the dolly, 0 to 1. Only ever non-zero after takeover().
let dz = 0;
let dollyEnd = 90;
// The window the crate is drawn into after takeover: the old square box (s, at x/y on screen)
// extended to the whole viewport. view1 is where that square ends up when landing on a target.
let view0 = null, view1 = null;
// Prints lie this far above the floor; the camera lands on them, not on the floor under them.
const PRINT_Y = 3;
let prints = [];
const DUR = TOTAL;
const still = window.matchMedia("(prefers-reduced-motion: reduce)");
const settled = () => onState(pq >= 1 ? "open" : t > 0.5 ? "folded" : "closed");
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
function set(v){ pq = 0; t = target = clamp01(v); apply(t); settled(); }
// Tween a value over a fixed time, for the home's own timing rather than the fold's 1.9s.
function tween(ms, step){
  return new Promise(done => {
    if (still.matches || ms <= 0) { step(1); done(); return; }
    let start = 0;
    const frame = now => {
      if (dead) return done();
      if (!start) start = now;
      const k = Math.min(1, (now - start) / ms);
      step(k);
      if (k < 1) requestAnimationFrame(frame); else done();
    };
    requestAnimationFrame(frame);
  });
}
/** Play the fold to a position over ms. The whole choreography plays, just at this pace. */
function play(to, ms){
  if (raf) { cancelAnimationFrame(raf); raf = null; last = 0; }
  const from = t; target = to;
  onState(to > from ? "folding" : "unfolding");
  return tween(ms, k => { t = from + (to - from) * k; apply(t); }).then(settled);
}
/** Lift the canvas out of its box into a host covering the screen, with the crate drawn exactly
 *  where it was. The projection is the old square view extended to the whole window, so nothing
 *  moves at the swap; after it the dolly has the whole screen to fill. */
function takeover(host, rect){
  const vw = innerWidth, vh = innerHeight;
  host.appendChild(renderer.domElement);
  renderer.setSize(vw, vh, false);
  renderer.domElement.style.cssText = "display:block;width:100%;height:100%";
  camera.aspect = 1;
  // A portrait frame becomes the square as tall as it is, centred on it: the same picture.
  const side = Math.max(rect.width, rect.height);
  view0 = {s: side, x: rect.left - (side - rect.width) / 2, y: rect.top, vw, vh};
  box = {...view0};
  camera.setViewOffset(view0.s, view0.s, -view0.x, -view0.y, vw, vh);
  camera.updateProjectionMatrix();
  apply(t);
}
function dolly(ms){ return tween(ms, k => { dz = k; apply(t); camera.updateProjectionMatrix(); }); }
/** The contents: pictures lying on the floor, top one last. Each is {image, w, h, x, z, rot}
 *  in floor units, x to the right and z towards you, rot clockwise as seen from above. They are
 *  unlit, so a print shows its picture's own colours -- the same pixels the page will show. */
function setPrints(list){
  for (const m of prints) { scene.remove(m); m.geometry.dispose(); m.material.map.dispose(); m.material.dispose(); }
  prints = list.map((p, i) => {
    const tex = new THREE.CanvasTexture(p.image);
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.anisotropy = 8;
    const mesh = new THREE.Mesh(new THREE.PlaneGeometry(p.w, p.h),
      new THREE.MeshBasicMaterial({map: tex, transparent: true, toneMapped: false}));
    mesh.rotation.set(-Math.PI/2, 0, -p.rot);
    mesh.position.set(p.x, FLOOR_Y + 1 + i * (PRINT_Y - 1) / Math.max(1, list.length - 1), p.z);
    scene.add(mesh);
    return mesh;
  });
  apply(t);
}
/** After takeover: land straight down on the floor's centre so that a print `width` floor units
 *  wide, lying there, covers exactly `target` on screen ({cx, cy, width} in CSS pixels). */
function land(target, width, ms){
  const f = Math.tan(camera.fov * Math.PI / 360);
  dollyEnd = width * view0.s / (2 * f * target.width);
  view1 = {x: target.cx - view0.s / 2, y: target.cy - view0.s / 2};
  return dolly(ms);
}

// ---------------------------------------------------------------- the record crate
/** The display state, painted at once: folded flat, then right, left and back standing. */
// The walls that would sweep through the records are standing.
const wallsUp = () => UP ? (t === 0 && pq === 0) : pq >= 1;
function setOpenFront(){
  if (UP) { set(0); return; }
  if (raf) { cancelAnimationFrame(raf); raf = null; last = 0; }
  t = target = 1; pq = 1; apply(t); settled();
}
/** From folded flat, raise the right, left and back walls; the front stays down.
 *  present(ms, 0) lowers them again. */
function present(ms = UP ? TOTAL : P_TOTAL, to = 1){
  // front up, presenting is the whole crate unfolding: it ends as the icon
  if (UP) return play(to ? 0 : 1, ms);
  if (raf) { cancelAnimationFrame(raf); raf = null; last = 0; }
  t = target = 1;
  const from = pq;
  onState(to > from ? "opening" : "folding");
  // linear in time: each wall carries its own easing, as it does in the fold
  return tween(ms, k => { pq = from + (to - from) * k; apply(t); }).then(settled);
}

// Records stand on the folded front wall, on edge, faces to the open front. They are hinged
// along their bottom edge and only ever lean, so two neighbours can meet but never cross as
// long as the one in front leans forward at least as far as the one behind it. Every pose this
// module makes, and every blend between two of them, keeps that order.
const REC_T = 6;                          // thickness of a record
// front down they stand on the front wall where it lies; front up, on the floor
const REC_Y = UP ? FLOOR_Y + 2 : FLOOR_Y + TH + 4;
// As wide as the crate allows with room to move, and tall enough to stand a little proud of
// the walls, the way folders do in a crate.
const REC_W = 840, REC_HMAX = 650;
// A record down in the crate is in the crate's shadow; it comes into the light as it rises.
const REC_SHADE = 0.70;
// front up they sit back from the front wall, or there is no room to flip them forward
const REC_FRONT = UP ? 250 : 398, REC_BACK = UP ? -230 : -70;
const WALL_IN = END_Z - TH / 2;             // the front wall's inner face
const WALL_TOP = H;                         // its highest point, the tab
// What a designer would want to try by hand: tune() changes these and lays the records again.
// Front up, these are Cameron's, set by hand in the playground on 28 Sep 2026.
// gain: how much light a record's surface gives back. 1 is the crate's own plastic. A pale
// record on a light page wants more, or the lamps that make the crate deep make it grey.
const TUNE = UP ? {gap: 140, lift: 0.69, backLean: 45, forwardLean: 60, gain: 1}
                : {gap: 80, lift: 0.30, backLean: 24, forwardLean: 60, gain: 1};
const FLIP_MS = UP ? 520 : 260;
let listed = [];
const RIM_EDGE = {z: D/2 - FASCIA, y: RIM};   // the top inner edge of the base's front face
// sel is -1 when nothing is chosen: every record sits down in the crate, leaning back together.
let records = [], sel = -1, flip = 0, lean = {fwd: 0, back: 0}, lift = 0, lifts = [];

// A record cut as a folder: the crate's own silhouette, with a tab standing up from its top
// edge. `at` slides the tab along, 0 hard left to 1 hard right, so a row of them can be staggered
// and every name read from above without lifting one out.
const TAB_H = 0.13, TAB_W = 0.34, TAB_RUN = 44;
function folderShape(w, h, r, at){
  const hb = h * (1 - TAB_H), tw = w * TAB_W, sh = new THREE.Shape();
  const x0 = at <= 0 ? 0 : TAB_RUN + at * (w - tw - TAB_RUN * 2), x1 = x0 + tw;
  const rt = Math.min(r, (h - hb) * 0.9);
  sh.moveTo(r, 0);
  sh.lineTo(w - r, 0);        sh.absarc(w - r, r, r, -PI/2, 0, false);
  if (x1 + TAB_RUN >= w - r) {                       // tab hard right: it IS the corner
    sh.lineTo(w, h - rt);     sh.absarc(w - rt, h - rt, rt, 0, PI/2, false);
  } else {
    sh.lineTo(w, hb - r);     sh.absarc(w - r, hb - r, r, 0, PI/2, false);
    sh.lineTo(x1 + TAB_RUN, hb);
    sh.bezierCurveTo(x1 + TAB_RUN * 0.45, hb, x1 + TAB_RUN * 0.55, h, x1, h);
  }
  if (x0 <= 0) {                                     // tab hard left: it IS the corner
    sh.lineTo(rt, h);         sh.absarc(rt, h - rt, rt, PI/2, PI, false);
  } else {
    sh.lineTo(x0, h);
    sh.bezierCurveTo(x0 - TAB_RUN * 0.55, h, x0 - TAB_RUN * 0.45, hb, x0 - TAB_RUN, hb);
    sh.lineTo(r, hb);         sh.absarc(r, hb - r, r, PI/2, PI, false);
  }
  sh.lineTo(0, r);            sh.absarc(r, r, r, PI, 1.5*PI, false);
  return sh;
}
function setRecords(list){
  // The side walls lie across the floor when folded and sweep the whole inside as they rise.
  // Records can only be in a crate whose walls are already up.
  if (list.length && !wallsUp())
    throw new Error("setRecords needs a crate with its walls up: present() or setOpenFront() first");
  for (const r of records) {
    scene.remove(r.pivot);
    r.pivot.traverse(o => { if (!o.isMesh) return; o.geometry.dispose();
      for (const m of [].concat(o.material)) { if (m.map) m.map.dispose(); m.dispose(); } });
  }
  listed = list;
  const n = list.length;
  const gap = n > 1 ? Math.min(TUNE.gap, (REC_FRONT - REC_BACK) / (n - 1)) : 0;
  let tallest = 0;
  records = list.map((it, i) => {
    let w = REC_W, h = w / it.aspect;
    if (h > REC_HMAX) { h = REC_HMAX; w = h * it.aspect; }
    tallest = Math.max(tallest, h);
    const tex = new THREE.CanvasTexture(it.image);
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.anisotropy = 8;
    // Lit by the same lamps as the crate, so a colour on a record is shaded the way that colour
    // is shaded on the crate. recordLit: false keeps the cover's own pixels, for a picture that
    // has to match the page.
    const Mat = recordLit ? THREE.MeshLambertMaterial : THREE.MeshBasicMaterial;
    const edgeOf = it.edge ?? recordEdge;
    const card = () => new Mat({color: edgeOf, toneMapped: false});
    const face = new Mat({map: tex, toneMapped: false});
    // A slab cut to a rounded outline, like every other part of the crate. Its faces carry the
    // cover; UVs come out in shape units, so the texture is scaled back to 0..1.
    tex.repeat.set(1 / w, 1 / h);
    const rr = Math.min(recordRadius, h / 4);
    const outlineOf = () => it.tab === undefined ? rectShape(w, h, rr) : folderShape(w, h, rr, it.tab);
    const geo = new THREE.ExtrudeGeometry(outlineOf(),
      {depth: REC_T, bevelEnabled: false, curveSegments: 12});
    geo.translate(-w / 2, -h / 2, -REC_T / 2);
    const mesh = new THREE.Mesh(geo, [face, card()]);
    // the back is plain card, a hair behind the slab's own rear face
    const rear = new THREE.Mesh(
      new THREE.ShapeGeometry(outlineOf(), 12), card());
    rear.geometry.translate(-w / 2, -h / 2, 0);
    rear.rotation.y = Math.PI; rear.position.z = -REC_T / 2 - 0.2;
    mesh.add(rear);
    mesh.userData.record = i;
    const pivot = new THREE.Group();
    pivot.position.set(0, REC_Y, REC_FRONT - i * gap);
    pivot.add(mesh);
    scene.add(pivot);
    const mats = [];
    pivot.traverse(o => { if (o.isMesh) for (const m of [].concat(o.material)) mats.push({m, base: m.color.clone()}); });
    return {pivot, mesh, h, mats, i, ang: 0, up: 0, drop: 0, a0: 0, u0: 0, a1: 0, u1: 0};
  });
  // Forward lean: as far as the front record can go before it meets something. Front down that
  // is the rim of the base, which it rests on. Front up it is the inside of the front wall.
  const clear = UP
    ? a => WALL_IN - 3 - (REC_FRONT + tallest * Math.sin(a) + REC_T / 2 * Math.cos(a))
    : a => (RIM_EDGE.z - REC_FRONT) * Math.cos(a)
         - (RIM_EDGE.y - REC_Y) * Math.sin(a) - REC_T / 2 - 2;
  let lo = 0, hi = TUNE.forwardLean * Math.PI/180;
  if (clear(hi) < 0) for (let i = 0; i < 30; i++) { const m = (lo+hi)/2; if (clear(m) > 0) lo = m; else hi = m; }
  else lo = hi;
  // Backward lean: until the last record would touch the back wall, and never more than asked.
  const zl = n ? REC_FRONT - (n - 1) * gap : 0;
  const reach = (zl - REC_T/2 - 3) - (-END_Z + TH/2);
  lean = {fwd: lo, back: Math.min(TUNE.backLean * Math.PI/180, Math.asin(Math.min(1, Math.max(0, reach / (tallest || 1)))))};
  // Lift. Front down: enough that the leaning record in front does not cover the chosen one's
  // foot. Front up: the record slides up until the camera sees its foot over the front wall,
  // so how far depends on how far back it stands; `lift` then adds to that.
  lift = Math.round(tallest * TUNE.lift);
  const slope = Math.tan(REC.el * Math.PI / 180);
  lifts = records.map((r, i) => {
    if (!UP) return lift;
    const z = REC_FRONT - i * gap;
    return Math.max(0, Math.round(WALL_TOP - (WALL_IN - z) * slope - REC_Y)) + lift;
  });
  sel = Math.max(-1, Math.min(sel, n - 1));
  for (const [i, r] of records.entries()) {
    const g = goal(i, sel); r.ang = r.a1 = g.ang; r.up = r.u1 = g.up;
  }
  settle();
  apply(t);
}
const goal = (i, s) => i < s ? {ang: lean.fwd, up: 0} : i > s ? {ang: -lean.back, up: 0}
                                                          : {ang: 0, up: lifts[i] ?? lift};
// How far forward a record may lean while it is `up` out of the crate: whatever part of it is
// still below the top of the front wall has to stay behind that wall.
function mayLean(r, up){
  if (!UP) return lean.fwd;
  const z = r.pivot.position.z;
  const ok = a => {
    const reach = Math.min(up + r.h, (WALL_TOP + 10 - REC_Y) / Math.cos(a));
    return reach <= up || z + reach * Math.sin(a) + REC_T / 2 * Math.cos(a) <= WALL_IN - 3;
  };
  if (ok(lean.fwd)) return lean.fwd;
  let lo = 0, hi = lean.fwd;
  for (let i = 0; i < 24; i++) { const m = (lo + hi) / 2; if (ok(m)) lo = m; else hi = m; }
  return lo;
}
// And the same behind: whatever is still below the top of the back wall stays in front of it.
function mayLeanBack(r, up){
  const z = r.pivot.position.z, wall = -END_Z + TH / 2;
  const ok = a => {
    const reach = Math.min(up + r.h, (HB + 10 - REC_Y) / Math.cos(a));
    return reach <= up || z - reach * Math.sin(a) - REC_T / 2 * Math.cos(a) >= wall + 4;
  };
  if (ok(lean.back)) return lean.back;
  let lo = 0, hi = lean.back;
  for (let i = 0; i < 24; i++) { const m = (lo + hi) / 2; if (ok(m)) lo = m; else hi = m; }
  return lo;
}
// Settle a frame: hold each record off the front wall, then make sure none leans further
// forward than the one in front of it, which is the rule that stops two of them crossing.
function settle(){
  // from the back: hold each record off the back wall, and bring those in front along with it
  let behind = -Infinity;
  for (let i = records.length - 1; i >= 0; i--) {
    const r = records[i];
    if (r.ang < 0) r.ang = Math.max(r.ang, -mayLeanBack(r, r.up + r.drop));
    r.ang = Math.max(r.ang, behind); behind = r.ang;
  }
  let ahead = Infinity;
  for (const r of records) {
    if (r.ang > 0) r.ang = Math.min(r.ang, mayLean(r, r.up + r.drop));
    r.ang = Math.min(r.ang, ahead); ahead = r.ang;
    place(r);
  }
}
function place(r){
  r.pivot.rotation.x = r.ang;
  r.mesh.position.y = r.h / 2 + r.up + r.drop;
  if (recordLit) {
    const out = clamp01((r.up + r.drop) / Math.max(1, (lifts[r.i] ?? lift) * 0.7));
    const k = (REC_SHADE + (1 - REC_SHADE) * out * out * (3 - 2 * out)) * TUNE.gain;
    for (const {m, base} of r.mats) m.color.copy(base).multiplyScalar(k);
  }
}
/** Put the records in, the way a hand would: lowered in from above, upright, the back one
 *  first, and only then flipped to the chosen one. Use this when the crate is already on
 *  screen; setRecords() is for a crate that is painted with its records in it. */
const DROP_FROM = 1250, DROP_STAGGER = 0.5;
function dropPose(k){
  const n = records.length;
  for (const [i, r] of records.entries()) {
    // the back record leads; each one takes half the time and they overlap
    const lead = n > 1 ? (n - 1 - i) / (n - 1) * DROP_STAGGER : 0;
    const e = house(clamp01((k - lead) / (1 - DROP_STAGGER)));
    r.ang = 0; r.up = 0; r.drop = DROP_FROM * (1 - e); place(r);
  }
}
function dropRecords(list, ms = 700, then = sel){
  setRecords(list);
  const mine = ++flip;
  return tween(ms, k => { if (mine === flip) { dropPose(k); apply(t); } })
    .then(() => mine === flip ? select(then) : undefined);
}
/** Flip to a record, or to none with -1, which sits them all back down in the crate.
 *  Those in front of the chosen one lean forward, it stands
 *  upright and lifts, those behind lean back. Safe to call again before it has finished: every
 *  record starts from wherever it is. */
function select(index, ms = FLIP_MS){
  if (!records.length) return Promise.resolve();
  sel = Math.max(-1, Math.min(index, records.length - 1));
  const mine = ++flip;
  for (const [i, r] of records.entries()) {
    const g = goal(i, sel); r.a0 = r.ang; r.u0 = r.up + r.drop; r.drop = 0; r.a1 = g.ang; r.u1 = g.up;
  }
  return tween(ms, k => {
    if (mine !== flip) return;            // a newer select() has taken over
    const e = house(k);
    for (const r of records) {
      r.ang = r.a0 + (r.a1 - r.a0) * e; r.up = r.u0 + (r.u1 - r.u0) * e;
    }
    settle();
    apply(t);
  });
}
/** Which record the pointer is asking for as it moves THROUGH the crate, or -1 when it is
 *  not over the crate. The crate's outline on screen is divided evenly between the records:
 *  "depth" runs front to back, which on screen is bottom to top; "across" runs left to right.
 *  It holds on to the current record near a boundary, so a hand resting there does not flutter. */
const corner = new THREE.Vector3();
function outline(){
  const r = renderer.domElement.getBoundingClientRect();
  let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
  camera.updateMatrixWorld();
  for (const x of [-W/2, W/2]) for (const y of [0, HB]) for (const z of [-D/2, D/2]) {
    corner.set(x, y, z).project(camera);
    const px = r.left + (corner.x + 1) / 2 * r.width, py = r.top + (1 - corner.y) / 2 * r.height;
    x0 = Math.min(x0, px); x1 = Math.max(x1, px); y0 = Math.min(y0, py); y1 = Math.max(y1, py);
  }
  return {left: x0, top: y0, right: x1, bottom: y1};
}
function through(clientX, clientY, axis = "depth"){
  const n = records.length;
  if (!n) return -1;
  const o = outline();
  if (clientX < o.left || clientX > o.right || clientY < o.top || clientY > o.bottom) return -1;
  const f = (axis === "across" ? (clientX - o.left) / (o.right - o.left)
                               : (o.bottom - clientY) / (o.bottom - o.top)) * n;
  const i = Math.max(0, Math.min(n - 1, Math.floor(f)));
  // stay put until the pointer is well into the next record's share
  if (i !== sel && Math.abs(f - (i > sel ? sel + 1 : sel)) < 0.18) return sel;
  return i;
}
/** Which record is under this point of the screen, or -1. */
const ray = new THREE.Raycaster(), ndc = new THREE.Vector2();
function pick(clientX, clientY){
  const r = renderer.domElement.getBoundingClientRect();
  if (!r.width || !records.length) return -1;
  ndc.set(((clientX - r.left) / r.width) * 2 - 1, -((clientY - r.top) / r.height) * 2 + 1);
  camera.updateMatrixWorld();
  ray.setFromCamera(ndc, camera);
  const hit = ray.intersectObjects(records.map(x => x.mesh), false)[0];
  return hit ? hit.object.userData.record : -1;
}
/** After takeover: carry the crate from where it sits to `to` ({left, top, size} in screen
 *  pixels), bringing the camera down to the records view on the way. With `open`, the walls
 *  come up during the flight, so it arrives as a display crate. */
function flyTo(to, ms, {open = true} = {}){
  if (!box) throw new Error("flyTo needs takeover() first");
  const b0 = {...box}, c0 = camMix, p0 = pq, t0 = t;
  if (open) { if (!UP) t = target = 1; else target = 0; onState("opening"); }
  return tween(ms, k => {
    const e = house(k);
    // `to` is the portrait frame: size wide, size / recordsAspect tall. The crate is drawn in a
    // square as tall as that frame and centred on it.
    const side = to.size / recordsAspect;
    box.s = b0.s + (side - b0.s) * e;
    box.x = b0.x + (to.left - (side - to.size) / 2 - b0.x) * e;
    box.y = b0.y + (to.top - b0.y) * e;
    camMix = c0 + (1 - c0) * k;           // eased inside apply()
    if (open && UP) t = t0 * (1 - k); else if (open) pq = p0 + (1 - p0) * k;
    apply(t);
  }).then(() => { view0 = {...box}; settled(); });
}
/** After takeover: the reverse of flyTo. Carry the display crate back to a square slot on the
 *  shelf, bringing the camera back up to the view from above. The items leave first, drawn up
 *  and out of the top of the window the way they came, because the walls cannot fold with
 *  anything standing between them. With `fold` it arrives folded flat, as it rests on the shelf.
 *
 *  The fold alone is 1.9s at its own pace. Under about 1100ms this reads as hurried. */
const BACK_ITEMS = 0.5, BACK_WALLS = 0.4;     // items are clear by 0.4; the walls start then
function backPlan(to, fold){
  // how far an item has to rise to be off the top of the window once the crate is on the shelf
  const span = 2 * 4300 * Math.tan(FOV * Math.PI / 360);           // units across the slot
  const rise = (to.top + to.size) * span / (to.size * Math.cos(49 * Math.PI / 180));
  return {to, fold, b0: {...box}, c0: camMix, t0: t, p0: pq,
          rise: Math.max(1500, rise * 1.2), ups: records.map(r => r.up)};
}
function backPose(plan, k){
  const e = house(k), {to, b0} = plan;
  box.s = b0.s + (to.size - b0.s) * e;
  box.x = b0.x + (to.left - b0.x) * e;
  box.y = b0.y + (to.top - b0.y) * e;
  camMix = plan.c0 * (1 - k);
  // Gathering speed, not shot out: on the house curve they were gone inside one frame, which
  // is disappearing by another name. They lift, are seen to lift, and then go.
  const u = clamp01(k / BACK_ITEMS), out = u * u;
  for (const [i, r] of records.entries()) { r.up = plan.ups[i]; r.drop = plan.rise * out; }
  settle();
  if (plan.fold) {
    const w = clamp01((k - BACK_WALLS) / (1 - BACK_WALLS));
    if (UP) t = target = plan.t0 + (1 - plan.t0) * w; else pq = plan.p0 * (1 - w);
  }
  apply(t);
}
function flyBack(to, ms, {fold = true} = {}){
  if (!box) throw new Error("flyBack needs takeover() first");
  if (raf) { cancelAnimationFrame(raf); raf = null; last = 0; }
  ++flip;                                  // a flip in progress stops here
  const plan = backPlan(to, fold);
  if (fold) onState("folding");
  return tween(ms, k => backPose(plan, k)).then(() => {
    setRecords([]);                        // they are off the top of the window by now
    sel = -1; view0 = {...box}; settled();
  });
}
/** The box the canvas is drawn into has changed size. */
function resize(px){
  if (box) {
    box.vw = innerWidth; box.vh = innerHeight;
    renderer.setSize(box.vw, box.vh, false);
  } else renderer.setSize(px, Math.round(px / ASPECT), false);
  apply(t);
}
const selected = () => sel;
/** Change how the records sit: {gap, lift, backLean, forwardLean}. Forward lean is a ceiling;
 *  the record still stops where it would rest on the rim. Returns the values in force. */
function tune(v = {}){
  Object.assign(TUNE, v);
  if (listed.length) setRecords(listed);
  const n = records.length;
  const gapActual = n > 1 ? +(records[0].pivot.position.z - records[1].pivot.position.z).toFixed(1) : TUNE.gap;
  return {...TUNE, gapActual, front: UP ? "up" : "down", forwardLeanActual: +(lean.fwd * 180 / Math.PI).toFixed(1),
          liftUnits: lifts[sel] ?? lift};
}
/** For review: paint one instant. `present` is 0..1 through the walls rising; `from`, `to` and
 *  `k` paint the flip from one record to another at k, 0..1 in time; `flight` paints flyTo
 *  part-way. Nothing animates. */
function __camera(name){ spy = name; for (const w of [left, right]) w.visible = name !== "side"; apply(t); }
const __angles = () => records.map(r => [r.ang, r.up]);
/** For review: the least clearances in the pose as it stands. Negative means something is
 *  inside something else. `order` above zero means two records have crossed. */
function __gaps(){
  let order = 0, neighbour = 1e9, frontGap = 1e9, backGap = 1e9;
  records.forEach((r, i) => {
    const z = r.pivot.position.z, lo = r.up + r.drop, hi = lo + r.h;
    const sn = Math.sin(r.ang), cs = Math.cos(r.ang);
    // likewise behind: only what is below the top of the back wall can touch it
    for (let k = 0; k <= 20; k++) {
      const q = lo + (hi - lo) * k / 20;
      if (REC_Y + q * cs < HB + 8) backGap = Math.min(backGap, z + q * sn - REC_T/2 - (-END_Z + TH/2));
    }
    if (UP) {
      // any part of the record still below the top of the front wall must be behind it
      for (let k = 0; k <= 20; k++) {
        const q = lo + (hi - lo) * k / 20;
        if (REC_Y + q * cs < HB + 8) frontGap = Math.min(frontGap, WALL_IN - (z + q * sn + REC_T/2));
      }
    } else if (r.ang > 0) {
      frontGap = Math.min(frontGap, (RIM_EDGE.z - z) * cs - (RIM_EDGE.y - REC_Y) * sn - REC_T/2);
    }
    if (i) {
      const p = records[i - 1], pz = p.pivot.position.z;
      order = Math.max(order, r.ang - p.ang);
      for (const q of [lo, hi])
        neighbour = Math.min(neighbour,
          (pz - (z + q * sn)) * Math.cos(p.ang) + q * cs * Math.sin(p.ang) - REC_T);
    }
  });
  return {order, neighbour, frontGap, backGap};
}
function seek({present: q, from, to, k = 1, flight, drop, back} = {}){
  if (q !== undefined) { t = target = 1; pq = q; }
  if (flight && view0) {                 // {to: {left, top, size}, k}: the flight at k
    const e = house(flight.k);
    box = {...view0, s: view0.s + (flight.to.size - view0.s) * e,
           x: view0.x + (flight.to.left - (flight.to.size / recordsAspect - flight.to.size) / 2 - view0.x) * e,
           y: view0.y + (flight.to.top - view0.y) * e};
    box.s = view0.s + (flight.to.size / recordsAspect - view0.s) * e;
    camMix = flight.k;
    if (UP) { t = target = 1 - flight.k; pq = 0; } else { t = target = 1; pq = flight.k; }
  }
  if (to !== undefined && records.length) {
    const e = house(k);
    for (const [i, r] of records.entries()) {
      const a = goal(i, from ?? to), b = goal(i, to);
      r.ang = a.ang + (b.ang - a.ang) * e; r.up = a.up + (b.up - a.up) * e;
    }
    settle();
    sel = to;
  }
  if (drop !== undefined && records.length) dropPose(drop);
  if (back && box) {                     // {to, k, fold}: flyBack at k, from where it stands now
    seek.plan ??= backPlan(back.to, back.fold ?? true);
    backPose(seek.plan, back.k);
    return;
  }
  apply(t);
}

function dispose(){
  dead = true;
  if (raf) cancelAnimationFrame(raf);
  scene.traverse(o => {
    if (!o.isMesh) return;
    o.geometry.dispose();
    for (const m of [].concat(o.material)) { if (m.map) m.map.dispose(); m.dispose(); }
  });
  for (const m of prints) { m.material.map?.dispose(); }
  renderer.dispose();
  renderer.domElement.remove();
}
manager.onLoad = () => { if (!dead) { apply(t); onReady(); } };
apply(t);
if (view === "records") settled();
return { toggle, set, play, takeover, dolly, land, setPrints,
         setOpenFront, present, setRecords, dropRecords, select, selected, pick, through, outline, flyTo, flyBack, resize, tune, seek, __camera, __angles, __gaps,
         dispose, aspect: ASPECT, recordsAspect, tabHeight: TAB_H, tabWidth: TAB_W, tabRun: TAB_RUN / REC_W, duration: TOTAL, presentDuration: UP ? TOTAL : P_TOTAL, flipDuration: FLIP_MS };
}
