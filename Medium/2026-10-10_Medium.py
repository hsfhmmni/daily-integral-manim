import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import (IntegralVideo, LIMIT, NEW, cap, eq, mt, build_graph, caption, mark, fit_into, CAPTION_TOP,
                    SAFE_LEFT, SAFE_RIGHT, DIM_OPACITY, CURVE_COLOR, BACKGROUND)

INTEGRAND = r"\Bigg|\,\Big|\,\big|\,|x|-1\,\big|-2\,\Big|-3\,\Bigg|^{3}"
HALF = r"\Bigg|\,\Big|\,\big|\,x-1\,\big|-2\,\Big|-3\,\Bigg|^{3}"

# the inside, built one operation at a time: subtract, then fold (absolute value)
UNWRAP = [
    (lambda x: np.abs(x), r"|x|"),
    (lambda x: np.abs(x) - 1, r"|x|-1"),
    (lambda x: np.abs(np.abs(x) - 1), r"\big||x|-1\big|"),
    (lambda x: np.abs(np.abs(x) - 1) - 2, r"\big||x|-1\big|-2"),
    (lambda x: np.abs(np.abs(np.abs(x) - 1) - 2), r"\Big|\big||x|-1\big|-2\Big|"),
    (lambda x: np.abs(np.abs(np.abs(x) - 1) - 2) - 3, r"\Big|\big||x|-1\big|-2\Big|-3"),
    (lambda x: np.abs(np.abs(np.abs(np.abs(x) - 1) - 2) - 3), r"\Bigg|\Big|\big||x|-1\big|-2\Big|-3\Bigg|"),
]


