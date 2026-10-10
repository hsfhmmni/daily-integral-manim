import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import IntegralVideo, LIMIT, NEW, cap, eq

L = 5.5 * np.pi          # rectangle window; at 64 rectangles the estimate is within 0.21% of pi/2


def sigma(x):
    return 1 / (1 + np.exp(-x))


class MediumIntegral(IntegralVideo):
    DIFFICULTY = "Medium"
    DATE = "2026-10-08"

    @staticmethod
    def FUNC(x):
        return np.sinc(x / np.pi) * sigma(x)          # = e^x sin x / (x e^x + x), with the hole at 0 filled

    @classmethod
    def exact_integral(cls):
        f = lambda x: mp.e ** x * mp.sin(x) / (x * mp.e ** x + x)
        return mp.quadosc(lambda x: f(x) + f(-x), [0, mp.inf], period=2 * mp.pi)

    COLORS = {r"\sigma(x)": NEW, r"\sigma(-x)": NEW}
    PROBLEM = eq(r"\int_{", (r"-\infty", LIMIT), r"}^{", (r"\infty", LIMIT), r"}",
                 r"\frac{e^{x}\sin(x)}{xe^{x}+x}", r"\,dx")
    CURVE_LABEL = eq("y", "=", r"\frac{e^{x}\sin(x)}{xe^{x}+x}")
    LABEL_AT = (3.0, 0.33)      # above the small right-hand waves

    WINDOW = (-L, L)
    CLOSE_WIDEN = (-60.5 * np.pi, 60.5 * np.pi)
    GRAPH = dict(x_range=[-18, 18, 6], y_range=[-0.3, 0.9, 0.3], a=-L, b=L, size=(8.5, 4.2), hole=(0, 0.5),
                 x_labels={-12: "-12", -6: "-6", 6: "6", 12: "12"},          # the peak is about 0.62 near x = 1
                 y_labels={-0.3: "-0.3", 0.3: "0.3", 0.6: "0.6", 0.9: "0.9"})

    HOOK = cap(r"No elementary antiderivative, and $x=0$ divides by zero. Now what?")
    HOOK_NOTE = cap(r"The hole at $x=0$ is removable: the curve tends to $\frac{1}{2}$.")
    INTUITION = cap(r"Rectangles on $[-\frac{11\pi}{2},\frac{11\pi}{2}]$ estimate the area; the gap shrinks.")
    INSIGHT = dict(
        before=cap(r"Look at the bottom: $x$ factors out."),
        parts=[r"\frac{e^{x}\sin(x)}{xe^{x}+x}"],
        label=cap(r"$=\frac{\sin x}{x}\cdot\frac{e^{x}}{e^{x}+1}$"),
        say=cap(r"Split it: $\frac{\sin x}{x}$ times a weight that climbs from $0$ to $1$."),
    )

    STEPS = [
        dict(tex=eq(r"\int_{", (r"-\infty", LIMIT), r"}^{", (r"\infty", LIMIT), r"}", r"\frac{\sin x}{x}", r"\cdot",
                    r"\frac{e^{x}}{e^{x}+1}", r"\,dx"),
             say=cap(r"Factor: $xe^{x}+x=x(e^{x}+1)$.")),
        dict(tex=eq(r"\int_{", (r"-\infty", LIMIT), r"}^{", (r"\infty", LIMIT), r"}", r"\frac{\sin x}{x}", r"\cdot",
                    r"\sigma(x)", r"\,dx"),
             say=cap(r"Call the weight $\sigma(x)$; it climbs from $0$ to $1$."),
             then="reflection"),
        dict(tex=eq(r"\int_{", ("0", LIMIT), r"}^{", (r"\infty", LIMIT), r"}", r"\frac{\sin x}{x}", r"\cdot", r"\Big(",
                    r"\sigma(x)", "+", r"\sigma(-x)", r"\Big)", r"\,dx"),
             say=cap(r"Pair $x$ with $-x$: $\frac{\sin x}{x}$ is even, so fold at $0$.")),
        dict(tex=eq(r"\int_{", ("0", LIMIT), r"}^{", (r"\infty", LIMIT), r"}", r"\frac{\sin x}{x}", r"\cdot", "1",
                    r"\,dx"),
             say=cap(r"The weights add to $1$, so they vanish.")),
        dict(tex=eq(r"\int_{", ("0", LIMIT), r"}^{", (r"\infty", LIMIT), r"}", r"\frac{\sin x}{x}", r"\,dx"),
             say=cap(r"The Dirichlet integral, which a Laplace transform evaluates.")),
    ]

    REFLECTION = dict(
        spec=dict(x_range=[-6, 6, 2], y_range=[0, 1.5, 0.5], size=(7, 3.2), color_limits=False, curve_color=NEW,
                  mirror_color=PURPLE_B, sum=1, x_labels={-4: "-4", 4: "4"}, y_labels={0.5: "0.5"}),
        func=sigma,
        mode="mirror",
        says=(cap(r"Mirror $\sigma(x)$ in the $y$-axis to get $\sigma(-x)$."),
              cap(r"At every $x$ the two heights add to exactly $1$.")),
    )

    ANSWER = eq(r"\frac{\pi}{2}")
    ANSWER_VALUE = float(np.pi / 2)
    CLOSE_SAYS = (cap(r"More rectangles on a wider window close in on $\frac{\pi}{2}$."),
                  cap(r"Takeaway: pair $x$ with $-x$ when a weight satisfies $w(x)+w(-x)=1$."))
