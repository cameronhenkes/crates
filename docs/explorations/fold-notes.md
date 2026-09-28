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

### Frame-by-frame, verified against the shipped build

The previous corner grid was rendered with the BoxGeometry version that was
then replaced, so its findings were stale. Re-run against what is actually on
disk, all eight instants:

| t | reads as |
|---|---|
| 0 | the icon, tab left, clean silhouette |
| 0.14 | front tipping back, crate appearing behind it |
| 0.28 | open crate, back wall standing, sides at the edges |
| 0.42 | back folding forward, perforated floor visible |
| 0.56 | back down, both sides still standing |
| 0.70 | left side folding in |
| 0.84 | right side folding in |
| 1.0 | flat, layered slab |

Two faults it caught and fixed:

**The interior went almost black.** `0x9a9a9a` times Lambert falloff at
grazing angles reads as a void rather than shade. Lifted to `0xcfcfcf` with
ambient at 1.05.

**The side walls sat near edge-on for most of the fold.** Camera elevation
topped out at 37 degrees, so their artwork was never legible. Now 49.

## The front was folding through the sides

Cameron: "The front and backs open up through the sides. This is physically
impossible."

Correct, and it was structural. The front is full width (900) and hinges at
the crate's front edge, so rotating down it sweeps the entire span between
the sides. With the sides parked *inside* that span at x = +/-412, the front
passed straight through them.

Only two ways out, and the fold order decides which:

- **Sides fold first**, then the front and back drop over them. This is what
  the real crate does (short edge first), but it contradicts the front-first
  order Cameron specified.
- **Sides move outboard** of the front's width, so the front and back fold
  *between* them. This is also how a real crate is assembled -- the end walls
  drop between the side walls -- and it keeps the front-first order.

Took the second. `SIDE_X = W/2 + TH/2`.

### The trade
The sides are now a sliver outside the front's silhouette, so at rest you can
see a thin vertical strip at each edge rather than the icon alone. That is
unavoidable with a full-width front: either the sides are inboard and get
passed through, or they are outboard and visible. Honest either way -- a real
crate's side walls are its outermost surface at that point.

## The crate had no visible bottom

Two causes, both mine.

**The floor was shaded as an interior face.** It is the surface you look down
onto, so `0xcfcfcf` times Lambert falloff took it almost to black. It is not
an interior wall and should catch light — now unshaded.

**Its pattern rendered as specks.** `floor_piece` drew slots far smaller than
the front's, so at scene scale it read as texture noise rather than a
perforated base. Redrawn in the front's own vocabulary: double-framed panel,
centre rib, the same slot size and bevels.

Verified in `fold-floor-check.png` at t=0.30 and 0.45 — the base is visible
and reads as a crate floor.

Worth knowing: the front wall is 684 tall against a 720-deep crate, so once
it folds it covers nearly the whole floor. The window where the base is
properly visible is roughly t=0.26 to 0.45. Widening it means a deeper crate,
which changes the proportions.

## Feedback audit

| # | Your feedback | State |
|---|---|---|
| 1 | Sides unclick then fold down; look up the real construction | done — Aykasa, short-edge-first, patents |
| 2 | Shape must change, not elements appearing over the top | done — moved to real 3D |
| 3 | Direction B, the one that animates and changes shape | done |
| 4 | Front folds toward back, far side folds forward, sides in perspective | done — one rotation per wall, directions emergent |
| 5 | The original icon must be the default state | done — base is the canonical icon, hash-verified |
| 6 | The icon IS the front of the crate; click reveals sides and back | done |
| 7 | Order: front, back, left, right | done — 0 / 26 / 50 / 74% |
| 8 | Weird transition, sides/back pop to the top | done — CSS centroid sorting; Three.js depth buffer |
| 9 | Style the sides to the real HAY crate | done — piano-key slots, rim, rail, feet |
| 10 | Thickness inconsistent with the HAY crate | done — twin faces, TH=13 (~1.4%), stack spacing = thickness |
| 11 | Front and back open through the sides — impossible | done — sides outboard, front folds between them |
| 12 | There is no bottom | done — unshaded, redrawn in the front's grid |
| 13 | The back should be the exact same piece as the front | **partial** |
| 14 | Corners connected through the rounded edge, top corners too | **partial** |

