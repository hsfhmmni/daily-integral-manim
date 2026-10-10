"""Shared helpers: turn a worked integral into an explained Manim video.

Every video follows the same story:
  1. Intro card (difficulty + date + the integral)
  2. "The big idea" - plain-language plan
  3. A graph with the area the integral measures shaded
  4. Step by step: WHAT we do, the maths, and WHY we do it
  5. Optional extra diagram (after_steps hook)
  6. The answer, boxed, with a sanity check against the graph
A small difficulty | date badge stays in the corner the whole time.

Two rules keep every video clean:
  * Sentences are drawn with rich(), never Text(). Write every piece of maths in
    $...$ with LaTeX commands: r"Let $u=\\sin(\\pi x)$, so $du=\\pi\\cos(\\pi x)\\,dx$."
  * Every group goes through fit_to_frame() / fit_below() before it is animated.
    A frame guard then checks the screen after every animation and stops the
    render if anything leaves the safe area, overlaps other text, or is too small.
"""
import re

import numpy as np
from manim import *

DIFFICULTY_COLORS = {
    "Beginner": GREEN,
    "Easy": BLUE,
    "Medium": ORANGE,
    "Hard": RED,
}

# ---------------------------------------------------------------- safe area
FRAME_HALF_W = config.frame_width / 2            # about 7.11
FRAME_HALF_H = config.frame_height / 2           # 4
SAFE_MARGIN = 0.4                                # gap kept from every frame edge
SAFE_LEFT, SAFE_RIGHT = -FRAME_HALF_W + SAFE_MARGIN, FRAME_HALF_W - SAFE_MARGIN
SAFE_BOTTOM, SAFE_TOP = -FRAME_HALF_H + SAFE_MARGIN, FRAME_HALF_H - SAFE_MARGIN
SAFE_WIDTH = SAFE_RIGHT - SAFE_LEFT

# Smallest font the guard accepts. Tex glyphs are about 0.69x the size of Text
# glyphs at the same font_size, so the two need different floors.
MIN_FONT_TEXT = 15
MIN_FONT_TEX = 22

# Sizes for rich() sentences (Tex font sizes, about 1.45x the old Text sizes).
WHAT_SIZE, WHY_SIZE, IDEA_SIZE, CHECK_SIZE = 42, 34, 36, 36


def _fit(mobject, max_width=SAFE_WIDTH):
    if mobject.width > max_width:
        mobject.scale_to_fit_width(max_width)
    return mobject


def fit_into(mobject, left, right, bottom, top, center=False):
    """Shrink (never enlarge) mobject to fit the box [left, right] x [bottom, top].

    With center=True it is then centred in the box; otherwise it only moves as far
    as needed to stop sticking out.
    """
    avail_w, avail_h = right - left, top - bottom
    if avail_w <= 0 or avail_h <= 0:
        raise ValueError(f"fit_into: empty box x=[{left:.2f},{right:.2f}] y=[{bottom:.2f},{top:.2f}]")
    scale = 1.0
    if mobject.width > avail_w:
        scale = avail_w / mobject.width
    if mobject.height * scale > avail_h:
        scale = avail_h / mobject.height
    if scale < 1:
        mobject.scale(scale)
    if center:
        return mobject.move_to([(left + right) / 2, (bottom + top) / 2, 0])
    dx = dy = 0.0
    if mobject.get_left()[0] < left:
        dx = left - mobject.get_left()[0]
    elif mobject.get_right()[0] > right:
        dx = right - mobject.get_right()[0]
    if mobject.get_top()[1] > top:
        dy = top - mobject.get_top()[1]
    elif mobject.get_bottom()[1] < bottom:
        dy = bottom - mobject.get_bottom()[1]
    return mobject.shift([dx, dy, 0])


def fit_to_frame(mobject, top_limit=SAFE_TOP):
    """Shrink (never enlarge) and shift mobject so it fits the safe area below top_limit.

    The safe area is the frame minus SAFE_MARGIN on every side; top_limit is usually
    just under the problem line so content stays clear of it and of the badge.
    """
    top = min(top_limit, SAFE_TOP)
    if top - SAFE_BOTTOM <= 0:
        raise ValueError(f"fit_to_frame: no room below y={top_limit:.2f}")
    return fit_into(mobject, SAFE_LEFT, SAFE_RIGHT, SAFE_BOTTOM, top)


def fit_below(mobject, anchor, buff=0.5):
    """Place mobject under anchor, then fit_to_frame it in the room that is left.

    Call this on every group before animating it, including in after_steps diagrams.
    """
    limit = anchor.get_bottom()[1] - buff
    mobject.next_to(anchor, DOWN, buff=buff)
    fit_to_frame(mobject, limit)
    mobject.next_to(anchor, DOWN, buff=buff)   # re-attach after shrinking
    return fit_to_frame(mobject, limit)


def fit_in_frame(mobject):
    """Shrink and shift a free-standing mobject so it sits inside the whole safe area."""
    return fit_to_frame(mobject, SAFE_TOP)


# ---------------------------------------------------------------- sentences
_TEX_UNITS_PER_CM_AT_48 = 1.41732                # measured: a 10cm rule is 14.17 units at font_size 48


def _escape_prose(s):
    """Escape LaTeX special characters that are meant literally in prose."""
    return re.sub(r"(?<!\\)([%&#_])", r"\\\1", s)


def rich(text, font_size=WHY_SIZE, width=11.5, color=WHITE):
    """A sentence with real maths: prose stays text, anything in $...$ is typeset by LaTeX.

    width is the line length in Manim units (the frame is about 14.2 wide); the paragraph
    wraps inside a LaTeX minipage of that width. Use raw strings: r"... $\\frac{\\pi}{2}$ ...".
    """
    parts = re.split(r"(?<!\\)\$", text)
    if len(parts) % 2 == 0:
        raise ValueError(f"rich(): unbalanced $ in {text!r}")
    body = "".join(f"${p}$" if i % 2 else _escape_prose(p) for i, p in enumerate(parts))
    cm = width / (_TEX_UNITS_PER_CM_AT_48 * font_size / 48)
    tex = Tex(r"\begin{minipage}{%.3fcm}\raggedright %s\end{minipage}" % (cm, body),
              font_size=font_size, color=color)
    return _fit(tex)


def _badge(difficulty, date_short):
    label = Text(f"{difficulty}  |  {date_short}", font_size=22, color=GREY_B)
    box = SurroundingRectangle(label, color=GREY_B, buff=0.12)
    return VGroup(box, label).to_corner(UR, buff=SAFE_MARGIN)


# ---------------------------------------------------------------- frame guard
TEXTY = (Text, MarkupText, SingleStringMathTex)  # SingleStringMathTex covers MathTex and Tex
GUARD_MODE = "raise"        # "raise" stops the render; "collect" records into GUARD_LOG
GUARD_LOG = []              # (section, animation number, message) when GUARD_MODE == "collect"
_TOL = 1e-3


class FrameGuardError(RuntimeError):
    pass


def _label(m):
    if isinstance(m, (Text, MarkupText)):
        return "Text " + repr(getattr(m, "original_text", m.text).replace("\n", " ")[:60])
    if isinstance(m, SingleStringMathTex):
        return "TeX " + repr(m.get_tex_string()[:60])
    return type(m).__name__


