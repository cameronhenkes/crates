# Making the crate fold properly

## What the real object does

Sources: the Aykasa crate (HAY rebadges it) folds by **pushing the short edge
first, then the long edge**. Collapsible-crate patents describe the same
order: latches in the end walls engage receivers in the side walls, the short
end walls fall inward onto the base, and the long side walls then fold down
over them. The first wall is weighted so its centre of gravity sits inboard of
its hinge — it falls in on its own once released.

Four beats, in this order:

1. **Latch release.** Nothing moves yet. Worth a beat of its own — it is the
   "unclick" that makes the rest read as mechanical rather than magical.
2. **Short end walls fall inward** onto the base.
3. **Long side walls fold down over them.**
4. **Flat.** Same footprint, four wall-thicknesses high.

Our crate is 900 x 684, so **left and right are the short edges** and top and
bottom are the long ones.

## The digital problem

The icon is already a flat plan view, so there is no height to lose. A wall
"folding down" has to be expressed some other way. That is the whole question.

See `fold-mechanism.png` for the storyboard. `fold-mechanism.py` regenerates it.

## What the current branch does

A vertical squash — `scaleY(1 -> 0.34)`. It is wrong: it collapses the
footprint, which a real crate never does, and it folds nothing in any order.
It reads as "flattened", not "folded".

## The three options, built

`fold-options.png` — all three as working prototypes.
`fold-options.py` regenerates any frame: `python3 fold-options.py frame A 0.6 out.html`.

Prerequisite, now done: `generate.py` emits the wall groups **after** the
floor and grid. A wall laying inward has to cover the floor it lands on, and
paint order is the only z-order SVG has. The rails sit at x<108 and x>792 and
the grid at 126..774, so they never overlap — the resting raster is
byte-identical before and after (verified by hash).

### A · Plan fold
Short walls lay inward, long walls fold over, footprint constant. Hinges are
on the base perimeter, so the transform origin is each wall's **outer** edge
and it grows inward — no zero-crossing, no flicker.

Correct in every structural respect, and it still does not look right.
Stretching the existing rail artwork 3.4x turns the recess ladder into
smears, and because a laid-down wall is the same fill as the floor it lands
on, the motion is nearly invisible until you add a contact shadow. **To ship
this, the laid-down wall needs to be drawn as its own panel** — the wall's
inner face with its ribs — rather than a scaled copy of the rail.

### B · Perspective dip
`rotateX` out of plan and back, with the same wall folds underneath. The tilt
does the work on its own: you see the object had height, which is the thing
the flat icon cannot say. Cheapest route to a fold that reads.

Costs: it leaves the icon language for ~400ms, and it is the longest of the
three. If the piece sits among flat UI, that departure is the whole question.

### D · Retract
Walls thin to nothing at the rim, body collapses to a slab. No stretched
artwork and no paint-order dependency, but it never shows an order, so it
reads as dissolving rather than folding.

### Where this leaves it
B is the only one that currently reads as a fold without new artwork. A is
the most faithful and would beat B if the laid-down panels were drawn. D is
not worth shipping.

## Built: laid-down panels, and option A properly

`fold-demo.html` — all three live, side by side, clickable.

`generate.py --parts` now also emits four hidden `c-panel` groups: purpose-drawn
laid-down walls, painted last so a folded wall covers what it lands on. Each
panel shows the wall's **inner** face — the rim that used to be the top edge
now pointing inward, ribs running hinge-to-rim, two rows of perforations, and
a contact shadow cast away from the hinge. The perforations are drawn dark
rather than cut through, because a panel lying on the base shows shadow
through its holes, not wallpaper.

Each panel starts at exactly the apparent width of the upright wall it
replaces (`scaleX(.36)` for the short ends, `scaleY(.22)` for the long sides)
and grows to full depth from its hinge, so the swap is continuous. Long sides
carry a 150ms delay — short edge first, then long, as the object does.

The plain (non-`--parts`) output is byte-identical throughout; verified by
raster hash after each change.

## Cameron's correction, and what it exposed

> "The shape of the folder does not change per how it is in real life. It
> seems like elements appear over the top, but doesn't accurately reflect
> real-world functionality."

Correct, and it has three separate causes — two fixable, one structural.

**Fixed: the panel showed the wrong face.** A wall hinged at the base and
folding inward rotates its *inner* face down onto the floor. What ends up
pointing at you is the **outer** face — smoother, one row of perforations,
stronger ribs. The first version drew the inner face.

**Fixed: a cross-fade is not a rotation.** A real wall passes through
edge-on: its visible face narrows to just the top rim, and the outer face
then opens from that same line. Fading one layer into another skips the only
moment that reads as hinging, which is exactly why it looked like layers
appearing. Now built as two-phase keyframes sharing a hinge.

**Fixed: the outline does change, slightly.** Crate walls splay outward for
stacking, so an assembled crate's outline is a few percent larger than its
base. Collapsing brings the walls vertical and the silhouette shrinks to the
footprint. Now a `scale(.958)` across the fold.

**Structural: plan view cannot carry this.** The footprint is constant *by
design* — that is the point of the mechanism. So the entire information
content of the fold lives in the axis a top-down icon does not show. Every
fix above makes A more honest without making it more legible, because the
thing that changes most in reality (height) is the thing plan view discards.

That is the case for B. Leaving plan view for ~500ms is not decoration; it is
the only way to show a change that happens in the third axis.
