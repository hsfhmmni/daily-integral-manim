import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import IntegralVideo, LIMIT, NEW, cap, eq


class HardIntegral(IntegralVideo):
    DIFFICULTY = "Hard"
    DATE = "2026-10-22"

    # cosh x + sinh x = e^x and cosh x - sinh x = e^{-x} (both positive, so the complex powers
    # are e^{(1+i)x} and e^{-(1-i)x}); the integrand is e^{-x^2 - 2ix} = e^{-1} e^{-(x+i)^2},
    # and shifting the line back to the real axis leaves the Gaussian: sqrt(pi)/e.
    # The imaginary part -e^{-x^2} sin 2x is odd, so the graph shows the real part.
    @staticmethod
    def FUNC(x):
        x = np.asarray(x, dtype=float)
        return np.exp(-x ** 2) * np.cos(2 * x)

    @classmethod
    def exact_integral(cls):
        return mp.quad(lambda x: mp.exp(-x ** 2) * mp.cos(2 * x), [-mp.inf, 0, mp.inf])

    COLORS = {r"(e^{x})": NEW, r"(e^{-x})": NEW, r"e^{2ix}": NEW}
    LIMS = (r"\int_{", (r"-\infty", LIMIT), r"}^{", (r"\infty", LIMIT), r"}")
    PROBLEM = eq(*LIMS, r"\frac{", r"e^{-x^{2}}", r"}{", r"(\cosh x+\sinh x)", r"^{1+i}",
                 r"(\cosh x-\sinh x)", r"^{1-i}", r"}", r"\,dx")
    CURVE_LABEL = None

    GRAPH = dict(x_range=[-3, 3, 1], y_range=[-0.4, 1.2, 0.4], a=-3, b=3, size=(8.5, 4.2),
                 x_labels={-2: "-2", -1: "-1", 1: "1", 2: "2"},
                 y_labels={0.4: "0.4", 0.8: "0.8"})
    CLOSE_WIDEN = (-6, 6)       # the tails beyond 3 add about 1e-5

    HOOK = cap(r"Complex powers everywhere. Why is this area a real number?")
    HOOK_NOTE = cap(r"The blue curve is the real part of the integrand.")
    INTUITION = cap(r"Thin rectangles estimate the area; watch the gap shrink.")
    INSIGHT = dict(
        parts=[r"(\cosh x+\sinh x)", r"(\cosh x-\sinh x)"],
        label=cap(r"just $e^{x}$ and $e^{-x}$"),
        say=cap(r"As exponentials, the complex powers merge into one."),
    )

    STEPS = [
        dict(tex=eq(*LIMS, r"\frac{", r"e^{-x^{2}}", r"}{", r"(e^{x})", r"^{1+i}", r"(e^{-x})", r"^{1-i}", r"}",
                    r"\,dx"),
             say=cap(r"$\cosh x+\sinh x=e^{x}$ and $\cosh x-\sinh x=e^{-x}$."),
             rule="cosh_sinh_exp"),
        dict(tex=eq(*LIMS, r"\frac{", r"e^{-x^{2}}", r"}{", r"e^{2ix}", r"}", r"\,dx"),
             say=cap(r"Add the powers: $(1+i)x-(1-i)x=2ix$."),
             rule="exponent_laws"),
        dict(tex=eq(*LIMS, r"e^{-x^{2}-2ix}", r"\,dx"),
             say=cap(r"Its imaginary part $-e^{-x^{2}}\sin 2x$ is odd, so it cancels."),
             rule=["exponent_laws", "euler_formula", "odd_even_symmetry"],
             then="reflection"),
        dict(tex=eq(r"e^{-1}", *LIMS, r"e^{-(x+i)^{2}}", r"\,dx"),
             say=cap(r"Complete the square: $-x^{2}-2ix=-(x+i)^{2}-1$."),
             rule=["completing_the_square", "exponent_laws"]),
        dict(tex=eq(r"e^{-1}", *LIMS, r"e^{-x^{2}}", r"\,dx"),
             say=cap(r"Slide the path $x+i$ back down to the real axis."),
             rule="contour_shift",
             mapping=[cap(r"Here $c=1$: the path $x+i$ runs one unit above.")]),
        dict(tex=eq(r"\frac{\sqrt{\pi}}{e}"),
             say=cap(r"The bell curve's area is $\sqrt{\pi}$, so the answer is $\frac{\sqrt{\pi}}{e}$."),
             rule=["gaussian_integral", "improper_integral"],
             mapping={"gaussian_integral": [cap(r"Here the whole bell $e^{-x^{2}}$ is left, times $e^{-1}$.")]}),
    ]

    REFLECTION = dict(
        spec=dict(x_range=[-3, 3, 1], y_range=[-0.75, 0.75, 0.25], size=(8, 3.4),
                  x_labels={-2: "-2", -1: "-1", 1: "1", 2: "2"}, y_labels={0.5: "0.5", -0.5: "-0.5"}),
        func=lambda x: -np.exp(-np.asarray(x, dtype=float) ** 2) * np.sin(2 * np.asarray(x, dtype=float)),
        mode="point",
        says=(cap(r"The imaginary part $-e^{-x^{2}}\sin 2x$ is odd."),
              cap(r"Spun half a turn, the left piece cancels the right piece.")),
    )

    ANSWER = eq(r"\frac{\sqrt{\pi}}{e}")
    ANSWER_VALUE = float(np.sqrt(np.pi) / np.e)
    CLOSE_SAYS = (cap(r"Rectangles under the real part close in on $0.6520$."),
                  cap(r"Takeaway: complete the square, then slide the bell back home."))
