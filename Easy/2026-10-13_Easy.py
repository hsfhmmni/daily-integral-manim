import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import IntegralVideo, LIMIT, NEW, TRAP, cap, eq

AL = float(np.arctan(1 / 3))    # the new upper limit, about 0.322
B = float(np.exp(AL))           # the old upper limit e^{tan^{-1}(1/3)}, about 1.380


class EasyIntegral(IntegralVideo):
    DIFFICULTY = "Easy"
    DATE = "2026-10-13"

    @staticmethod
    def FUNC(x):
        x = np.asarray(x, dtype=float)
        return np.sqrt(np.maximum(0.0, 1 - np.sin(2 * np.log(x)))) / x ** 3

    @classmethod
    def exact_integral(cls):
        return mp.quad(lambda x: mp.sqrt(1 - mp.sin(2 * mp.log(x))) / x ** 3, [1, mp.exp(mp.atan(mp.mpf(1) / 3))])

    COLORS = {r"\ln x": NEW, r"\frac{1}{x}\,dx": NEW, "t": NEW, r"\,dt": NEW}
    LIMS = (r"\int_{", ("1", LIMIT), r"}^{", (r"e^{\tan^{-1}\frac{1}{3}}", LIMIT), r"}")
    LIMT = (r"\int_{", ("0", LIMIT), r"}^{", (r"\tan^{-1}\frac{1}{3}", LIMIT), r"}")
    PROBLEM = eq(*LIMS, r"\frac{\sqrt{1-\sin(2", r"\ln x", r")}}{", r"x^{3}", r"}", r"\,dx")
    CURVE_LABEL = eq("y", "=", r"\frac{\sqrt{1-\sin(2", r"\ln x", r")}}{", r"x^{3}", r"}")
    LABEL_AT = (1.25, 0.65)     # empty space above the curve, which is below 0.4 for x > 1.25

    GRAPH = dict(x_range=[1, 1.5, 0.1], y_range=[0, 1.2, 0.2], a=1, b=B, size=(8, 4.2), plot_range=(1, 1.5),
                 x_labels={1: "1", 1.2: "1.2", B: r"e^{\tan^{-1}\frac{1}{3}}"},
                 y_labels={0.4: "0.4", 0.8: "0.8", 1.2: "1.2"})

    HOOK = cap(r"Why can't we just drop this square root?")
    INTUITION = cap(r"Thin rectangles estimate the area; watch the gap shrink.")
    INSIGHT = dict(
        parts=[r"\ln x"],
        side=UP,                # below, the arrow would cross the fraction bar
        label=cap(r"$t=\ln x$"),
        say=cap(r"$\ln x$ hides inside the sine: make it the new variable."),
    )

    STEPS = [
        dict(tex=eq(*LIMS, r"\frac{\sqrt{1-\sin(2", r"\ln x", r")}}{", r"x^{2}", r"}", r"\cdot",
                    r"\frac{1}{x}\,dx"),
             say=cap(r"Split $x^{3}$ as $x^{2}\cdot x$, keeping $\frac{1}{x}\,dx$ aside."),
             highlight=([r"\ln x", r"\frac{1}{x}\,dx"], cap(r"$t$ and $dt$")),
             rule="exponent_laws"),
        dict(tex=eq(*LIMT, r"\frac{\sqrt{1-\sin(2", "t", r")}}{", r"e^{2t}", r"}", r"\,dt"),
             say=cap(r"Let $t=\ln x$: the limits become $0$ and $\tan^{-1}\frac{1}{3}$."),
             rule=["u_substitution", "change_of_limits", "exp_log_inverse", "log_values"],
             mapping={"u_substitution": [cap(r"Here $t=\ln x$, so $dt=\frac{1}{x}\,dx$ and $x^{2}=e^{2t}$.")],
                      "change_of_limits": [cap(r"$x=1$ gives $t=0$; the top gives $\tan^{-1}\frac{1}{3}$.")]},
             then="substitution"),
        dict(tex=eq(*LIMT, r"\sqrt{", r"(\cos t-\sin t)", r"^{2}}", r"\,", r"e^{-2t}", r"\,dt"),
             say=cap(r"$1-\sin 2t$ is the perfect square $(\cos t-\sin t)^{2}$."),
             rule=["pythagorean_identity", "double_angle"],
             mapping={"pythagorean_identity": [cap(r"Write the $1$ as $\cos^{2}t+\sin^{2}t$.")],
                      "double_angle": [cap(r"$\sin 2t=2\sin t\cos t$ is the cross term.")]}),
        dict(tex=eq(*LIMT, (r"\big|", TRAP), r"\cos t-\sin t", (r"\big|", TRAP), r"\,", r"e^{-2t}", r"\,dt"),
             say=cap(r"Careful: $\sqrt{w^{2}}=|w|$, not $w$."),
             rule="absolute_value"),
        dict(tex=eq(*LIMT, r"(\cos t-\sin t)", r"\,", r"e^{-2t}", r"\,dt"),
             say=cap(r"Here $t<\frac{\pi}{4}$, so $\cos t>\sin t$: the bars drop."),
             rule="absolute_value"),
        dict(tex=eq(r"\Big[", r"\tfrac{1}{5}", r"e^{-2t}", r"(3\sin t-\cos t)", r"\Big]_{", ("0", LIMIT), r"}^{",
                    (r"\tan^{-1}\frac{1}{3}", LIMIT), r"}"),
             say=cap(r"Check: this differentiates back to $e^{-2t}(\cos t-\sin t)$."),
             rule=["product_rule", "chain_rule"],
             mapping={"product_rule": [cap(r"Try $e^{-2t}(A\sin t+B\cos t)$: matching gives $A=\frac{3}{5}$, $B=-\frac{1}{5}$.")],
                      "chain_rule": [cap(r"$\frac{d}{dt}e^{-2t}=-2e^{-2t}$: the inside $-2t$ gives $-2$.")]}),
        dict(tex=eq("0", "-", r"\tfrac{1}{5}", r"(0-1)"),
             say=cap(r"At the top $\tan t=\frac{1}{3}$, so $3\sin t=\cos t$: zero."),
             rule="ftc"),
        dict(tex=eq(r"\frac{1}{5}"),
             say=cap(r"The bottom limit alone gives $\frac{1}{5}$."),
             rule="algebra"),
    ]

    SUBSTITUTION = dict(
        u_graph=dict(x_range=[0, 0.5, 0.1], y_range=[0, 1.2, 0.2], a=0, b=AL, var="t", size=(8, 4.2),
                     plot_range=(0, 0.5), x_labels={0.1: "0.1", AL: r"\tan^{-1}\frac{1}{3}", 0.5: "0.5"},
                     y_labels={0.4: "0.4", 0.8: "0.8", 1.2: "1.2"}),
        u_func=lambda t: np.sqrt(np.maximum(0.0, 1 - np.sin(2 * t))) * np.exp(-2 * t),
        says=(cap(r"In $x$: the green area is about $0.200$."),
              cap(r"In $t$: a new curve, the same area.")),
    )

    ANSWER = eq(r"\frac{1}{5}")
    ANSWER_VALUE = 0.2
    CLOSE_SAYS = (cap(r"Thin rectangles close in on exactly $\frac{1}{5}=0.2$."),
                  cap(r"Takeaway: $\sqrt{w^{2}}=|w|$; check the sign before dropping bars."))