def _texty_leaves(m):
    if isinstance(m, TEXTY):
        yield m
        return
    for s in m.submobjects:
        yield from _texty_leaves(s)


def _has_points(m):
    return len(m.get_all_points()) > 0


def _visible(m):
    """False when every part of m is fully transparent (hidden on purpose)."""
    for s in m.get_family():
        if isinstance(s, VMobject) and len(s.points) and (s.get_fill_opacity() > 0.01 or s.get_stroke_opacity() > 0.01):
            return True
    return False


def _boxes_overlap(a, b, pad=0.0):
    return not (a.get_right()[0] + pad <= b.get_left()[0] or b.get_right()[0] + pad <= a.get_left()[0]
                or a.get_top()[1] + pad <= b.get_bottom()[1] or b.get_top()[1] + pad <= a.get_bottom()[1])


def _view(scene):
    """(left, right, bottom, top, zoom) of what the camera shows; zoom < 1 means zoomed in."""
    frame = getattr(getattr(scene, "camera", None), "frame", None)
    if frame is None:
        return -FRAME_HALF_W, FRAME_HALF_W, -FRAME_HALF_H, FRAME_HALF_H, 1.0
    c, w, h = frame.get_center(), frame.width, frame.height
    return c[0] - w / 2, c[0] + w / 2, c[1] - h / 2, c[1] + h / 2, w / config.frame_width


def frame_problems(scene):
    """Every layout problem on screen right now, as readable strings.

    Works with a moving camera: the safe area is the current view minus the margin.
    While zoomed in, text must be wholly inside the view or wholly outside it (cut-off
    text is the failure); camera-following HUD items (badge, captions) must stay inside.
    """
    out = []
    frame = getattr(getattr(scene, "camera", None), "frame", None)
    tops = [m for m in scene.mobjects
            if _has_points(m) and m is not frame and not isinstance(m, ValueTracker) and _visible(m)]
    reserved = [m for m in getattr(scene, "_guard_reserved", []) if m in tops]
    vl, vr, vb, vt, zoom = _view(scene)
    margin = SAFE_MARGIN * zoom
    sl, sr, sb, st = vl + margin, vr - margin, vb + margin, vt - margin
    zoomed = zoom < 0.999

    def in_view(m):
        return not (m.get_right()[0] < vl or m.get_left()[0] > vr
                    or m.get_top()[1] < vb or m.get_bottom()[1] > vt)

    for top in tops:
        hud = getattr(top, "_hud", False)
        items = list(_texty_leaves(top))
        if not isinstance(top, TEXTY):
            items.append(top)                    # diagrams, axes, boxes too
        for m in items:
            if not _has_points(m):
                continue
            texty = isinstance(m, TEXTY)
            if zoomed and not hud:
                if not texty or not in_view(m):
                    continue                     # off-view on purpose while zoomed
                if (m.get_left()[0] < vl - _TOL or m.get_right()[0] > vr + _TOL
                        or m.get_bottom()[1] < vb - _TOL or m.get_top()[1] > vt + _TOL):
                    out.append(f"{_label(m)} is cut off by the edge of the zoomed view")
                continue
            over = []
            if m.get_left()[0] < sl - _TOL:
                over.append(f"left by {sl - m.get_left()[0]:.2f}")
            if m.get_right()[0] > sr + _TOL:
                over.append(f"right by {m.get_right()[0] - sr:.2f}")
            if m.get_bottom()[1] < sb - _TOL:
                over.append(f"bottom by {sb - m.get_bottom()[1]:.2f}")
            if m.get_top()[1] > st + _TOL:
                over.append(f"top by {m.get_top()[1] - st:.2f}")
            if over:
                out.append(f"{_label(m)} crosses the safe area ({SAFE_MARGIN} from the edge): "
                           + ", ".join(over))
        for m in _texty_leaves(top):
            floor = MIN_FONT_TEXT if isinstance(m, (Text, MarkupText)) else MIN_FONT_TEX
            if _has_points(m) and _visible(m) and in_view(m) and m.font_size / zoom < floor - 0.5:
                out.append(f"{_label(m)} is too small to read: font {m.font_size / zoom:.0f} on screen "
                           f"< {floor} (the group was shrunk to fit; shorten the wording)")

    for i, A in enumerate(tops):
        for B in tops[i + 1:]:
            for a in _texty_leaves(A):
                for b in _texty_leaves(B):
                    if (_has_points(a) and _has_points(b) and _visible(a) and _visible(b)
                            and in_view(a) and in_view(b) and _boxes_overlap(a, b)):
                        out.append(f"{_label(a)} overlaps {_label(b)}")

    for r in reserved:                            # badge and problem line: nothing may touch them
        for t in tops:
            if t is r or (t in reserved and tops.index(t) < tops.index(r)):
                continue
            if _boxes_overlap(r, t, pad=0.05):
                out.append(f"{_label(t) if not isinstance(t, VGroup) else type(t).__name__} "
                           f"touches the reserved {_label(list(_texty_leaves(r))[0])}")
    return out


def install_frame_guard(scene):
    """Wrap scene.play and scene.wait so the screen is checked after every animation."""
    if isinstance(scene, ThreeDScene) or getattr(scene, "_guard_installed", False):
        return                                    # 3D camera projection makes 2D bounds meaningless
    scene._guard_installed = True
    scene._guard_section = "Intro"
    scene._guard_count = 0
    orig_play, orig_wait = scene.play, scene.wait

    def check(kind):
        scene._guard_count += 1
        for msg in frame_problems(scene):
            where = f"[{scene._guard_section}] after animation #{scene._guard_count} ({kind})"
            if GUARD_MODE == "raise":
                raise FrameGuardError(f"Frame guard: {where}: {msg}")
            GUARD_LOG.append((scene._guard_section, scene._guard_count, msg))

    def play(*args, **kwargs):
        orig_play(*args, **kwargs)
        check("play")

    def wait(*args, **kwargs):
        orig_wait(*args, **kwargs)
        check("wait")

    scene.play, scene.wait = play, wait


# ---------------------------------------------------------------- the story
def _intro(scene, difficulty, date_long, problem_tex):
    colour = DIFFICULTY_COLORS.get(difficulty, WHITE)
    diff = Text(f"{difficulty} Integral", font_size=64, color=colour)
    date = Text(date_long, font_size=32, color=GREY_B)
    prob = _fit(MathTex(problem_tex).scale(1.2), 12)
    group = fit_in_frame(VGroup(diff, date, prob).arrange(DOWN, buff=0.6))
    scene.play(FadeIn(diff), FadeIn(date))
    scene.play(Write(prob))
    scene.wait(2)
    scene.play(FadeOut(group))


