import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import IntegralVideo, LIMIT, cap, eq

Q = float(3 + 2 * np.sqrt(2))           # upper limit, about 5.83
H = float(3 - 2 * np.sqrt(2))           # = 1/Q, the constant height, about 0.172


class BeginnerIntegral(IntegralVideo):
    DIFFICULTY = "Beginner"
    DATE = "2026-10-12"

    @staticmethod
    def FUNC(x):
        # (3-2*sqrt2)^((5x+3)^2) * (3+2*sqrt2)^((5x+4)(5x+2)) is the constant 3-2*sqrt2 exactly;
        # the literal powers overflow a float near the top limit, so the constant is plotted
        return H + 0 * np.asarray(x, dtype=float)

    @classmethod
    def exact_integral(cls):
        with mp.workdps(30):
            q = 3 + 2 * mp.sqrt(2)
            f = lambda x: (3 - 2 * mp.sqrt(2)) ** ((5 * x + 3) ** 2) * q ** ((5 * x + 4) * (5 * x + 2))
            return mp.quad(f, [0, q])

    PROBLEM_X = (-6.2, 3.3)     # a long line: shift it left, clear of the badge
    LIMS = (r"\int_{", ("0", LIMIT), r"}^{", (r"3+2\sqrt{2}", LIMIT), r"}")
    PROBLEM = eq(*LIMS, r"(3-2\sqrt{2})", r"^{(5x+3)^{2}}", r"\cdot", r"(3+2\sqrt{2})", r"^{(5x+4)(5x+2)}", r"\,dx")
    CURVE_LABEL = eq("y", "=", r"(3-2\sqrt{2})", r"^{(5x+3)^{2}}", r"\cdot", r"(3+2\sqrt{2})", r"^{(5x+4)(5x+2)}")
    LABEL_AT = (0.3, 0.215)     # empty band above the flat line at height 0.17

    GRAPH = dict(x_range=[0, 6.5, 1], y_range=[0, 0.3, 0.1], a=0, b=Q, size=(8, 4.2),
                 x_labels={2: "2", 4: "4", Q: r"3+2\sqrt{2}"},
                 y_labels={0.1: "0.1", 0.2: "0.2", 0.3: "0.3"})

    HOOK = cap(r"Two enormous powers, yet the curve is perfectly flat. Why?")
    INTUITION = cap(r"Thin rectangles estimate the area; watch the gap shrink.")
    INSIGHT = dict(
        parts=[r"(3-2\sqrt{2})", r"(3+2\sqrt{2})"],
        label=cap(r"product $=1$"),
        say=cap(r"These bases multiply to $1$: each is the other's reciprocal."),
    )

    STEPS = [
        dict(tex=eq(*LIMS, r"(3+2\sqrt{2})", r"^{-(5x+3)^{2}}", r"\cdot", r"(3+2\sqrt{2})", r"^{(5x+4)(5x+2)}",
                    r"\,dx"),
             say=cap(r"Write $3-2\sqrt{2}$ as $(3+2\sqrt{2})^{-1}$: that power turns negative."),
             rule="exponent_laws"),
        dict(tex=eq(*LIMS, r"(3+2\sqrt{2})", r"^{(5x+4)(5x+2)", r"-(5x+3)^{2}}", r"\,dx"),
             say=cap(r"Same base, so multiplying the powers adds the exponents."),
             rule="exponent_laws"),
        dict(tex=eq(*LIMS, r"(3+2\sqrt{2})", r"^{(", r"25x^{2}+30x", r"+8)-(", r"25x^{2}+30x", r"+9)}", r"\,dx"),
             say=cap(r"Expand both: $25x^{2}+30x$ appears twice and cancels."),
             highlight=([r"25x^{2}+30x"], cap(r"the same twice")),
             rule="algebra"),
        dict(tex=eq(*LIMS, r"(3+2\sqrt{2})", r"^{-1}", r"\,dx"),
             say=cap(r"Only $8-9=-1$ survives in the exponent."),
             rule="algebra"),
        dict(tex=eq(*LIMS, r"(3-2\sqrt{2})", r"\,dx"),
             say=cap(r"So the height is the constant $3-2\sqrt{2}\approx 0.17$."),
             rule="exponent_laws"),
        dict(tex=eq(r"(", (r"3+2\sqrt{2}", LIMIT), r")", r"(3-2\sqrt{2})"),
             say=cap(r"A constant height: the area is width times height."),
             rule=["power_rule", "ftc"]),
        dict(tex=eq("9", "-", "8"),
             say=cap(r"Difference of squares: $3^{2}-(2\sqrt{2})^{2}=9-8$."),
             rule="algebra"),
    ]

    ANSWER = eq("1")
    ANSWER_VALUE = 1.0
    CLOSE_SAYS = (cap(r"Every rectangle has the same height: the estimate is exactly $1$."),
                  cap(r"Takeaway: check whether two bases are reciprocals before integrating."))
