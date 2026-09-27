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

## Built in 3D, to Cameron's model

> "the front should fold down toward the back. Then in the background there is
> the other short side which then folds down forward. Then the side, which is
> a perspective and scales from the front to the back"

That is the correct model, and it cannot be faked in 2D. Opposing walls fold
in **opposite screen directions**, and the side walls foreshorten along their
length. Both fall out of real perspective for free, and neither can be
approximated with scale.

So `pieces.py` now emits the crate as separate planes — `base.svg` plus outer
and inner faces for the long and short walls — and `fold3d.html` assembles
them in a `preserve-3d` scene. Each wall is hinged on its base edge:

| wall | placement | upright | folded inward |
|---|---|---|---|
| front (near) | `top:H`, origin `0 0` | `rotateX(-90deg)` | `rotateX(-180deg)` |
| back (far) | `left:W; top:0` | `rotateZ(180) rotateX(-90)` | `rotateZ(180) rotateX(-180)` |
| left | `left:0; top:0` | `rotateZ(90) rotateX(-90)` | `rotateZ(90) rotateX(-180)` |
| right | `left:W; top:H` | `rotateZ(-90) rotateX(-90)` | `rotateZ(-90) rotateX(-180)` |

Every wall runs the same `rotateX(-90deg -> -180deg)`; the `rotateZ` only
orients the hinge. The near wall folding away and the far wall folding toward
you is not authored — it is what that single rotation looks like from a tilted
camera.

**Faces.** Each wall carries two layers with `backface-visibility:hidden`,
the front layer being the INNER face. Flat-outward it points up, upright it
points into the crate, folded inward it points down at the floor. The right
face is showing at every angle without being told which.

**Order.** Short ends (left/right, 684) lead; long sides (front/back, 900)
follow at 34%. Short edge first, then long, as the manufacturer says.

Note Cameron's description had front/back as the short pair. In this icon the
crate is wider than deep, so front/back are the LONG walls and left/right the
short ones — the order above follows the object, not the screen. Worth
confirming, since swapping it is one line.

### Still to tune
Wall thickness is not modelled, so the flat state is a single plane rather
than a four-layer stack. Duration (760ms) is long for a click.

## The icon is the default state

> "The folder icon which we created through original should be the default
> state, but currently it looks like we're rebuilt it."

Right, and it was a real regression. `pieces.py` had been redrawing a
simplified floor for the base, so the 3D scene's resting image was a
reconstruction rather than the icon. The canonical artwork is the default
state; the walls and the tilt are part of the *answer*, not the resting image.

Fixed two ways:

1. `base_piece()` now calls `generate.build()` — the base **is** the icon.
   Verified pixel-identical to `crate.py` output by raster hash, not by eye.
2. The scene rests at `rotateX(0)` with the walls hidden, so the default
   frame is the flat icon exactly as it appears everywhere else. It only
   leaves plan view once you ask it to fold.

### Open defect
With the scene resting flat, the upright walls are not appearing during the
tilt — frames 2 to 4 of `fold3d-from-icon.png` show a tilted plane with no
walls standing. Either they are z-fighting with the base or the
`preserve-3d` chain is breaking under the scaled parent. The resting state
and the flat end state are both correct; the middle of the animation is not.
Needs a debugging pass before this is worth wiring into the component.

## The icon is the FRONT of the crate (Cameron's reframe)

> "so this is the front of the crate. When I click it, this front folds down
> backwards revealing that there is also sides and a back too."

This is the right model and it dissolves the problem the previous five
attempts were fighting. The icon is not a view from above that has to somehow
imply depth — it is the crate's **front wall, seen face-on**. The resting
state is then the canonical icon *by construction*, not by patching. Click,
the front falls back on its bottom hinge, and the sides and back are revealed
behind it — which is exactly the sequence described earlier: front folds away,
back folds forward, sides fold in with front-to-back foreshortening.

