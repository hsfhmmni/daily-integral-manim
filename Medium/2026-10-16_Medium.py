import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import IntegralVideo, LIMIT, NEW, TRAP, cap, eq

P6 = float(np.pi / 6)
P4 = float(np.pi / 4)
P2 = float(np.pi / 2)


class MediumIntegral(IntegralVideo):
    DIFFICULTY = "Medium"
    DATE = "2026-10-16"

    @staticmethod
    def FUNC(x):
        x = np.asarray(x, dtype=float)
        return np.sin(x + np.pi / 4) ** 2 / np.sqrt(1 + np.sin(2 * x))

    @classmethod
    def exact_integral(cls):
        return mp.quad(lambda x: mp.sin(x + mp.pi / 4) ** 2 / mp.sqrt(1 + mp.sin(2 * x)), [mp.pi / 6, mp.pi / 2])

    SIN2 = r"\sin^{2}\left(x+\frac{\pi}{4}\right)"
    SC = r"\sin x+\cos x"
    COLORS = {r"1+\sin 2x": NEW, r"(\sin x+\cos x)^{2}": NEW}
    LIMS = (r"\int_{", (r"\frac{\pi}{6}", LIMIT), r"}^{", (r"\frac{\pi}{2}", LIMIT), r"}")
    PROBLEM = eq(*LIMS, r"\frac{", SIN2, r"}{", r"\sqrt{", r"1+\sin 2x", r"}}", r"\,dx")
    CURVE_LABEL = eq("y", "=", r"\frac{", SIN2, r"}{", r"\sqrt{", r"1+\sin 2x", r"}}")
    LABEL_AT = (0.1, 0.76)      # empty space above the curve, which peaks at 0.71

    GRAPH = dict(x_range=[0, 2, 0.25], y_range=[0, 1, 0.2], a=P6, b=P2, size=(8, 4.2), plot_range=(0.1, 1.9),
                 x_labels={P6: r"\frac{\pi}{6}", P2: r"\frac{\pi}{2}"},
                 y_labels={0.2: "0.2", 0.4: "0.4", 0.6: "0.6", 0.8: "0.8"})

    HOOK = cap(r"A square root of $1+\sin 2x$. Can it simply disappear?")
    INTUITION = cap(r"Thin rectangles estimate the area; watch the gap shrink.")
    INSIGHT = dict(
        parts=[r"1+\sin 2x"],
        label=cap(r"$(\sin x+\cos x)^{2}$"),
        say=cap(r"$1+\sin 2x$ is a perfect square in disguise."),
    )

    STEPS = [
        dict(tex=eq(*LIMS, r"\frac{", SIN2, r"}{", r"\sqrt{", r"(\sin x+\cos x)^{2}", r"}}", r"\,dx"),
             say=cap(r"$1+2\sin x\cos x=\sin^{2}x+2\sin x\cos x+\cos^{2}x$."),
             rule=["pythagorean_identity", "double_angle"],
             mapping={"pythagorean_identity": [cap(r"Write the $1$ as $\sin^{2}x+\cos^{2}x$.")],
                      "double_angle": [cap(r"$\sin 2x=2\sin x\cos x$ is the cross term.")]}),
        dict(tex=eq(*LIMS, r"\frac{", SIN2, r"}{", (r"|", TRAP), SC, (r"|", TRAP), r"}", r"\,dx"),
             say=cap(r"Careful: $\sqrt{w^{2}}=|w|$, not $w$."),
             rule="absolute_value"),
        dict(tex=eq(*LIMS, r"\frac{", SIN2, r"}{", SC, r"}", r"\,dx"),
             say=cap(r"On $\big[\frac{\pi}{6},\frac{\pi}{2}\big]$, $\sin x$ and $\cos x$ are $\ge 0$: bars drop."),
             rule="absolute_value"),
        dict(tex=eq(*LIMS, r"\frac{", r"(", SC, r")^{2}", r"}{", r"2", r"(", SC, r")", r"}", r"\,dx"),
             say=cap(r"$\sin\big(x+\frac{\pi}{4}\big)=\frac{\sin x+\cos x}{\sqrt{2}}$, so its square halves."),
             highlight=([r"(", SC, r")^{2}", r")"], cap(r"cancel")),
             side=UP,
             rule="sine_addition",
             mapping=[cap(r"Here $A=x$, $B=\frac{\pi}{4}$, and $\cos B=\sin B=\frac{1}{\sqrt{2}}$.")]),
        dict(tex=eq(*LIMS, r"\frac{1}{2}", r"(", SC, r")", r"\,dx"),
             say=cap(r"One factor cancels: just half of $\sin x+\cos x$."),
             rule="algebra"),
        dict(tex=eq(r"\frac{1}{2}", r"\Big[", r"\sin x-\cos x", r"\Big]_{", (r"\frac{\pi}{6}", LIMIT), r"}^{",
                    (r"\frac{\pi}{2}", LIMIT), r"}"),
             say=cap(r"$\sin x$ integrates to $-\cos x$, and $\cos x$ to $\sin x$."),
             rule=["sin_integral", "cos_integral", "linearity"]),
        dict(tex=eq(r"\frac{1}{2}", r"\Big(", r"(1-0)", "-", r"\Big(\frac{1}{2}-\frac{\sqrt{3}}{2}\Big)", r"\Big)"),
             say=cap(r"Upper limit minus lower limit."),
             rule="ftc"),
        dict(tex=eq(r"\frac{1+\sqrt{3}}{4}"),
             say=cap(r"So the area is exactly $\frac{1+\sqrt{3}}{4}\approx 0.683$."),
             rule="algebra"),
    ]

    ANSWER = eq(r"\frac{1+\sqrt{3}}{4}")
    ANSWER_VALUE = float((1 + np.sqrt(3)) / 4)
    CLOSE_SAYS = (cap(r"Thin rectangles close in on $0.6830$."),
                  cap(r"Takeaway: $1\pm\sin 2x$ is a square; then mind the absolute value."))
