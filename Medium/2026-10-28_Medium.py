import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import IntegralVideo, LIMIT, cap, eq

P6 = float(np.pi / 6)
P3 = float(np.pi / 3)
P2 = float(np.pi / 2)


class MediumIntegral(IntegralVideo):
    DIFFICULTY = "Medium"
    DATE = "2026-10-28"

    # A geometric series with first term and ratio r = cos^2 x, and 1/4 <= r <= 3/4 on [pi/6, pi/3],
    # so it sums to r / (1 - r) = cos^2 x / sin^2 x = cot^2 x = csc^2 x - 1. The integral is
    # [-cot x - x] from pi/6 to pi/3 = sqrt3 - 1/sqrt3 - pi/6 = 2 sqrt3 / 3 - pi/6 = 0.631102.
    @staticmethod
    def FUNC(x):
        x = np.asarray(x, dtype=float)
        return 1 / np.tan(x) ** 2

    @classmethod
    def exact_integral(cls):
        # the series summed term by term: cos^2 x <= 3/4 here, so 300 terms leave under 1e-37
        return mp.quad(lambda x: mp.fsum(mp.cos(x) ** (2 * n) for n in range(1, 301)), [mp.pi / 6, mp.pi / 3])

    LIMS = (r"\int_{", (r"\frac{\pi}{6}", LIMIT), r"}^{", (r"\frac{\pi}{3}", LIMIT), r"}")
    S = r"\cos(x)^{2}+\cos(x)^{4}+\cos(x)^{6}+\dots"
    PROBLEM = eq(*LIMS, r"\Big(", S, r"\Big)", r"\,dx")
    CURVE_LABEL = eq("y", "=", S)
    LABEL_AT = (0.75, 2.3)      # empty space top-right, above the falling curve (y is about 1.15 at x = 0.75)

    GRAPH = dict(x_range=[0, P2, P2 / 6], y_range=[0, 4, 1], a=P6, b=P3, size=(8, 4.2),
                 plot_range=(0.47, P2),
                 x_labels={P6: r"\frac{\pi}{6}", P3: r"\frac{\pi}{3}", P2: r"\frac{\pi}{2}"},
                 y_labels={1: "1", 2: "2", 3: "3"})

    HOOK = cap(r"Endless powers of $\cos x$. Can they add to a finite area?")
    INTUITION = cap(r"The curve falls from $3$ to $\frac{1}{3}$; watch the gap shrink.")
    INSIGHT = dict(
        parts=[S],
        label=cap(r"ratio $\cos^{2}x$"),
        say=cap(r"Each term is the one before times $\cos^{2}x$: geometric."),
    )

    STEPS = [
        dict(tex=eq(*LIMS, r"\frac{", r"\cos^{2}x", r"}{", r"1-\cos^{2}x", r"}", r"\,dx"),
             say=cap(r"Starting at $r$: $r+r^{2}+r^{3}+\dots=\frac{r}{1-r}$."),
             rule="geometric_series",
             mapping=[cap(r"Here $r=\cos^{2}x$, between $\frac{1}{4}$ and $\frac{3}{4}$, so it converges.")]),
        dict(tex=eq(*LIMS, r"\frac{", r"\cos^{2}x", r"}{", r"\sin^{2}x", r"}", r"\,dx"),
             say=cap(r"The bottom $1-\cos^{2}x$ is just $\sin^{2}x$."),
             rule="pythagorean_identity",
             mapping=[cap(r"Here $1-\cos^{2}x=\sin^{2}x$.")]),
        dict(tex=eq(*LIMS, r"\cot^{2}x", r"\,dx"),
             say=cap(r"$\frac{\cos x}{\sin x}=\cot x$, so the integrand is $\cot^{2}x$."),
             rule="algebra"),
        dict(tex=eq(*LIMS, r"\big(", r"\csc^{2}x", "-1", r"\big)", r"\,dx"),
             say=cap(r"Divide the identity by $\sin^{2}x$: $\cot^{2}x=\csc^{2}x-1$."),
             rule="pythagorean_identity"),
        dict(tex=eq(r"\Big[", r"-\cot x", "-x", r"\Big]_{", (r"\frac{\pi}{6}", LIMIT), r"}^{",
                    (r"\frac{\pi}{3}", LIMIT), r"}"),
             say=cap(r"Integrate each term: $\csc^{2}x$ gives $-\cot x$, and $1$ gives $x$."),
             rule=["csc2_integral", "linearity"],
             mapping={"csc2_integral": [cap(r"Here $\int\csc^{2}x\,dx=-\cot x$.")]}),
        dict(tex=eq(r"\Big(", r"-\frac{1}{\sqrt{3}}", r"-\frac{\pi}{3}", r"\Big)", "-", r"\Big(", r"-\sqrt{3}",
                    r"-\frac{\pi}{6}", r"\Big)"),
             say=cap(r"$\cot\frac{\pi}{3}=\frac{1}{\sqrt{3}}$ and $\cot\frac{\pi}{6}=\sqrt{3}$: top minus bottom."),
             rule="ftc"),
        dict(tex=eq(r"\frac{2\sqrt{3}}{3}", r"-\frac{\pi}{6}"),
             say=cap(r"$\sqrt{3}-\frac{1}{\sqrt{3}}=\frac{2\sqrt{3}}{3}$, and $\frac{\pi}{3}-\frac{\pi}{6}=\frac{\pi}{6}$."),
             rule="algebra"),
    ]

    ANSWER = eq(r"\frac{2\sqrt{3}}{3}", r"-\frac{\pi}{6}")
    ANSWER_VALUE = float(2 * mp.sqrt(3) / 3 - mp.pi / 6)
    CLOSE_SAYS = (cap(r"Thin rectangles close in on $0.6311$."),
                  cap(r"Takeaway: an endless sum of powers is often a geometric series."))
