import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import IntegralVideo, LIMIT, NEW, cap, eq


class BeginnerIntegral(IntegralVideo):
    DIFFICULTY = "Beginner"
    DATE = "2026-10-08"

    @staticmethod
    def FUNC(x):
        return 3 * x ** 2 * np.sqrt(x ** 3 + 5)

    @classmethod
    def exact_integral(cls):
        return mp.quad(lambda x: 3 * x ** 2 * mp.sqrt(x ** 3 + 5), [-1, 1])

    COLORS = {"x^{3}+5": NEW, "u": NEW, "u^{1/2}": NEW, "u^{3/2}": NEW}
    PROBLEM = eq(r"\int_{", ("-1", LIMIT), r"}^{", ("1", LIMIT), r"}", "3x^{2}", r"\sqrt{", "x^{3}+5", r"}", r"\,dx")
    CURVE_LABEL = eq("y", "=", "3x^{2}", r"\sqrt{", "x^{3}+5", r"}")
    LABEL_AT = (1.12, 5.6)      # just right of the curve's end at x = 1

    GRAPH = dict(x_range=[-1.5, 1.5, 0.5], y_range=[0, 8, 2], a=-1, b=1, size=(8, 4.2), plot_range=(-1.15, 1.02),
                 x_labels={-1: "-1", 1: "1"}, y_labels={2: "2", 4: "4", 6: "6", 8: "8"})

    HOOK = cap(r"How big is the green area between $x=-1$ and $x=1$?")
    INTUITION = cap(r"Thin rectangles estimate the area; watch the gap shrink.")
    INSIGHT = dict(
        before=cap(r"Look under the root: $x^{3}+5$, in orange."),
        parts=["3x^{2}"],
        label=cap(r"$\frac{d}{dx}(x^{3}+5)=3x^{2}$"),
        say=cap(r"Its derivative is already in front, so substitute."),
    )

    STEPS = [
        dict(tex=eq(r"\int_{", ("-1", LIMIT), r"}^{", ("1", LIMIT), r"}", r"\sqrt{", "x^{3}+5", r"}", "3x^{2}", r"\,dx"),
             say=cap(r"Move $3x^{2}$ next to $dx$: together they make $du$.")),
        dict(tex=eq(r"\int_{", ("4", LIMIT), r"}^{", ("6", LIMIT), r"}", r"\sqrt{", "u", r"}", r"\,d", "u"),
             say=cap(r"With $u=x^{3}+5$, the limits $-1$ and $1$ become $4$ and $6$."),
             then="substitution"),
        dict(tex=eq(r"\int_{", ("4", LIMIT), r"}^{", ("6", LIMIT), r"}", "u^{1/2}", r"\,d", "u"),
             say=cap(r"A square root is the power $\frac{1}{2}$.")),
        dict(tex=eq(r"\Big[", r"\frac{2}{3}", "u^{3/2}", r"\Big]_{", ("4", LIMIT), r"}^{", ("6", LIMIT), r"}"),
             say=cap(r"Power rule: add one to the power, then divide by it.")),
        dict(tex=eq(r"\frac{2}{3}", r"\Big(", "6^{3/2}", "-", "4^{3/2}", r"\Big)"),
             say=cap(r"Upper limit minus lower limit.")),
        dict(tex=eq(r"\frac{2}{3}", r"\Big(", r"6\sqrt{6}", "-", "8", r"\Big)"),
             say=cap(r"$6^{3/2}=6\sqrt{6}$ and $4^{3/2}=8$.")),
    ]

    SUBSTITUTION = dict(
        u_graph=dict(x_range=[3, 7, 1], y_range=[0, 3, 1], a=4, b=6, var="u", size=(8, 4.2), plot_range=(3.2, 6.8),
                     x_labels={4: "4", 5: "5", 6: "6"}, y_labels={1: "1", 2: "2", 3: "3"}),
        u_func=lambda u: np.sqrt(u),
        says=(cap(r"In $x$: the green area is about $4.465$."),
              cap(r"In $u$: the curve is $\sqrt{u}$, and the area is unchanged.")),
    )

    ANSWER = eq(r"4\sqrt{6}-\frac{16}{3}")
    ANSWER_VALUE = float(4 * np.sqrt(6) - 16 / 3)
    CLOSE_SAYS = (cap(r"More, thinner rectangles close in on $4\sqrt{6}-\frac{16}{3}$."),
                  cap(r"Takeaway: spot an inside function whose derivative is also present."))