def _show_graph(scene, anchor, g, pause):
    """Plot the integrand and shade the area between the limits.

    g keys: func, x_range, y_range, plot_range, a, b, a_label, b_label, caption,
            optional size=(x_length, y_length), optional marker=(x, y).
    The caption is a rich() sentence: put maths in $...$.
    """
    x_len, y_len = g.get("size", (8, 3.6))
    axes = Axes(x_range=g["x_range"], y_range=g["y_range"],
                x_length=x_len, y_length=y_len, tips=False)
    axes.next_to(anchor, DOWN, buff=0.5)
    curve = axes.plot(g["func"], x_range=g["plot_range"], color=BLUE)
    area = axes.get_area(curve, x_range=(g["a"], g["b"]), color=GREEN, opacity=0.5)
    a_lab = _fit(MathTex(g["a_label"]).scale(0.7)).next_to(axes.c2p(g["a"], 0), DOWN, buff=0.15)
    b_lab = _fit(MathTex(g["b_label"]).scale(0.7)).next_to(axes.c2p(g["b"], 0), DOWN, buff=0.15)
    caption = rich(g["caption"], font_size=WHY_SIZE, width=12)
    caption.next_to(axes, DOWN, buff=0.7)
    pieces = [axes, curve, area, a_lab, b_lab, caption]
    ring = None
    if "marker" in g:
        mx, my = g["marker"]
        ring = Circle(radius=0.1, color=RED, stroke_width=4).move_to(axes.c2p(mx, my))
        pieces.append(ring)
    # Graph + labels + caption move and shrink together so the caption cannot fall off.
    fit_below(VGroup(*pieces), anchor, buff=0.5)

    scene.play(Create(axes), run_time=1.5)
    scene.play(Create(curve), run_time=2)
    scene.play(FadeIn(area), FadeIn(a_lab), FadeIn(b_lab))
    if ring is not None:
        scene.play(Create(ring))
    scene.play(FadeIn(caption))
    scene.wait(pause + 2)
    scene.play(FadeOut(VGroup(*pieces)))


def solve(scene, difficulty, date_long, date_short, problem_tex, idea, steps,
          answer_tex, check, graph=None, after_steps=None, pause=3.0):
    """Animate a full explained solution.

    idea, check -- rich() sentences (maths in $...$)
    steps       -- list of (what_we_do, why_we_do_it, latex) triples; what and why
                   are rich() sentences, latex is a MathTex string
    answer_tex  -- LaTeX of the final value (no leading '=')
    graph       -- dict for _show_graph, or None
    after_steps -- optional function(scene, anchor) that draws an extra diagram
                   and returns the mobject to fade out afterwards; place the
                   diagram with fit_below(layout, anchor) before animating it
    """
    install_frame_guard(scene)
    _intro(scene, difficulty, date_long, problem_tex)

    badge = _badge(difficulty, date_short)
    problem = MathTex(problem_tex).scale(0.9)
    # Keep the problem line clear of the corner badge: centred, so it may reach
    # at most to just left of the badge on both sides.
    _fit(problem, min(9, 2 * (badge.get_left()[0] - 0.25)))
    problem.to_edge(UP, buff=0.8)
    scene._guard_reserved = [badge, problem]
    scene._guard_section = "Problem line"
    scene.play(FadeIn(badge), Write(problem))

    # 1. The big idea
    scene._guard_section = "Big idea"
    idea_title = Text("The big idea", font_size=30, color=YELLOW)
    idea_body = rich(idea, font_size=IDEA_SIZE, width=10.5)
    idea_group = VGroup(idea_title, idea_body).arrange(DOWN, buff=0.4)
    fit_below(idea_group, problem, buff=1.0)
    scene.play(FadeIn(idea_title))
    scene.play(FadeIn(idea_body))
    scene.wait(pause + 2)
    scene.play(FadeOut(idea_group))

    # 2. What the integral means, as a picture
    if graph is not None:
        scene._guard_section = "Graph"
        _show_graph(scene, problem, graph, pause)

    # 3. Step by step, with reasons
    previous = None
    for i, (what, why, tex) in enumerate(steps, 1):
        scene._guard_section = f"Step {i}"
        what_t = rich(what, font_size=WHAT_SIZE, width=12, color=YELLOW)
        eq = _fit(MathTex(tex), 12)
        why_t = rich(why, font_size=WHY_SIZE, width=11.5)
        group = VGroup(what_t, eq, why_t).arrange(DOWN, buff=0.45)
        fit_below(group, problem, buff=0.8)
        if previous is None:
            scene.play(FadeIn(what_t), Write(eq))
        else:
            scene.play(FadeOut(previous), FadeIn(what_t), Write(eq))
        scene.play(FadeIn(why_t))
        scene.wait(pause)
        previous = group

    # 4. Optional extra diagram
    if previous is not None:
        scene.play(FadeOut(previous))
        previous = None
    if after_steps is not None:
        scene._guard_section = "Extra diagram"
        extra = after_steps(scene, problem)
        scene.wait(pause + 2)
        scene.play(FadeOut(extra))

    # 5. Answer and sanity check
    scene._guard_section = "Answer"
    final = _fit(MathTex(r"\text{Answer}\;=\;" + answer_tex, color=GREEN).scale(1.4), 12)
    box = SurroundingRectangle(final, color=GREEN, buff=0.25)
    check_t = rich("Sanity check: " + check, font_size=CHECK_SIZE, width=10.5, color=YELLOW)
    check_t.next_to(box, DOWN, buff=0.7)
    fit_below(VGroup(final, box, check_t), problem, buff=1.0)
    scene.play(Write(final))
    scene.play(Create(box))
    scene.play(FadeIn(check_t))
    scene.wait(5)


def revolve_about_x_axis(scene3d, func, x_min, x_max):
    """For a ThreeDScene: spin y = f(x) about the x-axis to show a solid of revolution.

    Use this when an integral is secretly a volume (pi * integral of f(x)^2 dx).
    """
    scene3d.set_camera_orientation(phi=65 * DEGREES, theta=-50 * DEGREES)
    axes = ThreeDAxes()
    curve = ParametricFunction(lambda t: np.array([t, func(t), 0]),
                               t_range=[x_min, x_max], color=BLUE)
    surface = Surface(
        lambda u, v: np.array([u, func(u) * np.cos(v), func(u) * np.sin(v)]),
        u_range=[x_min, x_max], v_range=[0, TAU], resolution=(24, 24), fill_opacity=0.6,
    )
    scene3d.play(Create(axes))
    scene3d.play(Create(curve))
    scene3d.begin_ambient_camera_rotation(rate=0.2)
    scene3d.play(Create(surface), run_time=4)
    scene3d.wait(4)
    scene3d.stop_ambient_camera_rotation()


# =====================================================================================
# 3Blue1Brown-style story pipeline (used by scripts from 2026-10-08 on).
# A day's script subclasses IntegralVideo and fills in data; see README.md and
# STYLE_NOTES.md. Every helper below has a tiny test scene in test_helpers.py.
# =====================================================================================
import datetime as _dt
import os as _os
import sys as _sys
from types import SimpleNamespace

# ---- colour code: one meaning per colour, the same in every video
CURVE_COLOR = BLUE          # the integrand's graph
AREA_COLOR = GREEN          # the area / anything that equals the answer
LIMIT_COLOR = YELLOW        # limits of integration
NEW_VAR_COLOR = ORANGE      # the new variable in a substitution (and the part that becomes it)
TRAP_COLOR = RED            # traps: holes, divisions by zero, invalid steps
LIMIT, NEW, TRAP = LIMIT_COLOR, NEW_VAR_COLOR, TRAP_COLOR      # short names for day data
AREA_OPACITY = 0.45
DIM_OPACITY = 0.35
BACKGROUND = "#0b0d12"      # near-black

# ---- pacing
CAPTION_MAX_WORDS = 12
SECONDS_PER_WORD = 0.4
MIN_HOLD = 1.5
CAPTION_SIZE = 38
TARGET_LENGTH = (90, 180)   # seconds