`fold-front.html` builds this. `pieces.py` gained `floor.svg`, `back.svg` and
`side.svg` — the inner faces you see once the front is out of the way, drawn
quieter than the front because they are background.

### Iteration log

1. Nothing rendered. `transform-origin:50% 100%` with `scale()` parks the
   crate below its stage — scale does not change layout size.
2. Split scale and rotation onto separate elements. Geometry appeared.
3. Sides flared outward: `rotateY(90deg)` on the left wall swings it toward
   the camera, not away. Signs inverted; floor had the same fault.
4. Back wall now converges correctly behind the front. Sides now flare the
   other way — forward, in front of the icon.

### Open blocker
The front pane renders *behind* the back pane despite sitting at `+1px` and
the back at `-300px`. Forcing `translateZ` did not change it, so the depth
axis itself is suspect: the `scale()` on the `preserve-3d` ancestor very
likely collapses or rescales z along with x and y, which would flatten the
whole depth ordering.

Next attempt should take the scale off the 3D chain entirely — size the
panes in already-scaled pixels and drop `scale()` — so the only transforms in
the preserve-3d context are rotations and translations.

## Four beats, in order

Cameron: "Front, then back, then left side then right-side."

Sequenced accordingly — four discrete beats rather than two, with the sides
no longer moving together:

| beat | delay | wall |
|---|---|---|
| 1 | 0% | front falls back |
| 2 | 25% | back falls forward |
| 3 | 49% | left side folds in |
| 4 | 73% | right side folds in |

Unfold runs the reverse. Each wall also carries a `--stack` offset applied
after its rotation, so the first to fold ends up at the bottom of the pile —
which is both what a real crate does and a help to the depth sorting, since
fewer planes are ever in motion at once.

`fold-sequence-4beat.png` shows the beats reading distinctly.

### Remaining defect
The side walls project as thin spikes rising well above the frame instead of
reading as walls. Their far edges being higher on screen is correct
perspective, but the shape is wrong — they are being seen far closer to
edge-on than a 245-deep wall should be at a 34 degree tilt. Geometry fault,
not a sorting one.

## Moved to Three.js

CSS 3D was the wrong renderer. Four hinged planes genuinely intersect at their
hinges, and browsers sort `preserve-3d` siblings by transformed centroid, so
the order flips in a single frame whenever two centroids cross. No amount of
z-staggering removes that; it is how the compositor works.

`fold-three.html` rebuilds the scene with a real depth buffer.

- Each wall is a `Group` positioned **on** its hinge line with the plane
  offset to stand up from it, so rotating the group *is* the fold. No
  compound transforms to get the sign wrong on.
- Rotations derived, not guessed: front `+Y` must reach `-Z` (`rot.x -90`);
  back `+Y` to `+Z` (`+90`); left `+Y` to `+X` (`rot.z -90`); right to `-X`
  (`+90`).
- Materials use `alphaTest: 0.5` rather than alpha blending, so the fragment
  shader discards transparent pixels and the depth buffer stays
  authoritative. The perforations are genuinely see-through at every angle —
  the thing CSS could not do at all.
- Camera is a 17-degree FOV from far back, so the resting frame reads as the
  icon rather than a photograph of it. It lifts and pulls back as the crate
  opens.
- Four beats at 0 / 26 / 50 / 74 percent: front, back, left, right.
- `?t=0.42` renders that instant and stops, for frame-by-frame review.

### Verification gap
Headless Chrome needs software GL (`WEBGL=1` on `lib/render.sh`, now
supported) and it renders the canvas blank even with textures confirmed
loading. So this scene cannot be checked the way every earlier version was.
It has an on-page diagnostic instead: three's revision, renderer context,
texture progress and any thrown error print under the canvas. Check it in a
real browser.

## Frame-by-frame review does work

