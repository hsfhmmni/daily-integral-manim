import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import IntegralVideo, LIMIT, NEW, cap, eq

HP = float(np.pi / 2)


def f(x):
    return np.exp(-x) * np.cos(x) / np.cosh(x)


class MediumIntegral(IntegralVideo):
    DIFFICULTY = "Medium"
    DATE = "2026-10-12"

    @staticmethod
    def FUNC(x):
        return f(x)

    @classmethod
    def exact_integral(cls):
        return mp.quad(lambda x: mp.exp(-x) * mp.cos(x) / mp.cosh(x), [-mp.pi / 2, mp.pi / 2])

    COLORS = {r"e^{-x}": NEW, r"e^{x}": NEW}
    LIMS = (r"\int_{", (r"-\frac{\pi}{2}", LIMIT), r"}^{", (r"\frac{\pi}{2}", LIMIT), r"}")
    PROBLEM = eq(*LIMS, r"\frac{", r"e^{-x}", r"\cos x", r"}{", r"\cosh x", r"}", r"\,dx")
    CURVE_LABEL = eq("y", "=", r"\frac{", r"e^{-x}", r"\cos x", r"}{", r"\cosh x", r"}")
    LABEL_AT = (0.45, 0.95)     # empty upper-right region; the curve is below 0.5 for x > 0.5

    GRAPH = dict(x_range=[-2, 2, 1], y_range=[0, 1.5, 0.5], a=-HP, b=HP, size=(8, 4.2), plot_range=(-HP, HP),
                 x_labels={-HP: r"-\frac{\pi}{2}", HP: r"\frac{\pi}{2}"},
                 y_labels={0.5: "0.5", 1: "1", 1.5: "1.5"})

    HOOK = cap(r"A lopsided curve on symmetric limits. Can a mirror even it out?")
    INTUITION = cap(r"Thin rectangles estimate the area; watch the gap shrink.")
    INSIGHT = dict(
        parts=[r"e^{-x}"],
        label=cap(r"$x\to -x$"),
        side=UP,                # below, the arrow would cross the denominator
        say=cap(r"Only $e^{-x}$ changes under $x\to -x$; $\cos$ and $\cosh$ are even."),
    )

    STEPS = [
        dict(tex=eq("I", "=", *LIMS, r"\frac{", r"e^{x}", r"\cos x", r"}{", r"\cosh x", r"}", r"\,dx"),
             say=cap(r"Mirror $x\to -x$: same limits, same area, now with $e^{x}$."),
             rule="reflection_property",
             mapping=[cap(r"Here $f(-x)=\frac{e^{x}\cos x}{\cosh x}$, since $\cos$ and $\cosh$ are even.")],
             then="reflection"),
        dict(tex=eq("2I", "=", *LIMS, r"\frac{", r"(e^{-x}+e^{x})", r"\cos x", r"}{", r"\cosh x", r"}", r"\,dx"),
             say=cap(r"Add the original and its mirror: two copies of $I$."),
             rule="linearity"),
        dict(tex=eq("2I", "=", *LIMS, r"\frac{", r"2\cosh x", r"\cos x", r"}{", r"\cosh x", r"}", r"\,dx"),
             say=cap(r"The bracket is exactly $2\cosh x$, so $\cosh x$ cancels."),
             highlight=([r"2\cosh x", r"\cosh x"], cap(r"cancel")),
             rule="cosh_definition",
             mapping=[cap(r"So $e^{-x}+e^{x}=2\cosh x$.")]),
        dict(tex=eq("2I", "=", *LIMS, r"2\cos x", r"\,dx"),
             say=cap(r"What is left is the even curve $2\cos x$."),
             rule="algebra"),
        dict(tex=eq("2I", "=", r"\Big[", r"2\sin x", r"\Big]_{", (r"-\frac{\pi}{2}", LIMIT), r"}^{",
                    (r"\frac{\pi}{2}", LIMIT), r"}"),
             say=cap(r"Integrate: $\int 2\cos x\,dx=2\sin x$."),
             rule=["cos_integral", "linearity"]),
        dict(tex=eq("2I", "=", "4"),
             say=cap(r"$2\sin\frac{\pi}{2}-2\sin\big(-\frac{\pi}{2}\big)=2+2=4$."),
             rule="ftc"),
        dict(tex=eq("I", "=", "2"),
             say=cap(r"Halve it: $I=2$."),
             rule="algebra"),
    ]

    REFLECTION = dict(
        spec=dict(x_range=[-HP, HP, 1], y_range=[0, 2.2, 0.5], size=(8, 3.6),
                  x_labels={-HP: r"-\frac{\pi}{2}", HP: r"\frac{\pi}{2}"},
                  y_labels={1: "1"},      # a "2" label would sit under the 2cos x label
                  sum=lambda x: 2 * np.cos(x), sum_label=r"2\cos x", label_side=RIGHT),
        func=f,
        mode="mirror",
        says=(cap(r"Mirror the curve in the $y$-axis: the area stays the same."),
              cap(r"Together they make $2\cos x$: the lean cancels out.")),
    )

    ANSWER = eq("2")
    ANSWER_VALUE = 2.0
    CLOSE_SAYS = (cap(r"Thin rectangles agree: the lopsided area is exactly $2$."),
                  cap(r"Takeaway: on symmetric limits, add $f(x)$ and $f(-x)$."))
