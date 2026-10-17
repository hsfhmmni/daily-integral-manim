import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import IntegralVideo, LIMIT, NEW, cap, eq

LN3 = float(np.log(3))


class BeginnerIntegral(IntegralVideo):
    DIFFICULTY = "Beginner"
    DATE = "2026-10-17"

    @staticmethod
    def FUNC(x):
        x = np.asarray(x, dtype=float)
        return np.exp(x) / (1 + np.exp(x)) ** 2

    @classmethod
    def exact_integral(cls):
        return mp.quad(lambda x: mp.exp(x) / (1 + mp.exp(x)) ** 2, [0, mp.log(3)])

    INSIDE = r"1 + e^{x}"
    COLORS = {INSIDE: NEW, r"e^{x}\,dx": NEW, "u": NEW, r"\,du": NEW}
    LIMS = (r"\int_{", ("0", LIMIT), r"}^{", (r"\ln 3", LIMIT), r"}")
    LIMU = (r"\int_{", ("2", LIMIT), r"}^{", ("4", LIMIT), r"}")
    PROBLEM = eq(*LIMS, r"\frac{", r"e^{x}", r"}{(", INSIDE, r")^{2}}", r"\,dx")
    CURVE_LABEL = eq("y", "=", r"\frac{", r"e^{x}", r"}{(", INSIDE, r")^{2}}")
    LABEL_AT = (0.55, 0.27)     # empty space above the curve, which falls from 0.25 to 0.19

    GRAPH = dict(x_range=[0, 1.25, 0.25], y_range=[0, 0.35, 0.05], a=0, b=LN3, size=(8, 4.2), plot_range=(0, 1.25),
                 x_labels={0.5: "0.5", LN3: r"\ln 3"},
                 y_labels={0.1: "0.1", 0.2: "0.2", 0.3: "0.3"})

    HOOK = cap(r"An exponential over its own square. Is there a pattern?")
    INTUITION = cap(r"Thin rectangles estimate the area; watch the gap shrink.")
    INSIGHT = dict(
        parts=[r"e^{x}", INSIDE],
        label=cap(r"$u=1+e^{x}$"),
        say=cap(r"The top $e^{x}$ is the derivative of $1+e^{x}$."),
    )

    STEPS = [
        dict(tex=eq(*LIMS, r"(", INSIDE, r")^{-2}", r"\cdot ", r"e^{x}\,dx"),
             say=cap(r"Keep $e^{x}\,dx$ together: it becomes $du$."),
             highlight=([INSIDE, r"e^{x}\,dx"], cap(r"$u$ and $du$")),
             rule="exponent_laws"),
        dict(tex=eq(*LIMU, "u", r"^{-2}", r"\,du"),
             say=cap(r"Let $u=1+e^{x}$: the limits $0$ and $\ln 3$ become $2$ and $4$."),
             rule=["u_substitution", "exp_derivative", "change_of_limits", "exp_log_inverse"],
             mapping={"u_substitution": [cap(r"Here $u=1+e^{x}$, so $du=e^{x}\,dx$.")],
                      "change_of_limits": [cap(r"$x=0$ gives $u=2$; $x=\ln 3$ gives $u=4$.")]},
             then="substitution"),
        dict(tex=eq(r"\Big[", "-", "u", r"^{-1}", r"\Big]_{", ("2", LIMIT), r"}^{", ("4", LIMIT), r"}"),
             say=cap(r"Power rule: $u^{-2}$ integrates to $-u^{-1}$."),
             rule="power_rule"),
        dict(tex=eq(r"-\frac{1}{4}", "+", r"\frac{1}{2}"),
             say=cap(r"Top limit minus bottom limit."),
             rule="ftc"),
        dict(tex=eq(r"\frac{1}{4}"),
             say=cap(r"Exactly one quarter."),
             rule="algebra"),
    ]

    SUBSTITUTION = dict(
        u_graph=dict(x_range=[0, 4.5, 0.5], y_range=[0, 0.3, 0.05], a=2, b=4, var="u", size=(8, 4.2),
                     plot_range=(1.9, 4.5), x_labels={1: "1", 2: "2", 3: "3", 4: "4"},
                     y_labels={0.1: "0.1", 0.2: "0.2"}),
        u_func=lambda u: u ** -2.0,
        says=(cap(r"In $x$: the green area is about $0.25$."),
              cap(r"In $u$: the curve $\frac{1}{u^{2}}$, with exactly the same area.")),
    )

    ANSWER = eq(r"\frac{1}{4}")
    ANSWER_VALUE = 0.25
    CLOSE_SAYS = (cap(r"Thin rectangles close in on $\frac{1}{4}=0.25$."),
                  cap(r"Takeaway: a top that is the bottom's derivative invites $u$."))
