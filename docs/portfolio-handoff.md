# Portfolio handoff — crates

Everything the portfolio agent needs. Nothing here writes into the portfolio
repo; copy what you need.

## 1. Images

All 2x, transparent or composed on their own background, in `docs/media/`.

| File | Size | What it shows | Use it for |
|---|---|---|---|
| `in-finder.png` | 2480×1580 | A Finder window in icon view, all 14 project folders coloured, one selected | **The hero.** It is the only image that proves the thing works. |
| `anatomy.png` | 2480×1600 | The crate with its parametric dimensions called out, plus the derived OKLab ramp | The thinking. Use it where the case study explains the system. |
| `motion-fold.png` | 2592×1302 | The fold as sixteen frames, closed icon to flat stack, each labelled in milliseconds | Beside the interactive piece, or instead of it as a fallback. |
| `transparency.png` | 2000×680 | Crates over a deliberately busy background, wallpaper visible through every hole | The one craft decision a viewer would otherwise miss. |
| `sizes.png` | 1640×1560 | Both detail levels, 256px down to 16px | Evidence of rigour. Pairs with the "two detail levels" paragraph. |
| `palette.png` | 1360×1440 | All twelve colours | Index shot, or the collection thumbnail. |
| `hero.png` | 2400×1350 | Three crates on a colour-field background | Decorative. Weakest of the set — use only if a pure visual is needed. |

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

## 3. Draft content

`docs/portfolio-item.json` is a study object in your existing
`selectedWorks.studies[]` shape — id, slug, title, description, image, tags,
date, longDescription, sections[].blocks[]. Paste and edit.

**Open question:** Cameron asked for a new *collection* with this as an item.
`content.json` has one collection (`selectedWorks`). If crates belongs in a
separate collection — tools, side projects, open source — that is a new
top-level key plus a route and an index component, which is your call, not
mine. The draft is written so it works either way.
