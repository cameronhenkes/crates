# Portfolio handoff — crates

Everything the portfolio agent needs. Nothing here writes into the portfolio
repo; copy what you need.

## 1. Images

All 2x, transparent or composed on their own background, in `docs/media/`.

| File | Size | What it shows | Use it for |
|---|---|---|---|
| `in-finder.png` | 2480×1580 | A Finder window in icon view, all 14 project folders coloured, one selected | **The hero.** It is the only image that proves the thing works. |
| `anatomy.png` | 2480×1600 | The crate with its parametric dimensions called out, plus the derived OKLab ramp | The thinking. Use it where the case study explains the system. |
| `motion-fold.png` | 3020×660 | The fold as five frames, 0→340ms, timed | Beside the interactive piece, or instead of it as a fallback. |
| `transparency.png` | 2000×680 | Crates over a deliberately busy background, wallpaper visible through every hole | The one craft decision a viewer would otherwise miss. |
| `sizes.png` | 1640×1560 | Both detail levels, 256px down to 16px | Evidence of rigour. Pairs with the "two detail levels" paragraph. |
| `palette.png` | 1360×1440 | All twelve colours | Index shot, or the collection thumbnail. |
| `hero.png` | 2400×1350 | Three crates on a colour-field background | Decorative. Weakest of the set — use only if a pure visual is needed. |

Copy into the portfolio as `public/images/projects/crates/`.

## 2. The interactive piece

`docs/interactive/react/` — `CrateFold.tsx` + `CrateFold.module.css`, plus
five SVGs in `docs/interactive/svg/`. Drop the SVGs in
`public/images/crates/` and:

```tsx
<CrateFold src="/images/crates/rust.svg" name="rust" />
```

It is self-contained: no motion library, no dependency, CSS transitions only.

**The renderer has no interactive block type.** `content.json` supports
`text`, `image`, `pullQuote` and `list` only. Either add a block type that
renders a named component, or place `<CrateFold>` directly in the page and
use `motion-fold.png` inside the case study itself. Not a decision I should
make inside your repo.

### Motion contract

- **Hover** — `translateY(-7px)` and a tighter shadow, 140ms. Affordance
  only. This is the high-frequency tier, so it stays near the threshold of
  perception; anything more charges attention on every pass.
- **Click** — the body collapses to `scaleY(0.34)` over 340ms, walls lead by
  70ms, shadow tightens as it meets the surface. This is *explanation*: it
  demonstrates the one thing about the object a still image cannot show.
- `cubic-bezier(0.2, 0, 0, 1)` throughout. Bounce 0.
- Hover is gated behind `(hover: hover) and (pointer: fine)`.
- `prefers-reduced-motion` collapses all durations to 1ms.
- It is a real `<button>` with `aria-pressed` and a text label stating the
  state, because motion is never the only feedback channel.

An earlier version also folded the side walls inward. It was cut: the walls
sit inside the shell clip so collapsing them only revealed body colour, and a
folding crate keeps its footprint and loses its height — so the vertical
collapse *is* the fold. Worth a line in the case study if you want a "what I
removed" beat.

## 3. Draft content

`docs/portfolio-item.json` is a study object in your existing
`selectedWorks.studies[]` shape — id, slug, title, description, image, tags,
date, longDescription, sections[].blocks[]. Paste and edit.

**Open question:** Cameron asked for a new *collection* with this as an item.
`content.json` has one collection (`selectedWorks`). If crates belongs in a
separate collection — tools, side projects, open source — that is a new
top-level key plus a route and an index component, which is your call, not
mine. The draft is written so it works either way.