**13 — back as the exact same piece.** It is the front artwork, cropped to
the body. Not literally the same piece, because the front carries a folder
tab and the back does not: seen from inside the artwork mirrors, so an
uncropped back put a second tab on the wrong side of the resting
silhouette. Cameron's call which is worse — a cropped back, or a second tab.

**14 — top corners.** Resolved. The sides sit outboard of the front (they
have to, or the front folds through them), so wherever the front's
silhouette curved in at a corner the side was left exposed as a nub. The
sides now stop below where that curve starts: `SIDE_H = HB - R_TR`. Side
walls slightly lower than end walls is normal on a real crate. Bottom
corners were already clean; verified at rest and 0.28 in
`fold-corners.png`.

## Sides in the front's language, and latches

**The sides were in a different vocabulary.** I had drawn them with the
piano-key slots visible in the reference photo — truthful to the object, but
the front of this crate is the icon, and a side in a different language does
not read as the same part. `panel_art` now draws the icon's body at any
aspect: rounded silhouette, rails with their ladder of recesses, the
double-framed panel, the same slot size and bevels, centre divider, bottom
rail with feet. Consistency with the front wins over fidelity to the photo.

**Latches.** On the real crate the end walls carry a catch that drops into a
recessed channel on the side wall. Drawn as a vertical groove inboard of each
corner post — lit near edge, shadowed far edge, so it reads as cut into the
moulding rather than printed on it — with the catch step about a third of the
way down.

**Edges.** The side's front corner was appearing past the point where the
front's silhouette curves in. `DEPTH_IN` raised from `R*0.62` to `R*1.15`, so
the sides start further back and cannot show at the corner.

## The folded state that was not folded

Cameron screenshotted a flat base with both side walls still standing, label
reading "folded flat". The sides do fold — a render at t=1.0 is flat — so
what he caught was mid-animation. Two faults made that possible, and the
second is the one I should have caught.

**The label lied.** It claimed the end state the instant you clicked, then
sat there for the 1250ms the crate was still visibly folding. It now reads
"Folding…" during, and settles to the real state only when the animation
arrives.

**The beats were queued, not overlapped.** At 0 / 0.26 / 0.50 / 0.74 with a
0.26 span, the base was flat by t=0.52 with two walls still upright — half
the animation spent in a state that reads as broken rather than as folding.
Now 0 / 0.18 / 0.36 / 0.54 with a 0.34 span, so the walls overlap and the
tail is short.

**What I missed.** The frame strip sampled 0.56 and 0.70, both of which show
exactly that state. I described them as "back down, both sides still
standing" and read it as correct sequencing. It is correct sequencing, and it
still looks broken — a frame review that only checks whether the right thing
is happening will miss whether it looks right while it happens.

## Walls sitting free — two separate bugs

Cameron: "some sides are sitting entirely free and not connected at all."
Correct, twice over, and both were mine.

**The stack lift was baked in.** A folded crate is a stack, so each wall is
raised by the thickness of the ones folded before it. I added that lift to
the pivot's position at construction, so it applied *always* — every wall
hovered above the floor even while upright, the right one by 52 units, ~8% of
the crate's height. `apply()` now rides the lift in with the fold, so a
standing wall sits on the floor and only rises as it lies down.

**The floor did not reach its own hinges.** It was `W - R*0.4` = 875 wide,
half-width 437, while the sides hinge at `SIDE_X` = 456.5. They were pivoting
about 20 units beyond the floor's edge — hinged in mid-air. The floor is now
`SIDE_X * 2` so its edge and the hinge line coincide.

Verified across ten instants (`fold-dense-frames.png`) and at the three that
were worst, 0.36 / 0.48 / 0.60 (`fold-hinge-check.png`). The sides still read
as thin slivers around 0.48 because they are near edge-on there, but they are
attached.

## How the crate is actually built