# ---- layout zones (scene units, unzoomed camera)
CAPTION_TOP = -2.45                         # captions live below this line
PROBLEM_SLOT = np.array([0.0, SAFE_TOP - 0.5, 0.0])
STAGE = (SAFE_LEFT, SAFE_RIGHT, CAPTION_TOP + 0.1, 1.05)     # current equation area (below trail)
GRAPH_BOX = (SAFE_LEFT, 3.0, CAPTION_TOP + 0.1, 2.55)        # graph area while the problem is on top
READOUT_BOX = (3.25, SAFE_RIGHT, CAPTION_TOP + 0.1, 2.55)    # live numbers beside the graph


def cap(text):
    """Mark an on-screen sentence (maths in $...$, at most 12 words).

    It returns the text unchanged; the marker lets check_text.py find every caption.
    """
    return text


class Eq(tuple):
    """An equation as a tuple of parts: "tex" or ("tex", COLOUR). Built into MathTex by mt()."""


def eq(*parts):
    """Write an equation as separate parts so TransformMatchingTex can match them.

    Example: eq(r"\\int_{", ("-1", LIMIT), "}^{", ("1", LIMIT), "}", r"\\cos^{-1}(", "u", ")")
    A part that is a tuple carries its own colour; other parts take colours from the
    scene's COLORS map (exact match), e.g. COLORS = {"u": NEW}.
    """
    return Eq(parts)


def mt(spec, colors=None, **kwargs):
    """Build MathTex from an eq() spec and colour whole parts.

    MathTex.set_color_by_tex does not recolour the visible parts in Manim 0.21, so each
    part is coloured directly; MathTex makes exactly one part per argument.
    """
    strings = [p[0] if isinstance(p, tuple) else p for p in spec]
    mob = MathTex(*strings, **kwargs)
    colors = colors or {}
    for part, p in zip(mob.submobjects, spec):
        colour = p[1] if isinstance(p, tuple) else colors.get(p)
        if colour is not None:
            part.set_color(colour)
    return mob


def parts_of(mob, *texs):
    """VGroup of the parts of mob whose tex string is one of texs (every occurrence)."""
    return VGroup(*[p for p in mob.submobjects if getattr(p, "tex_string", None) in texs])


def caption_words(text):
    """Words in a caption; each $...$ maths chunk counts as one word."""
    tokens = re.sub(r"(?<!\\)\$[^$]*\$", " M ", text).split()
    return sum(1 for t in tokens if re.search(r"\w", t))       # lone punctuation is not a word


def hold_time(text):
    """How long a caption stays: 0.4 s per word, at least 1.5 s."""
    return max(MIN_HOLD, SECONDS_PER_WORD * caption_words(text))


class CaptionTooLong(ValueError):
    pass


def mark(scene, name, offset=0.0):
    """Record a key moment (for frame extraction): now + offset seconds."""
    scene._keyframes.append((round(scene.renderer.time + offset, 2), name))


# ---- HUD: things that stay put on screen even when the camera moves
def attach_hud(scene, mob):
    """Pin mob to the screen: laid out as if the camera were unzoomed at the origin,
    it then follows camera.frame (position and scale). Used for the badge and captions."""
    mob._hud = True
    frame = getattr(scene.camera, "frame", None)
    if frame is None:
        return mob
    mob._hud_offset = mob.get_center().copy()
    mob._hud_width = mob.width

    def follow(m):
        z = frame.width / config.frame_width
        if m._hud_width > 0:
            m.scale_to_fit_width(m._hud_width * z)
        m.move_to(frame.get_center() + m._hud_offset * z)

    mob.add_updater(follow)
    follow(mob)
    return mob


def make_badge(scene, difficulty, date_short):
    """Small low-opacity 'Difficulty | date' badge in the top-right corner, all video long."""
    label = Text(f"{difficulty}  |  {date_short}", font_size=20, color=GREY_B)
    label.set_opacity(0.7)
    box = SurroundingRectangle(label, color=GREY_B, buff=0.1, stroke_width=1.5)
    box.set_stroke(opacity=0.5)
    badge = VGroup(box, label).to_corner(UR, buff=SAFE_MARGIN + 0.05)
    return attach_hud(scene, badge)


def caption(scene, text, color=WHITE, wait=True, key=None):
    """Show one caption at the bottom of the screen, replacing the previous one.

    Raises CaptionTooLong above 12 words. Holds 0.4 s per word (min 1.5 s) and
    records the sentence for the narration script. key: name a key moment just after
    the caption appears (for frame extraction).
    """
    words = caption_words(text)
    if words > CAPTION_MAX_WORDS:
        raise CaptionTooLong(f"caption has {words} words (max {CAPTION_MAX_WORDS}): {text!r}")
    new = rich(text, font_size=CAPTION_SIZE, width=12.4, color=color)
    new.set_stroke(BACKGROUND, width=6, background=True)
    fit_into(new, SAFE_LEFT, SAFE_RIGHT, SAFE_BOTTOM, CAPTION_TOP)
    new.move_to([0, (SAFE_BOTTOM + CAPTION_TOP) / 2, 0])
    attach_hud(scene, new)
    old = getattr(scene, "_caption", None)
    anims = [FadeIn(new, shift=0.15 * UP)]
    if old is not None:
        anims.insert(0, FadeOut(old, shift=0.15 * UP))
    scene.play(*anims, run_time=0.8)
    scene._caption = new
    scene._narration.append(text)
    if key:
        mark(scene, key, offset=0.3)
    if wait:
        scene.wait(hold_time(text))
    return new


def clear_caption(scene):
    """Fade out the current caption, if any."""
    old = getattr(scene, "_caption", None)
    if old is not None:
        scene.play(FadeOut(old), run_time=0.5)
        scene._caption = None


def intro_card(scene, difficulty, date_long, problem_spec, colors=None):
    """2-second title card: difficulty, full date and the integral."""
    title = Text(f"{difficulty} Integral", font_size=60, color=DIFFICULTY_COLORS.get(difficulty, WHITE))
    date = Text(date_long, font_size=30, color=GREY_B)
    prob = mt(problem_spec, colors).scale(1.1)
    group = fit_in_frame(VGroup(title, date, prob).arrange(DOWN, buff=0.5))
    scene.play(LaggedStart(FadeIn(title, shift=0.2 * UP), FadeIn(date), FadeIn(prob),
                           lag_ratio=0.25), run_time=1.0)
    scene.wait(1.0)
    scene.play(FadeOut(group), run_time=0.5)


