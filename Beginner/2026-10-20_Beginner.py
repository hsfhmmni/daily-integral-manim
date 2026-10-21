import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import (AREA_COLOR, AREA_OPACITY, CAPTION_TOP, CURVE_COLOR, LIMIT_COLOR, IntegralVideo, LIMIT, cap,
                    caption, clear_caption, eq, fit_into, mark)

# The website's problem (a word problem, no integral in its TeX): the region bounded by the line
# through A(4, 5) and B(-2, 2), the vertical lines x = 0 and x = 6, and the horizontal line y = -2.
# The line is y = x/2 + 3, which stays above y = -2 on [0, 6], so the area is the integral of
# (x/2 + 3) - (-2) = x/2 + 5 from 0 to 6.


def line(x):
    return x / 2 + 3


class BeginnerIntegral(IntegralVideo):
    DIFFICULTY = "Beginner"
    DATE = "2026-10-20"

    @staticmethod
    def FUNC(x):
        """The height of each strip, measured from the floor y = -2."""
        x = np.asarray(x, dtype=float)
        return line(x) - (-2)

    @classmethod
    def exact_integral(cls):
        return mp.quad(lambda x: (x / 2 + 3) - (-2), [0, 6])

    LIMS = (r"\int_{", ("0", LIMIT), r"}^{", ("6", LIMIT), r"}")
    BAR = (r"\Big]_{", ("0", LIMIT), r"}^{", ("6", LIMIT), r"}")
    PROBLEM = eq("A", "=", *LIMS, r"\big(", "y", "-", "(-2)", r"\big)", r"\,dx")
    CURVE_LABEL = eq("h", "=", "y", "-", "(-2)")
    LABEL_AT = (0.3, 7.2)       # empty upper-left: the line is below 6.2 for x < 2.4

    GRAPH = dict(x_range=[0, 6, 1], y_range=[0, 9, 1], a=0, b=6, size=(8, 4.2), plot_range=(0, 6),
                 x_labels={2: "2", 4: "4", 6: "6"},
                 y_labels={5: "5", 8: "8"})

    HOOK = cap(r"Each strip is $y-(-2)$ tall. What is the total area?")
    INTUITION = cap(r"Under a straight top, midpoint rectangles are exact: watch.")
    INSIGHT = dict(
        parts=["y"],
        label=cap(r"the line through $A$ and $B$"),
        say=cap(r"First we need the line's equation, from $A$ and $B$."),
    )

    STEPS = [
        dict(tex=eq("A", "=", *LIMS, r"\big(", r"\frac{x}{2}+3", "-", "(-2)", r"\big)", r"\,dx"),
             say=cap(r"Gradient $\frac{5-2}{4-(-2)}=\frac{1}{2}$, so the line is $y=\frac{x}{2}+3$."),
             rule=["area_between_curves", "straight_line"],
             mapping={"area_between_curves": [cap(r"Top: the line. Bottom: the floor $y=-2$.")],
                      "straight_line": [cap(r"Through $A(4,5)$: $y-5=\frac{1}{2}(x-4)$.")]}),
        dict(tex=eq("A", "=", *LIMS, r"\big(", r"\frac{x}{2}", "+", "5", r"\big)", r"\,dx"),
             say=cap(r"Minus a negative is a plus: $3-(-2)=5$."),
             rule="algebra"),
        dict(tex=eq("A", "=", r"\Big[", r"\frac{x^{2}}{4}", "+", "5x", *BAR),
             say=cap(r"Power rule: $\frac{x}{2}$ gives $\frac{x^{2}}{4}$, and $5$ gives $5x$."),
             rule=["power_rule", "linearity"]),
        dict(tex=eq("A", "=", r"\Big(", "9", "+", "30", r"\Big)", "-", r"\Big(", "0", "+", "0", r"\Big)"),
             say=cap(r"Top limit $6$ minus bottom limit $0$."),
             rule="ftc"),
        dict(tex=eq("A", "=", "39"),
             say=cap(r"Check: a trapezium, $\frac{5+8}{2}\times 6=39$."),
             rule="algebra"),
    ]

    ANSWER = eq("39")
    ANSWER_VALUE = 39.0
    CLOSE_SAYS = (cap(r"Thin rectangles agree: the area is exactly $39$."),
                  cap(r"Takeaway: measure each strip from the floor, not the axis."))

    def hook(self):
        self.region_sketch()
        return super().hook()

    def region_sketch(self):
        """The region as the website describes it, then lifted up by 2 so its floor is the x-axis."""
        self._guard_section = "Region"
        axes = Axes(x_range=[-3, 7, 1], y_range=[-3, 9, 1], x_length=7.0, y_length=5.0, tips=False,
                    axis_config=dict(stroke_color=GREY_A, stroke_width=2, include_ticks=False))
        x_lab = MathTex("x", font_size=34, color=GREY_A).next_to(axes.x_axis.get_right(), RIGHT, buff=0.15)
        y_lab = MathTex("y", font_size=34, color=GREY_A).next_to(axes.y_axis.get_top(), UP, buff=0.1)
        top = axes.plot(line, x_range=[-3, 7], color=CURVE_COLOR, stroke_width=4)
        floor = DashedLine(axes.c2p(-3, -2), axes.c2p(7, -2), color=WHITE, dash_length=0.12)
        wall = DashedLine(axes.c2p(6, -2), axes.c2p(6, line(6)), color=LIMIT_COLOR, dash_length=0.12)
        y_axis_wall = Line(axes.c2p(0, -2), axes.c2p(0, 3), color=LIMIT_COLOR, stroke_width=4)
        region = Polygon(axes.c2p(0, -2), axes.c2p(6, -2), axes.c2p(6, line(6)), axes.c2p(0, line(0)),
                         stroke_width=0).set_fill(AREA_COLOR, AREA_OPACITY)
        pa, pb = Dot(axes.c2p(4, 5), color=WHITE), Dot(axes.c2p(-2, 2), color=WHITE)
        la = MathTex(r"A(4,5)", font_size=32).next_to(pa, UL, buff=0.12)
        lb = MathTex(r"B(-2,2)", font_size=32).next_to(pb, UP, buff=0.2)
        lf = MathTex(r"y=-2", font_size=32).next_to(axes.c2p(-3, -2), UP, buff=0.12).shift(0.45 * RIGHT)
        lw = MathTex(r"x=6", font_size=32, color=LIMIT_COLOR).next_to(axes.c2p(6, -2), DR, buff=0.1)
        group = VGroup(axes, x_lab, y_lab, top, floor, wall, y_axis_wall, region, pa, pb, la, lb, lf, lw)
        fit_into(group, -5.2, 5.2, CAPTION_TOP + 0.15, 2.95, center=True)
        for m in (la, lb, lf, lw):
            m.set_stroke(BLACK, width=6, background=True)
        self.play(Create(axes), FadeIn(x_lab), FadeIn(y_lab), run_time=1.0)
        self.play(FadeIn(pa), FadeIn(pb), FadeIn(la), FadeIn(lb), run_time=1.0)
        self.play(Create(top), run_time=1.2)
        self.play(Create(floor), Create(wall), Create(y_axis_wall), FadeIn(lf), FadeIn(lw), run_time=1.2)
        self.play(FadeIn(region), run_time=1.0)
        caption(self, cap(r"The line through $A$ and $B$, walls $x=0$ and $x=6$, floor $y=-2$."),
                key="hook: region")
        lift = axes.c2p(0, 2) - axes.c2p(0, 0)
        mark(self, "lift", offset=1.0)
        # the point labels would read wrong once lifted, so they fade as everything moves up
        self.play(VGroup(top, floor, wall, y_axis_wall, region, pa, pb, lw).animate.shift(lift),
                  FadeOut(lf), FadeOut(la), FadeOut(lb), run_time=2.0)
        caption(self, cap(r"Lift it all up by $2$: the floor becomes the $x$-axis."))
        clear_caption(self)
        self.play(FadeOut(VGroup(axes, x_lab, y_lab, top, floor, wall, y_axis_wall, region, pa, pb, lw)),
                  run_time=0.8)
