import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import IntegralVideo, LIMIT, NEW, cap, eq

PI = float(np.pi)


def f(x):
    x = np.asarray(x, dtype=float)
    sec, tan = 1 / np.cos(x), np.tan(x)
    return sec ** 2 / (sec + tan) ** 4.5


class MediumIntegral(IntegralVideo):
    DIFFICULTY = "Medium"
    DATE = "2026-10-20"

    # sec and tan blow up at pi/2, but the integrand tends to 0 there (about cos(x)^{5/2} / 2^{9/2});
    # with u = sec x + tan x the upper limit becomes infinity: an improper integral, 18/77.
    @staticmethod
    def FUNC(x):
        return f(x)

    @classmethod
    def exact_integral(cls):
        return mp.quad(lambda x: mp.sec(x) ** 2 / (mp.sec(x) + mp.tan(x)) ** mp.mpf(4.5), [0, mp.pi / 2])

    ST = r"\sec x+\tan x"
    COLORS = {ST: NEW, "u": NEW, "u^{2}": NEW, r"u^{-\frac{9}{2}}": NEW, r"u^{-\frac{13}{2}}": NEW}
    LIMS = (r"\int_{", ("0", LIMIT), r"}^{", (r"\frac{\pi}{2}", LIMIT), r"}")
    ULIMS = (r"\int_{", ("1", LIMIT), r"}^{", (r"\infty", LIMIT), r"}")
    PROBLEM = eq(*LIMS, r"\frac{", r"\sec^{2}x", r"}{(", ST, r")^{\frac{9}{2}}}", r"\,dx")
    CURVE_LABEL = eq("y", "=", r"\frac{", r"\sec^{2}x", r"}{(", ST, r")^{\frac{9}{2}}}")
    LABEL_AT = (0.75, 0.62)     # empty upper-right: the curve is below 0.3 for x > 0.75

    GRAPH = dict(x_range=[0, PI / 2, PI / 8], y_range=[0, 1.2, 0.25], a=0, b=PI / 2, size=(8, 4.2),
                 plot_range=(0, PI / 2 - 1e-6),
                 x_labels={PI / 4: r"\frac{\pi}{4}", PI / 2: r"\frac{\pi}{2}"},
                 y_labels={0.5: "0.5", 1: "1"})

    HOOK = cap(r"At $\frac{\pi}{2}$, $\sec x$ and $\tan x$ blow up. Is the area finite?")
    INTUITION = cap(r"Thin rectangles estimate the area; watch the gap shrink.")
    INSIGHT = dict(
        parts=[ST],
        label=cap(r"let $u=\sec x+\tan x$"),
        say=cap(r"Its derivative is $u\sec x$: the bracket reproduces itself."),
    )

    STEPS = [
        dict(tex=eq("u", "=", ST, r",\quad ", "d", "u", "=", "u", r"\sec x", r"\,dx"),
             say=cap(r"Differentiate: $du=(\sec x\tan x+\sec^{2}x)\,dx=u\sec x\,dx$."),
             rule=["u_substitution", "trig_derivatives"],
             mapping={"u_substitution": [cap(r"Here $u=\sec x+\tan x$, the bracket.")],
                      "trig_derivatives": [cap(r"So $\frac{du}{dx}=\sec x\tan x+\sec^{2}x$.")]}),
        dict(tex=eq(r"\sec x-\tan x", "=", r"\frac{1}{", "u", "}"),
             say=cap(r"$(\sec x+\tan x)(\sec x-\tan x)=1$, so this is $\frac{1}{u}$."),
             rule="sec_tan_identity",
             mapping=[cap(r"Factorise: $\sec^{2}x-\tan^{2}x=(\sec x+\tan x)(\sec x-\tan x)$.")]),
        dict(tex=eq(r"\sec x", "=", r"\frac{1}{2}", r"\Big(", "u", "+", r"\frac{1}{", "u", "}", r"\Big)"),
             say=cap(r"Add $u$ and $\frac{1}{u}$: the $\tan x$ terms cancel."),
             rule="algebra"),
        dict(tex=eq(r"\sec^{2}x", r"\,dx", "=", r"\frac{1}{2}", r"\Big(", "1", "+", r"\frac{1}{", "u^{2}", "}",
                    r"\Big)", "d", "u"),
             say=cap(r"$\sec^{2}x\,dx=\sec x\cdot\frac{du}{u}$: one $\sec x$ from each."),
             rule="algebra"),
        dict(tex=eq(r"\frac{1}{2}", *ULIMS, r"\Big(", "1", "+", r"\frac{1}{", "u^{2}", "}", r"\Big)",
                    r"u^{-\frac{9}{2}}", "d", "u"),
             say=cap(r"The bracket becomes $u^{\frac{9}{2}}$; the limits move to $1$ and $\infty$."),
             rule=["change_of_limits", "improper_integral"],
             mapping={"change_of_limits": [cap(r"$x=0$ gives $u=1$; $x\to\frac{\pi}{2}$ gives $u\to\infty$.")],
                      "improper_integral": [cap(r"Integrate to $b$, then let $b\to\infty$.")]},
             highlight=([r"\infty"], cap(r"$x\to\frac{\pi}{2}$ sends $u\to\infty$")), side=UP),
        dict(tex=eq(r"\frac{1}{2}", *ULIMS, r"\Big(", r"u^{-\frac{9}{2}}", "+", r"u^{-\frac{13}{2}}", r"\Big)",
                    "d", "u"),
             say=cap(r"Multiply out: $u^{-2}\cdot u^{-\frac{9}{2}}=u^{-\frac{13}{2}}$."),
             rule="exponent_laws"),
        dict(tex=eq(r"\frac{1}{2}", r"\Big[", r"-\frac{2}{7}u^{-\frac{7}{2}}", "-", r"\frac{2}{11}u^{-\frac{11}{2}}",
                    r"\Big]_{", ("1", LIMIT), r"}^{", (r"\infty", LIMIT), r"}"),
             say=cap(r"Power rule; both terms shrink to $0$ as $u\to\infty$."),
             rule=["power_rule", "improper_integral"]),
        dict(tex=eq(r"\frac{1}{2}", r"\Big(", r"\frac{2}{7}", "+", r"\frac{2}{11}", r"\Big)"),
             say=cap(r"Only the bottom limit $u=1$ is left, with signs flipped."),
             rule="ftc"),
        dict(tex=eq(r"\frac{18}{77}"),
             say=cap(r"So the area is $\frac{1}{7}+\frac{1}{11}=\frac{18}{77}\approx 0.2338$."),
             rule="algebra"),
    ]

    ANSWER = eq(r"\frac{18}{77}")
    ANSWER_VALUE = 18 / 77
    CLOSE_SAYS = (cap(r"Thin rectangles close in on $\frac{18}{77}\approx 0.2338$."),
                  cap(r"Takeaway: $\sec x+\tan x$ and $\sec x-\tan x$ are reciprocals."))