# ---- graphs
def build_graph(g, func, box=GRAPH_BOX):
    """Axes with numbered ticks, a faint grid, the curve (BLUE) and the area (GREEN).

    g keys: x_range, y_range ([min, max, step]), a, b, optional size=(w, h),
    plot_range, x_labels / y_labels ({value: tex}), var ("x"), hole=(x, y),
    curve_color. Limit labels at a and b are YELLOW. Returns a SimpleNamespace with
    axes, grid, curve, area, hole, var_label and group (everything), fitted into box.
    """
    x_min, x_max, x_step = g["x_range"]
    y_min, y_max, y_step = g["y_range"]
    w, h = g.get("size", (8.5, 4.2))
    axes = Axes(x_range=g["x_range"], y_range=g["y_range"], x_length=w, y_length=h, tips=False,
                axis_config={"stroke_color": GREY_A, "stroke_width": 2})
    x_labels = g.get("x_labels") or {v: f"{v:g}" for v in np.arange(x_min, x_max + 1e-9, x_step) if abs(v) > 1e-9}
    y_labels = g.get("y_labels") or {v: f"{v:g}" for v in np.arange(y_min, y_max + 1e-9, y_step) if abs(v) > 1e-9}
    # add_labels turns *strings* into text-mode Tex even with label_constructor=MathTex (0.21),
    # so pass ready-made MathTex objects.
    axes.x_axis.add_labels({v: MathTex(t, font_size=32) for v, t in x_labels.items()}, font_size=32)
    axes.y_axis.add_labels({v: MathTex(t, font_size=32) for v, t in y_labels.items()}, font_size=32)
    for value, label in zip(x_labels, axes.x_axis.labels):
        if g.get("color_limits", True) and any(abs(value - lim) < 1e-9 for lim in (g["a"], g["b"])):
            label.set_color(LIMIT_COLOR)
        if y_min < 0:                     # axis in the middle: put the number on the side away from the curve
            below = float(func(value)) >= 0
            label.next_to(axes.c2p(value, 0), DOWN if below else UP, buff=0.15)
    xs = np.arange(x_min, x_max + 1e-9, x_step)
    ys = np.arange(y_min, y_max + 1e-9, y_step)
    grid = VGroup(*[Line(axes.c2p(x, y_min), axes.c2p(x, y_max)) for x in xs],
                  *[Line(axes.c2p(x_min, y), axes.c2p(x_max, y)) for y in ys])
    grid.set_stroke(GREY_B, width=1, opacity=0.18)
    lo, hi = g.get("plot_range", (g["a"], g["b"]))
    curve = axes.plot(func, x_range=[lo, hi, (hi - lo) / 600], color=g.get("curve_color", CURVE_COLOR),
                      stroke_width=4)
    top_y, bottom_y = axes.c2p(x_min, y_max)[1], axes.c2p(x_min, y_min)[1]
    if curve.get_top()[1] > top_y + 0.05 or curve.get_bottom()[1] < bottom_y - 0.05:
        raise ValueError(f"build_graph: the curve leaves y_range {g['y_range']} on plot_range "
                         f"{(lo, hi)}; widen y_range or narrow plot_range")
    area = axes.get_area(curve, x_range=(g["a"], g["b"]), color=AREA_COLOR, opacity=AREA_OPACITY)
    var = g.get("var", "x")
    var_label = MathTex(var, font_size=34, color=NEW_VAR_COLOR if var != "x" else GREY_A)
    var_label.next_to(axes.x_axis.get_end(), RIGHT, buff=0.2)
    parts = [grid, axes, area, curve, var_label]
    hole = None
    if "hole" in g:
        hole = Circle(radius=0.09).set_stroke(TRAP_COLOR, 3).set_fill(BACKGROUND, 1)
        hole.move_to(axes.c2p(*g["hole"]))
        parts.append(hole)
    group = VGroup(*parts)
    fit_into(group, *box, center=True)
    return SimpleNamespace(axes=axes, grid=grid, curve=curve, area=area, hole=hole,
                           var_label=var_label, group=group, spec=g, func=func)


def draw_graph(scene, gr, label=None):
    """Animate a built graph: grid and axes, then the curve, then the shaded area."""
    scene.play(FadeIn(gr.grid), Create(gr.axes, lag_ratio=0.02), FadeIn(gr.var_label), run_time=1.5)
    scene.play(Create(gr.curve), *([FadeIn(label, shift=0.1 * UP)] if label is not None else []),
               run_time=1.5)
    scene.play(FadeIn(gr.area), *([GrowFromCenter(gr.hole)] if gr.hole is not None else []), run_time=1.0)


def midpoint_sum(func, a, b, n):
    """Midpoint Riemann sum with n rectangles (the number the video shows)."""
    xs = a + (np.arange(n) + 0.5) * (b - a) / n
    return float(np.sum(np.vectorize(func, otypes=[float])(xs)) * (b - a) / n)


def _readout(rows, box=READOUT_BOX):
    """Rows of (label tex, number mobject) stacked in the readout column."""
    group = VGroup()
    for tex, number in rows:
        label = MathTex(tex, font_size=34)
        number.next_to(label, RIGHT, buff=0.15)
        group.add(VGroup(label, number))
    group.arrange(DOWN, aligned_edge=LEFT, buff=0.35)
    fit_into(group, *box, center=True)
    for label, number in group:
        number.add_updater(lambda m, l=label: m.next_to(l, RIGHT, buff=0.15))
    return group


def riemann_rectangles(scene, gr, a, b, true_value, counts=(4, 8, 16, 32, 64), keyframes=(0, 2, 4)):
    """Rectangles that get thinner (ValueTracker for n), with a live estimate and gap.

    Uses midpoint rectangles from Axes.get_riemann_rectangles inside always_redraw, and
    DecimalNumber updaters. Leaves rectangles and readout on screen; returns
    (rects, readout, tracker, final_estimate).
    """
    n = ValueTracker(counts[0])

    def count():
        return max(1, int(round(n.get_value())))

    def make_rects():
        k = count()
        dx = (b - a) / k
        return gr.axes.get_riemann_rectangles(gr.curve, x_range=[a, b - dx / 2], dx=dx,
                                              input_sample_type="center", stroke_width=1,
                                              stroke_color=WHITE, fill_opacity=0.6,
                                              color=AREA_COLOR, show_signed_area=False)

    rects = always_redraw(make_rects)
    n_num = Integer(counts[0], font_size=34, group_with_commas=False)
    est = DecimalNumber(midpoint_sum(gr.func, a, b, counts[0]), num_decimal_places=4, font_size=34)
    gap = DecimalNumber(abs(midpoint_sum(gr.func, a, b, counts[0]) - true_value), num_decimal_places=4,
                        font_size=34, color=TRAP_COLOR)
    readout = _readout([(r"n=", n_num), (r"\text{estimate}\approx", est), (r"\text{gap}=", gap)])
    n_num.add_updater(lambda m: m.set_value(count()))
    est.add_updater(lambda m: m.set_value(midpoint_sum(gr.func, a, b, count())))
    gap.add_updater(lambda m: m.set_value(abs(midpoint_sum(gr.func, a, b, count()) - true_value)))
    scene.play(FadeOut(gr.area), FadeIn(rects, lag_ratio=0.1), FadeIn(readout, lag_ratio=0.2), run_time=1.5)
    if 0 in keyframes:
        mark(scene, f"rectangles n={counts[0]}")
    scene.wait(1.0)
    for i, k in enumerate(counts[1:], 1):
        scene.play(n.animate.set_value(k), run_time=1.5, rate_func=smooth)
        if i in keyframes:
            mark(scene, f"rectangles n={k}")
        scene.wait(0.6)
    return rects, readout, n, midpoint_sum(gr.func, a, b, counts[-1])


