import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import IntegralVideo, LIMIT, NEW, cap, eq


class MediumIntegral(IntegralVideo):
    DIFFICULTY = "Medium"
    DATE = "2026-10-26"

    # cos^-1 x = pi/2 - sin^-1 x, so the top is 2 sin^-1 x - pi/2. The pi/2 part gives
    # (pi/2) [-1/x] = pi/2. By parts, int sin^-1 x / x^2 = [-sin^-1 x / x] + int dx / (x sqrt(1-x^2)),
    # and x = sin(theta) turns the last integral into int csc = -ln(csc + cot) from pi/6 to pi/2,
    # which is ln(2 + sqrt 3). Total 2 ln(2 + sqrt 3) - 5pi/6 = 0.01592: the negative part left
    # of 1/sqrt 2 and the positive part right of it almost cancel.
    @staticmethod
    def FUNC(x):
        x = np.asarray(x, dtype=float)
        return (np.arcsin(x) - np.arccos(x)) / x ** 2

    @classmethod
    def exact_integral(cls):
        return mp.quad(lambda x: (mp.asin(x) - mp.acos(x)) / x ** 2, [0.5, 1 / mp.sqrt(2), 1])

    COLORS = {r"\theta": NEW, r"\,d\theta": NEW, r"\cos\theta": NEW, r"\frac{1}{\sin\theta}": NEW, r"\csc\theta": NEW,
              r"-\ln(\csc\theta+\cot\theta)": NEW}
    LIMS = (r"\int_{", (r"\frac{1}{2}", LIMIT), r"}^{", ("1", LIMIT), r"}")
    TH = (r"\int_{", (r"\frac{\pi}{6}", LIMIT), r"}^{", (r"\frac{\pi}{2}", LIMIT), r"}")
    NUM = r"\sin^{-1}(x)-\cos^{-1}(x)"
    ROOT = (r"\frac{", "1", r"}{", r"x\sqrt{1-x^{2}}", r"}", r"\,dx")
    PROBLEM = eq(*LIMS, r"\frac{", NUM, r"}{", "x^{2}", r"}", r"\,dx")
    CURVE_LABEL = eq("y", "=", r"\frac{", NUM, r"}{", "x^{2}", r"}")
    LABEL_AT = (0.74, -2.35)    # empty space below the axis, right of where the curve crosses it

    # x_range starts left of 1/2 so the limit's label clears the y-axis
    GRAPH = dict(x_range=[0.375, 1, 0.125], y_range=[-2.5, 2, 0.5], a=0.5, b=1, size=(8, 4.2),
                 x_labels={0.5: r"\frac{1}{2}", float(1 / np.sqrt(2)): r"\frac{1}{\sqrt{2}}", 1: "1"},
                 y_labels={-2: "-2", -1: "-1", 1: "1"})

    HOOK = cap(r"Below the axis, then above. How much is left over?")
    INTUITION = cap(r"Area below the axis counts as negative; watch the gap.")
    INSIGHT = dict(
        parts=[NUM],
        label=cap(r"$2\sin^{-1}x-\frac{\pi}{2}$"),
        say=cap(r"$\cos^{-1}x=\frac{\pi}{2}-\sin^{-1}x$, so one inverse is enough."),
        side=UP,                # below, the arrow would point into the $x^{2}$
    )

    STEPS = [
        dict(tex=eq(*LIMS, r"\frac{", r"2\sin^{-1}x-\frac{\pi}{2}", r"}{", "x^{2}", r"}", r"\,dx"),
             say=cap(r"Swap $\cos^{-1}x$ for $\frac{\pi}{2}-\sin^{-1}x$."),
             rule="inverse_trig_sum",
             mapping=[cap(r"Here $\cos^{-1}x=\frac{\pi}{2}-\sin^{-1}x$ for $\frac{1}{2}\le x\le 1$.")]),
        dict(tex=eq("2", *LIMS, r"\frac{", r"\sin^{-1}x", r"}{", "x^{2}", r"}", r"\,dx", "-", r"\frac{\pi}{2}"),
             say=cap(r"Split it: $\int_{\frac{1}{2}}^{1}\frac{dx}{x^{2}}=\Big[-\frac{1}{x}\Big]_{\frac{1}{2}}^{1}=1$."),
             rule=["linearity", "power_rule", "ftc"]),
        dict(tex=eq("2", r"\Big[", r"-\frac{\sin^{-1}x}{x}", r"\Big]_{", (r"\frac{1}{2}", LIMIT), r"}^{",
                    ("1", LIMIT), r"}", "+", "2", *LIMS, *ROOT, "-", r"\frac{\pi}{2}"),
             say=cap(r"By parts: integrate $\frac{1}{x^{2}}$, differentiate $\sin^{-1}x$."),
             rule=["integration_by_parts", "arcsin_derivative"],
             mapping={"integration_by_parts": [cap(r"Here $u=\sin^{-1}x$, $dv=\frac{dx}{x^{2}}$, so $v=-\frac{1}{x}$.")],
                      "arcsin_derivative": [cap(r"So $du=\frac{dx}{\sqrt{1-x^{2}}}$.")]}),
        dict(tex=eq(r"-\frac{\pi}{3}", "+", "2", *LIMS, *ROOT, "-", r"\frac{\pi}{2}"),
             say=cap(r"$2\Big(-\frac{\pi}{2}+\frac{\pi/6}{1/2}\Big)=-\frac{\pi}{3}$, since $\sin^{-1}\frac{1}{2}=\frac{\pi}{6}$."),
             rule="ftc"),
        dict(tex=eq(r"-\frac{\pi}{3}", "+", "2", *TH, r"\frac{", r"\cos\theta", r"}{", r"\cos\theta", r"}", r"\cdot",
                    r"\frac{1}{\sin\theta}", r"\,d\theta", "-", r"\frac{\pi}{2}"),
             say=cap(r"Let $x=\sin\theta$: $dx=\cos\theta\,d\theta$ and $\sqrt{1-x^{2}}=\cos\theta$."),
             rule=["trig_substitution", "change_of_limits", "pythagorean_identity", "absolute_value"],
             mapping={"trig_substitution": [cap(r"Here $a=1$: $x=\sin\theta$, $dx=\cos\theta\,d\theta$.")],
                      "change_of_limits": [cap(r"$x=\frac{1}{2}$ gives $\theta=\frac{\pi}{6}$; $x=1$ gives $\theta=\frac{\pi}{2}$.")],
                      "pythagorean_identity": [cap(r"$\sqrt{1-\sin^{2}\theta}=\cos\theta$, since $\cos\theta\ge 0$ here.")]},
             highlight=([r"\cos\theta"], cap(r"these cancel")), side=UP),
        dict(tex=eq(r"-\frac{\pi}{3}", "+", "2", *TH, r"\csc\theta", r"\,d\theta", "-", r"\frac{\pi}{2}"),
             say=cap(r"The $\cos\theta$ cancel, leaving $\frac{1}{\sin\theta}=\csc\theta$."),
             rule="algebra"),
        dict(tex=eq(r"-\frac{\pi}{3}", "+", "2", r"\Big[", r"-\ln(\csc\theta+\cot\theta)", r"\Big]_{",
                    (r"\frac{\pi}{6}", LIMIT), r"}^{", (r"\frac{\pi}{2}", LIMIT), r"}", "-", r"\frac{\pi}{2}"),
             say=cap(r"Integrate $\csc\theta$; $\csc\theta+\cot\theta>0$ here, so no bars."),
             rule=["csc_integral", "absolute_value"],
             mapping={"csc_integral": [cap(r"Here the variable is $\theta$, from $\frac{\pi}{6}$ to $\frac{\pi}{2}$.")]}),
        dict(tex=eq(r"-\frac{\pi}{3}", "+", r"2\ln(2+\sqrt{3})", "-", r"\frac{\pi}{2}"),
             say=cap(r"At $\frac{\pi}{2}$: $-\ln(1+0)=0$. At $\frac{\pi}{6}$: $-\ln(2+\sqrt{3})$."),
             rule=["ftc", "log_values"]),
        dict(tex=eq(r"2\ln(2+\sqrt{3})", "-", r"\frac{5\pi}{6}"),
             say=cap(r"$2.6339-2.6180$: two nearly equal parts almost cancel."),
             rule="algebra"),
    ]

    ANSWER = eq(r"2\ln(2+\sqrt{3})", "-", r"\frac{5\pi}{6}")
    ANSWER_VALUE = float(2 * mp.log(2 + mp.sqrt(3)) - 5 * mp.pi / 6)
    CLOSE_SAYS = (cap(r"Thin rectangles close in on $0.0159$."),
                  cap(r"Takeaway: $\sin^{-1}x+\cos^{-1}x=\frac{\pi}{2}$ turns two inverses into one."))
