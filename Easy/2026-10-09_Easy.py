import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import IntegralVideo, LIMIT, NEW, cap, eq

PI6 = float(np.pi / 6)


class EasyIntegral(IntegralVideo):
    DIFFICULTY = "Easy"
    DATE = "2026-10-09"

    @staticmethod
    def FUNC(x):
        return np.cos(x) / (2 + np.sin(x))

    @classmethod
    def exact_integral(cls):
        return mp.quad(lambda x: mp.cos(x) / (2 + mp.sin(x)), [0, mp.pi / 6])

    COLORS = {r"2+\sin x": NEW, "u": NEW}
    PROBLEM = eq(r"\int_{", ("0", LIMIT), r"}^{", (r"\frac{\pi}{6}", LIMIT), r"}", r"\frac{", r"\cos x", r"}{",
                 r"2+\sin x", r"}", r"\,dx")
    CURVE_LABEL = eq("y", "=", r"\frac{", r"\cos x", r"}{", r"2+\sin x", r"}")
    LABEL_AT = (0.55, 0.5)      # empty space above the right part of the curve

    GRAPH = dict(x_range=[0, 1, 0.25], y_range=[0, 0.8, 0.2], a=0, b=PI6, size=(8, 4.2), plot_range=(0, 0.98),
                 x_labels={PI6: r"\frac{\pi}{6}", 1: "1"}, y_labels={0.2: "0.2", 0.4: "0.4", 0.6: "0.6", 0.8: "0.8"})

    HOOK = cap(r"How big is the green area from $0$ to $\frac{\pi}{6}$?")
    INTUITION = cap(r"Thin rectangles estimate the area; watch the gap shrink.")
    INSIGHT = dict(
        before=cap(r"Look at the bottom, $2+\sin x$, in orange."),
        parts=[r"\cos x"],
        side=UP,                # below would cross the denominator
        label=cap(r"$\frac{d}{dx}(2+\sin x)=\cos x$"),
        say=cap(r"The top is the bottom's derivative, so substitute."),
    )

    STEPS = [
        dict(tex=eq(r"\int_{", ("0", LIMIT), r"}^{", (r"\frac{\pi}{6}", LIMIT), r"}", r"\frac{1}{", r"2+\sin x", r"}",
                    r"\cos x", r"\,dx"),
             say=cap(r"Move $\cos x$ beside $dx$: together they make $du$.")),
        dict(tex=eq(r"\int_{", ("2", LIMIT), r"}^{", (r"\frac{5}{2}", LIMIT), r"}", r"\frac{1}{", "u", r"}", r"\,d", "u"),
             say=cap(r"With $u=2+\sin x$, the limits become $2$ and $\frac{5}{2}$."),
             then="substitution"),
        dict(tex=eq(r"\Big[", r"\ln ", "u", r"\Big]_{", ("2", LIMIT), r"}^{", (r"\frac{5}{2}", LIMIT), r"}"),
             say=cap(r"$\frac{1}{u}$ is the derivative of $\ln u$, and here $u>0$.")),
        dict(tex=eq(r"\ln\frac{5}{2}", "-", r"\ln 2"),
             say=cap(r"Upper limit minus lower limit.")),
        dict(tex=eq(r"\ln\frac{5}{4}"),
             say=cap(r"$\ln a-\ln b=\ln\frac{a}{b}$, and $\frac{5}{2}\div 2=\frac{5}{4}$.")),
    ]

    SUBSTITUTION = dict(
        u_graph=dict(x_range=[0, 3, 0.5], y_range=[0, 1.5, 0.5], a=2, b=2.5, var="u", size=(8, 4.2),
                     plot_range=(0.7, 3), x_labels={1: "1", 2: "2", 2.5: r"\frac{5}{2}"},
                     y_labels={0.5: "0.5", 1: "1", 1.5: "1.5"}),
        u_func=lambda u: 1 / u,
        says=(cap(r"In $x$: the green area is about $0.223$."),
              cap(r"In $u$: the curve is $\frac{1}{u}$, and the area is unchanged.")),
    )

    ANSWER = eq(r"\ln\frac{5}{4}")
    ANSWER_VALUE = float(np.log(1.25))
    CLOSE_SAYS = (cap(r"More, thinner rectangles close in on $\ln\frac{5}{4}\approx 0.2231$."),
                  cap(r"Takeaway: when the top is the bottom's derivative, expect a logarithm."))