# ---- emphasis
def highlight(scene, target, label, side=DOWN, zoom=True, color=YELLOW, hold=2.0, context=None):
    """Point at the key idea: Circumscribe it, keep a box, add a short arrow with a
    label, zoom the camera onto it (MovingCameraScene) and hold at least 1.5 s.

    context: the whole object target belongs to (e.g. the full equation); the zoom
    keeps all of it in view so nothing is cut off. Returns the box+arrow+label group;
    call unzoom(scene) afterwards if zoomed.
    """
    box = SurroundingRectangle(target, color=color, buff=0.1, stroke_width=3)
    lab = rich(label, font_size=34, width=5.5, color=color)
    lab.set_stroke(BACKGROUND, width=6, background=True)
    lab.next_to(box, side, buff=0.8)
    arrow = Arrow(lab.get_edge_center(-side), box.get_edge_center(side), buff=0.1, color=color,
                  stroke_width=4, max_tip_length_to_length_ratio=0.35)
    extra = VGroup(box, arrow, lab)
    scene.play(Circumscribe(target, color=color, time_width=0.6, run_time=1.2))
    anims = [Create(box), GrowArrow(arrow), FadeIn(lab, shift=-0.2 * side)]
    frame = getattr(scene.camera, "frame", None)
    if zoom and frame is not None:
        focus = VGroup(context if context is not None else target, extra)
        band = (CAPTION_TOP - SAFE_BOTTOM) + 0.3            # keep focus above the caption band
        z = max(0.55, min(1.0, max((focus.width + 2 * SAFE_MARGIN + 0.6) / config.frame_width,
                                   (focus.height + band + 2 * SAFE_MARGIN + 0.6) / config.frame_height)))
        frame.save_state()
        scene._zoomed = True
        anims.append(frame.animate.scale(z).move_to(focus.get_center() + DOWN * band * z / 2))
    mark(scene, "insight", offset=1.5)
    scene.play(*anims, run_time=1.5)
    scene.wait(max(MIN_HOLD, hold))
    return extra


def unzoom(scene, *anims):
    """Ease the camera back to the full view (after highlight(zoom=True))."""
    if getattr(scene, "_zoomed", False):
        scene.play(Restore(scene.camera.frame), *anims, run_time=1.2)
        scene._zoomed = False
    elif anims:
        scene.play(*anims, run_time=1.0)


# ---- the method: morphing lines with a dimmed trail
class Trail:
    """Earlier lines, shrunk and dimmed, stacked at the top-left (newest at the bottom)."""
    MAX_LINES, FONT, MAX_WIDTH, BUFF = 4, 26, 6.2, 0.12

    def __init__(self):
        self.lines = []
        self.planned_bottom = SAFE_TOP

    def push(self, scene, line):
        """Animations that move a dimmed copy of line into the trail (oldest drops off)."""
        ghost = line.copy()
        ghost.generate_target()
        # a fixed on-screen size, whatever scaling the line went through before
        ghost.target.scale(self.FONT / ghost.target.font_size).set_opacity(DIM_OPACITY)
        if ghost.target.width > self.MAX_WIDTH:
            ghost.target.scale_to_fit_width(self.MAX_WIDTH)
        anims = []
        lines = self.lines + [ghost]
        if len(lines) > self.MAX_LINES:
            anims.append(FadeOut(lines[0]))
            lines = lines[1:]
        targets = [ghost.target if l is ghost else l.copy() for l in lines]
        col = VGroup(*targets).arrange(DOWN, aligned_edge=LEFT, buff=self.BUFF).to_corner(UL, buff=SAFE_MARGIN + 0.05)
        self.planned_bottom = col.get_bottom()[1]
        for l, t in zip(lines, targets):
            anims.append(MoveToTarget(ghost) if l is ghost else l.animate.move_to(t))
        self.lines = lines
        return anims

    def bottom(self):
        return self.planned_bottom if self.lines else SAFE_TOP

    def fade(self):
        return [FadeOut(l) for l in self.lines]


def place_on_stage(mob, trail=None):
    """Put the current equation in the stage area under the trail, shrinking if needed."""
    top = STAGE[3] if trail is None else min(STAGE[3], trail.bottom() - 0.25)
    top = max(top, STAGE[2] + 1.0)
    return fit_into(mob, STAGE[0], STAGE[1], STAGE[2], top, center=True)


def morph_to(scene, current, new_spec, colors, trail, run_time=1.5, name=None):
    """Morph the current line into the next in place (TransformMatchingTex) while a
    dimmed copy slides into the trail. Returns the new line."""
    new = mt(new_spec, colors)
    trail_anims = trail.push(scene, current)
    place_on_stage(new, trail)
    if name:
        mark(scene, name, offset=run_time / 2)
    # matching parts glide; parts that change fade out/in (transform_mismatches=True turns
    # them into unreadable glyph soup mid-morph, seen in review round 1)
    scene.play(TransformMatchingTex(current, new, path_arc=-15 * DEGREES), *trail_anims, run_time=run_time)
    return new


def morph_steps(scene, current, steps, colors, trail, hooks=None):
    """Walk through the method: each step morphs the line and shows its caption.

    steps: list of dicts {tex: eq(...), say: cap(...), optional highlight: ([tex parts], cap(label)),
    optional then: name of a hook in `hooks` (a function(scene, current) -> None)}.
    """
    hooks = hooks or {}
    for i, step in enumerate(steps, 1):
        scene._guard_section = f"Step {i}"
        current = morph_to(scene, current, step["tex"], colors, trail,
                           name=f"mid-morph {i}" if i <= 2 else None)
        if "highlight" in step:
            texs, label = step["highlight"]
            extra = highlight(scene, parts_of(current, *texs), label, side=step.get("side", DOWN),
                              zoom=False, hold=0.5)
            caption(scene, step["say"])
            scene.play(FadeOut(extra), run_time=0.6)
        else:
            caption(scene, step["say"])
        if step.get("then"):
            hooks[step["then"]](scene, current)
    return current


# ---- substitution: same area, the axis re-labels
def substitution_view(scene, current, trail, x_graph, x_func, u_graph, u_func, area_value, says):
    """Show that a substitution keeps the area: the x-graph morphs into the u-graph,
    the axis relabels from x to u (ORANGE), and the area readout never changes.

    says: two captions (before and after the morph).
    """
    scene._guard_section = "Substitution view"
    current.save_state()
    small = current.copy().scale(0.62)
    fit_into(small, -0.3, SAFE_RIGHT, 1.3, SAFE_TOP - 0.75, center=True)
    top = min(small.get_bottom()[1], trail.bottom()) - 0.3
    box = (SAFE_LEFT, 3.0, CAPTION_TOP + 0.1, top)
    gx, gu = build_graph(x_graph, x_func, box), build_graph(u_graph, u_func, box)
    value = DecimalNumber(area_value, num_decimal_places=3, font_size=36, color=AREA_COLOR)
    readout = _readout([(r"\text{area}\approx", value)], box=(3.25, SAFE_RIGHT, CAPTION_TOP + 0.1, top))
    scene.play(Transform(current, small), run_time=1.0)
    draw_graph(scene, gx)
    scene.play(FadeIn(readout, shift=0.1 * UP), run_time=0.8)
    caption(scene, says[0], key="substitution: x view")
    scene.play(ReplacementTransform(gx.grid, gu.grid), ReplacementTransform(gx.axes, gu.axes),
               ReplacementTransform(gx.var_label, gu.var_label), run_time=1.5)
    scene.play(ReplacementTransform(gx.curve, gu.curve), ReplacementTransform(gx.area, gu.area), run_time=1.5)
    scene.play(Indicate(value, color=AREA_COLOR), run_time=1.0)
    caption(scene, says[1], key="substitution: u view")
    scene.play(FadeOut(gu.group), FadeOut(readout), Restore(current), run_time=1.2)


