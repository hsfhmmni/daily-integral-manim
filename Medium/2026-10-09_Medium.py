import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import IntegralVideo, LIMIT, NEW, cap, eq, substitution_view

PHI = float((1 + np.sqrt(5)) / 2)
TOP = r"\sqrt{x-\sqrt{x-\sqrt{x-\cdots}}}"       # A: the positive solution of A = sqrt(x - A)
BOTTOM = r"\sqrt{x+\sqrt{x+\sqrt{x+\cdots}}}"    # B: the positive solution of B = sqrt(x + B)


class MediumIntegral(IntegralVideo):
    DIFFICULTY = "Medium"
    DATE = "2026-10-09"

    @staticmethod
    def FUNC(x):
        return 1 - 2 / (1 + np.sqrt(1 + 4 * x))       # A/B with A = (s-1)/2, B = (s+1)/2, s = sqrt(1+4x)

    @classmethod
    def exact_integral(cls):
        # A and B as the positive roots of A^2 = x - A and B^2 = x + B
        A = lambda x: (mp.sqrt(1 + 4 * x) - 1) / 2
        B = lambda x: (mp.sqrt(1 + 4 * x) + 1) / 2
        return mp.quad(lambda x: A(x) / B(x), [0, 1])

    COLORS = {BOTTOM: NEW, "B": NEW, "B-1": NEW, "(2B-1)": NEW, "B^{2}": NEW}
    PROBLEM = eq(r"\int_{", ("0", LIMIT), r"}^{", ("1", LIMIT), r"}", r"\frac{", TOP, r"}{", BOTTOM, r"}\;", r"\,dx")
    CURVE_LABEL = eq("y", "=", r"\frac{", TOP, r"}{", BOTTOM, r"}")
    LABEL_AT = (0.1, 0.46)      # empty upper-left region, above the slowly rising curve

    GRAPH = dict(x_range=[0, 1.25, 0.25], y_range=[0, 0.8, 0.2], a=0, b=1, size=(8, 4.2), plot_range=(0, 1.2),
                 x_labels={0.5: "0.5", 1: "1"}, y_labels={0.2: "0.2", 0.4: "0.4", 0.6: "0.6", 0.8: "0.8"})

    HOOK = cap(r"Endless roots on top and bottom. Can this area be exact?")
    INTUITION = cap(r"Thin rectangles estimate the area; watch the gap shrink.")
    INSIGHT = dict(
        before=cap(r"Look at the bottom: it contains a copy of itself."),
        parts=[BOTTOM],
        label=cap(r"$B=\sqrt{x+B}$"),
        say=cap(r"So $B^{2}=x+B$; the top $A$ obeys $A^{2}=x-A$."),
    )

    STEPS = [
        dict(tex=eq(r"\int_{", ("0", LIMIT), r"}^{", ("1", LIMIT), r"}", r"\frac{", "A", r"}{", "B", r"}", r"\,dx"),
             say=cap(r"Name the top $A$ and the bottom $B$, both positive.")),
        dict(tex=eq(r"\int_{", ("0", LIMIT), r"}^{", ("1", LIMIT), r"}", r"\frac{", "B-1", r"}{", "B", r"}", r"\,dx"),
             say=cap(r"Subtract: $B^{2}-A^{2}=B+A$, so $B-A=1$.")),
        dict(tex=eq(r"\int_{", ("1", LIMIT), r"}^{", (r"\varphi", LIMIT), r"}", r"\frac{", "B-1", r"}{", "B", r"}",
                    "(2B-1)", r"\,d", "B"),
             say=cap(r"Switch to $B$: $x=B^{2}-B$, so $dx=(2B-1)\,dB$."),
             then="substitution"),
        dict(tex=eq(r"\int_{", ("1", LIMIT), r"}^{", (r"\varphi", LIMIT), r"}", r"\Big(", "2", "B", "-3+", r"\frac{1}{",
                    "B", r"}", r"\Big)", r"\,d", "B"),
             say=cap(r"Expand $(B-1)(2B-1)=2B^{2}-3B+1$, then divide by $B$.")),
        dict(tex=eq(r"\Big[", "B^{2}", "-3", "B", r"+\ln ", "B", r"\Big]_{", ("1", LIMIT), r"}^{", (r"\varphi", LIMIT),
                    r"}"),
             say=cap(r"Integrate term by term.")),
        dict(tex=eq(r"\varphi^{2}-3\varphi+\ln\varphi", "-", r"(1-3+0)"),
             say=cap(r"Upper limit minus lower limit; $\ln 1=0$.")),
        dict(tex=eq("3-2\\varphi", r"+\ln\varphi"),
             say=cap(r"The golden ratio obeys $\varphi^{2}=\varphi+1$.")),
        dict(tex=eq(r"2-\sqrt{5}", r"+\ln\varphi"),
             say=cap(r"With $\varphi=\frac{1+\sqrt{5}}{2}$, $3-2\varphi=2-\sqrt{5}$.")),
    ]

    SUBSTITUTION = dict(
        u_graph=dict(x_range=[0.5, 2, 0.5], y_range=[0, 1.5, 0.5], a=1, b=PHI, var="B", size=(6, 2.6),
                     plot_range=(1, 1.85), x_labels={1: "1", PHI: r"\varphi", 2: "2"},
                     y_labels={0.5: "0.5", 1: "1", 1.5: "1.5"}),
        u_func=lambda b: (b - 1) * (2 * b - 1) / b,
        says=(cap(r"As $x\to 0^{+}$, $B\to 1$; at $x=1$, $B^{2}=B+1$, so $B=\varphi$."),
              cap(r"In $B$: a new curve from $1$ to $\varphi$, same area.")),
    )

    def _substitution(self, scene, current):
        # the fraction lines above leave a short box, so draw smaller graphs that need no shrinking
        s = self.SUBSTITUTION
        x_graph = dict(self.GRAPH, size=(6, 2.6), y_labels={0.4: "0.4", 0.8: "0.8"})
        substitution_view(self, current, self._trail, x_graph, self.FUNC, s["u_graph"], s["u_func"],
                          self.ANSWER_VALUE, s["says"])

    ANSWER = eq(r"2-\sqrt{5}", r"+\ln\varphi")
    ANSWER_VALUE = float(2 - np.sqrt(5) + np.log(PHI))
    CLOSE_SAYS = (cap(r"More, thinner rectangles close in on $2-\sqrt{5}+\ln\varphi\approx 0.2451$."),
                  cap(r"Takeaway: an endless expression contains itself, so write an equation."))