I had said this build could not be verified the way the CSS ones were. That
was wrong. The headless blank was the `file://` texture failure, which the
data-URI inlining fixed for an unrelated reason — once textures were inlined,
headless WebGL rendered fine. `review-frames.sh` renders the `?t=` hook at
eight instants and stitches them, and motion reads perfectly well from stills:
pacing, ordering, pops and stacking all show up.

Two faults it caught immediately, neither of which I would have guessed:

**The front was 90% folded by t=0.14.** `ease-out cubic` is heavily
front-loaded — 90% complete at 54% through its span. On a four-beat sequence
that makes each wall snap and then wait, which reads as a jump. Now
ease-in-out, which spends the time in the middle where the motion is.

**The camera stopped moving at t=0.55.** It reached its final angle while
three of the four walls were still folding, so the back half of the animation
played out in a static frame. Now lifts across the whole fold.

`three-motion-frames.png` is the strip after both fixes: front tips back,
crate revealed, back drops, left in, right in, flat. Sequential and evenly
paced.

### Still open
- The back and side faces read as large flat panels at grazing angles; their
  perforations are not carrying.
- D=720 against H=684 makes the crate read as a deep carton rather than a
  shallow crate. A real one is far wider than it is tall, but the icon's
  front face fixes that ratio at 1.32:1.

## Wall styling, and why the corners would not join

Three faults, all structural rather than cosmetic.

**The walls had the floor's pattern.** The reference photo settles it: the
floor carries a grid of short slots; the walls carry tall piano-key slots
running up into the rim, with tapered ribs between them, a smooth rail across
the bottom, and small raised feet on that rail. `panel_art` now draws a wall.

**The box was sized to the folder, not to the crate.** The icon is a folder:
its tab rises 96 above the body. Sizing every wall to the full 684 pushed the
sides proud of the front wherever the tab was not. The box is the body only
(588), and the tab overhangs it — which is what a folder tab does.

**A flat plane meeting a rounded corner always leaves a wedge.** The front's
silhouette pulls in by its 62-unit radius at every corner, and a side wall
parked at the extreme edge left its square corner sticking into that gap. No
texture change could fix it. On a real crate the front and back wrap the
sides, so the sides sit inboard; `INSET` is that overlap, and the floor pulls
in to match so it cannot poke past the outline either.

**Front and back are one moulding.** The back now uses the icon artwork, as
Cameron asked — `DoubleSide` shows it mirrored from inside, which is what you
would actually see.

## Review round: thickness, and what it broke

Frame review of the current build found five things.

**Walls were zero-thickness planes.** At every mid-fold angle they read as
paper, not moulded plastic — Cameron's "thickness is not consistent with the
HAY crate". Fixed, but see below for how.

**Interior faces were as bright as the front**, so when the front tipped away
you saw two identical grids stacked and it read as confusion rather than
depth. The back and sides are now shaded (`color: 0x9a9a9a`), which is also
just true: they sit inside a crate.

**The stack spacing was arbitrary.** It is now the wall thickness itself, so
a folded crate is as thick as four walls, which is what the real one is.

**The back carried a tab.** Front and back are the same moulding, but a tab
is a FOLDER affordance and belongs on the front. Seen from inside the
artwork mirrors, so the back's tab landed on the wrong side and put a second
tab in the resting silhouette. Mirroring the texture did not fix it cleanly
(a box's -z face has mirrored UVs, so the correction cancels). The back is
now the front artwork cropped to the body — same moulding, no tab.

**BoxGeometry broke the silhouette.** Giving walls thickness as boxes was
wrong: a box's edge faces are solid rectangles that ignore the texture's
alpha cutout, so the folder shape ended up wrapped in a rectangular bar and
the resting frame showed a phantom second tab. Thickness now comes from two
textured faces `TH` apart — the cutout survives, and it still reads as
thickness at every angle except dead-on.

### Corners
Checked at rest, 0.20, 0.45 and 0.75. Bottom corners are clean at all four —
the inset holds now that the front and back wrap the sides. Side walls show
their moulded edge at 0.20 and 0.45 rather than reading as paper.
