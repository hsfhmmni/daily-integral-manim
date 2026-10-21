import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import IntegralVideo, LIMIT, NEW, cap, eq

P8 = float(np.pi / 8)
LN2 = float(np.log(2))


def h(t):
    """ln(1 + tan theta) with theta = t + pi/8, so the mirror line theta = pi/8 is t = 0."""
    return np.log(1 + np.tan(np.asarray(t, dtype=float) + P8))


def ln2_line(t):
    return LN2


class MediumIntegral(IntegralVideo):
    DIFFICULTY = "Medium"
    DATE = "2026-10-21"

    # x^2/(1+x^2) = 1 - 1/(1+x^2): int ln(1+x) = 2 ln 2 - 1 by parts, and with x = tan(theta)
    # the rest is int_0^{pi/4} ln(1+tan(theta)) = (pi/8) ln 2 (reflect theta in pi/8).
    @staticmethod
    def FUNC(x):
        x = np.asarray(x, dtype=float)
        return x ** 2 * np.log(1 + x) / (1 + x ** 2)

    @classmethod
    def exact_integral(cls):
        return mp.quad(lambda x: x ** 2 * mp.log(1 + x) / (1 + x ** 2), [0, 1])

    COLORS = {r"\tan\theta": NEW, r"\,d\theta": NEW}
    LIMS = (r"\int_{", ("0", LIMIT), r"}^{", ("1", LIMIT), r"}")
    TLIMS = (r"\int_{", ("0", LIMIT), r"}^{", (r"\frac{\pi}{4}", LIMIT), r"}")
    REST = (*LIMS, r"\frac{", r"\ln(1+x)", r"}{", "1+x^{2}", r"}", r"\,dx")
    HEAD = (r"2\ln 2", "-", "1", "-")
    PROBLEM = eq(*LIMS, r"\frac{", "x^{2}", r"\ln(1+x)", r"}{", "1+x^{2}", r"}", r"\,dx")
    CURVE_LABEL = eq("y", "=", r"\frac{", "x^{2}", r"\ln(1+x)", r"}{", "1+x^{2}", r"}")
    LABEL_AT = (0.03, 0.2)      # empty upper-left: the curve is below 0.06 for x < 0.45

    GRAPH = dict(x_range=[0, 1, 0.25], y_range=[0, 0.4, 0.1], a=0, b=1, size=(8, 4.2),
                 x_labels={0.5: "0.5", 1: "1"},
                 y_labels={0.1: "0.1", 0.2: "0.2", 0.3: "0.3"})

    HOOK = cap(r"No antiderivative in sight. How can this area be exact?")
    INTUITION = cap(r"Thin rectangles estimate the area; watch the gap shrink.")
    INSIGHT = dict(
        parts=["x^{2}", r"\ln(1+x)", "1+x^{2}"],
        label=cap(r"$x^{2}=(1+x^{2})-1$"),
        say=cap(r"Split the fraction: one easy integral, one with a twist."),
    )

    STEPS = [
        dict(tex=eq(*LIMS, r"\ln(1+x)", r"\,dx", "-", *REST),
             say=cap(r"$\frac{x^{2}}{1+x^{2}}=1-\frac{1}{1+x^{2}}$: split into two integrals."),
             rule="linearity"),
        dict(tex=eq(r"\Big[", r"(1+x)\ln(1+x)", "-", "x", r"\Big]_{", ("0", LIMIT), r"}^{", ("1", LIMIT), r"}",
                    "-", *REST),
             say=cap(r"By parts, choosing $v=1+x$ so that $v\,du=dx$."),
             rule=["integration_by_parts", "chain_rule", "ln_derivative"],
             mapping={"integration_by_parts": [cap(r"Here $u=\ln(1+x)$ and $dv=dx$; pick $v=1+x$.")],
                      "chain_rule": [cap(r"$\frac{d}{dx}\ln(1+x)=\frac{1}{1+x}$, so $v\,du=dx$.")]}),
        dict(tex=eq(*HEAD, *REST),
             say=cap(r"At $x=1$: $2\ln 2-1$. At $x=0$: $\ln 1=0$."),
             rule=["ftc", "log_values"]),
        dict(tex=eq(*HEAD, *TLIMS, r"\ln(1+", r"\tan\theta", ")", r"\,d\theta"),
             say=cap(r"Let $x=\tan\theta$: the factor $1+x^{2}$ cancels."),
             rule=["tan_substitution", "change_of_limits"],
             mapping={"tan_substitution": [cap(r"Here $dx=(1+x^{2})\,d\theta$, which cancels the bottom.")],
                      "change_of_limits": [cap(r"$x=0$ gives $\theta=0$; $x=1$ gives $\theta=\frac{\pi}{4}$.")]},
             highlight=([r"\,d\theta"], cap(r"$dx=(1+x^{2})\,d\theta$")), side=UP),
        dict(tex=eq(*HEAD, *TLIMS, r"\ln", r"\frac{2}{1+", r"\tan\theta", "}", r"\,d\theta"),
             say=cap(r"Replace $\theta$ by $\frac{\pi}{4}-\theta$: the area stays the same."),
             rule=["kings_rule", "tan_subtraction"],
             mapping={"kings_rule": [cap(r"Here $a=\frac{\pi}{4}$: a mirror in $\theta=\frac{\pi}{8}$.")],
                      "tan_subtraction": [cap(r"$1+\tan(\frac{\pi}{4}-\theta)=1+\frac{1-\tan\theta}{1+\tan\theta}=\frac{2}{1+\tan\theta}$.")]},
             then="reflection"),
        dict(tex=eq(*HEAD, r"\frac{1}{2}", *TLIMS, r"\Big(", r"\ln(1+", r"\tan\theta", ")", "+", r"\ln",
                    r"\frac{2}{1+", r"\tan\theta", "}", r"\Big)", r"\,d\theta"),
             say=cap(r"Both forms equal the same integral, so take their average."),
             rule="algebra"),
        dict(tex=eq(*HEAD, r"\frac{1}{2}", *TLIMS, r"\ln 2", r"\,d\theta"),
             say=cap(r"$\ln a+\ln\frac{2}{a}=\ln 2$: the $\tan\theta$ cancels."),
             rule="log_laws"),
        dict(tex=eq(*HEAD, r"\frac{\pi}{8}", r"\ln 2"),
             say=cap(r"Half of $\ln 2$ times the width $\frac{\pi}{4}$ is $\frac{\pi}{8}\ln 2$."),
             rule=["power_rule", "ftc"]),
    ]

    REFLECTION = dict(
        spec=dict(x_range=[-P8, P8, P8 / 2], y_range=[0, 1, 0.2], size=(8, 3.6), var=r"\theta",
                  x_labels={-P8: "0", 0: r"\frac{\pi}{8}", P8: r"\frac{\pi}{4}"},
                  y_labels={0.8: "0.8"},       # a 0.4 label would sit where the two curves cross
                  sum=ln2_line, sum_label=r"\ln 2", label_side=UP),
        func=h, mode="mirror",
        says=(cap(r"Mirror $\ln(1+\tan\theta)$ in the middle line $\theta=\frac{\pi}{8}$."),
              cap(r"The curve and its mirror always add up to $\ln 2$.")),
    )

    ANSWER = eq(*HEAD, r"\frac{\pi}{8}", r"\ln 2")
    ANSWER_VALUE = float(2 * np.log(2) - 1 - np.pi * np.log(2) / 8)
    CLOSE_SAYS = (cap(r"Thin rectangles close in on $0.1141$."),
                  cap(r"Takeaway: after $x=\tan\theta$, try reflecting $\theta$ in the middle."))
