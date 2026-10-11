import os
import sys
from contextlib import contextmanager

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from scipy.special import lambertw
import common
from common import IntegralVideo, LIMIT, NEW, cap, eq

E2 = float(np.e / 2)                # upper limit; the curve plunges to -infinity here
INV_LN2 = float(1 / np.log(2))      # lower limit (the larger number)
LN4 = float(2 * np.log(2))
FLOOR = -8.0                        # the drawn curve and rectangles stop at the bottom of the axes
NESTED = r"\ln(2x\ln(2x\ln(\dots)))"

def tower(x):
    """y = ln(2x ln(2x ln(...))): the limit of y -> ln(2xy), the root of y = ln(2xy) with y >= 1."""
    z = np.maximum(-1 / (2 * np.asarray(x, dtype=float)), -1 / np.e + 1e-16)
    return -lambertw(z, -1).real

def drawn(x):
    """The integrand as drawn: cut off at the bottom of the axes near the spike."""
    return np.maximum(MediumIntegral.FUNC(x), FLOOR)

@contextmanager
def drawn_curve():
    """Build graphs of the integrand from the cut-off curve; estimates still use FUNC."""
    original = common.build_graph

    def build(g, func, box=common.GRAPH_BOX):
        if func is not MediumIntegral.FUNC:
            return original(g, func, box)
        gr = original(g, drawn, box)
        gr.func = func
        rects = gr.axes.get_riemann_rectangles

        def thin_edges(*args, **kwargs):
            # white edges on more than 64 rectangles merge into a solid white block
            if abs(kwargs.get("dx", 1.0)) < (INV_LN2 - E2) / 64 * 0.99:
                kwargs["stroke_width"] = 0
            return rects(*args, **kwargs)

        gr.axes.get_riemann_rectangles = thin_edges
        return gr

    common.build_graph = build
    try:
        yield
    finally:
        common.build_graph = original

