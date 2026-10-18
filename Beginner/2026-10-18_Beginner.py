import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import IntegralVideo, LIMIT, NEW, cap, eq


class BeginnerIntegral(IntegralVideo):
    DIFFICULTY = "Beginner"
    DATE = "2026-10-18"

    @staticmethod
    def FUNC(x):
        x = np.asarray(x, dtype=float)
        return (x * np.exp(x ** 2) * np.sqrt(np.e * x)) ** 2 / np.exp(np.sqrt(1 + 2 * x ** 2 + x ** 4))

    @classmethod
    def exact_integral(cls):
        return mp.quad(lambda x: (x * mp.exp(x ** 2) * mp.sqrt(mp.e * x)) ** 2 / mp.exp(mp.sqrt(1 + 2 * x ** 2 + x ** 4)),
                       [0, 1])

    SQ = r"1+2x^{2}+x^{4}"
    COLORS = {"x^{2}": NEW, r"2x\,dx": NEW, "u": NEW, r"\,du": NEW}
    LIMS = (r"\int_{", ("0", LIMIT), r"}^{", ("1", LIMIT), r"}")
    LIMU = (r"\int_{", ("0", LIMIT), r"}^{", ("1", LIMIT), r"}")
    TOP = r"\left(xe^{x^{2}}\sqrt{ex}\right)^{2}"
    PROBLEM = eq(*LIMS, r"\frac{", TOP, r"}{", r"e^{\sqrt{", SQ, r"}}", r"}", r"\,dx")
    CURVE_LABEL = eq("y", "=", r"\frac{", TOP, r"}{", r"e^{\sqrt{", SQ, r"}}", r"}")
    LABEL_AT = (0.03, 1.75)     # empty upper-left, where the curve is still below 0.5

    GRAPH = dict(x_range=[0, 1, 0.25], y_range=[0, 3, 0.5], a=0, b=1, size=(8, 3.8), plot_range=(0, 1),
                 x_labels={0.5: "0.5", 1: "1"},
                 y_labels={1: "1", 2: "2", 3: "3"})

    HOOK = cap(r"A tangle of exponents and roots. What is really underneath?")
    INTUITION = cap(r"Thin rectangles estimate the area; watch the gap shrink.")
    INSIGHT = dict(
        parts=[SQ],
        label=cap(r"$(1+x^{2})^{2}$"),
        say=cap(r"Under the root hides a perfect square: $(1+x^{2})^{2}$."),
    )

    STEPS = [
        dict(tex=eq(*LIMS, r"x^{2}e^{2x^{2}}\cdot ex", r"\cdot ", r"e^{-(1+x^{2})}", r"\,dx"),
             say=cap(r"Square the top; the root of $(1+x^{2})^{2}$ is $1+x^{2}$."),
             rule="exponent_laws"),
        dict(tex=eq(*LIMS, r"\tfrac{1}{2}", "x^{2}", r"e^{", "x^{2}", r"}", r"\cdot", r"2x\,dx"),
             say=cap(r"Exponents combine to $x^{3}e^{x^{2}}$; write $x^{3}=\frac{1}{2}x^{2}\cdot 2x$."),
             highlight=(["x^{2}", r"2x\,dx"], cap(r"$u$ and $du$")),
             rule="exponent_laws"),
        dict(tex=eq(r"\tfrac{1}{2}", *LIMU, "u", r"e^{", "u", r"}", r"\,du"),
             say=cap(r"Let $u=x^{2}$: the limits $0$ and $1$ stay put."),
             rule=["u_substitution", "change_of_limits"],
             mapping={"u_substitution": [cap(r"Here $u=x^{2}$, so $du=2x\,dx$.")],
                      "change_of_limits": [cap(r"$x=0$ gives $u=0$; $x=1$ gives $u=1$.")]},
             then="substitution"),
        dict(tex=eq(r"\tfrac{1}{2}", r"\Big[", "u", r"e^{", "u", r"}", "-", r"e^{", "u", r"}", r"\Big]_{",
                    ("0", LIMIT), r"}^{", ("1", LIMIT), r"}"),
             say=cap(r"By parts: $\int ue^{u}\,du=ue^{u}-\int e^{u}\,du$."),
             rule=["integration_by_parts", "exp_integral"],
             mapping={"integration_by_parts": [cap(r"Differentiate $u$ to $1$; integrate $e^{u}$ to $e^{u}$.")],
                      "exp_integral": [cap(r"So $\int e^{u}\,du=e^{u}$ finishes it.")]}),
        dict(tex=eq(r"\tfrac{1}{2}", r"\Big(", r"(e-e)", "-", r"(0-1)", r"\Big)"),
             say=cap(r"Top limit minus bottom limit."),
             rule="ftc"),
        dict(tex=eq(r"\frac{1}{2}"),
             say=cap(r"Exactly one half."),
             rule="algebra"),
    ]

    SUBSTITUTION = dict(
        u_graph=dict(x_range=[0, 1, 0.25], y_range=[0, 1.5, 0.5], a=0, b=1, var="u", size=(8, 3.8),
                     plot_range=(0, 1), x_labels={0.5: "0.5", 1: "1"},
                     y_labels={0.5: "0.5", 1: "1"}),
        u_func=lambda u: 0.5 * u * np.exp(u),
        says=(cap(r"In $x$: the green area is about $0.5$."),
              cap(r"In $u$: the curve $\frac{1}{2}ue^{u}$, with the same area.")),
    )

    ANSWER = eq(r"\frac{1}{2}")
    ANSWER_VALUE = 0.5
    CLOSE_SAYS = (cap(r"Thin rectangles close in on $\frac{1}{2}=0.5$."),
                  cap(r"Takeaway: simplify first; the real integral is often small."))
