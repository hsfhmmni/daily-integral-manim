import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import IntegralVideo, LIMIT, NEW, cap, eq

E = float(np.e)
E1 = E + 1                  # the new upper limit, about 3.72


class BeginnerIntegral(IntegralVideo):
    DIFFICULTY = "Beginner"
    DATE = "2026-10-13"

    @staticmethod
    def FUNC(x):
        return 1 / (x ** 2 + 2 * x + 2)

    @classmethod
    def exact_integral(cls):
        return mp.quad(lambda x: 1 / (x ** 2 + 2 * x + 2), [1, mp.e])

    COLORS = {"(x+1)": NEW, "u": NEW}
    PROBLEM = eq(r"\int_{", ("1", LIMIT), r"}^{", ("e", LIMIT), r"}", r"\frac{1}{", r"x^{2}+2x+2", r"}", r"\,dx")
    CURVE_LABEL = eq("y", "=", r"\frac{1}{", r"x^{2}+2x+2", r"}")
    LABEL_AT = (1.5, 0.3)       # empty space above the curve, which is below 0.2 for x > 1

    GRAPH = dict(x_range=[0, 3.5, 0.5], y_range=[0, 0.6, 0.2], a=1, b=E, size=(8, 4.2), plot_range=(0, 3.5),
                 x_labels={1: "1", 2: "2", E: "e", 3.5: "3.5"},
                 y_labels={0.2: "0.2", 0.4: "0.4", 0.6: "0.6"})

    HOOK = cap(r"No power rule fits this curve. How big is the green area?")
    INTUITION = cap(r"Thin rectangles estimate the area; watch the gap shrink.")
    INSIGHT = dict(
        parts=[r"x^{2}+2x+2"],
        label=cap(r"$(x+1)^{2}+1$"),
        say=cap(r"Complete the square: the bottom is a square plus $1$."),
    )

    STEPS = [
        dict(tex=eq(r"\int_{", ("1", LIMIT), r"}^{", ("e", LIMIT), r"}", r"\frac{1}{", "(x+1)", r"^{2}+1", r"}",
                    r"\,dx"),
             say=cap(r"Rewrite the bottom as $(x+1)^{2}+1$."),
             rule="completing_the_square",
             mapping=[cap(r"Here $b=1$: $x^{2}+2x+2=(x+1)^{2}+1$.")]),
        dict(tex=eq(r"\int_{", ("2", LIMIT), r"}^{", ("e+1", LIMIT), r"}", r"\frac{1}{", "u", r"^{2}+1", r"}",
                    r"\,d", "u"),
             say=cap(r"Let $u=x+1$: the limits $1$ and $e$ become $2$ and $e+1$."),
             rule=["u_substitution", "change_of_limits"],
             mapping={"u_substitution": [cap(r"Here $u=x+1$, so $du=dx$.")],
                      "change_of_limits": [cap(r"$x=1$ gives $u=2$; $x=e$ gives $u=e+1$.")]},
             then="substitution"),
        dict(tex=eq(r"\Big[", r"\tan^{-1}", "u", r"\Big]_{", ("2", LIMIT), r"}^{", ("e+1", LIMIT), r"}"),
             say=cap(r"$\frac{1}{u^{2}+1}$ integrates to $\tan^{-1}u$."),
             rule="arctan_integral",
             mapping=[cap(r"Here the variable is $u$, so we get $\tan^{-1}u$.")]),
        dict(tex=eq(r"\tan^{-1}", r"(e+1)", "-", r"\tan^{-1}", "2"),
             say=cap(r"Top limit minus bottom limit."),
             rule="ftc"),
    ]

    SUBSTITUTION = dict(
        u_graph=dict(x_range=[0, 4.5, 0.5], y_range=[0, 0.6, 0.2], a=2, b=E1, var="u", size=(8, 4.2),
                     plot_range=(1, 4.5), x_labels={1: "1", 2: "2", E1: "e+1", 4.5: "4.5"},
                     y_labels={0.2: "0.2", 0.4: "0.4", 0.6: "0.6"}),
        u_func=lambda u: 1 / (u ** 2 + 1),
        says=(cap(r"In $x$: the green area is about $0.201$."),
              cap(r"In $u$: the curve slides right by $1$; the area stays.")),
    )

    ANSWER = eq(r"\tan^{-1}", r"(e+1)", "-", r"\tan^{-1}", "2")
    ANSWER_VALUE = float(np.arctan(E1) - np.arctan(2))
    CLOSE_SAYS = (cap(r"Thin rectangles close in on $0.2009$."),
                  cap(r"Takeaway: square plus $1$ on the bottom means inverse tangent."))
