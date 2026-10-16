import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import IntegralVideo, LIMIT, NEW, cap, eq


class BeginnerIntegral(IntegralVideo):
    DIFFICULTY = "Beginner"
    DATE = "2026-10-16"

    @staticmethod
    def FUNC(x):
        x = np.asarray(x, dtype=float)
        return (np.sqrt(x) - 1) ** 5 / np.sqrt(x)

    @classmethod
    def exact_integral(cls):
        return mp.quad(lambda x: (mp.sqrt(x) - 1) ** 5 / mp.sqrt(x), [1, 4])

    INSIDE = r"\sqrt{x}-1"
    COLORS = {INSIDE: NEW, r"\frac{1}{\sqrt{x}}\,dx": NEW, "u": NEW, r"\,du": NEW}
    LIMS = (r"\int_{", ("1", LIMIT), r"}^{", ("4", LIMIT), r"}")
    LIMU = (r"\int_{", ("0", LIMIT), r"}^{", ("1", LIMIT), r"}")
    PROBLEM = eq(*LIMS, r"\frac{(", INSIDE, r")^{5}}{", r"\sqrt{x}", r"}", r"\,dx")
    CURVE_LABEL = eq("y", "=", r"\frac{(", INSIDE, r")^{5}}{", r"\sqrt{x}", r"}")
    LABEL_AT = (0.9, 0.42)      # empty space above the curve, which stays below 0.12 for x < 3

    GRAPH = dict(x_range=[0, 4.5, 0.5], y_range=[0, 0.8, 0.2], a=1, b=4, size=(8, 4.2), plot_range=(1, 4.3),
                 x_labels={1: "1", 2: "2", 3: "3", 4: "4"},
                 y_labels={0.2: "0.2", 0.4: "0.4", 0.6: "0.6"})

    HOOK = cap(r"A fifth power over a root. Must we expand it?")
    INTUITION = cap(r"Thin rectangles estimate the area; watch the gap shrink.")
    INSIGHT = dict(
        parts=[INSIDE, r"\sqrt{x}"],
        label=cap(r"$u=\sqrt{x}-1$"),
        say=cap(r"$\frac{1}{\sqrt{x}}$ is nearly the derivative of $\sqrt{x}-1$."),
    )

    STEPS = [
        dict(tex=eq(*LIMS, r"(", INSIDE, r")^{5}", r"\cdot", r"\frac{1}{\sqrt{x}}\,dx"),
             say=cap(r"Keep $\frac{1}{\sqrt{x}}\,dx$ together: it becomes $2\,du$."),
             highlight=([INSIDE, r"\frac{1}{\sqrt{x}}\,dx"], cap(r"$u$ and $2\,du$")),
             rule="algebra"),
        dict(tex=eq(*LIMU, "u", r"^{5}", r"\cdot", "2", r"\,du"),
             say=cap(r"Let $u=\sqrt{x}-1$: the limits $1$ and $4$ become $0$ and $1$."),
             rule=["u_substitution", "change_of_limits", "power_rule"],
             mapping={"u_substitution": [cap(r"Here $u=\sqrt{x}-1$, so $du=\frac{1}{2\sqrt{x}}\,dx$.")],
                      "change_of_limits": [cap(r"$x=1$ gives $u=0$; $x=4$ gives $u=1$.")]},
             then="substitution"),
        dict(tex=eq(r"\Big[", r"\frac{1}{3}", "u", r"^{6}", r"\Big]_{", ("0", LIMIT), r"}^{", ("1", LIMIT), r"}"),
             say=cap(r"Power rule: $2\cdot\frac{u^{6}}{6}=\frac{u^{6}}{3}$."),
             rule=["power_rule", "linearity"]),
        dict(tex=eq(r"\frac{1}{3}", r"(1-0)"),
             say=cap(r"Top limit minus bottom limit."),
             rule="ftc"),
        dict(tex=eq(r"\frac{1}{3}"),
             say=cap(r"No expanding needed: exactly one third."),
             rule="algebra"),
    ]

    SUBSTITUTION = dict(
        u_graph=dict(x_range=[0, 1.2, 0.2], y_range=[0, 2, 0.5], a=0, b=1, var="u", size=(8, 4.2),
                     plot_range=(0, 1), x_labels={0.5: "0.5", 1: "1"},
                     y_labels={0.5: "0.5", 1: "1", 1.5: "1.5", 2: "2"}),
        u_func=lambda u: 2 * u ** 5,
        says=(cap(r"In $x$: the green area is about $0.333$."),
              cap(r"In $u$: the curve $2u^{5}$, with exactly the same area.")),
    )

    ANSWER = eq(r"\frac{1}{3}")
    ANSWER_VALUE = 1 / 3
    CLOSE_SAYS = (cap(r"Thin rectangles close in on $\frac{1}{3}\approx 0.3333$."),
                  cap(r"Takeaway: spot an inside function whose derivative is also there."))
