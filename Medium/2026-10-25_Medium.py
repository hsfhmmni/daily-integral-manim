import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import IntegralVideo, LIMIT, NEW, cap, eq

P2 = float(np.pi / 2)


class MediumIntegral(IntegralVideo):
    DIFFICULTY = "Medium"
    DATE = "2026-10-25"

    # y = sin x / (2 + y) gives y^2 + 2y - sin x = 0, so y = -1 + sqrt(1 + sin x) (the root with
    # y >= 0; it attracts, since |g'(y)| = sin x / (1 + sqrt(1 + sin x))^2 < 1). The integrand
    # 1 + y = sqrt(1 + sin x) = sin(x/2) + cos(x/2) on [0, pi/2], and the integral is exactly 2.
    @staticmethod
    def FUNC(x):
        return np.sqrt(1 + np.sin(np.asarray(x, dtype=float)))

    @classmethod
    def exact_integral(cls):
        return mp.quad(lambda x: mp.sqrt(1 + mp.sin(x)), [0, mp.pi / 2])

    REPEAT = r"\frac{\sin x}{2+\frac{\sin x}{2+\dots}}"
    COLORS = {REPEAT: NEW, "y": NEW, r"y^{2}": NEW, "2y": NEW}
    LIMS = (r"\int_{", ("0", LIMIT), r"}^{", (r"\frac{\pi}{2}", LIMIT), r"}")
    PROBLEM = eq(*LIMS, r"\Bigg(", "1", "+", r"\frac{", r"\sin x", r"}{2+", REPEAT, r"}", r"\Bigg)", r"\,dx")
    PROBLEM_X = (-5.6, 3.3)     # a tall line: give it room, clear of the badge
    CURVE_LABEL = None          # the continued fraction is too big to sit beside the curve

    GRAPH = dict(x_range=[0, P2, np.pi / 8], y_range=[0, 1.6, 0.4], a=0, b=P2, size=(8, 4.2), plot_range=(0, P2),
                 x_labels={np.pi / 4: r"\frac{\pi}{4}", P2: r"\frac{\pi}{2}"},
                 y_labels={0.8: "0.8", 1.2: "1.2"})

    HOOK = cap(r"A fraction that never ends, yet a gentle curve. What area?")
    INTUITION = cap(r"Thin rectangles estimate the area; watch the gap shrink.")
    INSIGHT = dict(
        parts=[REPEAT],
        label=cap(r"the fraction again"),
        say=cap(r"Below the first $2+$, the whole fraction starts again."),
    )

    STEPS = [
        dict(tex=eq("y", "=", r"\frac{", r"\sin x", r"}{2+", "y", r"}"),
             say=cap(r"Call the fraction $y$: below the first $2+$ sits $y$."),
             rule="nested_fixed_point",
             mapping=[cap(r"Here $g(y)=\frac{\sin x}{2+y}$.")]),
        dict(tex=eq(r"y^{2}", "+", "2y", "-", r"\sin x", "=", "0"),
             say=cap(r"Multiply by $2+y$: a quadratic in $y$."),
             rule="algebra"),
        dict(tex=eq("y", "=", "-1", "+", r"\sqrt{1+\sin x}"),
             say=cap(r"Take the $+$ root: every layer is positive, so $y\ge 0$."),
             rule=["quadratic_formula", "nested_fixed_point"]),
        dict(tex=eq(*LIMS, r"\sqrt{1+\sin x}", r"\,dx"),
             say=cap(r"So the integrand $1+y$ is just $\sqrt{1+\sin x}$."),
             rule="algebra"),
        dict(tex=eq(*LIMS, r"\sqrt{\Big(\sin\frac{x}{2}+\cos\frac{x}{2}\Big)^{2}}", r"\,dx"),
             say=cap(r"In half angles, $1+\sin x$ is a perfect square."),
             rule=["pythagorean_identity", "double_angle"],
             mapping={"pythagorean_identity": [cap(r"Here $1=\sin^{2}\frac{x}{2}+\cos^{2}\frac{x}{2}$.")],
                      "double_angle": [cap(r"Here $\sin x=2\sin\frac{x}{2}\cos\frac{x}{2}$.")]}),
        dict(tex=eq(*LIMS, r"\Big(", r"\sin\frac{x}{2}", "+", r"\cos\frac{x}{2}", r"\Big)", r"\,dx"),
             say=cap(r"Both are positive on $[0,\frac{\pi}{2}]$, so the root is exact."),
             rule="absolute_value"),
        dict(tex=eq(r"\Big[", r"-2\cos\frac{x}{2}", "+", r"2\sin\frac{x}{2}", r"\Big]_{", ("0", LIMIT), r"}^{",
                    (r"\frac{\pi}{2}", LIMIT), r"}"),
             say=cap(r"Reverse chain rule: $\int\cos\frac{x}{2}\,dx=2\sin\frac{x}{2}$."),
             rule=["sin_integral", "cos_integral", "chain_rule", "linearity"],
             mapping={"chain_rule": [cap(r"Inside is $\frac{x}{2}$, with derivative $\frac{1}{2}$: so a factor $2$.")]}),
        dict(tex=eq(r"\big(", r"-\sqrt{2}+\sqrt{2}", r"\big)", "-", r"\big(", "-2+0", r"\big)"),
             say=cap(r"At $\frac{\pi}{2}$: $\cos\frac{\pi}{4}=\sin\frac{\pi}{4}=\frac{\sqrt{2}}{2}$."),
             rule="ftc"),
        dict(tex=eq("2"),
             say=cap(r"The roots cancel: the area is exactly $2$."),
             rule="algebra"),
    ]

    ANSWER = eq("2")
    ANSWER_VALUE = 2.0
    CLOSE_SAYS = (cap(r"Thin rectangles close in on $2$."),
                  cap(r"Takeaway: name the repeating tail, then solve for it."))
