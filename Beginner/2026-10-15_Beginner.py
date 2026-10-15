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
    DATE = "2026-10-15"

    @staticmethod
    def FUNC(x):
        x = np.asarray(x, dtype=float)
        return x ** (1 / np.log(x))

    @classmethod
    def exact_integral(cls):
        return mp.quad(lambda x: x ** (1 / mp.log(x)), [2, 5])

    POWER = r"x^{\frac{1}{\ln x}}"
    COLORS = {POWER: NEW, r"\big(e^{\ln x}\big)^{\frac{1}{\ln x}}": NEW}
    LIMS = (r"\int_{", ("2", LIMIT), r"}^{", ("5", LIMIT), r"}")
    PROBLEM = eq(*LIMS, POWER, r"\,dx")
    CURVE_LABEL = eq("y", "=", POWER)
    LABEL_AT = (0.3, 3.2)       # empty space above the flat line, left of where it starts

    GRAPH = dict(x_range=[0, 6, 1], y_range=[0, 4, 1], a=2, b=5, size=(8, 4.2), plot_range=(1.25, 5.8),
                 x_labels={1: "1", 2: "2", 3: "3", 4: "4", 5: "5"},
                 y_labels={1: "1", 2: "2", E: "e"})

    HOOK = cap(r"A strange power, yet the curve is flat. Why?")
    HOOK_NOTE = cap(r"At $x=1$, $\ln x=0$: undefined, but $1$ is outside the limits.")
    INTUITION = cap(r"Every rectangle has height $e$, so the estimate never moves.")
    INSIGHT = dict(
        before=cap(r"A power of $x$ with $\ln x$ in the exponent."),
        parts=[POWER],
        label=cap(r"$x=e^{\ln x}$"),
        say=cap(r"Write $x$ as $e^{\ln x}$, and watch the exponent."),
    )

    STEPS = [
        dict(tex=eq(*LIMS, r"\big(e^{\ln x}\big)^{\frac{1}{\ln x}}", r"\,dx"),
             say=cap(r"$e$ and $\ln$ undo each other, so $x=e^{\ln x}$."),
             rule="exp_log_inverse"),
        dict(tex=eq(*LIMS, r"e^{\ln x\cdot\frac{1}{\ln x}}", r"\,dx"),
             say=cap(r"A power of a power: multiply the exponents."),
             rule="exponent_laws"),
        dict(tex=eq(*LIMS, "e", r"\,dx"),
             say=cap(r"$\ln x\neq 0$ on $[2,5]$, so the exponent is $1$."),
             rule="algebra"),
        dict(tex=eq(r"\Big[", "e", "x", r"\Big]_{", ("2", LIMIT), r"}^{", ("5", LIMIT), r"}"),
             say=cap(r"A constant $e$ integrates to $ex$."),
             rule=["power_rule", "linearity"]),
        dict(tex=eq("5e", "-", "2e"),
             say=cap(r"Upper limit minus lower limit."),
             rule="ftc"),
        dict(tex=eq("3e"),
             say=cap(r"A rectangle $3$ wide and $e$ tall."),
             rule="algebra"),
    ]

    ANSWER = eq("3e")
    ANSWER_VALUE = float(3 * np.e)
    CLOSE_SAYS = (cap(r"Thin rectangles agree: $3e\approx 8.155$."),
                  cap(r"Takeaway: a variable in the exponent? Rewrite the base as $e^{\ln x}$."))
