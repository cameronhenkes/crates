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