class MediumIntegral(IntegralVideo):
    DIFFICULTY = "Medium"
    DATE = "2026-10-11"

    @staticmethod
    def FUNC(x):
        return 1 / (x ** 2 * (1 - tower(x)))

    @classmethod
    def exact_integral(cls):
        with mp.workdps(40):            # the integrand has an inverse-square-root spike at e/2
            f = lambda x: 1 / (x ** 2 * (1 + mp.lambertw(-1 / (2 * x), -1).real))
            return mp.quad(f, [1 / mp.log(2), mp.e / 2])

    COLORS = {NESTED: NEW, "y": NEW, r"\,dy": NEW}
    PROBLEM = eq(r"\int_{", (r"\frac{1}{\ln 2}", LIMIT), r"}^{", (r"\frac{e}{2}", LIMIT), r"}", r"\frac{1}{", "x^{2}",
                 r"(1-", NESTED, ")", r"}", r"\,dx")
    CURVE_LABEL = eq("y", "=", r"\frac{1}{", "x^{2}", r"(1-", NESTED, ")", r"}")
    LABEL_AT = (1.385, -6.6)    # empty lower-right region, below the curve (which is above -2 there)

    GRAPH = dict(x_range=[1.34, 1.46, 0.02], y_range=[-8, 0, 2], a=E2, b=INV_LN2, size=(8, 4.2),
                 plot_range=(1.3621, 1.46),
                 x_labels={E2: r"\frac{e}{2}", 1.4: "1.4", INV_LN2: r"\frac{1}{\ln 2}"},
                 y_labels={-2: "-2", -4: "-4", -6: "-6", -8: "-8"})
    WINDOW = (INV_LN2, E2)      # the integral runs from 1/ln 2 down to e/2
    COUNTS = (8, 32, 128, 512, 2048)    # the spike at e/2 needs many thin rectangles

    HOOK = cap(r"Backwards limits, a curve below the axis. What sign results?")
    INTUITION = cap(r"Thin rectangles estimate the area; watch the gap shrink.")
    INSIGHT = dict(
        parts=[NESTED],
        label=cap(r"$y=\ln(2xy)$"),
        say=cap(r"The tower repeats inside itself: call it $y$."),
    )

    LIMS = (r"\int_{", (r"\frac{1}{\ln 2}", LIMIT), r"}^{", (r"\frac{e}{2}", LIMIT), r"}")
    BODY = (r"\frac{1}{", "x^{2}", r"(1-", "y", ")", r"}", r"\,dx")
    STEPS = [
        dict(tex=eq(*LIMS, *BODY, r",\quad", "y", "=", r"\ln(2x", "y", ")"),
             say=cap(r"Under the outer $\ln$ sits $y$ again: $y=\ln(2xy)$."),
             rule="nested_fixed_point",
             mapping=[cap(r"$g'(y)=\frac{1}{y}$, so the limit has $y\ge 1$.")]),
        dict(tex=eq(*LIMS, *BODY, r",\quad", "x", "=", r"\frac{e^{y}}{2y}", r",\quad", "dx", "=",
                    r"\frac{e^{y}(y-1)}{2y^{2}}", r"\,dy"),
             say=cap(r"Solve for $x$, then trade $dx$ for $dy$."),
             rule=["exp_log_inverse", "exp_derivative", "quotient_rule"],
             mapping={"exp_log_inverse": [cap(r"$e^{y}=e^{\ln(2xy)}=2xy$.")],
                      "exp_derivative": [cap(r"The top, $e^{y}$, has derivative $e^{y}$.")],
                      "quotient_rule": [cap(r"$\frac{e^{y}\cdot 2y-e^{y}\cdot 2}{4y^{2}}=\frac{e^{y}(y-1)}{2y^{2}}$.")]}),
        dict(tex=eq(r"\int_{", (r"2\ln 2", LIMIT), r"}^{", ("1", LIMIT), r"}", "-2", "e^{-y}", r"\,dy"),
             say=cap(r"Substitute: $y^{2}$ cancels and $\frac{y-1}{1-y}=-1$."),
             rule=["u_substitution", "change_of_limits", "exponent_laws"],
             mapping={"u_substitution": [cap(r"$\frac{1}{x^{2}}=\frac{4y^{2}}{e^{2y}}$, times $dx=\frac{e^{y}(y-1)}{2y^{2}}\,dy$.")],
                      "change_of_limits": [cap(r"$x=\frac{1}{\ln 2}$ gives $y=2\ln 2$; $x=\frac{e}{2}$ gives $y=1$.")],
                      "exponent_laws": [cap(r"$\frac{e^{y}}{e^{2y}}=e^{y-2y}=e^{-y}$.")]}),
        dict(tex=eq(r"\Big[", "2", "e^{-y}", r"\Big]_{", (r"2\ln 2", LIMIT), r"}^{", ("1", LIMIT), r"}"),
             say=cap(r"Integrate $-2e^{-y}$."),
             rule=["linearity", "exp_integral"],
             mapping={"linearity": [cap(r"Pull out the constant $-2$.")],
                      "exp_integral": [cap(r"$\int e^{-y}\,dy=-e^{-y}$.")]}),
        dict(tex=eq(r"\frac{2}{e}", "-", r"\frac{1}{2}"),
             say=cap(r"$2e^{-1}-\frac{2}{4}=\frac{2}{e}-\frac{1}{2}$."),
             rule=["ftc", "exponent_laws", "exp_log_inverse"],
             mapping={"ftc": [cap(r"Upper minus lower: $2e^{-1}-2e^{-2\ln 2}$.")],
                      "exponent_laws": [cap(r"$e^{-2\ln 2}=\big(e^{\ln 2}\big)^{-2}$.")],
                      "exp_log_inverse": [cap(r"$e^{\ln 2}=2$, so that is $2^{-2}=\frac{1}{4}$.")]}),
    ]

    def hook(self):
        with drawn_curve():
            return super().hook()

    ANSWER = eq(r"\frac{2}{e}", "-", r"\frac{1}{2}")
    ANSWER_VALUE = float(2 / np.e - 0.5)
    CLOSE_SAYS = (cap(r"$2048$ rectangles agree: about $0.2358$, positive."),
                  cap(r"Takeaway: name a self-repeating tower, then solve for it."))
