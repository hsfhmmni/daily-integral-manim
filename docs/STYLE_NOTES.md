# Style notes: what makes a 3Blue1Brown-style integral video

Written in my own words after reading (not running) these files, which are kept read-only
in `Documents/_manim_references`:
`3b1b/videos`: `CLAUDE.md`, `_2023/gauss_int/integral.py`, `_2025/laplace/integration.py`,
`_2023/convolutions2/continuous.py`; `3b1b/manim`: `example_scenes.py`; Manim Community
`docs/source/examples.rst`.

His videos repository is licensed CC BY-NC-SA 4.0, and his library (ManimGL) differs from
Manim Community Edition (CE). Nothing below is copied: these are techniques, re-implemented
with CE 0.21.0 functions whose signatures were checked with `inspect` and against the
reference manual (docs.manim.community, v0.21.0). No pi creatures, logos, music or voice.

## Techniques

| # | What he does | Why it works | How we do it in CE 0.21 |
|---|---|---|---|
| 1 | **Picture before symbols.** The axes are already there, the curve is drawn, the region fills in, and only then is the integral written above it. | The viewer sees what is being measured before seeing notation. | `Create(curve)`, `FadeIn(area)`, then `Write(problem)`. Helper: `hook()` |
| 2 | **The label becomes the formula.** The curve's label morphs into the integrand inside the integral. | Ties a symbol to its picture. | `TransformFromCopy(label, integrand_part)` (not `FadeTransform`: in 0.21 it crashes when the two shapes have different numbers of pieces) |
| 3 | **Colour means something, and never changes.** The same symbol keeps the same colour in every equation (his `t2c` maps). | Your eye tracks a symbol through algebra without reading it. | `mt()` builds `MathTex` from parts and colours whole parts from one palette in `common.py` (curve BLUE, area GREEN, limits YELLOW, new variable ORANGE, traps RED). `set_color_by_tex` does not colour the visible parts in 0.21, so `mt()` colours `mob[i]` directly. |
| 4 | **Rectangles that get thinner.** The area is built from rectangles with thin white edges, then swapped for thinner ones again and again. | It makes "integral = limit of sums" visible. | `Axes.get_riemann_rectangles(..., input_sample_type="center")` inside `always_redraw`, driven by a `ValueTracker` for n. Helper: `riemann_rectangles()` |
| 5 | **Live numbers.** A value updates as a tracker moves. | The audience watches convergence instead of being told. | `DecimalNumber` + `add_updater`, showing the estimate and the gap to the answer. |
| 6 | **Flash around the symbol you mean.** A light sweeps around one sub-expression while the matching geometry is shown. | Pointing without words. | `Circumscribe(part, time_width=...)` (CE has no `FlashAround`), plus `SurroundingRectangle` that stays, plus a short `Arrow` and a two-to-four-word label. Helper: `highlight()` |
| 7 | **Equations morph, they do not get replaced.** Matching pieces glide into place; new pieces appear. Sometimes with a slight arc. | Shows exactly what changed between lines. | `TransformMatchingTex(old, new, transform_mismatches=True, path_arc=...)` (CE has no `TransformMatchingStrings`, and `key_map` crashes in 0.21, so unmatched pieces morph into each other). Helper: `morph_steps()` |
| 8 | **Keep the history.** Earlier lines shrink and dim instead of vanishing. | You can glance back at where you came from. | Copy of the old line `.animate.scale(...).set_opacity(0.35)` into a trail at the top-left. |
| 9 | **Stagger, don't dump.** Groups enter with a small lag between members. | Each part registers; nothing arrives as a wall. | `LaggedStart(..., lag_ratio=0.15)` / `FadeIn(group, lag_ratio=0.1)`; at most 3 new things per `play`. |
| 10 | **Hold the important moment.** After a key reveal there is a real pause. | Time to think replaces the narrator. | `wait(max(1.5, 0.4 * words))` per caption; at least 1.5 s on the insight. Helper: `caption()` |
| 11 | **The camera moves to make room or to focus.** He eases the frame in or out rather than shrinking everything. | Zooming says "look here". | `MovingCameraScene`; `self.camera.frame.animate.scale(0.6).move_to(target)`, then `Restore(frame)`. The badge follows the frame with an updater. |
| 12 | **Dim everything that is not the point.** Lowers the opacity of the rest while one piece is discussed. | Contrast directs attention. | `.animate.set_opacity(0.25)` on the rest, then back to 1. |
| 13 | **Legible labels over busy graphs.** A dark outline behind text drawn on top of curves. | Text never fights the picture. | `set_stroke(BLACK, width=6, background=True)` |
| 14 | **Faint grid, numbered axes.** A soft background grid under clear axis numbers. | Gives scale without noise. | `Axes` + `NumberLine.add_labels` for nice values (fractions, multiples of pi), with faint grid lines from `axes.c2p` at stroke opacity 0.15. Helper: `build_graph()` |
| 15 | **Gentle easing everywhere.** Smooth starts and stops; there-and-back for pulses. | Motion feels physical, not mechanical. | `rate_functions.smooth` (default), `there_and_back` for pulses, `ease_out_cubic` for trackers; run times of 1 to 2 s. |

## Rule Cards
Every rule, theorem, technique or identity a step uses is stated and explained on screen
before the step, even "basic" ones such as the power rule or linearity. A step names it with
`rule="key"` (or a list of keys; `rule="algebra"` for pure simplification) and gives
`mapping=[cap(r"...")]` lines (or `{key: [...]}`) saying how the rule applies to this
problem. Cards live in `rules.py` as `RULE_CARDS[key] = dict(name, statement, symbols, when,
why)`: `statement` is a MathTex string; `symbols`, `when` and `why` are lists of `cap()`
lines (12 words at most, maths in `$...$`). The `why` gives the actual reason, never just a
restatement.

On screen (`rule_cards()` / `show_rule_card()` in `common.py`): the working fades to 20%
(technique 12, dim everything that is not the point), a bordered box with a teal title
appears in the middle of the frame, and it reveals one beat at a time: name and statement,
then the symbols, when to use it, why it works, and the mapping. The first use in a video
gets the full card; later uses get a reminder (name, statement and the mapping). Teal is
outside the maths colour code, so cards never borrow a meaning from the equations.

## Hold times
Every caption and every card beat stays at least `read_time = max(2.0, words / 2.5)` s, with
each `$...$` block counting as 2 words. This replaces the old 0.4 s per word (technique 10).
`caption()` keeps it automatically and logs it; `check_frame.py` verifies every hold.
Length limits: Beginner 90-270 s, Easy 90-240 s, Medium 90-300 s.

## Watermark
`@d\_dxmercy` (Tex, size 24, white, 45% opacity) in the bottom-right corner, inside the safe
area. Added once by `add_watermark()` with `add_foreground_mobject`, it sits above every
animation and card, follows the camera like the badge, and is reserved in the frame guard so
nothing touches it. Captions sit just above it. `check_frame.py --frames` compares the
corner of a frame every 2 s with a reference crop. Clear the screen with
`clear_scene_keep_watermark()`.

## What we deliberately do not do
- No characters, no logos, no music and no voice. Captions carry the words (12 words at most each).
- No decoration: geometry or 3D only when it explains something (a reflection for symmetry,
  a hollow dot for a removable hole, a solid of revolution for a volume).