# ---- symmetry pictures
def reflection_view(scene, spec, func, mode, says, box=None):
    """A reflection that explains a symmetry step.

    mode="point":  odd function; the left piece of area spins 180 degrees about the origin
                   onto the right piece, showing they cancel.
    mode="mirror": a curve and its mirror image in the y-axis add to a constant
                   (spec["sum"], drawn dashed).
    says: two captions. Everything fades out at the end.
    """
    scene._guard_section = "Reflection"
    lo, hi = spec["x_range"][0], spec["x_range"][1]
    g = dict(spec)
    g.setdefault("a", lo)
    g.setdefault("b", hi)
    g.setdefault("plot_range", (lo, hi))
    gr = build_graph(g, func, box or (SAFE_LEFT, SAFE_RIGHT, CAPTION_TOP + 0.1, 1.0))
    scene.play(FadeIn(gr.grid), Create(gr.axes, lag_ratio=0.02), FadeIn(gr.var_label), run_time=1.2)
    scene.play(Create(gr.curve), run_time=1.2)
    origin = gr.axes.c2p(0, 0)
    if mode == "point":
        left = gr.axes.get_area(gr.curve, x_range=(lo, 0), color=GREY_B, opacity=0.5)   # negative area
        right = gr.axes.get_area(gr.curve, x_range=(0, hi), color=AREA_COLOR, opacity=0.5)
        scene.play(FadeIn(left), FadeIn(right), run_time=1.0)
        caption(scene, says[0])
        ghost = left.copy()
        mark(scene, "reflection", offset=1.0)
        # clockwise, so the piece swings over the top and never sweeps through the caption
        scene.play(Rotate(ghost, angle=-PI, about_point=origin), run_time=2.0)
        scene.play(Indicate(VGroup(ghost, right), color=WHITE), run_time=1.0)
        caption(scene, says[1], key="reflection: result")
        scene.play(FadeOut(VGroup(gr.group, left, right, ghost)), run_time=1.0)
    else:
        mirror = gr.curve.copy()
        mirror.set_color(spec.get("mirror_color", NEW_VAR_COLOR))
        caption(scene, says[0])
        mark(scene, "reflection", offset=1.0)
        scene.play(mirror.animate.flip(UP, about_point=origin), run_time=2.0)
        total = DashedLine(gr.axes.c2p(lo, spec["sum"]), gr.axes.c2p(hi, spec["sum"]),
                           color=WHITE, dash_length=0.12)
        total_label = MathTex(f"{spec['sum']:g}", font_size=34).next_to(total, RIGHT, buff=0.15)
        scene.play(Create(total), FadeIn(total_label), run_time=1.2)
        caption(scene, says[1], key="reflection: result")
        scene.play(FadeOut(VGroup(gr.group, mirror, total, total_label)), run_time=1.0)


# ---- the close
def close(scene, current, trail, answer_spec, colors, func, window, answer_value, final_count,
          says, widen_to=None, end_count=2048):
    """The answer once (boxed, morphed from the last line), the rectangle estimate
    meeting it, then the takeaway.

    says: (estimate caption, takeaway caption). widen_to=(a, b) also widens the window
    while n grows (for infinite limits).
    """
    scene._guard_section = "Close"
    answer = mt(eq(r"\text{Answer}", "=", *answer_spec), colors).scale(1.3)
    answer.set_color(AREA_COLOR)
    fit_into(answer, SAFE_LEFT, SAFE_RIGHT, 0.4, 2.6, center=True)
    scene.play(TransformMatchingTex(current, answer), *trail.fade(), run_time=1.5)
    trail.lines = []
    box = SurroundingRectangle(answer, color=AREA_COLOR, buff=0.25)
    scene.play(Create(box), run_time=0.8)
    mark(scene, "answer")
    t = ValueTracker(0)
    a0, b0 = window
    a1, b1 = widen_to or window

    def state():
        s = t.get_value()
        k = int(round(final_count * (end_count / final_count) ** s))
        return a0 + (a1 - a0) * s, b0 + (b1 - b0) * s, k

    def estimate():
        a, b, k = state()
        return midpoint_sum(func, a, b, k)

    n_num = Integer(final_count, font_size=34, group_with_commas=False)   # "2,048" reads like 2.048
    est = DecimalNumber(estimate(), num_decimal_places=5, font_size=34)
    gap = DecimalNumber(abs(estimate() - answer_value), num_decimal_places=5, font_size=34, color=TRAP_COLOR)
    readout = _readout([(r"\text{rectangles}=", n_num), (r"\text{estimate}\approx", est),
                        (r"\text{gap}=", gap)], box=(-3.5, 3.5, CAPTION_TOP + 0.15, -0.1))
    n_num.add_updater(lambda m: m.set_value(state()[2]))
    est.add_updater(lambda m: m.set_value(estimate()))
    gap.add_updater(lambda m: m.set_value(abs(estimate() - answer_value)))
    scene.play(FadeIn(readout, lag_ratio=0.2), run_time=1.0)
    scene.play(t.animate.set_value(1), run_time=2.5, rate_func=smooth)
    caption(scene, says[0], key="estimate meets answer")
    caption(scene, says[1], color=YELLOW)
    scene.wait(1.0)


# ---- narration
_SPEAK = [(r"\\t?frac\{([^{}]*)\}\{([^{}]*)\}", r"\1 over \2"),
          (r"\\sqrt\{([^{}]*)\}", r"root \1"), (r"\^\{-1\}", " inverse "), (r"\^\{?2\}?", " squared "),
          (r"\^\{?3\}?", " cubed"), (r"\^\{([^{}]*)\}", r" to the \1"), (r"\\infty", "infinity"),
          (r"\\pi", " pi "), (r"\\sigma", "sigma"), (r"\\sin", "sine "), (r"\\cos", "cos "), (r"\\ln", "log "),
          (r"\\to", " tends to "), (r"\\approx", " about "), (r"\\pm", " plus or minus "), (r"\\cdot", " times "),
          (r"\\,|\\;|\\quad|\\left|\\right|\\Big|\\big", " "), (r"\\[a-zA-Z]+", ""), (r"[{}]", ""),
          (r"=", " equals "), (r"\+", " plus "), (r"-", " minus "), (r"\(\s*", "("), (r"\s*\)", ")"),
          (r"\s+", " ")]


def speakable(text):
    """Turn a caption into words you could read aloud (approximate)."""
    def speak_math(m):
        s = m.group(1)
        for pat, rep in _SPEAK:
            s = re.sub(pat, rep, s)
        return s.strip()
    return re.sub(r"\s+", " ", re.sub(r"(?<!\\)\$([^$]*)\$", speak_math, text)).strip()


