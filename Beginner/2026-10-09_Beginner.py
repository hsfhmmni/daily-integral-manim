import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import IntegralVideo, LIMIT, NEW, cap, eq

LN3 = float(np.log(3))


class BeginnerIntegral(IntegralVideo):
    DIFFICULTY = "Beginner"
    DATE = "2026-10-09"

    @staticmethod
    def FUNC(x):
        return np.exp(x) / (1 + np.exp(2 * x))

    @classmethod
    def exact_integral(cls):
        return mp.quad(lambda x: mp.e ** x / (1 + mp.e ** (2 * x)), [0, mp.log(3)])

    COLORS = {"e^{x}": NEW, "e^{2x}": NEW, "(e^{x})^{2}": NEW, "u": NEW, "u^{2}": NEW}
    PROBLEM = eq(r"\int_{", ("0", LIMIT), r"}^{", (r"\ln 3", LIMIT), r"}", r"\frac{", "e^{x}", r"}{1+", "e^{2x}", r"}",
                 r"\,dx")
    CURVE_LABEL = eq("y", "=", r"\frac{", "e^{x}", r"}{1+", "e^{2x}", r"}")
    LABEL_AT = (0.6, 0.5)       # empty space above the falling right half of the curve

    GRAPH = dict(x_range=[0, 1.5, 0.5], y_range=[0, 0.8, 0.2], a=0, b=LN3, size=(8, 4.2), plot_range=(0, 1.45),
                 x_labels={0.5: "0.5", LN3: r"\ln 3"}, y_labels={0.2: "0.2", 0.4: "0.4", 0.6: "0.6", 0.8: "0.8"})

    HOOK = cap(r"How big is the green area from $x=0$ to $x=\ln 3$?")
    INTUITION = cap(r"Thin rectangles estimate the area; watch the gap shrink.")
    INSIGHT = dict(
        before=cap(r"Look at the bottom: $e^{2x}$ hides the top, $e^{x}$."),
        parts=["e^{2x}"],
        label=cap(r"$e^{2x}=(e^{x})^{2}$"),
        say=cap(r"So set $u=e^{x}$: the bottom becomes $1+u^{2}$."),
    )

    STEPS = [
        dict(tex=eq(r"\int_{", ("0", LIMIT), r"}^{", (r"\ln 3", LIMIT), r"}", r"\frac{1}{1+", "(e^{x})^{2}", r"}",
                    "e^{x}", r"\,dx"),
             say=cap(r"Write $e^{2x}=(e^{x})^{2}$ and move $e^{x}$ beside $dx$.")),
        dict(tex=eq(r"\int_{", ("1", LIMIT), r"}^{", ("3", LIMIT), r"}", r"\frac{1}{1+", "u^{2}", r"}", r"\,d", "u"),
             say=cap(r"With $u=e^{x}$, $du=e^{x}\,dx$; the limits become $1$ and $3$."),
             then="substitution"),
        dict(tex=eq(r"\Big[", r"\tan^{-1}", "u", r"\Big]_{", ("1", LIMIT), r"}^{", ("3", LIMIT), r"}"),
             say=cap(r"$\frac{1}{1+u^{2}}$ is the derivative of $\tan^{-1}u$.")),
        dict(tex=eq(r"\tan^{-1}", "3", "-", r"\tan^{-1}", "1"),
             say=cap(r"Upper limit minus lower limit.")),
        dict(tex=eq(r"\tan^{-1}", "3", "-", r"\frac{\pi}{4}"),
             say=cap(r"$\tan^{-1}1=\frac{\pi}{4}$, because $\tan\frac{\pi}{4}=1$.")),
        dict(tex=eq(r"\tan^{-1}", "3", "-", r"\frac{\pi}{4}", "=", r"\tan^{-1}\frac{1}{2}"),
             say=cap(r"Subtraction formula: $\frac{3-1}{1+3\cdot 1}=\frac{1}{2}$.")),
    ]

    SUBSTITUTION = dict(
        u_graph=dict(x_range=[0, 4, 1], y_range=[0, 0.8, 0.2], a=1, b=3, var="u", size=(8, 4.2), plot_range=(0.6, 3.8),
                     x_labels={1: "1", 2: "2", 3: "3"}, y_labels={0.2: "0.2", 0.4: "0.4", 0.6: "0.6"}),
        u_func=lambda u: 1 / (1 + u ** 2),
        says=(cap(r"In $x$: the green area is about $0.464$."),
              cap(r"In $u$: the curve is $\frac{1}{1+u^{2}}$, and the area is unchanged.")),
    )

    ANSWER = eq(r"\tan^{-1}", "3", "-", r"\frac{\pi}{4}")
    ANSWER_VALUE = float(np.arctan(3) - np.pi / 4)
    CLOSE_SAYS = (cap(r"More, thinner rectangles close in on $\tan^{-1}3-\frac{\pi}{4}\approx 0.4636$."),
                  cap(r"Takeaway: spot $1+u^{2}$ in disguise, then expect an inverse tangent."))