Cameron: no bottom visible once the front folds, and nothing the sides are
hinged to. Researched properly (collapsible-crate patents, WO2005082728A1,
US7195127, US8627973B2, US7478726B2) rather than guessed.

The mechanism: the base is **not a bare plane**. It carries an upstanding
**perimeter rim**, and hinge **sockets are formed in that rim**. Each wall's
bottom edge carries **pins or knuckles** that seat into them. The pins have
radial projections that lock while the wall is upright and release when it is
folded flat — which is exactly why Aykasa panels are removable. The rim also
holds all four wall tops at the same level.

Three changes follow:

**The rim is modelled.** Four runs around the base with the sockets drawn in,
and every wall now hinges on top of it rather than on the floor plane. A wall
has something to be attached *to*.

**Walls carry hinge knuckles.** Drawn along each wall's bottom edge, sized
and spaced to match the sockets.

**The crate is deeper: D 720 -> 950.** The front is 684 tall, so against a
720-deep base a folded front covered the entire floor and the crate read as
bottomless. At 950 the base stays visible behind it.

### The trade
The rim is visible below the front wall at rest, so the resting frame is the
icon sitting on a base band rather than the icon alone. That is what a real
crate looks like -- the front wall sits on the base rim -- but it is a
departure from the pure icon. Cameron's call.

## Alignment: one footprint, derived

Cameron: the sides and the front are not aligned with the bottom.

Correct, and it was fallout from deepening the crate. `DEPTH_IN` had been
tuned when `D` was 720; once `D` became 950 the sides were still inset by
that fixed amount, leaving them 807 wide against a 925-deep base — and their
texture squashed to fit the narrower plane.

Everything now derives from one footprint, `(W + TH) x D`:

| part | size | from |
|---|---|---|
| floor | 913 x 950 | footprint |
| long rim | 913 | footprint width |
| short rim | 950 | footprint depth |
| side wall | 924 | `D - TH*2`, spanning between front and back |
| front / back | 900 | the icon |

The floor and long rim were also being drawn at 900 and used at 913 — a 1.4%
stretch, small enough to pass a glance and exactly the kind of drift that
resurfaces later as "the alignment is off". Both now generate at the
footprint width.

Every texture is checked against the plane it maps to before inlining.

## Rounding the rim to the front's shape

Cameron: the bottom corners do not line up — can the corner be rounded to
keep the shape of the front?

Yes. The rim was four straight `BoxGeometry` runs, so they met at square
corners and pushed past the front's rounded silhouette. It is now a single
continuous ring: a rounded-rect `Shape` with a rounded-rect hole, extruded to
the rim height. Its radius is the crate's own `R`, so the base follows the
front's outline exactly.

Camera elevation at rest also dropped from 5 degrees to 0, so the view is
level rather than looking slightly down into the crate.

### What remains
A base band is still visible below the front at rest — that is the rim itself,
seen edge-on, and it is now rounded to match. Whether it should be visible at
all is the trade noted earlier: a real crate's front wall sits *on* its base
rim, so the band is true to the object but is a departure from the icon alone.
Reducing `RIM` until the icon's own bottom rail covers it would hide it, at
the cost of the hinge being less legible.

## The extra bottom piece

Cameron: "we have an extra bottom piece and the corners are still not being
aligned."

That piece is the floor, and its width is correct. The side walls sit
outboard so the front can fold *between* them — which is how a real crate
works, the long side walls being outermost and the short end walls fitting
between — so the base spans their outer faces and is `TH*2` wider than the
front. A crate's base really is wider than its end wall.

But correctness was not the point. At rest you are looking at a **closed**
crate, and you should not be able to see its floor at all. The only reason it
showed was the camera sitting above floor level, which turns that 13-unit
overhang into a visible sliver past the front's rounded corners — reading as
a stray part rather than as the base.

So the base fades in as the crate opens: floor and rim are hidden at rest and
ramp up over `t` 0.02 to 0.12, once the front has begun to fall. At rest the
frame is the icon alone, which is what it was always supposed to be, and by
the time the crate is open the base is fully there.

This is the one place the build cheats rather than models. It is worth it: no
camera position both shows a closed crate face-on and hides a base that is
genuinely wider than the wall in front of it.

