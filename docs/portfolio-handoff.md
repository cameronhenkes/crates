# Portfolio handoff — crates

Everything the portfolio agent needs. Nothing here writes into the portfolio
repo; copy what you need.

## 1. Images

All 2x, transparent or composed on their own background, in `docs/media/`.

| File | Size | What it shows | Use it for |
|---|---|---|---|
| `in-finder.png` | 2560×1600 | A real Finder window, captured, of twelve folders each a different crate, on the macOS default desktop | **The hero.** It is the only image that proves the thing works. |
| `fold.mp4` / `fold.gif`, and `fold-dark` | 1920×1080, 6.4s | The crate folding flat and standing again, on a blank page | Beside the interactive piece, or in place of it. |
| `records.mp4` / `records.gif`, and `records-dark` | 1920×1080, 9.7s | The record crate: folders sliding up one at a time, on a blank page | The collection page's behaviour, shown. |
| `redline-dimensions.png` | 3800×2640 | The crate with every dimension marked in red | What makes it a crate and not a folder with holes. |
| `redline-detail.png` | 3800×2840 | The perforations, enlarged, with sizes and spacing | Evidence of rigour. |
| `anatomy.png` | 2480×1600 | The crate's parts called out, plus the derived OKLab ramp | The thinking. Keep it; the redlines measure, this names. |
| `transparency.png` | 2000×680 | Crates over the bridge and rocks, desktop visible through every hole | The one craft decision a viewer would otherwise miss. |
| `sizes.png` | 1640×1560 | Both detail levels, 256px down to 16px | Pairs with the "two detail levels" paragraph. |
| `palette.png` | 2720×2100 | All twelve colours, named | Index shot, or the collection thumbnail. |
| `hero.png` | 2400×1350 | Three crates on the desktop | Decorative. |
| `motion-fold.png` | 2592×1302 | The fold as sixteen labelled frames | A still fallback for the video. |

The desktop picture in the stills is Apple's default. It appears as a backdrop, the way it
does in any screenshot of a Mac. The videos have no backdrop: a blank page, light or dark.

Copy into the portfolio as `public/images/projects/crates/`.

## 2. The interactive piece

`docs/interactive/fold/`:

| File | What it is |
|---|---|
| `CrateFold3D.tsx` + `CrateFold3D.module.css` | The React component. A real button, a label, the hover lift. |
| `crate-fold.js` + `crate-fold.d.ts` | The scene itself. No framework. This is the source: the fold, the portfolio's camera work (palette, views, takeover, dolly, prints) and the record crate (open front, records, flip, pick, flight). |
| `shoot.sh` | Renders `demo.html` at one instant, for frame review. |
| `tex/front.png`, `back.png`, `side.png`, `floor.png` | The four textures, 640k together. |
| `demo.html` | The module with no framework around it. Serve the folder over http to view. |

To install:

1. `npm install three` and `npm install -D @types/three`. The portfolio does
   not have either yet.
2. Copy the two `CrateFold3D` files and the two `crate-fold` files into one
   component folder, together.
3. Copy `tex/*.png` to `public/images/crates/fold/`.
4. Copy `docs/interactive/svg/rust.svg` to `public/images/crates/rust.svg`.
   It is the poster shown until the scene is ready, and the fallback where
   WebGL is missing.

```tsx
<CrateFold3D />
```

`three` is imported on the client after mount, so it costs nothing on pages
that do not show the crate.

**The renderer has no interactive block type.** `content.json` supports
`text`, `image`, `pullQuote` and `list` only. Either add a block type that
renders a named component, or place `<CrateFold3D>` directly in the page and
use `motion-fold.png` inside the case study itself. Not a decision I should
make inside your repo.

**Read `docs/learnings.md` before placing it.** It is the feedback Cameron
gave while this was built and the reasons behind it.

### Motion contract

- **Hover**: `translateY(-4px)`, 140ms. Affordance only. This is the
  high-frequency tier, so it stays near the threshold of perception.
- **Click**: the crate folds as the real one does, 1.9 seconds in total.
  Front, back, left, right. Each end wall is squeezed (130ms), pops free
  (110ms) and is lowered (520ms). Each side folds in one motion (420ms).
- Nothing is transparent and nothing fades, at any point.
- Bounce 0.
- Hover is gated behind `(hover: hover) and (pointer: fine)`.
- `prefers-reduced-motion`: the state changes without travelling.
- It is a real `<button>` with `aria-pressed` and a text label stating the
  state, because motion is never the only feedback channel.
- One colour, rust. Its page background can be anything; the canvas is
  transparent around the crate.

The earlier component, `docs/interactive/react/CrateFold.tsx`, squashed the
icon vertically. It is superseded and kept only as history. Do not ship it.

## 2b. The record crate

Settled with Cameron in the playground on 28 Sep 2026. The reasons behind
each decision are in `docs/explorations/fold-notes.md`, from "The record
crate" onward.

| File | What it is |
|---|---|
| `crate-fold.js` + `crate-fold.d.ts` | The crate, including the display state and the records |
| `crate-items.js` + `crate-items.d.ts` | Draws an item. Copy it; do not redraw the items by hand |
| `playground.html` | Every interaction, live, with the settled values as defaults |
| `serve.sh` | Serves the folder and opens the playground |

What was decided:

| Decision | Setting |
|---|---|
| Front of the crate | Stays up. The display crate is the whole crate, so it is still the icon |
| Chosen item | Slides straight up until its foot clears the front wall, then 69% of its height more |
| Steering | `through()`: the cursor moving through the crate, front to back |
| Nothing hovered | `select(-1)`: every item sits down in the crate |
| Flip | 520 ms, cubic-bezier(0.2, 0, 0, 1) |
| Item cut | Folder, tabs staggered left, middle, right |
| Item face | Moulded like the crate. No picture, no label on the tab, no words |
| Item colour | The crate's colour, 70% darker. The same on a light or dark page |
| Item light | Lit by the crate's lamps, and shaded down inside it |
| Frame | Portrait, 0.72 wide to 1 tall |

## 3. Draft content

`docs/portfolio-item.json` is a study object in your existing
`selectedWorks.studies[]` shape — id, slug, title, description, image, tags,
date, longDescription, sections[].blocks[]. Paste and edit.

**Open question:** Cameron asked for a new *collection* with this as an item.
`content.json` has one collection (`selectedWorks`). If crates belongs in a
separate collection — tools, side projects, open source — that is a new
top-level key plus a route and an index component, which is your call, not
mine. The draft is written so it works either way.
