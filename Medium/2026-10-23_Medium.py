import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import IntegralVideo, LIMIT, NEW, cap, eq

P2 = float(np.pi / 2)
P4 = float(np.pi / 4)


class MediumIntegral(IntegralVideo):
    DIFFICULTY = "Medium"
    DATE = "2026-10-23"

    # t = tan(x/2): the integral is int_0^1 dt / (6t^2 + t + 6) = (1/6) int dt / ((t + 1/12)^2 + 143/144)
    # = (2/sqrt143) [atan((12t+1)/sqrt143)]_0^1, and atan(13/r) - atan(1/r) = atan(r/13), r = sqrt143.
    @staticmethod
    def FUNC(x):
        return 1 / (12 + np.sin(np.asarray(x, dtype=float)))

    @classmethod
    def exact_integral(cls):
        return mp.quad(lambda x: 1 / (12 + mp.sin(x)), [0, mp.pi / 2])

    COLORS = {r"\sin(x)": NEW, r"\frac{2t}{1+t^{2}}": NEW, r"\frac{2}{1+t^{2}}": NEW, r"\,dt": NEW}
    LIMS = (r"\int_{", ("0", LIMIT), r"}^{", (r"\frac{\pi}{2}", LIMIT), r"}")
    TLIMS = (r"\int_{", ("0", LIMIT), r"}^{", ("1", LIMIT), r"}")
    PROBLEM = eq(*LIMS, r"\frac{", "1", r"}{", "12+", r"\sin(x)", r"}", r"\,dx")
    CURVE_LABEL = eq("y", "=", r"\frac{", "1", r"}{", "12+", r"\sin(x)", r"}")
    LABEL_AT = (0.15, 0.12)     # empty space above the nearly flat curve (y is about 0.08)

    GRAPH = dict(x_range=[0, P2, P2 / 4], y_range=[0, 0.2, 0.05], a=0, b=P2, size=(8, 4.2),
                 x_labels={P4: r"\frac{\pi}{4}", P2: r"\frac{\pi}{2}"},
                 y_labels={0.05: "0.05", 0.1: "0.1", 0.15: "0.15"})

    HOOK = cap(r"A sine trapped under a fraction. Which substitution frees it?")
    INTUITION = cap(r"The curve is almost flat, so even $4$ rectangles are close.")
    INSIGHT = dict(
        parts=[r"\sin(x)"],
        label=cap(r"$t=\tan\frac{x}{2}$"),
        say=cap(r"With $t=\tan\frac{x}{2}$, $\sin x$ becomes a fraction in $t$."),
    )

    STEPS = [
        dict(tex=eq(*TLIMS, r"\frac{", r"\frac{2}{1+t^{2}}", r"}{", "12+", r"\frac{2t}{1+t^{2}}", r"}", r"\,dt"),
             say=cap(r"Let $t=\tan\frac{x}{2}$; the limits become $0$ and $1$."),
             rule=["weierstrass_substitution", "change_of_limits"],
             mapping={"weierstrass_substitution": [cap(r"Here $\frac{2t}{1+t^{2}}$ replaces the $\sin(x)$ on the bottom.")],
                      "change_of_limits": [cap(r"$x=0$ gives $t=0$; $x=\frac{\pi}{2}$ gives $t=\tan\frac{\pi}{4}=1$.")]},
             highlight=([r"\frac{2}{1+t^{2}}", r"\,dt"], cap(r"$dx=\frac{2\,dt}{1+t^{2}}$")), side=UP,
             then="substitution"),
        dict(tex=eq(*TLIMS, r"\frac{", "2", r"}{", r"12(1+t^{2})+2t", r"}", r"\,dt"),
             say=cap(r"Multiply top and bottom by $1+t^{2}$."),
             rule="algebra"),
        dict(tex=eq(*TLIMS, r"\frac{", "1", r"}{", r"6t^{2}+t+6", r"}", r"\,dt"),
             say=cap(r"Expand, then halve the top and the bottom."),
             rule="algebra"),
        dict(tex=eq(r"\frac{1}{6}", *TLIMS, r"\frac{", "1", r"}{", r"\big(t+\frac{1}{12}\big)^{2}+\frac{143}{144}", r"}",
                    r"\,dt"),
             say=cap(r"Take out $6$ and complete the square on the bottom."),
             rule="completing_the_square",
             mapping=[cap(r"$t^{2}+\frac{t}{6}+1$: here $b=\frac{1}{12}$, and $1-\frac{1}{144}=\frac{143}{144}$.")]),
        dict(tex=eq(r"\frac{1}{6}", r"\cdot", r"\frac{12}{\sqrt{143}}", r"\Big[",
                    r"\tan^{-1}\frac{12t+1}{\sqrt{143}}", r"\Big]_{", ("0", LIMIT), r"}^{", ("1", LIMIT), r"}"),
             say=cap(r"Scale the square to $u^{2}$, and the bottom becomes $1+u^{2}$."),
             rule=["u_substitution", "arctan_integral"],
             mapping={"u_substitution": [cap(r"Let $u=\frac{12t+1}{\sqrt{143}}$, so $dt=\frac{\sqrt{143}}{12}\,du$.")],
                      "arctan_integral": [cap(r"Then the integral is $\frac{12}{\sqrt{143}}\int\frac{du}{1+u^{2}}$.")]}),
        dict(tex=eq(r"\frac{2}{\sqrt{143}}", r"\Big(", r"\tan^{-1}\frac{13}{\sqrt{143}}", "-",
                    r"\tan^{-1}\frac{1}{\sqrt{143}}", r"\Big)"),
             say=cap(r"At $t=1$ the angle is $\tan^{-1}\frac{13}{\sqrt{143}}$; at $t=0$, $\tan^{-1}\frac{1}{\sqrt{143}}$."),
             rule="ftc"),
        dict(tex=eq(r"\frac{2}{\sqrt{143}}", r"\tan^{-1}\frac{\sqrt{143}}{13}"),
             say=cap(r"Merge the two angles with the tangent of a difference."),
             rule="tan_subtraction",
             mapping=[cap(r"$\frac{\tan A-\tan B}{1+\tan A\tan B}=\frac{12/\sqrt{143}}{156/143}=\frac{\sqrt{143}}{13}$.")]),
    ]

    SUBSTITUTION = dict(
        u_graph=dict(x_range=[0, 1, 0.25], y_range=[0, 0.2, 0.05], a=0, b=1, var="t", size=(8, 4.2),
                     plot_range=(0, 1), x_labels={0.5: "0.5", 1: "1"},
                     y_labels={0.05: "0.05", 0.1: "0.1", 0.15: "0.15"}),
        u_func=lambda t: 1 / (6 * np.asarray(t, dtype=float) ** 2 + np.asarray(t, dtype=float) + 6),
        says=(cap(r"In $x$: a low, wide strip with area about $0.124$."),
              cap(r"In $t$: narrower and taller, with exactly the same area.")),
    )

    ANSWER = eq(r"\frac{2}{\sqrt{143}}", r"\tan^{-1}\frac{\sqrt{143}}{13}")
    ANSWER_VALUE = float(2 / np.sqrt(143) * np.arctan(np.sqrt(143) / 13))
    CLOSE_SAYS = (cap(r"Thin rectangles close in on $0.1244$."),
                  cap(r"Takeaway: $t=\tan\frac{x}{2}$ turns trig fractions into ordinary fractions."))