## The rim is the housing, not a plinth

Cameron: "onclick after the front collapses the stray piece reappears."

Hiding the base at rest treated the symptom. The plate was visible beneath
the folded front because the front was lying **67 units above the floor**,
and that was a modelling error, not a camera one.

I had hinged every wall on *top* of the rim and then lifted each one further
as it folded. A real crate is the other way round: the rim exists to **house
the folded stack**. Each wall hinges at its own height *inside* the rim, the
first to fold sitting lowest, directly on the floor, and each later one a
wall-thickness higher.

| wall | hinge height |
|---|---|
| front (folds 1st) | 6.5 |
| back | 19.5 |
| left | 32.5 |
| right (folds last) | 45.5 |

Four walls stack to 52; the rim is 54. The stagger is static, in the hinge
positions, so the animated lift is gone entirely.

Also found while in there: the rim ring was positioned one rim-height too
high. `ExtrudeGeometry` runs 0..depth along +Z, which after the -90 degree
rotation is already 0..RIM in Y, so adding `position.y = RIM` put it at
54..108. It sat above the floor with a gap underneath.

The rim ring is now `(W + 2*TH) x D` outside and `W x (D - 2*TH)` inside, so
the walls sit in the middle of its thickness and the front fits exactly
within its inner edge.

## Corners, fixed as one problem instead of six

Cameron flagged the front/side corners (early fold) and the side showing
past the front's top-right corner (rest). Same root as every corner complaint
before them: the front is the icon, with rounded corners, and everything else
is flat panels arranged around it. Wherever the icon's outline curves away,
whatever sits behind shows through or pokes past. I had been patching those
one at a time.

**At rest, only the front exists.** A closed crate seen face-on shows its
front and nothing else. The back and sides now fade in with the base over
`t` 0.02 to 0.12. `alphaTest` scales with the fade, otherwise the cutout
discards every fragment until opacity passes 0.5 and the walls pop instead
of fading.

**The box has consistent corners.**

| | was | now | why |
|---|---|---|---|
| rim height | 54 | 72 | covers the front's rounded bottom corners (R=62 plus hinge offset); above it the front's edge is straight |
| rim plan radius | 62 | 36 | walls meet at a square corner and were poking out through a large-radius rim |
| rim band thickness | 13 | 24 | wider than a wall, so no two faces are coplanar |
| side height | 534 | 495 | tops sit below where the front's top-right corner starts to curve |
| side hinge | W/2 + 6.5 | W/2 + 7.5 | inner face 1 unit clear of the front's edge |

Stack of four walls is 52, housed in a 72 rim.

Verified: rest top-right, 0.16 bottom-left and bottom-right, and all eight
frames of the sequence.

### What this costs
During the fold the rim is a band slightly wider than the front with
near-square corners. That is the crate's base and is only on screen while the
front is visibly falling, never at rest.

## Solid walls, latches, and folding the way a hand does it

### The renders had been cropping the crate
The canvas is 460 wide and the review harness rendered a 440 viewport, so the
right-hand side of the crate was outside every frame. Every right-hand corner
reported as checked before this point was never in shot.
`review-frames.py` replaces the shell script: 580 wide, locates the crate in
each frame, and crops every frame to one shared window.

### Walls are solid slabs
A corner check on real corners showed each side wall as two thin blades with
a gap. Thickness had been faked with two textured sheets a wall-thickness
apart and nothing joining them. Every wall is now an `ExtrudeGeometry` of its
own outline -- the folder silhouette for the front, the body for the back, a
square-cornered rectangle for the sides -- so the edges are real and follow
the shape. Faces keep the artwork and its cut-through perforations.

### The latch, from the reference panel
- at each end of an end wall, in its upper third
- a spring tongue moulded into the wall; a stepped slot around it lets it flex
- a round catch on the tongue that clicks into the side wall
- grip ridges on the outer edge
- along the bottom edge, hinge knuckles alternating with wider support ledges

The end walls carry the latches. The sides carry none, which is why they fold
freely once the ends are down.

