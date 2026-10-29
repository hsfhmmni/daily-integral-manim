import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import IntegralVideo, LIMIT, NEW, cap, eq

X0 = float(np.exp(-5))          # the curve is drawn from here (y is just under 6)


class MediumIntegral(IntegralVideo):
    DIFFICULTY = "Medium"
    DATE = "2026-10-29"

    # x = 1/u turns I into int_0^inf (1 + ln u) u^2 / (1 + u^2)^2 du. Adding the two forms,
    # 2I = int 1/(1+x^2) dx - int ln x (1 - x^2)/(1 + x^2)^2 dx, and (1 - x^2)/(1 + x^2)^2 is the
    # derivative of x/(1 + x^2). By parts the second integral is [x ln x/(1+x^2)] - int 1/(1+x^2),
    # and the bracket is 0 at both ends, so 2I = 2 int_0^inf dx/(1+x^2) = pi and I = pi/2.
    # The integrand blows up like -ln x at 0 but is integrable there; it is negative (tiny) for x > e.
    @staticmethod
    def FUNC(x):
        x = np.asarray(x, dtype=float)
        return (1 - np.log(x)) / (1 + x * x) ** 2

    @classmethod
    def exact_integral(cls):
        return mp.quad(lambda x: (1 - mp.log(x)) / (1 + x ** 2) ** 2, [0, 1, mp.inf])

    COLORS = {"u": NEW, r"\,du": NEW, r"\Big(-\frac{du}{u^{2}}\Big)": NEW}
    LIMS = (r"\int_{", ("0", LIMIT), r"}^{", (r"\infty", LIMIT), r"}")
    TOP, LN, BOT = r"\frac{1-", r"\ln(x)", r"}{(1+x^{2})^{2}}"
    ATAN = r"\frac{1}{1+x^{2}}"
    LOGPART = r"\ln x\,\frac{1-x^{2}}{(1+x^{2})^{2}}"
    PROBLEM = eq(*LIMS, TOP, LN, BOT, r"\,dx")
    CURVE_LABEL = eq("y", "=", TOP, LN, BOT)
    LABEL_AT = (1.0, 2.6)       # empty space right of the spike, well above the curve (y = 0.25 at x = 1)

    GRAPH = dict(x_range=[0, 3, 0.5], y_range=[0, 6, 1], a=X0, b=3, size=(8.5, 4.2),
                 plot_range=(X0, 3), color_limits=False,
                 x_labels={1: "1", 2: "2", 3: "3"},
                 y_labels={2: "2", 4: "4", 6: "6"})
    WINDOW = (0, 3)                     # beyond 3 the curve is negative and tiny (about -0.0004 in all)
    CLOSE_WIDEN = (0, 30)
    END_COUNT = 16384                   # the log spike at 0 needs thin strips

    HOOK = cap(r"Infinite at $0$. Can the area still be finite?")
    INTUITION = cap(r"Thin rectangles still hug the spike; watch the gap shrink.")
    INSIGHT = dict(
        parts=[LN],
        label=cap(r"$x\to\frac{1}{x}$ flips its sign"),
        say=cap(r"We want $\ln x$ gone: $x\to\frac{1}{x}$ flips it."),
        side=UP,
    )

    STEPS = [
        dict(tex=eq(r"\int_{", (r"\infty", LIMIT), r"}^{", ("0", LIMIT), r"}",
                    r"\frac{1+\ln u}{(1+u^{-2})^{2}}", r"\Big(-\frac{du}{u^{2}}\Big)"),
             say=cap(r"Put $x=\frac{1}{u}$: $\ln\frac{1}{u}=-\ln u$, and the limits swap."),
             rule=["u_substitution", "change_of_limits", "log_laws"],
             mapping={"u_substitution": [cap(r"Here $x=\frac{1}{u}$, so $dx=-\frac{du}{u^{2}}$.")],
                      "change_of_limits": [cap(r"Here $x=0$ gives $u=\infty$; $x=\infty$ gives $u=0$.")]},
             highlight=([r"\Big(-\frac{du}{u^{2}}\Big)"], cap(r"$dx=-\frac{du}{u^{2}}$")), side=DOWN),
        dict(tex=eq(*LIMS, r"\frac{(1+\ln u)\,u^{2}}{(1+u^{2})^{2}}", r"\,du"),
             say=cap(r"The minus flips the limits back; $u^{2}$ is left."),
             rule=["reversing_limits", "exponent_laws"],
             mapping={"reversing_limits": [cap(r"Here $-\int_{\infty}^{0}$ becomes $\int_{0}^{\infty}$.")]}),
        dict(tex=eq("2I", "=", *LIMS, r"\frac{(1-\ln x)+(1+\ln x)\,x^{2}}{(1+x^{2})^{2}}", r"\,dx"),
             say=cap(r"Call it $I$; rename $u$ as $x$ and add."),
             rule="linearity"),
        dict(tex=eq("2I", "=", *LIMS, ATAN, r"\,dx", "-", *LIMS, LOGPART, r"\,dx"),
             say=cap(r"The top is $(1+x^{2})-(1-x^{2})\ln x$. Split it."),
             rule="algebra"),
        dict(tex=eq("2I", "=", *LIMS, ATAN, r"\,dx", "-", *LIMS, r"\ln x", r"\,\frac{d}{dx}\Big(\frac{x}{1+x^{2}}\Big)",
                    r"\,dx"),
             say=cap(r"That fraction is the derivative of $\frac{x}{1+x^{2}}$."),
             rule="quotient_rule",
             mapping=[cap(r"Here $f=x$, $g=1+x^{2}$: $\frac{(1+x^{2})-2x^{2}}{(1+x^{2})^{2}}$.")]),
        dict(tex=eq("2I", "=", *LIMS, ATAN, r"\,dx", "-", r"\Big[\frac{x\ln x}{1+x^{2}}\Big]_{0}^{\infty}", "+",
                    *LIMS, ATAN, r"\,dx"),
             say=cap(r"By parts: $\ln x$ gives $\frac{1}{x}$, cancelling the $x$."),
             rule=["integration_by_parts", "ln_derivative"],
             mapping={"integration_by_parts": [cap(r"Here $u=\ln x$ and $\frac{dv}{dx}=\Big(\frac{x}{1+x^{2}}\Big)'$.")]}),
        dict(tex=eq("2I", "=", "2", *LIMS, ATAN, r"\,dx"),
             say=cap(r"Logs lose to powers: the bracket is $0$."),
             rule="log_limits",
             mapping=[cap(r"Here $\frac{x\ln x}{1+x^{2}}\to0$ at both $0$ and $\infty$.")]),
        dict(tex=eq("2I", "=", "2", r"\Big[", r"\tan^{-1}x", r"\Big]_{", ("0", LIMIT), r"}^{", (r"\infty", LIMIT), r"}"),
             say=cap(r"What is left: the area under $\frac{1}{1+x^{2}}$."),
             rule=["arctan_integral", "improper_integral"],
             mapping={"arctan_integral": [cap(r"Here the whole integrand is $\frac{1}{1+x^{2}}$.")],
                      "improper_integral": [cap(r"Here $\tan^{-1}b\to\frac{\pi}{2}$ as $b\to\infty$.")]}),
        dict(tex=eq("I", "=", r"\frac{\pi}{2}"),
             say=cap(r"$\tan^{-1}x$ climbs to $\frac{\pi}{2}$, so $2I=\pi$."),
             rule="ftc"),
    ]

    ANSWER = eq(r"\frac{\pi}{2}")
    ANSWER_VALUE = float(mp.pi / 2)
    CLOSE_SAYS = (cap(r"Rectangles out to $30$ close in on $1.5708$."),
                  cap(r"Yes, finite: pairing $x$ with $\frac{1}{x}$ cancels $\ln x$."))