class MediumIntegral(IntegralVideo):
    DIFFICULTY = "Medium"
    DATE = "2026-10-10"

    @staticmethod
    def FUNC(x):
        return np.abs(np.abs(np.abs(np.abs(x) - 1) - 2) - 3) ** 3

    @classmethod
    def exact_integral(cls):
        f = lambda x: abs(abs(abs(abs(x) - 1) - 2) - 3) ** 3
        return mp.quad(f, [-6, -3, -1, 0, 1, 3, 6])          # split at the corners

    COLORS = {"(2-x)^{3}": NEW, "x^{3}": NEW, "(6-x)^{3}": NEW, "t^{3}": NEW, r"\,dt": NEW}
    PROBLEM = eq(r"\int_{", ("-6", LIMIT), r"}^{", ("6", LIMIT), r"}", INTEGRAND, r"\,dx")
    CURVE_LABEL = eq("y", "=", INTEGRAND)
    LABEL_AT = (0.4, 29.5)      # right of the central y-axis, above the peak (height 27) at x = 3

    GRAPH = dict(x_range=[-7, 7, 1], y_range=[0, 40, 10], a=-6, b=6, size=(8.5, 4.2), plot_range=(-6, 6),
                 x_labels={-6: "-6", -3: "-3", -1: "-1", 1: "1", 3: "3", 6: "6"},
                 y_labels={10: "10", 20: "20", 30: "30", 40: "40"})

    HOOK = cap(r"Four nested absolute values. How big is this green area?")
    HOOK_NOTE = cap(r"Each corner is where some inside expression hits $0$.")
    INTUITION = cap(r"Thin rectangles estimate the area; watch the gap shrink.")
    INSIGHT = dict(
        before=cap(r"Start from the innermost bars, $|x|$."),
        parts=[INTEGRAND],
        label=cap(r"$|{-x}|=|x|$"),
        say=cap(r"$|x|$ is even, so the whole integrand is even."),
    )

    STEPS = [
        dict(tex=eq("2", r"\int_{", ("0", LIMIT), r"}^{", ("6", LIMIT), r"}", HALF, r"\,dx"),
             say=cap(r"Even integrand: double the half from $0$ to $6$, where $|x|=x$."),
             then="reflection"),
        dict(tex=eq("2", r"\Big(", r"\int_{", ("0", LIMIT), r"}^{", ("1", LIMIT), r"}", "(2-x)^{3}", r"\,dx", "+",
                    r"\int_{", ("1", LIMIT), r"}^{", ("3", LIMIT), r"}", "x^{3}", r"\,dx", "+",
                    r"\int_{", ("3", LIMIT), r"}^{", ("6", LIMIT), r"}", "(6-x)^{3}", r"\,dx", r"\Big)"),
             say=cap(r"On $[0,6]$ the zigzag is $2-x$, then $x$, then $6-x$.")),
        dict(tex=eq("2", r"\Big(", r"\int_{", ("1", LIMIT), r"}^{", ("2", LIMIT), r"}", "t^{3}", r"\,dt", "+",
                    r"\int_{", ("1", LIMIT), r"}^{", ("3", LIMIT), r"}", "t^{3}", r"\,dt", "+",
                    r"\int_{", ("0", LIMIT), r"}^{", ("3", LIMIT), r"}", "t^{3}", r"\,dt", r"\Big)"),
             say=cap(r"Let $t$ be each piece's height: every part becomes $\int t^{3}\,dt$.")),
        dict(tex=eq("2", r"\Big(", r"\frac{15}{4}", "+", "20", "+", r"\frac{81}{4}", r"\Big)"),
             say=cap(r"Each piece: $\int_{a}^{b}t^{3}\,dt=\frac{b^{4}-a^{4}}{4}$.")),
        dict(tex=eq("2", r"\cdot", "44"),
             say=cap(r"$\frac{15}{4}+\frac{80}{4}+\frac{81}{4}=\frac{176}{4}=44$.")),
        dict(tex=eq("88"),
             say=cap(r"Double it to count the left half too.")),
    ]

    REFLECTION = dict(
        spec=dict(x_range=[-6, 6, 1], y_range=[-3, 6, 3], a=-6, b=6, size=(7, 3.4), plot_range=(-6, 6),
                  color_limits=False, x_labels={-6: "-6", -3: "-3", 3: "3", 6: "6"},
                  y_labels={-3: "-3", 3: "3", 6: "6"}),
        says=(cap(r"Unwrap from inside: subtract a number, then fold negatives up."),
              cap(r"A zigzag of straight pieces, reaching height $3$ at $x=\pm 3$.")),
    )

    def _reflection(self, scene, current):
        """Build the inside one operation at a time: each subtraction drops the graph,
        each absolute value folds the part below the axis back up."""
        r = self.REFLECTION
        current.save_state()
        lines = self._trail.lines
        self.play(current.animate.set_opacity(0), *[l.animate.set_opacity(0) for l in lines], run_time=0.6)
        self._guard_section = "Unwrap"
        gr = build_graph(r["spec"], UNWRAP[0][0], (SAFE_LEFT, SAFE_RIGHT, CAPTION_TOP + 0.1, 1.0))
        ax = gr.axes

        def curve_for(fn):
            return ax.plot(fn, x_range=[-6, 6, 0.01], color=CURVE_COLOR, stroke_width=4, use_smoothing=False)

        def label_for(tex):
            lab = mt(eq("y", "=", tex), font_size=40)
            lab.set_stroke(BACKGROUND, width=6, background=True)
            return fit_into(lab, -4.5, 4.5, 1.35, 2.55, center=True)

        curve = curve_for(UNWRAP[0][0])
        label = label_for(UNWRAP[0][1])
        self.play(FadeIn(gr.grid), Create(ax, lag_ratio=0.02), FadeIn(gr.var_label), run_time=1.2)
        self.play(Create(curve), FadeIn(label), run_time=1.2)
        caption(self, r["says"][0])
        for i, (fn, tex) in enumerate(UNWRAP[1:], 1):
            if i == 4:
                mark(self, "reflection", offset=0.5)
            self.play(Transform(curve, curve_for(fn)), Transform(label, label_for(tex)), run_time=1.2)
            self.wait(0.5)
        caption(self, r["says"][1], key="reflection: result")
        self.play(FadeOut(VGroup(gr.grid, ax, gr.var_label, curve, label)), run_time=1.0)
        self.play(Restore(current), *[l.animate.set_opacity(DIM_OPACITY) for l in lines], run_time=0.6)

    ANSWER = eq("88")
    ANSWER_VALUE = 88.0
    CLOSE_SAYS = (cap(r"More, thinner rectangles close in on $88$."),
                  cap(r"Takeaway: unwrap nested absolute values from the inside out."))