### Timing, in milliseconds

| wall | press | snap | lower |
|---|---|---|---|
| front | 0-130 | 130-240 | 240-760 |
| back | 640-770 | 770-880 | 880-1400 |
| left | folds 1300-1720 | | |
| right | folds 1470-1890 | | |

- **press**: the tongues squeeze in 9 units; the wall moves 2% of its travel,
  because it is still held
- **snap**: the catch clears and the wall jumps to 15%, fast, ease-out
- **lower**: placed down over 520 ms on a sine ease, slowing as it lands
- **sides**: one 420 ms motion each, overlapping

No overshoot anywhere, per the house rule that bounce is always 0. The snap
reads from the speed change, not from a rebound.

### Known simplifications
- The tongue slides inward rather than flexing about its root.
- Unfolding is the fold played backwards, so the latch "clicks" at the end of
  raising rather than being pushed home.
- While the base fades in (roughly 40 to 230 ms) it passes through a darker
  half-transparent state.

## The fade is gone: the icon's bottom band is the base

Finding (Cameron): at the start of the fold, and again at the end of the
unfold, a dark band flickered across the bottom of the front and the base was
visibly see-through.

Cause: the base was wider than the icon, because the sides sat outboard of a
full-width front. To keep the resting frame clean the base, back and sides were
hidden and faded in over the first 190 ms, and the rim, 72 high and in front of
the front wall, rose over the front's lower edge as it appeared.

Fix, at the source rather than the symptom:

- The crate is one footprint, as wide as the icon. The icon is its front
  elevation.
- The icon's bottom band (80 high) is the base. It is a tray extruded front to
  back from the icon's own lower outline, and its front face carries the band's
  artwork. It never moves, so nothing can cover the front or be left behind.
- The end walls hinge behind that face and are a wall thickness narrower than
  the icon each side, so they fold between the side walls. The strip of icon at
  each edge is the side wall seen end-on.
- No material is transparent and nothing is switched on or off. `opacity` does
  not appear in the file.
- The closed interior is shaded, and lightens with the front wall's angle.

Known compromises:

