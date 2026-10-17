import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import IntegralVideo, LIMIT, NEW, cap, eq

LO = float(np.log(np.sqrt(2)))      # the lower limit, about 0.347


class EasyIntegral(IntegralVideo):
    DIFFICULTY = "Easy"
    DATE = "2026-10-17"

    @staticmethod
    def FUNC(x):
        x = np.asarray(x, dtype=float)
        return (2 * x - 1) / (2 * np.exp(2 * x) - x)

    @classmethod
    def exact_integral(cls):
        return mp.quad(lambda x: (2 * x - 1) / (2 * mp.exp(2 * x) - x), [mp.log(mp.sqrt(2)), 1, 5, mp.inf])

    BOT = r"2-xe^{-2x}"
    TOP = r"(2x-1)e^{-2x}"
    COLORS = {BOT: NEW, "u": NEW, r"\,du": NEW}
    LIMS = (r"\int_{", (r"\ln\sqrt{2}", LIMIT), r"}^{", (r"\infty", LIMIT), r"}")
    LIMU = (r"\int_{", (r"2-\frac{\ln 2}{4}", LIMIT), r"}^{", ("2", LIMIT), r"}")
    PROBLEM = eq(*LIMS, r"\frac{", r"2x-1", r"}{", r"2e^{2x}-x", r"}", r"\,dx")
    CURVE_LABEL = eq("y", "=", r"\frac{", r"2x-1", r"}{", r"2e^{2x}-x", r"}")
    LABEL_AT = (2.6, 0.06)      # empty space above the tail, which is below 0.03 for x > 2

    GRAPH = dict(x_range=[0, 6, 1], y_range=[-0.1, 0.1, 0.05], a=LO, b=6, size=(8, 4.2), plot_range=(LO, 6),
                 x_labels={1: "1", 2: "2", 3: "3", 4: "4", 5: "5"},
                 y_labels={-0.05: "-0.05", 0.05: "0.05"})
    WINDOW = (LO, 6)            # the tail beyond 6 adds less than 0.00002
    CLOSE_WIDEN = (LO, 10)

    HOOK = cap(r"Negative, then positive, out to $\infty$. Does the area settle?")
    INTUITION = cap(r"Thin rectangles estimate the signed area; watch the gap shrink.")
    INSIGHT = dict(
        parts=[r"2e^{2x}-x"],
        label=cap(r"$\times\, e^{-2x}$"),
        say=cap(r"Tame the bottom: multiply top and bottom by $e^{-2x}$."),
    )

    STEPS = [
        dict(tex=eq(*LIMS, r"\frac{", TOP, r"}{", BOT, r"}", r"\,dx"),
             say=cap(r"Now the top is exactly the derivative of the bottom."),
             highlight=([TOP], cap(r"$(2x-1)e^{-2x}\,dx=du$")),
             side=UP,
             rule="exponent_laws"),
        dict(tex=eq(*LIMU, r"\frac{1}{", "u", r"}", r"\,du"),
             say=cap(r"Let $u=2-xe^{-2x}$: then $du=(2x-1)e^{-2x}\,dx$."),
             rule=["u_substitution", "product_rule", "chain_rule", "exp_derivative", "change_of_limits",
                   "improper_integral"],
             mapping={"u_substitution": [cap(r"Here $u=2-xe^{-2x}$, the new bottom.")],
                      "product_rule": [cap(r"Here $f=x$ and $g=e^{-2x}$.")],
                      "chain_rule": [cap(r"$\frac{d}{dx}e^{-2x}=-2e^{-2x}$: the inside $-2x$ gives $-2$.")],
                      "change_of_limits": [cap(r"$x=\ln\sqrt{2}$ makes $e^{-2x}=\frac{1}{2}$, so $u=2-\frac{\ln 2}{4}$.")],
                      "improper_integral": [cap(r"As $x\to\infty$, $xe^{-2x}\to 0$, so $u\to 2$.")]}),
        dict(tex=eq(r"\Big[", r"\ln|", "u", r"|", r"\Big]_{", (r"2-\frac{\ln 2}{4}", LIMIT), r"}^{", ("2", LIMIT), r"}"),
             say=cap(r"The integral of $\frac{1}{u}$ is $\ln|u|$."),
             rule="reciprocal_integral",
             mapping=[cap(r"Here the variable is $u$, and $u>0$ throughout.")]),
        dict(tex=eq(r"\ln 2", "-", r"\ln\Big(2-\frac{\ln 2}{4}\Big)"),
             say=cap(r"Upper limit minus lower limit."),
             rule=["ftc", "absolute_value"]),
        dict(tex=eq(r"\ln\frac{8}{8-\ln 2}"),
             say=cap(r"Combine the logs, then multiply top and bottom by $4$."),
             rule="log_laws"),
    ]

    ANSWER = eq(r"\ln\frac{8}{8-\ln 2}")
    ANSWER_VALUE = float(np.log(8 / (8 - np.log(2))))
    CLOSE_SAYS = (cap(r"Thin rectangles close in on $0.0906$."),
                  cap(r"Takeaway: rescale until the top is the bottom's derivative."))
