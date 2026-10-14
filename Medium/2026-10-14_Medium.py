import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import IntegralVideo, LIMIT, NEW, cap, eq

B = float(2 - np.sqrt(3))       # the upper limit tan(pi/12), about 0.268
P12 = float(np.pi / 12)


class MediumIntegral(IntegralVideo):
    DIFFICULTY = "Medium"
    DATE = "2026-10-14"

    @staticmethod
    def FUNC(x):
        return 6 * x * (3 - x ** 2) / (1 - 2 * x ** 2 - 3 * x ** 4)

    @classmethod
    def exact_integral(cls):
        return mp.quad(lambda x: 6 * x * (3 - x ** 2) / (1 - 2 * x ** 2 - 3 * x ** 4), [0, 2 - mp.sqrt(3)])

    COLORS = {r"(1+x^{2})": NEW, r"\,d\theta": NEW, r"\tan 3\theta": NEW}
    LIMS = (r"\int_{", ("0", LIMIT), r"}^{", (r"2-\sqrt{3}", LIMIT), r"}")
    LIMT = (r"\int_{", ("0", LIMIT), r"}^{", (r"\frac{\pi}{12}", LIMIT), r"}")
    PROBLEM = eq(*LIMS, r"\frac{", r"6x(3-x^{2})", r"}{", r"1-2x^{2}-3x^{4}", r"}", r"\,dx")
    CURVE_LABEL = eq("y", "=", r"\frac{", r"6x(3-x^{2})", r"}{", r"1-2x^{2}-3x^{4}", r"}")
    LABEL_AT = (0.01, 3.9)      # empty upper-left corner: the curve is below 2.5 for x < 0.12

    GRAPH = dict(x_range=[0, 0.3, 0.05], y_range=[0, 7, 1], a=0, b=B, size=(8, 4.2), plot_range=(0, 0.28),
                 x_labels={0.1: "0.1", B: r"2-\sqrt{3}"},
                 y_labels={2: "2", 4: "4", 6: "6"})

    HOOK = cap(r"A rational function, but why does it stop at $2-\sqrt{3}$?")
    INTUITION = cap(r"Thin rectangles estimate the area; watch the gap shrink.")
    INSIGHT = dict(
        parts=[r"1-2x^{2}-3x^{4}"],
        label=cap(r"$(1-3x^{2})(1+x^{2})$"),
        say=cap(r"The bottom factorises, and $1+x^{2}$ hints at $x=\tan\theta$."),
    )

    STEPS = [
        dict(tex=eq(*LIMS, r"\frac{", r"6x(3-x^{2})", r"}{", r"(1-3x^{2})", r"(1+x^{2})", r"}", r"\,dx"),
             say=cap(r"Factor the bottom: a quadratic in $x^{2}$."),
             highlight=([r"(1+x^{2})", r"\,dx"], cap(r"becomes $d\theta$")),
             rule="algebra"),
        dict(tex=eq(*LIMT, r"\frac{", r"6\tan\theta(3-\tan^{2}\theta)", r"}{", r"1-3\tan^{2}\theta", r"}",
                    r"\,d\theta"),
             say=cap(r"Let $x=\tan\theta$: $dx=(1+x^{2})\,d\theta$ cancels that factor."),
             rule=["tan_substitution", "change_of_limits"],
             mapping={"tan_substitution": [cap(r"Here $x=\tan\theta$, so $(1+x^{2})\,dx$ leaves just $d\theta$.")],
                      "change_of_limits": [cap(r"$\tan 0=0$ and $\tan\frac{\pi}{12}=2-\sqrt{3}$.")]}),
        dict(tex=eq(*LIMT, "6", r"\tan 3\theta", r"\,d\theta"),
             say=cap(r"The fraction is exactly $\tan 3\theta$."),
             rule="tan_triple_angle",
             mapping=[cap(r"Top $3\tan\theta-\tan^{3}\theta$ over $1-3\tan^{2}\theta$: the formula.")],
             then="substitution"),
        dict(tex=eq(r"\Big[", r"-2\ln|\cos 3\theta|", r"\Big]_{", ("0", LIMIT), r"}^{", (r"\frac{\pi}{12}", LIMIT),
                    r"}"),
             say=cap(r"Integrate $\tan 3\theta$; dividing by $3$ turns $6$ into $2$."),
             rule="tan_integral",
             mapping=[cap(r"Inside is $3\theta$, so the chain rule divides by $3$.")]),
        dict(tex=eq(r"-2\ln\cos\frac{\pi}{4}", "+", r"2\ln\cos 0"),
             say=cap(r"At $\theta=\frac{\pi}{12}$ the angle $3\theta$ is $\frac{\pi}{4}$."),
             rule="ftc"),
        dict(tex=eq("-2", r"\ln\frac{1}{\sqrt{2}}"),
             say=cap(r"$\cos\frac{\pi}{4}=\frac{1}{\sqrt{2}}$, and $\ln 1=0$ removes the second term."),
             rule="log_values"),
        dict(tex=eq(r"\ln 2"),
             say=cap(r"$-2\ln 2^{-\frac{1}{2}}=\ln 2$."),
             rule="log_laws"),
    ]

    SUBSTITUTION = dict(
        u_graph=dict(x_range=[0, 0.3, 0.05], y_range=[0, 7, 1], a=0, b=P12, var=r"\theta", size=(7.4, 3.8),
                     plot_range=(0, 0.27), x_labels={0.1: "0.1", P12: r"\frac{\pi}{12}"},
                     y_labels={2: "2", 4: "4", 6: "6"}),
        u_func=lambda t: 6 * np.tan(3 * t),
        says=(cap(r"In $x$: the green area is about $0.693$."),
              cap(r"In $\theta$: the curve $6\tan 3\theta$, the same area.")),
    )

    ANSWER = eq(r"\ln 2")
    ANSWER_VALUE = float(np.log(2))
    CLOSE_SAYS = (cap(r"Thin rectangles close in on $\ln 2\approx 0.6931$."),
                  cap(r"Takeaway: a factor $1+x^{2}$ invites $x=\tan\theta$."))
