import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import IntegralVideo, LIMIT, NEW, cap, eq


class BeginnerIntegral(IntegralVideo):
    DIFFICULTY = "Beginner"
    DATE = "2026-10-19"

    @staticmethod
    def FUNC(x):
        x = np.asarray(x, dtype=float)
        return x ** 2 * np.log(x)

    @classmethod
    def exact_integral(cls):
        return mp.quad(lambda x: x ** 2 * mp.log(x), [1, 2])

    LN = r"\ln(x)"
    COLORS = {LN: NEW, r"\frac{1}{x}": NEW}
    LIMS = (r"\int_{", ("1", LIMIT), r"}^{", ("2", LIMIT), r"}")
    BAR = (r"\Big]_{", ("1", LIMIT), r"}^{", ("2", LIMIT), r"}")
    PROBLEM = eq(*LIMS, "x^{2}", LN, r"\,dx")
    CURVE_LABEL = eq("y", "=", "x^{2}", LN)
    LABEL_AT = (0.15, 1.6)      # empty upper-left: the curve is below 0.5 for x < 1.2

    GRAPH = dict(x_range=[0, 2, 0.5], y_range=[-0.5, 3, 0.5], a=1, b=2, size=(8, 4.2), plot_range=(0.02, 2),
                 x_labels={0.5: "0.5", 1: "1", 1.5: "1.5", 2: "2"},
                 y_labels={1: "1", 2: "2", 3: "3"})

    HOOK = cap(r"A parabola times a logarithm. How do we undo a product?")
    INTUITION = cap(r"Thin rectangles estimate the area; watch the gap shrink.")
    INSIGHT = dict(
        parts=[LN],
        label=cap(r"let $u=\ln x$"),
        say=cap(r"Differentiating $\ln x$ gives $\frac{1}{x}$: simpler, not harder."),
    )

    STEPS = [
        dict(tex=eq(r"\Big[", r"\frac{x^{3}}{3}", LN, *BAR, "-", *LIMS, r"\frac{x^{3}}{3}", r"\cdot",
                    r"\frac{1}{x}", r"\,dx"),
             say=cap(r"Differentiate $\ln x$ to $\frac{1}{x}$; integrate $x^{2}$ to $\frac{x^{3}}{3}$."),
             rule=["integration_by_parts", "ln_derivative", "power_rule"],
             mapping={"integration_by_parts": [cap(r"Here $u=\ln x$ and $dv=x^{2}\,dx$, so $v=\frac{x^{3}}{3}$.")]}),
        dict(tex=eq(r"\Big[", r"\frac{x^{3}}{3}", LN, *BAR, "-", *LIMS, r"\frac{x^{2}}{3}", r"\,dx"),
             say=cap(r"One $x$ cancels: $\frac{x^{3}}{3}\cdot\frac{1}{x}=\frac{x^{2}}{3}$."),
             rule="algebra"),
        dict(tex=eq(r"\Big[", r"\frac{x^{3}}{3}", LN, "-", r"\frac{x^{3}}{9}", *BAR),
             say=cap(r"Power rule: $\int\frac{x^{2}}{3}\,dx=\frac{x^{3}}{9}$."),
             rule="power_rule"),
        dict(tex=eq(r"\Big(", r"\frac{8}{3}\ln 2", "-", r"\frac{8}{9}", r"\Big)", "-",
                    r"\Big(", "0", "-", r"\frac{1}{9}", r"\Big)"),
             say=cap(r"Top limit minus bottom; $\ln 1=0$ removes one term."),
             rule=["ftc", "log_values"]),
        dict(tex=eq(r"\frac{8}{3}\ln 2", "-", r"\frac{7}{9}"),
             say=cap(r"So the area is about $1.0706$."),
             rule="algebra"),
    ]

    ANSWER = eq(r"\frac{8}{3}\ln 2", "-", r"\frac{7}{9}")
    ANSWER_VALUE = float(8 / 3 * np.log(2) - 7 / 9)
    CLOSE_SAYS = (cap(r"Thin rectangles close in on $1.0706$."),
                  cap(r"Takeaway: in parts, let $u$ be the logarithm."))
