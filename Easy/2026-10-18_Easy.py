import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import (CAPTION_TOP, DIM_OPACITY, IntegralVideo, LIMIT, NEW, NEW_VAR_COLOR, SAFE_LEFT, SAFE_RIGHT,
                    build_graph, cap, caption, eq, mark)


def f(x):
    x = np.asarray(x, dtype=float)
    return np.log(1 + x) / np.log((1 + x) * (2 - x))


class EasyIntegral(IntegralVideo):
    DIFFICULTY = "Easy"
    DATE = "2026-10-18"

    @staticmethod
    def FUNC(x):
        return f(x)

    @classmethod
    def exact_integral(cls):
        return mp.quad(lambda x: mp.log(1 + x) / mp.log((1 + x) * (2 - x)), [0, 1])

    L1 = r"\ln(1+x)"
    L2 = r"\ln(2-x)"
    PROD = r"\ln\big((1+x)(2-x)\big)"
    COLORS = {L2: NEW}
    LIMS = (r"\int_{", ("0", LIMIT), r"}^{", ("1", LIMIT), r"}")
    PROBLEM = eq(*LIMS, r"\frac{", L1, r"}{", PROD, r"}", r"\,dx")
    CURVE_LABEL = eq("y", "=", r"\frac{", L1, r"}{", PROD, r"}")
    LABEL_AT = (0.03, 0.78)     # empty upper-left, where the curve is still below 0.5

    GRAPH = dict(x_range=[0, 1, 0.25], y_range=[0, 1.2, 0.25], a=0, b=1, size=(8, 4.2), plot_range=(0, 1),
                 x_labels={0.5: "0.5", 1: "1"},
                 y_labels={0.5: "0.5", 1: "1"})

    HOOK = cap(r"Logarithm over logarithm, from $0$ to $1$. Any symmetry?")
    INTUITION = cap(r"Even four rectangles give exactly $0.5$: a hint of symmetry.")
    INSIGHT = dict(
        parts=[PROD],
        label=cap(r"$\ln(1+x)+\ln(2-x)$"),
        say=cap(r"Swapping $x$ for $1-x$ swaps $1+x$ and $2-x$."),
    )

    STEPS = [
        dict(tex=eq("I", "=", *LIMS, r"\frac{", L1, r"}{", L1, "+", L2, r"}", r"\,dx"),
             say=cap(r"$\ln(ab)=\ln a+\ln b$ splits the bottom in two."),
             rule="log_laws"),
        dict(tex=eq("I", "=", *LIMS, r"\frac{", L2, r"}{", L2, "+", L1, r"}", r"\,dx"),
             say=cap(r"Swap $x$ for $1-x$: the two logs trade places."),
             rule="kings_rule",
             mapping=[cap(r"Here $a=1$: $1+(1-x)=2-x$ and $2-(1-x)=1+x$.")],
             then="reflection"),
        dict(tex=eq("2I", "=", *LIMS, r"\frac{", L1, "+", L2, r"}{", L1, "+", L2, r"}", r"\,dx"),
             say=cap(r"Add the two forms: the tops sum to the bottom."),
             rule="linearity"),
        dict(tex=eq("2I", "=", *LIMS, "1", r"\,dx"),
             say=cap(r"The fraction is exactly $1$ everywhere."),
             rule="algebra"),
        dict(tex=eq("2I", "=", "1"),
             say=cap(r"Height $1$ over width $1$: area $1$."),
             rule=["power_rule", "ftc"]),
        dict(tex=eq("I", "=", r"\frac{1}{2}"),
             say=cap(r"Halve it: exactly one half."),
             rule="algebra"),
    ]

    REFLECTION = dict(says=(cap(r"Mirror the area in $x=\frac{1}{2}$: its size is unchanged."),
                            cap(r"Now turn the mirrored area upside down."),
                            cap(r"It fills the gap exactly: together, area $1$.")))

    ANSWER = eq(r"\frac{1}{2}")
    ANSWER_VALUE = 0.5
    CLOSE_SAYS = (cap(r"Thin rectangles close in on $\frac{1}{2}=0.5$."),
                  cap(r"Takeaway: if $a-x$ swaps the pieces, add both forms."))

    def _reflection(self, scene, current):
        """The area (GREEN), mirrored in x = 1/2 (ORANGE copy), then turned upside down about y = 1/2.

        The mirror is the area under f(1-x) = 1 - f(x); flipped about y = 1/2 it becomes exactly the
        region between f(x) and 1, so the two pieces stack into the unit square."""
        current.save_state()
        lines = self._trail.lines
        self.play(current.animate.set_opacity(0), *[l.animate.set_opacity(0) for l in lines], run_time=0.6)
        self._guard_section = "Reflection"
        gs = dict(x_range=[0, 1, 0.25], y_range=[0, 1.2, 0.25], a=0, b=1, size=(8, 3.6),
                  x_labels={0.5: r"\frac{1}{2}", 1: "1"},
                  y_labels={0.5: "0.5", 1: "1"}, color_limits=False)
        gr = build_graph(gs, f, (SAFE_LEFT, SAFE_RIGHT, CAPTION_TOP + 0.1, 1.0))
        self.play(FadeIn(gr.grid), Create(gr.axes, lag_ratio=0.02), FadeIn(gr.var_label), run_time=1.2)
        self.play(Create(gr.curve), run_time=1.2)
        self.play(FadeIn(gr.area), run_time=0.8)
        line = DashedLine(gr.axes.c2p(0.5, 0), gr.axes.c2p(0.5, 1.2), color=WHITE, dash_length=0.12)
        self.play(Create(line), run_time=0.8)
        caption(self, self.REFLECTION["says"][0])
        mirror = VGroup(gr.curve.copy(), gr.area.copy()).set_color(NEW_VAR_COLOR)
        mirror[1].set_fill(NEW_VAR_COLOR, opacity=0.5)
        mark(self, "reflection", offset=1.0)
        self.play(mirror.animate.flip(UP, about_point=gr.axes.c2p(0.5, 0)), run_time=2.0)
        caption(self, self.REFLECTION["says"][1])
        self.play(mirror.animate.flip(RIGHT, about_point=gr.axes.c2p(0.5, 0.5)), run_time=2.0)
        top_line = DashedLine(gr.axes.c2p(0, 1), gr.axes.c2p(1, 1), color=WHITE, dash_length=0.12)
        self.play(Create(top_line), run_time=0.8)
        caption(self, self.REFLECTION["says"][2], key="reflection: result")
        self.play(FadeOut(VGroup(gr.group, line, mirror, top_line)), run_time=1.0)
        self.play(Restore(current), *[l.animate.set_opacity(DIM_OPACITY) for l in lines], run_time=0.6)