- Above the side walls' tops the end wall keeps the icon's full width (the
  rounded top-right corner and the tab's left edge). Those two slivers pass
  inside the side walls' thickness as the front folds.
- Through the slots at rest you now see the shaded inside of the crate, not
  the page behind it.

Checked in `three-motion-frames.png` (16 moments, six of them inside the first
quarter second) and `first-quarter-second-corners.png` (all four corners,
enlarged, 0 to 500 ms). The unfold is the same positions in reverse.

## The record crate (28 Sep 2026)

Asked for by the portfolio: a collection page as a record crate. The crate
stands open-fronted on the left with project covers in it like records, and
hovering a project flips to its record.

The module is now the source (`docs/interactive/fold/crate-fold.js`); this
exploration page is history and `build-component.py` is retired.

Added: `setOpenFront`, `present` (right, left, back rise; front stays down),
`setRecords`, `dropRecords`, `select`, `pick`, `flyTo`, `resize`, a `records`
view, and `seek` for painting single instants.

Decisions, and why:

- Records hinge on their bottom edge and only lean. Two neighbours cannot
  cross while the one in front leans forward at least as far as the one
  behind. Every pose and every blend between poses keeps that order, which is
  what makes `select` safe to interrupt.
- The forward lean is solved, not chosen: as far as the front record goes
  before it rests on the rim of the base (58.9 degrees).
- `setRecords` throws unless the walls are up. Folded side walls lie across
  the floor and sweep the whole inside as they rise; the first flight test
  had records in a flat crate and a wall passing through them.
- Records arrive by being lowered in (`dropRecords`), not by appearing.

Checked: 176 frames of a hover that changes its mind seven times, driven by
a manual clock because headless Chrome starves animation frames. No order
violation; least gap between neighbours 35.3; least gap to the rim 2.0; to
the back wall 240.2. Frame sheets of the flip (front and side), the walls
rising, the flight and the drop. A crate flown to a box and a crate painted
in that box differ only in edge antialiasing.

Compromises:

- Leaning records keep even gaps; they do not rest on each other.
- Records behind the chosen one lean back 24 degrees without reaching the
  back wall unless the crate is full.
- The chosen record stands lifted with nothing holding it.
- Records stand on the folded front wall, in the front 470 of the crate.

## The record crate keeps its front (28 Sep 2026)

Cameron: "The record should still have the front", and "the items in the
crate should slide out upwards to be able to view the item. The styling of the
items should be rounded and follow similar styling patterns."

Why it matters: with the front folded away the crate stopped being the icon.
The front wall is the identity of the piece, so the display state has to keep
it.

- `front: "up"` is now the default. The display crate is the whole crate, all
  four walls standing. `front: "down"` keeps the earlier open-front version.
- The chosen record slides straight up until the camera sees its foot over the
  front wall. How far depends on how far back it stands, so each record has its
  own lift. The front one comes right out of the crate.
- Records sit back from the front wall so there is room to flip them forward;
  the forward lean stops where a record would touch the inside of the wall
  (22.7 degrees with six records).
- Records are slabs cut to a rounded outline, not boxes.
- The camera is higher (27 degrees) to see over the wall.

Checked, front up: 176 frames of an interrupted hover, no two records cross;
least gap to the front wall 1.4, between neighbours 67.8, to the back wall 160.
Frame sheets of the flip from the front and the side, and of the flight.

Compromise: the chosen record hangs above the crate with nothing holding it.

## Cameron's values, and steering by cursor (28 Sep 2026)

Set by him in the playground and now the defaults with the front standing:
flip 700 ms, gap 134, extra lift 61%, lean back 21, lean forward at most 27.

Two things those values exposed:

- The lift took the chosen record out of the top of the frame. The records
  camera now stands further back. It is fixed, not fitted to the records,
  because a crate that flies in has none until they are lowered in, and a
  camera that moved when they arrived would jump.
- A record coming down while already leaning went 8 units into the front
  wall. Each frame is now settled: a record may only lean as far as the part
  of it still below the wall's top allows, and no record leans further
  forward than the one in front of it.

"I want to be able to easily move my cursor through the crate to go between
them." Touching a record was hard to steer: most of each record is behind the
front wall, and the chosen one leaves from under the cursor. `through()` shares
the crate's outline on screen evenly between the records, front to back or left
to right, and holds on near a boundary so a resting hand does not flutter.

## The items (28 Sep 2026)

Cameron: "animation looks good. But now lets focus on the items themselves."
He had also told the portfolio session "we need to create a different style
to covers".

The playground now shows his six real projects, with four ways to make an
item and two ways to cut it:

- Window: a moulded frame in the item's colour around the work.
- Sleeve: the work edge to edge, named along the foot.
- Label: a paper card with a band of colour, type and a small window.
- Moulded: the crate's own vocabulary, no image.
- Cut as a folder: the item takes the icon's silhouette, with a tab. Tabs are
  staggered left, middle, right, so every name reads from above while the
  items are still in the crate.
- Cut as a card: a plain rounded card.

Colours are the twelve from the icon palette. Project images are read from
`docs/interactive/fold/local/`, which is ignored by git: this repository is
public and the images are client work.

## The items are objects, not covers (28 Sep 2026)

Cameron, in order: "The tabs are going in the right direction, the visual
styling is not. It's not consistent with the visual design of the tabs." Then
"we shouldn't have a cover image on them as well", "the tab shouldn't have a
label either", and "no text on the cover items".

Why: the tab was a flat colour and a shape. Everything I had put on the body
(frames, a picture, a fade, tags) was a different visual language stuck to it.
Each thing he removed was a thing the icon does not have either.

So an item is a folder in one of the icon's colours: one fill, one lit rim
round the whole silhouette with no seam at the tab, and nothing printed on it.
The list beside the crate names the projects. Two variants remain: plain, and
moulded with the crate's recessed panel and slots.

## Items take the crate's light (28 Sep 2026)

Cameron: the items need to be larger, and "the colours of the item don't align
with the colour shading of the crate. There is obvious shadowing occurring" on
the crate that the items did not share.

Cause: the items were unlit, drawn in their own pixels, because covers with
pictures had to match the page. The crate is lit. Side by side, the items
looked stuck on.

- Items are lit by the crate's lamps (`recordLit`, default true), so a colour
  on an item is shaded as that colour would be on the crate.
- An item down in the crate is in its shadow and comes into the light as it
  rises. Shading tied to position, as with the crate's interior.
- Items are 840 wide (were 760) in the icon's own proportions, and stand a
  little proud of the walls.
- Each item's edges are its own colour, not card.
- Extra lift default dropped from 61% to 18%: a larger item with the same lift
  leaves the frame. The camera came in closer with the room that freed.

## An item is never the crate's colour (28 Sep 2026)

Cameron: "We need to ensure we're not using the same colour as the crate."

Why: a folder that matches the crate reads as part of the crate, not as
something in it. The first item had been rust in a rust crate.

Rule: items take the icon's palette less the crate's own colour and anything
close enough to be mistaken for it. With a rust crate that drops rust and
ochre. The rule is relative to the crate, so a sage crate drops sage.

## At rest, a portrait frame, and Cameron's third round (28 Sep 2026)

"If there are no items hovered over, then they should all be sitting within
the crate." Selection can now be none (-1), which is how records start and
what the pointer leaving returns to. Every item sits down, leaning back
together.

His third round of values: flip 520 ms, gap 140, extra lift 69%, lean back up
to 45, lean forward up to 60. Both leans are ceilings; the walls stop them
first (about 22 back and 18 forward with six items).

He wanted the items larger AND lifted further, which a square frame cannot
give: the two trade against each other. The records view is now a portrait
frame, 0.72 wide to 1 tall (`recordsAspect`). The angle of view is fixed
across the frame, so the crate fills the width as before and the extra height
is room above it. A crate flown in is drawn in a square that grows to the
frame's height while its angle of view opens, and lands on the same picture
as one painted there.

A lifted item leaning back could reach the back wall. Frames are now settled
from the back as well as the front.

## Item colours follow the page (28 Sep 2026)

Cameron: "if it's in a dark mode, we should opt for more dark colours than the
flat hues and in light mode, more lighter colours."

Why: the palette's flat hues were chosen for folder icons on a desktop. On a
dark page they glare; on a light page the deep ones punch holes in it.

- The icon's hues are kept and retoned: deep on a dark page (lightness 0.30 to
  0.40), pale on a light one (0.86 to 0.93). Each hue keeps its place in the
  order of lightness.
