import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import (AREA_COLOR, AREA_OPACITY, BACKGROUND, CAPTION_TOP, CURVE_COLOR, IntegralVideo, LIMIT, NEW,
                    TRAP, cap, caption, clear_caption, eq, fit_into, mark)

# The website's problem (a word problem, no integral in its TeX): the region enclosed by y = x and
# y = x^2 is rotated about the x-axis; find the volume. The curves meet at x = 0 and x = 1, where
# x^2 <= x, so each slice is a washer with outer radius x and inner radius x^2:
# V = pi * integral of (x^2 - x^4) from 0 to 1 = 2 pi / 15.


class EasyIntegral(IntegralVideo):
    DIFFICULTY = "Easy"
    DATE = "2026-10-20"

    @staticmethod
    def FUNC(x):
        """The area of the washer at x: pi (R^2 - r^2) with R = x, r = x^2."""
        x = np.asarray(x, dtype=float)
        return np.pi * (x ** 2 - x ** 4)

    @classmethod
    def exact_integral(cls):
        return mp.pi * mp.quad(lambda x: x ** 2 - x ** 4, [0, 1])

    COLORS = {}
    LIMS = (r"\int_{", ("0", LIMIT), r"}^{", ("1", LIMIT), r"}")
    BAR = (r"\Big]_{", ("0", LIMIT), r"}^{", ("1", LIMIT), r"}")
    PROBLEM = eq("V", "=", r"\pi", *LIMS, r"\big(", "R^{2}", "-", "r^{2}", r"\big)", r"\,dx")
    CURVE_LABEL = eq("A", "=", r"\pi", r"\big(", "R^{2}", "-", "r^{2}", r"\big)")
    LABEL_AT = (0.03, 0.82)     # empty upper-left: the curve is below 0.45 for x < 0.4

    GRAPH = dict(x_range=[0, 1, 0.25], y_range=[0, 1, 0.25], a=0, b=1, size=(8, 4.2), plot_range=(0, 1),
                 x_labels={0.5: "0.5", 1: "1"},
                 y_labels={0.5: "0.5", 1: "1"})

    HOOK = cap(r"Each washer has area $\pi(R^{2}-r^{2})$. Add them: what volume?")
    INTUITION = cap(r"Thin rectangles estimate the area; watch the gap shrink.")
    INSIGHT = dict(
        parts=["R^{2}", "-", "r^{2}"],
        label=cap(r"square each radius first"),
        say=cap(r"Square both radii, then subtract: the hole has its own radius."),
    )

    STEPS = [
        dict(tex=eq("V", "=", r"\pi", *LIMS, (r"(x-x^{2})^{2}", TRAP), r"\,dx"),
             say=cap(r"Tempting: spin the gap $x-x^{2}$ as one solid disc?"),
             rule="volume_of_revolution",
             mapping=[cap(r"Tempting: take $y=x-x^{2}$, the height of the gap.")],
             check=False,
             check_reason="trap: pi * int (x - x^2)^2 dx = pi/30 spins the gap's height from the axis, "
                          "not the region between the curves; the washer volume is pi * int (x^2 - x^4) dx"),
        dict(tex=eq("V", "=", r"\pi", *LIMS, r"\big(", "x^{2}", "-", r"(x^{2})^{2}", r"\big)", r"\,dx"),
             say=cap(r"No: that gives $\frac{\pi}{30}$. Each slice has a hole of radius $x^{2}$."),
             rule="washer_method",
             mapping=[cap(r"Outer $R=x$, inner $r=x^{2}$, since $x^{2}<x$ on $(0,1)$.")]),
        dict(tex=eq("V", "=", r"\pi", *LIMS, r"\big(", "x^{2}", "-", "x^{4}", r"\big)", r"\,dx"),
             say=cap(r"Square the inner radius: $(x^{2})^{2}=x^{4}$."),
             rule="exponent_laws"),
        dict(tex=eq("V", "=", r"\pi", r"\Big[", r"\frac{x^{3}}{3}", "-", r"\frac{x^{5}}{5}", *BAR),
             say=cap(r"Power rule on each term."),
             rule=["power_rule", "linearity"]),
        dict(tex=eq("V", "=", r"\pi", r"\Big(", r"\frac{1}{3}", "-", r"\frac{1}{5}", r"\Big)"),
             say=cap(r"At $x=1$ both powers are $1$; at $x=0$ both vanish."),
             rule="ftc"),
        dict(tex=eq("V", "=", r"\frac{2\pi}{15}"),
             say=cap(r"$\frac{1}{3}-\frac{1}{5}=\frac{2}{15}$, so the volume is about $0.419$."),
             rule="algebra"),
    ]

    ANSWER = eq(r"\frac{2\pi}{15}")
    ANSWER_VALUE = float(2 * np.pi / 15)
    CLOSE_SAYS = (cap(r"Rectangles under the washer areas close in on $0.419$."),
                  cap(r"Takeaway: square each radius, then subtract. Never square the gap."))

    def hook(self):
        self.solid_sketch()
        return super().hook()

    def solid_sketch(self):
        """The region between y = x and y = x^2, its mirror below the axis and thin washers:
        the solid seen side-on."""
        self._guard_section = "Solid"
        axes = Axes(x_range=[0, 1.2, 0.25], y_range=[-1.1, 1.1, 0.5], x_length=8.0, y_length=4.4,
                    tips=False, axis_config=dict(stroke_color=GREY_A, stroke_width=2, include_ticks=False))
        x_lab = MathTex("x", font_size=34, color=GREY_A).next_to(axes.x_axis.get_right(), RIGHT, buff=0.15)
        outer = axes.plot(lambda t: t, x_range=[0, 1], color=CURVE_COLOR, stroke_width=4)
        inner = axes.plot(lambda t: t ** 2, x_range=[0, 1], color=NEW, stroke_width=4)
        region = axes.get_area(outer, x_range=(0, 1), bounded_graph=inner, color=AREA_COLOR,
                               opacity=AREA_OPACITY)
        l_out = MathTex(r"y=x", font_size=34, color=CURVE_COLOR).next_to(axes.c2p(0.62, 0.62), UL, buff=0.15)
        l_in = MathTex(r"y=x^{2}", font_size=34, color=NEW).next_to(axes.c2p(0.8, 0.64), DR, buff=0.15)
        meet = VGroup(Dot(axes.c2p(0, 0)), Dot(axes.c2p(1, 1)))
        m_out = axes.plot(lambda t: -t, x_range=[0, 1], color=CURVE_COLOR, stroke_width=3, stroke_opacity=0.5)
        m_in = axes.plot(lambda t: -t ** 2, x_range=[0, 1], color=NEW, stroke_width=3, stroke_opacity=0.5)
        unit_y = axes.c2p(0, 1)[1] - axes.c2p(0, 0)[1]
        washers = VGroup()
        for t in np.arange(0.15, 1.0, 0.1):
            ring = Ellipse(width=0.22, height=2 * t * unit_y).move_to(axes.c2p(t, 0))
            ring.set_stroke(AREA_COLOR, 2).set_fill(AREA_COLOR, 0.35)
            hole = Ellipse(width=0.12, height=2 * t * t * unit_y).move_to(axes.c2p(t, 0))
            hole.set_stroke(NEW, 1.5).set_fill(BACKGROUND, 1)
            washers.add(VGroup(ring, hole))
        group = VGroup(axes, x_lab, outer, inner, region, l_out, l_in, meet, m_out, m_in, washers)
        fit_into(group, -5.2, 5.2, CAPTION_TOP + 0.15, 2.95, center=True)
        for m in (l_out, l_in):
            m.set_stroke(BLACK, width=6, background=True)
        self.play(Create(axes), FadeIn(x_lab), run_time=1.0)
        self.play(Create(outer), Create(inner), FadeIn(l_out), FadeIn(l_in), run_time=1.5)
        self.play(FadeIn(region), FadeIn(meet), run_time=1.0)
        caption(self, cap(r"The curves meet where $x=x^{2}$: at $x=0$ and $x=1$."), key="hook: region")
        caption(self, cap(r"Spin this region about the $x$-axis. What volume?"))
        self.play(TransformFromCopy(outer, m_out), TransformFromCopy(inner, m_in), run_time=1.2)
        # the washers cover the curve labels, so those fade as the washers grow
        self.play(LaggedStart(*[GrowFromCenter(w) for w in washers], lag_ratio=0.1), FadeOut(l_out), FadeOut(l_in),
                  run_time=2.0)
        mark(self, "washers")
        caption(self, cap(r"Each slice is a washer: a disc with a hole."))
        clear_caption(self)
        self.play(FadeOut(VGroup(axes, x_lab, outer, inner, region, meet, m_out, m_in, washers)),
                  run_time=0.8)
