import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import IntegralVideo, LIMIT, NEW, cap, eq

E = float(np.e)


class BeginnerIntegral(IntegralVideo):
    DIFFICULTY = "Beginner"
    DATE = "2026-10-10"

    @staticmethod
    def FUNC(x):
        return x ** 2 * np.log(x)

    @classmethod
    def exact_integral(cls):
        return mp.quad(lambda x: x ** 2 * mp.log(x), [1, mp.e])

    COLORS = {r"\ln(x)": NEW, r"\frac{1}{x}": NEW}
    PROBLEM = eq(r"\int_{", ("1", LIMIT), r"}^{", ("e", LIMIT), r"}", "x^{2}", r"\ln(x)", r"\,dx")
    CURVE_LABEL = eq("y", "=", "x^{2}", r"\ln(x)")
    LABEL_AT = (0.3, 5.5)       # empty upper-left region, above the flat start of the curve

    GRAPH = dict(x_range=[0, 3, 0.5], y_range=[0, 10, 2], a=1, b=E, size=(8, 4.2), plot_range=(1, 2.9),
                 x_labels={1: "1", 2: "2", E: "e"}, y_labels={2: "2", 4: "4", 6: "6", 8: "8", 10: "10"})

    HOOK = cap(r"How big is the green area from $x=1$ to $x=e$?")
    HOOK_NOTE = cap(r"The area starts exactly where $\ln x=0$, at $x=1$.")
    INTUITION =cap(r"Thin rectangles estimate the area; watch the gap shrink.")
    INSIGHT = dict(
        before=cap(r"Two factors: $x^{2}$ and $\ln x$, in orange."),
        parts=[r"\ln(x)"],
        label=cap(r"$\frac{d}{dx}\ln x=\frac{1}{x}$"),
        say=cap(r"Differentiating $\ln x$ makes it simpler, so integrate by parts."),
    )

    STEPS = [
        dict(tex=eq(r"\Big[", r"\frac{x^{3}}{3}", r"\ln(x)", r"\Big]_{", ("1", LIMIT), r"}^{", ("e", LIMIT), r"}",
                    "-", r"\int_{", ("1", LIMIT), r"}^{", ("e", LIMIT), r"}", r"\frac{x^{3}}{3}", r"\cdot",
                    r"\frac{1}{x}", r"\,dx"),
             say=cap(r"Parts: $\int u\,dv=uv-\int v\,du$, with $u=\ln x$.")),
        dict(tex=eq(r"\Big[", r"\frac{x^{3}}{3}", r"\ln(x)", r"\Big]_{", ("1", LIMIT), r"}^{", ("e", LIMIT), r"}",
                    "-", r"\int_{", ("1", LIMIT), r"}^{", ("e", LIMIT), r"}", r"\frac{x^{2}}{3}", r"\,dx"),
             say=cap(r"The logarithm is gone: $\frac{x^{3}}{3}\cdot\frac{1}{x}=\frac{x^{2}}{3}$.")),
        dict(tex=eq(r"\Big[", r"\frac{x^{3}}{3}", r"\ln(x)", "-", r"\frac{x^{3}}{9}", r"\Big]_{", ("1", LIMIT),
                    r"}^{", ("e", LIMIT), r"}"),
             say=cap(r"Integrate $\frac{x^{2}}{3}$ to get $\frac{x^{3}}{9}$.")),
        dict(tex=eq(r"\Big(", r"\frac{e^{3}}{3}", r"\ln(e)", "-", r"\frac{e^{3}}{9}", r"\Big)", "-", r"\Big(",
                    r"\frac{1}{3}", r"\ln(1)", "-", r"\frac{1}{9}", r"\Big)"),
             say=cap(r"Upper limit minus lower limit.")),
        dict(tex=eq(r"\Big(", r"\frac{e^{3}}{3}", "-", r"\frac{e^{3}}{9}", r"\Big)", "-", r"\Big(", "0", "-",
                    r"\frac{1}{9}", r"\Big)"),
             say=cap(r"Use $\ln e=1$ and $\ln 1=0$.")),
        dict(tex=eq(r"\frac{2e^{3}}{9}", "+", r"\frac{1}{9}"),
             say=cap(r"$\frac{1}{3}-\frac{1}{9}=\frac{2}{9}$, and minus $\left(-\frac{1}{9}\right)$ adds.")),
        dict(tex=eq(r"\frac{2e^{3}+1}{9}"),
             say=cap(r"Put both over the common denominator $9$.")),
    ]

    ANSWER = eq(r"\frac{2e^{3}+1}{9}")
    ANSWER_VALUE = float((2 * np.e ** 3 + 1) / 9)
    CLOSE_SAYS = (cap(r"More, thinner rectangles close in on $\frac{2e^{3}+1}{9}\approx 4.5746$."),
                  cap(r"Takeaway: with a logarithm, differentiate it and integrate the rest."))
