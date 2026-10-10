import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import IntegralVideo, LIMIT, NEW, cap, eq


class EasyIntegral(IntegralVideo):
    DIFFICULTY = "Easy"
    DATE = "2026-10-08"

    @staticmethod
    def FUNC(x):
        return np.pi * np.arccos(np.clip(np.sin(np.pi * x), -1, 1)) * np.cos(np.pi * x)

    @classmethod
    def exact_integral(cls):
        return mp.quad(lambda x: mp.pi * mp.acos(mp.sin(mp.pi * x)) * mp.cos(mp.pi * x), [-0.5, 0, 0.5])

    COLORS = {r"\sin(\pi x)": NEW, "u": NEW}
    PROBLEM = eq(r"\int_{", (r"-\frac{1}{2}", LIMIT), r"}^{", (r"\frac{1}{2}", LIMIT), r"}",
                 r"\pi", r"\cos^{-1}(", r"\sin(\pi x)", r")", r"\cos(\pi x)", r"\,dx")
    CURVE_LABEL = eq("y", "=", r"\pi", r"\cos^{-1}(", r"\sin(\pi x)", r")", r"\cos(\pi x)")
    LABEL_AT = (0.1, 4.4)       # empty upper-right region of the plot

    GRAPH = dict(x_range=[-0.75, 0.75, 0.25], y_range=[0, 6, 2], a=-0.5, b=0.5, size=(8, 4.2),
                 x_labels={-0.5: r"-\tfrac{1}{2}", 0.5: r"\tfrac{1}{2}"}, y_labels={2: "2", 4: "4", 6: "6"})

    HOOK = cap(r"How big is this green area under the curve?")
    INTUITION = cap(r"Thin rectangles estimate the area; watch the gap shrink.")
    INSIGHT = dict(
        before=cap(r"Look inside the inverse cosine: $\sin(\pi x)$, in orange."),
        parts=[r"\cos(\pi x)", r"\,dx"],
        label=cap(r"$\frac{d}{dx}\sin(\pi x)=\pi\cos(\pi x)$"),
        say=cap(r"Its derivative is already in the integral, so substitute."),
    )

    STEPS = [
        dict(tex=eq(r"\int_{", (r"-\frac{1}{2}", LIMIT), r"}^{", (r"\frac{1}{2}", LIMIT), r"}",
                    r"\cos^{-1}(", r"\sin(\pi x)", r")", r"\pi", r"\cos(\pi x)", r"\,dx"),
             say=cap(r"Slide $\pi$ next to $\cos(\pi x)\,dx$: together they make $du$.")),
        dict(tex=eq(r"\int_{", ("-1", LIMIT), r"}^{", ("1", LIMIT), r"}", r"\cos^{-1}(", "u", r")", r"\,d", "u"),
             say=cap(r"With $u=\sin(\pi x)$, the limits $\pm\frac{1}{2}$ become $\pm 1$."),
             then="substitution"),
        dict(tex=eq(r"\int_{", ("-1", LIMIT), r"}^{", ("1", LIMIT), r"}", r"\Big(", r"\frac{\pi}{2}", "-",
                    r"\sin^{-1}", "u", r"\Big)", r"\,d", "u"),
             say=cap(r"Use the identity $\cos^{-1}u=\frac{\pi}{2}-\sin^{-1}u$.")),
        dict(tex=eq(r"\frac{\pi}{2}", r"\cdot", "2", "-", r"\int_{", ("-1", LIMIT), r"}^{", ("1", LIMIT), r"}",
                    r"\sin^{-1}", "u", r"\,d", "u"),
             say=cap(r"The constant $\frac{\pi}{2}$ over a width of $2$ gives $\frac{\pi}{2}\cdot 2$."),
             then="reflection"),
        dict(tex=eq(r"\frac{\pi}{2}", r"\cdot", "2", "-", "0"),
             say=cap(r"So the inverse sine part contributes nothing.")),
    ]

    SUBSTITUTION = dict(
        u_graph=dict(x_range=[-1.5, 1.5, 0.5], y_range=[0, 4, 1], a=-1, b=1, var="u", size=(8, 4.2),
                     x_labels={-1: "-1", 1: "1"}, y_labels={1: "1", 2: "2", 3: "3"}),
        u_func=lambda u: np.arccos(np.clip(u, -1, 1)),
        says=(cap(r"In $x$: the area under the original curve is about $3.142$."),
              cap(r"In $u$: the curve is $\cos^{-1}u$, and the area is unchanged.")),
    )
    REFLECTION = dict(
        spec=dict(x_range=[-1, 1, 0.5], y_range=[-2, 2, 1], var="u", size=(6, 3.4),
                  x_labels={-1: "-1", 1: "1"}, y_labels={-1: "-1", 1: "1"}),
        func=lambda u: np.arcsin(np.clip(u, -1, 1)),
        mode="point",
        says=(cap(r"$\sin^{-1}u$ is odd: its two pieces are mirror images."),
              cap(r"Spun about the origin, they cancel: signed area $0$.")),
    )

    ANSWER = eq(r"\pi")
    ANSWER_VALUE = float(np.pi)
    CLOSE_SAYS = (cap(r"More, thinner rectangles close in on $\pi$."),
                  cap(r"Takeaway: when a function's derivative sits beside it, substitute."))