- Pale items under the crate's lamps came out grey, because those lamps are
  what make the crate deep. `tune({gain})` lets a surface give back more light;
  the light page uses 1.7, the dark page 1.
- The crate keeps its own colour on either page, and that is the colour items
  are kept away from.

First attempt at the light page made every item the same grey: I was filtering
against a retoned crate colour, and every pale colour is close to a pale
pink. Caught in the render.

## Correction: items go against the page, and are moulded (28 Sep 2026)

Cameron, after seeing deep-on-dark and pale-on-light: "invert the colour
directions for light mode vs. dark mode." Then: "I like the moulded like the
crate effect. Let's go with this too."

I had read his earlier note literally and matched the items to the page. Seen
on screen, matched items sink into it. Against the page, the items are what
stands out, and the crate, which keeps its own colour, sits between the two.

- Dark page: pale items, gain 1.7.
- Light page: deep items, gain 1.
- Moulded is the item style: the crate's recessed panel, two rows of slots and
  a foot rail, pressed into a folder of the item's colour. Plain stays as the
  alternative.

The section above, "Item colours follow the page", describes the direction he
rejected. Its mechanism (retoning, gain, keeping away from the crate's colour)
still stands.

## Colour retoning undone (28 Sep 2026)

Cameron: "undo the colour changes."

Items are back to the icon's own flat hues, the same on a dark page and a
light one. Retoning for the page was tried both ways round and neither held.
Kept: items never take the crate's colour or one near it; items are lit by the
crate's lamps; moulded is the default style. `tune({gain})` stays in the
module at 1, unused by the playground.