# ---- the video
class IntegralVideo(MovingCameraScene):
    """Base class for a day's video. A day's script sets the data attributes below
    (see Easy/2026-10-08_Easy.py) and usually nothing else.

    Story: intro card -> hook (picture + question, then the integral) -> intuition
    (rectangles) -> insight (highlight + zoom) -> method (morphing lines, substitution
    view, reflections) -> close (answer, estimate meets it, takeaway).
    """
    DIFFICULTY = "Easy"
    DATE = "2026-01-01"
    PROBLEM = eq("x")
    CURVE_LABEL = None          # eq(...) beside the curve; its parts glide into PROBLEM
    LABEL_AT = 0.0              # x where the curve label sits
    COLORS = {}
    GRAPH = {}
    HOOK = cap("What is the green area?")
    HOOK_NOTE = None            # optional second hook caption (e.g. about a hole)
    INTUITION = cap("Thin rectangles estimate the area; watch the gap shrink.")
    COUNTS = (4, 8, 16, 32, 64)
    WINDOW = None               # (a, b) for rectangles; defaults to GRAPH a, b
    INSIGHT = None              # dict(parts=[tex...], label=cap, say=cap, before=cap or None)
    STEPS = []
    ANSWER = eq("0")
    ANSWER_VALUE = 0.0
    CLOSE_SAYS = (cap("Thinner rectangles close in on the exact answer."), cap("Done."))
    CLOSE_WIDEN = None
    SUBSTITUTION = None         # dict(u_graph=..., u_func=..., says=(cap, cap))
    REFLECTION = None           # dict(spec=..., func=..., mode=..., says=(cap, cap))

    def __init__(self, *args, **kwargs):
        config.background_color = BACKGROUND
        super().__init__(*args, **kwargs)

    @staticmethod
    def FUNC(x):
        raise NotImplementedError

    @classmethod
    def exact_integral(cls):
        """The integral computed numerically with mpmath (used by check_text.py)."""
        raise NotImplementedError

    @classmethod
    def date_long(cls):
        d = _dt.date.fromisoformat(cls.DATE)
        return f"{d:%A} {d.day} {d:%B} {d.year}"

    @classmethod
    def date_short(cls):
        d = _dt.date.fromisoformat(cls.DATE)
        return f"{d.day} {d:%b} {d.year}"

    @classmethod
    def window(cls):
        return cls.WINDOW or (cls.GRAPH["a"], cls.GRAPH["b"])

    # story beats
    def hook(self):
        self._guard_section = "Hook"
        gr = build_graph(self.GRAPH, self.FUNC)
        label = None
        if self.CURVE_LABEL is not None:
            label = mt(self.CURVE_LABEL, self.COLORS, font_size=36)
            label.set_stroke(BACKGROUND, width=6, background=True)
            if isinstance(self.LABEL_AT, (tuple, list)):        # (x, y): lower-left corner of the label
                label.next_to(gr.axes.c2p(*self.LABEL_AT), UR, buff=0)
            else:                                               # x: just above-right of the curve
                label.next_to(gr.axes.i2gp(self.LABEL_AT, gr.curve), UR, buff=0.15)
            # the readout column is still empty during the hook, so the label may use it
            fit_into(label, SAFE_LEFT, SAFE_RIGHT, GRAPH_BOX[2], GRAPH_BOX[3])
        draw_graph(self, gr, label)
        caption(self, self.HOOK, key="hook")
        if self.HOOK_NOTE:
            if gr.hole is not None:
                self.play(Indicate(gr.hole, color=TRAP_COLOR, scale_factor=1.6), run_time=1.0)
            caption(self, self.HOOK_NOTE)
        problem = mt(self.PROBLEM, self.COLORS)
        fit_into(problem, -3.9, 3.9, GRAPH_BOX[3] + 0.1, SAFE_TOP - 0.05, center=True)
        if label is not None:
            self.play(TransformMatchingTex(label.copy(), problem), run_time=1.5)
        else:
            self.play(Write(problem), run_time=1.5)
        self.wait(1.0)
        return gr, label, problem

    def intuition(self, gr, label):
        self._guard_section = "Intuition"
        a, b = self.window()
        if label is not None:
            self.play(FadeOut(label), run_time=0.5)
        caption(self, self.INTUITION, wait=False)
        rects, readout, n, est = riemann_rectangles(self, gr, a, b, self.ANSWER_VALUE, self.COUNTS)
        self.wait(1.0)
        clear_caption(self)
        self.play(FadeOut(VGroup(gr.group, readout)), FadeOut(rects), run_time=1.0)
        return est

    def insight(self, problem):
        self._guard_section = "Insight"
        target = problem.copy().scale(1.25)
        fit_into(target, SAFE_LEFT, SAFE_RIGHT, STAGE[2], STAGE[3])
        target.move_to([0, 0.2, 0])
        self.play(Transform(problem, target), run_time=1.2)
        if not self.INSIGHT:
            return problem
        if self.INSIGHT.get("before"):
            caption(self, self.INSIGHT["before"])
        extra = highlight(self, parts_of(problem, *self.INSIGHT["parts"]), self.INSIGHT["label"],
                          side=self.INSIGHT.get("side", DOWN), context=problem)
        caption(self, self.INSIGHT["say"])
        unzoom(self, FadeOut(extra))
        return problem

    def method(self, problem):
        trail = Trail()
        self._trail = trail
        hooks = {"substitution": self._substitution, "reflection": self._reflection}
        return morph_steps(self, problem, self.STEPS, self.COLORS, trail, hooks), trail

    def _substitution(self, scene, current):
        s = self.SUBSTITUTION
        substitution_view(self, current, self._trail, dict(self.GRAPH), self.FUNC, s["u_graph"], s["u_func"],
                          self.ANSWER_VALUE, s["says"])

    def _reflection(self, scene, current):
        r = self.REFLECTION
        current.save_state()
        lines = self._trail.lines
        self.play(current.animate.set_opacity(0), *[l.animate.set_opacity(0) for l in lines], run_time=0.6)
        reflection_view(self, r["spec"], r["func"], r["mode"], r["says"])
        self.play(Restore(current), *[l.animate.set_opacity(DIM_OPACITY) for l in lines], run_time=0.6)

    def construct(self):
        install_frame_guard(self)
        self._narration, self._keyframes, self._caption = [], [], None
        intro_card(self, self.DIFFICULTY, self.date_long(), self.PROBLEM, self.COLORS)
        badge = make_badge(self, self.DIFFICULTY, self.date_short())
        self._guard_reserved = [badge]
        self.add(badge)
        gr, label, problem = self.hook()
        self.intuition(gr, label)
        problem = self.insight(problem)
        current, trail = self.method(problem)
        close(self, current, trail, self.ANSWER, self.COLORS, self.FUNC, self.window(), self.ANSWER_VALUE,
              self.COUNTS[-1], self.CLOSE_SAYS, widen_to=self.CLOSE_WIDEN)
        self.write_narration()

    def write_narration(self):
        """Write DATE_Difficulty_narration.txt next to the script: the captions in order."""
        owner = next(c for c in type(self).__mro__ if "DIFFICULTY" in c.__dict__ and c is not IntegralVideo)
        module = _sys.modules.get(owner.__module__)
        source = module.__file__ if module else owner.__dict__["FUNC"].__func__.__code__.co_filename
        folder = _os.path.dirname(_os.path.abspath(source))
        path = _os.path.join(folder, f"{self.DATE}_{self.DIFFICULTY}_narration.txt")
        lines = [f"{self.DIFFICULTY} Integral - {self.date_long()}", ""]
        lines += [f"{i}. {speakable(t)}" for i, t in enumerate(self._narration, 1)]
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
