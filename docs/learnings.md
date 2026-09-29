# What the crate fold taught us

For the portfolio agent, and for anyone building the next interactive piece.
This is the feedback Cameron gave while the fold was built, in the order it
arrived, with the reason behind each point. The reasons matter more than the
fixes: the fixes are specific to a crate, the reasons apply to anything.

The running technical log is `explorations/fold-notes.md`. This is the
distilled version.

## The short version

1. An animation of a real object is a claim about how that object works. If
   the claim is false, polish does not rescue it.
2. The resting state is sacred. Whatever the piece does when touched, it must
   start and end as the thing the viewer already knows.
3. Review frames, not impressions. Every defect Cameron caught was visible in
   a single still frame that had not been looked at.
4. Fix causes, not symptoms. Most of the corner, gap and flicker reports were
   one geometric contradiction surfacing in different places.
5. Never hide a modelling problem with opacity, a fade or a visibility
   switch. It reads as a glitch, because it is one.

## The feedback, and why

### 1. "I dont believe the collapse of the crate is well done"

> The sides typically unclick and then fold down. Lookup how the construction
> of these crates work in real-time.

The first animation squashed the icon vertically. It was smooth, well eased
and wrong. A folding crate does not get shorter; its walls unlatch and fold
inward onto the base.

**Why it matters.** The click exists to explain the one thing a still image
cannot: that this object folds. An animation that shows a different mechanism
teaches the viewer something untrue, and a designer's portfolio is judged on
exactly that kind of attention. Research the real thing before animating it.

### 2. "The shape of the folder does not change per how it is in real life"

> It seems like elements appear over the top, but doesn't accurately reflect
> real-world functionality.

The second attempt drew the folded panels as layers that appeared on top of
the icon.

**Why it matters.** Things appearing is not the same as things moving. If a
part is going to end up somewhere, the viewer has to see it travel there from
where it was. Overlays that fade or pop in break the sense that this is one
object.

### 3. "The folder icon which we created ... should be the default state"

> Currently it looks like we've rebuilt it.

In building a 3D version, the resting frame had drifted from the icon.

**Why it matters.** The icon is the product. The animation is a
demonstration of it. If the resting frame is a lookalike, the piece stops
being "my icon, which also folds" and becomes "a different thing that
resembles my icon". Build the resting state from the real artwork and treat
any difference as a defect.

### 4. "This is the front of the crate"

> When I click it, this front folds down backwards revealing that there is
> also sides and a back too.

This was the conceptual key. The icon is not a picture of a crate. It is the
front wall of one, seen straight on.

**Why it matters.** Once the flat artwork has a defined place in a 3D object,
every later decision has something to answer to. Without that, each fix is a
guess.

### 5. "There is a weird transition between each phase"

> It begins first at the background, the sides/back, then suddenly appears
> on the top.

CSS 3D sorts sibling planes by their centre point, so intersecting planes
swapped order mid-animation.

**Why it matters.** This was a limit of the tool, not a bug to tune away. The
right response was to change tools (to Three.js, with a real depth buffer)
rather than keep adjusting values. Know when the medium cannot do the job.

### 6. "Front, then back, then left side then right-side"

**Why it matters.** Order is part of the mechanism. On the real crate the end
walls carry the latches and must go first; the sides are free only once the
ends are down. A sequence chosen for visual rhythm alone would have been
wrong.

### 7. "The sides are not aligning to the look and feel of the crate"

> Like what it is for the front.

The sides and back were plainer than the front.

**Why it matters.** Detail has to be even. One carefully drawn face beside
three simple ones makes the simple ones look unfinished and the careful one
look pasted on. The back became the same moulding as the front, and the sides
were drawn in the same vocabulary.

### 8. "The corners are not connected"

> They need to be connected through the rounded edge like a real box.

Said several times, with screenshots, across several rounds.

**Why it matters.** Corners are where the eye checks whether something is
solid. A hairline gap at a corner tells the viewer these are separate sheets
arranged near each other. It took several rounds because each fix treated one
corner in one frame. The lesson is to check all four corners at every frame,
as a routine, before showing anything.

