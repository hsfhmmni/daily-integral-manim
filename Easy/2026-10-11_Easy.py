import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import IntegralVideo, LIMIT, NEW, cap, eq


class EasyIntegral(IntegralVideo):
    DIFFICULTY = "Easy"
    DATE = "2026-10-11"

    @staticmethod
    def FUNC(x):
        return (x * np.log(x ** 2 + x) + np.log(x + 1)) / (x ** 2 + x)

    @classmethod
    def exact_integral(cls):
        return mp.quad(lambda x: (x * mp.log(x ** 2 + x) + mp.log(x + 1)) / (x ** 2 + x), [1, 2])

    COLORS = {r"\ln x": NEW, r"\ln(x+1)": NEW}
    PROBLEM = eq(r"\int_{", ("1", LIMIT), r"}^{", ("2", LIMIT), r"}", r"\frac{", r"x\ln(x^{2}+x)", "+", r"\ln(x+1)",
                 r"}{", r"x^{2}+x", r"}", r"\,dx")
    CURVE_LABEL = eq("y", "=", r"\frac{", r"x\ln(x^{2}+x)", "+", r"\ln(x+1)", r"}{", r"x^{2}+x", r"}")
    LABEL_AT = (0.05, 0.84)     # empty band above the curve, which stays below 0.8

    GRAPH = dict(x_range=[0, 2.5, 0.5], y_range=[0, 1.25, 0.25], a=1, b=2, size=(8, 4.2), plot_range=(0.4, 2.5),
                 x_labels={0.5: "0.5", 1: "1", 1.5: "1.5", 2: "2"},
                 y_labels={0.25: "0.25", 0.5: "0.5", 0.75: "0.75", 1: "1"})

    HOOK = cap(r"How big is the green area from $x=1$ to $x=2$?")
    INTUITION = cap(r"Thin rectangles estimate the area; watch the gap shrink.")
    INSIGHT = dict(
        parts=[r"x^{2}+x"],
        label=cap(r"$x^{2}+x=x(x+1)$"),
        say=cap(r"Factor the bottom, and the logarithm on top splits too."),
    )

    STEPS = [
        dict(tex=eq(r"\int_{", ("1", LIMIT), r"}^{", ("2", LIMIT), r"}", r"\frac{", "x", r"\ln x", "+", "x", r"\ln(x+1)", "+",
                    r"\ln(x+1)", r"}{", r"x(x+1)", r"}", r"\,dx"),
             say=cap(r"$\ln\big(x(x+1)\big)$ becomes $\ln x+\ln(x+1)$."),
             rule="log_laws",
             mapping=[cap(r"Here $a=x$ and $b=x+1$, both positive on $[1,2]$.")]),
        dict(tex=eq(r"\int_{", ("1", LIMIT), r"}^{", ("2", LIMIT), r"}", r"\frac{", "x", r"\ln x", "+", "(x+1)", r"\ln(x+1)",
                    r"}{", r"x(x+1)", r"}", r"\,dx"),
             say=cap(r"Group the $\ln(x+1)$ terms into $(x+1)\ln(x+1)$."),
             rule="algebra"),
        dict(tex=eq(r"\int_{", ("1", LIMIT), r"}^{", ("2", LIMIT), r"}", r"\Big(", r"\frac{", r"\ln x", r"}{x+1}", "+",
                    r"\frac{", r"\ln(x+1)", r"}{x}", r"\Big)", r"\,dx"),
             say=cap(r"Split the fraction: each term cancels one factor of the bottom."),
             rule="algebra"),
        dict(tex=eq(r"\int_{", ("1", LIMIT), r"}^{", ("2", LIMIT), r"}", r"\frac{d}{dx}", r"\Big[", r"\ln x", r"\cdot",
                    r"\ln(x+1)", r"\Big]", r"\,dx"),
             say=cap(r"That is the product rule for $\ln x\cdot\ln(x+1)$."),
             rule=["product_rule", "ln_derivative", "chain_rule"],
             mapping={"product_rule": [cap(r"Here $f=\ln x$ and $g=\ln(x+1)$.")],
                      "ln_derivative": [cap(r"$f'=\frac{1}{x}$ gives the term $\frac{\ln(x+1)}{x}$.")],
                      "chain_rule": [cap(r"$g'=\frac{1}{x+1}\cdot 1$ gives the term $\frac{\ln x}{x+1}$.")]}),
        dict(tex=eq(r"\Big[", r"\ln x", r"\cdot", r"\ln(x+1)", r"\Big]_{", ("1", LIMIT), r"}^{", ("2", LIMIT), r"}"),
             say=cap(r"Integrating a derivative undoes it."),
             rule="ftc",
             mapping=[cap(r"Here $F=\ln x\cdot\ln(x+1)$, since $F'$ is our integrand.")]),
        dict(tex=eq(r"\ln 2", r"\cdot", r"\ln 3"),
             say=cap(r"At $x=2$: $\ln 2\cdot\ln 3$. At $x=1$: $\ln 1\cdot\ln 2=0$."),
             rule="log_values",
             mapping=[cap(r"$\ln 1=0$, so the lower limit adds nothing.")]),
    ]

    ANSWER = eq(r"\ln 2", r"\cdot", r"\ln 3")
    ANSWER_VALUE = float(np.log(2) * np.log(3))
    CLOSE_SAYS = (cap(r"More, thinner rectangles close in on $\ln 2\cdot\ln 3\approx 0.7615$."),
                  cap(r"Takeaway: when terms pair up as $f'g+fg'$, integrate to $fg$."))
