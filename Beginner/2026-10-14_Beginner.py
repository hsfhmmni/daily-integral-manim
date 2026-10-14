import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import (IntegralVideo, LIMIT, NEW, cap, eq, build_graph, caption, mark, CAPTION_TOP, SAFE_LEFT,
                    SAFE_RIGHT, DIM_OPACITY, AREA_COLOR, AREA_OPACITY)


def g(x):
    """The top of the fraction: ln(x^3 - 2) e^{sin x} (positive on [2, 4])."""
    return np.log(x ** 3 - 2) * np.exp(np.sin(x))


def f(x):
    return g(x) / (g(x) + g(6 - x))


def mirror_func(x):
    """f mirrored in x = 3: g(6 - x) / (g(x) + g(6 - x)), which is 1 - f(x)."""
    return f(6 - x)


TOP = r"\ln(x^{3}-2)\,e^{\sin x}"
MIR = r"\ln((6-x)^{3}-2)\,e^{\sin(6-x)}"


class BeginnerIntegral(IntegralVideo):
    DIFFICULTY = "Beginner"
    DATE = "2026-10-14"

    @staticmethod
    def FUNC(x):
        return f(x)

    @classmethod
    def exact_integral(cls):
        gm = lambda x: mp.log(x ** 3 - 2) * mp.exp(mp.sin(x))
        return mp.quad(lambda x: gm(x) / (gm(x) + gm(6 - x)), [2, 4])

    COLORS = {MIR: NEW, "g(6-x)": NEW}
    LIMS = (r"\int_{", ("2", LIMIT), r"}^{", ("4", LIMIT), r"}")
    PROBLEM = eq(*LIMS, r"\frac{", TOP, r"}{", TOP, "+", MIR, r"}", r"\,dx")
    PROBLEM_X = (-6.2, 3.3)     # a long line: shift it left, clear of the badge
    CURVE_LABEL = None          # the integrand is too long to sit beside the curve; it is written above

    GRAPH = dict(x_range=[2, 4, 0.5], y_range=[0, 1, 0.25], a=2, b=4, size=(8, 4.2), plot_range=(2, 4),
                 x_labels={2: "2", 3: "3", 4: "4"},
                 y_labels={0.5: "0.5", 1: "1"})

    HOOK = cap(r"No antiderivative in sight. What symmetry does this curve have?")
    INTUITION = cap(r"Even four rectangles give exactly $1.0000$. Why so exact?")     # midpoints: exact by symmetry
    INSIGHT = dict(
        parts=[MIR],
        label=cap(r"$x\to 6-x$"),
        say=cap(r"The second term is the top with $x$ swapped for $6-x$."),
    )

    STEPS = [
        dict(tex=eq("I", "=", *LIMS, r"\frac{", "g(x)", r"}{", "g(x)", "+", "g(6-x)", r"}", r"\,dx"),
             say=cap(r"Call the top $g(x)$; the other term is $g(6-x)$."),
             rule="algebra"),
        dict(tex=eq("I", "=", *LIMS, r"\frac{", "g(6-x)", r"}{", "g(6-x)", "+", "g(x)", r"}", r"\,dx"),
             say=cap(r"Swap $x$ for $6-x$: the ends $2$ and $4$ trade places."),
             rule="interval_reflection",
             mapping=[cap(r"Here $a=2$ and $b=4$, so $a+b-x=6-x$.")],
             then="reflection"),
        dict(tex=eq("2I", "=", *LIMS, r"\frac{", "g(x)+g(6-x)", r"}{", "g(x)+g(6-x)", r"}", r"\,dx"),
             say=cap(r"Add the two forms of $I$: same bottom, so add tops."),
             rule="linearity"),
        dict(tex=eq("2I", "=", *LIMS, "1", r"\,dx"),
             say=cap(r"The top equals the bottom, so the integrand is $1$."),
             rule="algebra"),
        dict(tex=eq("2I", "=", "4", "-", "2"),
             say=cap(r"The area under $y=1$ from $2$ to $4$ is $2$."),
             rule=["power_rule", "ftc"]),
        dict(tex=eq("I", "=", "1"),
             say=cap(r"Halve both sides."),
             rule="algebra"),
    ]

    REFLECTION = dict(
        spec=dict(x_range=[2, 4, 0.5], y_range=[0, 1, 0.25], a=2, b=4, size=(7, 3.2), plot_range=(2, 4),
                  x_labels={2: "2", 3: "3", 4: "4"}, y_labels={0.5: "0.5", 1: "1"}),
        says=(cap(r"Mirror the curve in $x=3$: the area stays the same."),
              cap(r"Stacked, the two curves fill height $1$: total area $2$.")),
    )

    def _reflection(self, scene, current):
        """Mirror the curve in x = 3 (ORANGE copy), then stack the two: the sum is exactly 1."""
        r = self.REFLECTION
        current.save_state()
        lines = self._trail.lines
        self.play(current.animate.set_opacity(0), *[l.animate.set_opacity(0) for l in lines], run_time=0.6)
        self._guard_section = "Reflection"
        gr = build_graph(r["spec"], self.FUNC, (SAFE_LEFT, SAFE_RIGHT, CAPTION_TOP + 0.1, 1.0))
        ax = gr.axes
        self.play(FadeIn(gr.grid), Create(ax, lag_ratio=0.02), FadeIn(gr.var_label), run_time=1.2)
        self.play(Create(gr.curve), FadeIn(gr.area), run_time=1.2)
        axis_line = DashedLine(ax.c2p(3, 0), ax.c2p(3, 1), color=GREY_B, dash_length=0.1)
        self.play(Create(axis_line), run_time=0.8)
        mirror = gr.curve.copy().set_color(NEW)
        caption(self, r["says"][0])
        mark(self, "reflection", offset=1.0)
        # morph into the mirror image (an animated flip squashes the curve halfway)
        mirrored = ax.plot(mirror_func, x_range=[2, 4, 2 / 600], color=NEW, stroke_width=4)
        self.play(Transform(mirror, mirrored), run_time=2.0)
        # stack: the orange curve rides on top of the blue one, giving the flat line y = 1
        stacked = ax.plot(lambda x: f(x) + mirror_func(x), x_range=[2, 4, 2 / 600], color=NEW, stroke_width=4)
        total = ax.get_area(stacked, x_range=(2, 4), color=AREA_COLOR, opacity=AREA_OPACITY)
        self.play(Transform(mirror, stacked), FadeOut(axis_line), FadeOut(gr.area), run_time=1.5)
        self.play(FadeIn(total), run_time=1.0)
        caption(self, r["says"][1], key="reflection: result")
        self.play(FadeOut(VGroup(gr.grid, ax, gr.var_label, gr.curve, mirror, total)), run_time=1.0)
        self.play(Restore(current), *[l.animate.set_opacity(DIM_OPACITY) for l in lines], run_time=0.6)

    ANSWER = eq("1")
    ANSWER_VALUE = 1.0
    CLOSE_SAYS = (cap(r"Thin rectangles close in on exactly $1$."),
                  cap(r"Takeaway: if $a+b-x$ appears, swap $x$ for it and add."))