### 9. "The thickness of the object is not consistent"

Walls were zero-thickness planes.

**Why it matters.** A plane reads as paper at every angle except face on, and
a folded stack of planes has no layers. Thickness is what makes it plastic.

### 10. "The front and backs open up through the sides. This is physically impossible"

**Why it matters.** Interpenetration is the clearest tell of a fake. People
may not be able to say what is wrong, but they see that it is. If two parts
would collide in reality, the model has to be changed so they do not, not
timed so it is brief.

### 11. "There is no bottom?" and "no hinge in which each side is connected"

> Lookup the crates and deeply understand how each side looks, operates and
> connects with each other.

Walls were pivoting about lines in empty space.

**Why it matters.** A hinge needs something to be attached to. Without a base
with a rim for the walls to seat into, the walls read as floating panels no
matter how well they move.

### 12. "We also need latches ... it's a groove"

> You apply a bit of force to snap open the side and then gently place it
> down. Then the same for the back. Once the front and backs are done, the
> sides easily fold down.

**Why it matters.** This is the difference between motion and behaviour. One
easing curve per wall is motion. Squeeze, release, lower is what a hand does,
and it is what makes the piece feel observed rather than generated. Timing
should come from the physical action, in milliseconds, not from a curve
picked for smoothness.

### 13. "There is a flicker toward a different state ... there is transparency"

> This is poor. ... there is transparency here which makes it not realistic
> to a real-world depiction.

The base, back and sides were hidden at rest and faded in over the first
fifth of a second, and the base's rim rose in front of the front wall.

**Why it matters.** This one is worth understanding fully, because it was the
root of most of the earlier corner reports too.

A crate whose end walls fold between its side walls must be wider than its
end walls. But the icon is the end wall, and the resting frame had to be
exactly the icon. So the model was wider than the icon, and the extra width
had to be hidden at rest. Every workaround for that (hiding the base, fading
it in, moving the sides outboard) produced a visible artefact somewhere.

The fix was not a better fade. It was to read the icon differently:

- the icon's bottom band is the **base**, which never moves
- the strip at each edge of the icon is a **side wall seen end on**
- the front wall is what is left, and it is narrower than the icon

With that reading the model is exactly as wide as the icon, nothing needs
hiding, and no material is transparent at any point.

**The general rule.** When you are reaching for opacity to cover a
transition, the model is wrong. Go back and find the contradiction.

## How we should have worked

Cameron had to ask for frame-by-frame review more than once:

> you can't do frame by frame reviews and then stitch them together so you
> can interpret motion?

> go through it frame by frame to review all feedback I have given you and
> ensure these are actioned

**Why it matters.** Motion hides defects at full speed and the author stops
seeing them. Stills do not lie. The practice that finally worked:

- render named moments in milliseconds, not evenly spaced percentages, so the
  frames land on the beats that matter
- sample densely where things change fastest (six frames inside the first
  quarter second)
- crop and enlarge all four corners at every one of those moments
- keep a ledger of every piece of feedback and re-check all of it each round,
  not only the latest item
- check the harness itself: an early one rendered a viewport narrower than
  the canvas, so the right-hand corners were never in frame and every "all
  clear" from it was worthless

## What is still a compromise

Stated plainly so nobody rediscovers them as bugs:

- Above the side walls' tops the front wall keeps the icon's full width (the
  rounded top-right corner and the tab's left edge). Those two slivers pass
  inside the side walls' thickness during the fold.
- At rest the slots show the shaded inside of the crate, not the page behind
  it. The flat icon's slots are see-through; the 3D piece's are not.
- The latch tongue slides rather than flexes.
- The unfold is the fold played backwards.
- One colour (rust). Other colours need their textures generated.

## For the portfolio specifically

- The piece makes a claim about craft. Anything on the page around it that is
  approximate will be read against it.
- The poster shown before the scene loads is the flat icon. It must sit
  exactly where the canvas will, at the same size, or the swap is a jump.
- Keep the text label. Motion is never the only channel that reports state.
- Do not add a bounce, a spin or an entrance animation. The restraint is the
  point.
