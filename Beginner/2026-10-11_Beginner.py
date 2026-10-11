import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import IntegralVideo, LIMIT, NEW, cap, eq


class BeginnerIntegral(IntegralVideo):
    DIFFICULTY = "Beginner"
    DATE = "2026-10-11"

    @staticmethod
    def FUNC(x):
        return (x + 1) ** 6 - x ** 6

    @classmethod
    def exact_integral(cls):
        return mp.quad(lambda x: (x + 1) ** 6 - x ** 6, [0, 1])

    COLORS = {"(x+1)^{6}": NEW, r"\frac{(x+1)^{7}}{7}": NEW}
    PROBLEM = eq(r"\int_{", ("0", LIMIT), r"}^{", ("1", LIMIT), r"}", r"\Big(", "(x+1)^{6}", "-", "x^{6}", r"\Big)",
                 r"\,dx")
    CURVE_LABEL = eq("y", "=", "(x+1)^{6}", "-", "x^{6}")
    LABEL_AT = (-0.48, 48)      # empty upper-left region, above the flat start of the curve

    GRAPH = dict(x_range=[-0.5, 1.25, 0.25], y_range=[0, 80, 20], a=0, b=1, size=(8, 4.2), plot_range=(-0.5, 1.05),
                 x_labels={-0.5: r"-\frac{1}{2}", 0.5: r"\frac{1}{2}", 1: "1"},
                 y_labels={20: "20", 40: "40", 60: "60", 80: "80"})

    HOOK = cap(r"How big is the green area from $x=0$ to $x=1$?")
    INTUITION = cap(r"Thin rectangles estimate the area; watch the gap shrink.")
    INSIGHT = dict(
        parts=["(x+1)^{6}"],
        label=cap(r"$x^{6}$ slid left by $1$"),
        say=cap(r"Both terms are sixth powers, so the power rule handles each."),
    )

    STEPS = [
        dict(tex=eq(r"\int_{", ("0", LIMIT), r"}^{", ("1", LIMIT), r"}", "(x+1)^{6}", r"\,dx", "-",
                    r"\int_{", ("0", LIMIT), r"}^{", ("1", LIMIT), r"}", "x^{6}", r"\,dx"),
             say=cap(r"Split the difference into two separate integrals."),
             rule="linearity",
             mapping=[cap(r"Here $f=(x+1)^{6}$ and $g=x^{6}$, with $a=1$, $b=-1$.")]),
        dict(tex=eq(r"\Big[", r"\frac{(x+1)^{7}}{7}", "-", r"\frac{x^{7}}{7}", r"\Big]_{", ("0", LIMIT), r"}^{",
                    ("1", LIMIT), r"}"),
             say=cap(r"Raise each power by one, then divide by $7$."),
             rule=["u_substitution", "power_rule"],
             mapping={"u_substitution": [cap(r"Let $u=x+1$, so $du=dx$ and $\int u^{6}\,du$ remains.")],
                      "power_rule": [cap(r"With $n=6$: $\int u^{6}\,du=\frac{u^{7}}{7}$; put back $u=x+1$.")]}),
        dict(tex=eq(r"\Big(", r"\frac{2^{7}}{7}", "-", r"\frac{1}{7}", r"\Big)", "-", r"\Big(", r"\frac{1}{7}", "-",
                    "0", r"\Big)"),
             say=cap(r"Upper limit minus lower limit."),
             rule="ftc",
             mapping=[cap(r"At $x=1$: $\frac{2^{7}}{7}-\frac{1}{7}$. At $x=0$: $\frac{1}{7}-0$.")]),
        dict(tex=eq(r"\frac{128}{7}", "-", r"\frac{2}{7}"),
             say=cap(r"$2^{7}=128$, and the two $\frac{1}{7}$ terms combine."),
             rule="algebra"),
        dict(tex=eq("18"),
             say=cap(r"$\frac{128-2}{7}=\frac{126}{7}=18$."),
             rule="algebra"),
    ]

    ANSWER = eq("18")
    ANSWER_VALUE = 18.0
    CLOSE_SAYS = (cap(r"More, thinner rectangles close in on $18$."),
                  cap(r"Takeaway: a shifted power like $(x+1)^{6}$ integrates like $x^{6}$."))
