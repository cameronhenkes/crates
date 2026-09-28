/**
 * The items that stand in the crate, drawn. No framework, no dependency.
 *
 *   const fold = createCrateFold({ ... view: "records" });
 *   fold.setRecords(projects.map((p, i) => drawItem({ crate: "#C0614B", index: i, fold })));
 *
 * An item is a folder in the crate's own colour, darker, with the crate's moulding pressed
 * into it: a lit rim round the whole outline, a recessed panel, two rows of slots, a foot rail.
 * It carries no picture, no label on its tab and no words. Items are told apart by where their
 * tabs sit and by the list beside the crate.
 *
 * Settled with Cameron in the playground, 28 Sep 2026. The reasons are in
 * docs/explorations/fold-notes.md.
 */

/** How much darker than the crate an item is. */
export const DARKER = 0.70;
/** Where the tabs sit, in order, repeating. 0 is hard left, 1 hard right. */
export const TABS = [0, 0.5, 1];
/** The canvas an item is drawn on: the icon's own proportions. */
export const ITEM_W = 1176, ITEM_H = 894;

const rgb = hex => { const n = parseInt(hex.slice(1), 16); return [n >> 16, (n >> 8) & 255, n & 255]; };
/** The crate's colour, darker by a share of itself. */
export const deepen = (hex, by = DARKER) =>
  "#" + rgb(hex).map(v => Math.round(v * (1 - by)).toString(16).padStart(2, "0")).join("");
const shade = (hex, by) => {
  const f = v => Math.max(0, Math.min(255, Math.round(v + by)));
  return `rgb(${rgb(hex).map(f).join(",")})`;
};
const rbox = (x, X, Y, W, H, R) => { x.beginPath(); x.roundRect(X, Y, W, H, R); };

/** The outline the crate cuts, as a canvas path. It must match the module's, or the rim drifts. */
function silhouette(x, W, H, top, at, r, fold){
  x.beginPath();
  if (at === undefined) { x.roundRect(0, 0, W, H, r); return; }
  const tw = W * fold.tabWidth, run = W * fold.tabRun, rt = Math.min(r, top * 0.9);
  const x0 = at <= 0 ? 0 : run + at * (W - tw - run * 2), x1 = x0 + tw;
  x.moveTo(r, H); x.lineTo(W - r, H); x.arcTo(W, H, W, H - r, r);
  if (x1 + run >= W - r) { x.lineTo(W, rt); x.arcTo(W, 0, W - rt, 0, rt); }
  else { x.lineTo(W, top + r); x.arcTo(W, top, W - r, top, r); x.lineTo(x1 + run, top);
         x.bezierCurveTo(x1 + run * 0.45, top, x1 + run * 0.55, 0, x1, 0); }
  if (x0 <= 0) { x.lineTo(rt, 0); x.arcTo(0, 0, 0, rt, rt); }
  else { x.lineTo(x0, 0); x.bezierCurveTo(x0 - run * 0.55, 0, x0 - run * 0.45, top, x0 - run, top);
         x.lineTo(r, top); x.arcTo(0, top, 0, top + r, r); }
  x.lineTo(0, H - r); x.arcTo(0, H, r, H, r); x.closePath();
}

/** One sheet of colour and one lit rim, round the whole outline, with no seam at the tab. */
function sheet(x, c, W, H, top, at, fold){
  const r = 46;
  silhouette(x, W, H, top, at, r, fold); x.save(); x.clip();
  const g = x.createLinearGradient(W * 0.1, 0, W * 0.4, H);
  g.addColorStop(0, shade(c, 12)); g.addColorStop(0.6, c); g.addColorStop(1, shade(c, -10));
  x.fillStyle = g; x.fillRect(0, 0, W, H);
  silhouette(x, W, H, top, at, r, fold); x.lineWidth = 22; x.strokeStyle = shade(c, 30); x.stroke();
  x.lineWidth = 3; x.strokeStyle = shade(c, -46); x.globalAlpha = 0.5; x.stroke(); x.globalAlpha = 1;
  x.restore();
}

/** The crate's face, pressed into the sheet. */
function moulding(x, c, W, H, top){
  const X = 64, Y = top + 60, w = W - 128, hh = H - top - 60 - 150;
  x.fillStyle = shade(c, -12); rbox(x, X, Y, w, hh, 22); x.fill();
  x.lineWidth = 3; x.strokeStyle = shade(c, -40); x.globalAlpha = 0.55; rbox(x, X, Y, w, hh, 22); x.stroke();
  x.globalAlpha = 1; x.strokeStyle = shade(c, 22); rbox(x, X + 14, Y + 14, w - 28, hh - 28, 14); x.stroke();
  const n = 18, pitch = (w - 120) / n, sh = (hh - 150) / 2;
  for (let r = 0; r < 2; r++) for (let k = 0; k < n; k++) {
    const sx = X + 60 + k * pitch + (pitch - 20) / 2, sy = Y + 50 + r * (sh + 50);
    x.fillStyle = shade(c, 26); rbox(x, sx, sy + 3, 20, sh, 7); x.fill();
    x.fillStyle = shade(c, -58); rbox(x, sx, sy, 20, sh, 7); x.fill();
  }
  x.fillStyle = shade(c, -6); x.fillRect(11, H - 118, W - 22, 107);
  x.fillStyle = shade(c, 28); x.fillRect(11, H - 118, W - 22, 3);
}

/**
 * Draw one item. Returns what setRecords() takes.
 *   crate   the crate's colour, as "#rrggbb"
 *   index   its place in the crate, which decides where its tab sits
 *   fold    the crate it is for (its tabHeight, tabWidth and tabRun set the outline)
 *   darker  how much darker than the crate (default 0.70)
 *   style   "moulded" (default) or "plain"
 *   cut     "folder" (default) or "card"
 */
export function drawItem({ crate, index, fold, darker = DARKER, style = "moulded", cut = "folder" }){
  const W = ITEM_W, H = ITEM_H, c = document.createElement("canvas");
  c.width = W; c.height = H;
  const x = c.getContext("2d"), colour = deepen(crate, darker);
  const at = cut === "folder" ? TABS[index % TABS.length] : undefined;
  const top = at === undefined ? 0 : Math.round(H * fold.tabHeight);
  sheet(x, colour, W, H, top, at, fold);
  if (style === "moulded") {
    x.save(); silhouette(x, W, H, top, at, 46, fold); x.clip();
    moulding(x, colour, W, H, top);
    // the rim again, over the ends of the foot rail
    silhouette(x, W, H, top, at, 46, fold); x.lineWidth = 22; x.strokeStyle = shade(colour, 30); x.stroke();
    x.restore();
  }
  return { image: c, aspect: W / H, tab: at, edge: parseInt(colour.slice(1), 16) };
}
