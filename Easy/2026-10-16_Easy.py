import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import IntegralVideo, LIMIT, NEW, cap, eq

P6 = float(np.pi / 6)
P4 = float(np.pi / 4)


class EasyIntegral(IntegralVideo):
    DIFFICULTY = "Easy"
    DATE = "2026-10-16"

    @staticmethod
    def FUNC(x):
        x = np.asarray(x, dtype=float)
        return np.cos(2 * x) / np.sin(2 * x)

    @classmethod
    def exact_integral(cls):
        f = lambda x: ((mp.cos(x) ** 4 - mp.sin(x) ** 4) * (1 - mp.cos(x)) * (1 + mp.cos(x))
                       / (((mp.sin(x) + mp.cos(x)) ** 2 - 1) * mp.exp(mp.log((1 - mp.cos(2 * x)) / 2))))
        return mp.quad(f, [mp.pi / 6, mp.pi / 4])

    N1 = r"(\cos^{4}x-\sin^{4}x)"
    N2 = r"(1-\cos x)(1+\cos x)"
    D1 = r"\left[(\sin x+\cos x)^{2}-1\right]"
    D2 = r"e^{\ln\left(\frac{1-\cos 2x}{2}\right)}"
    COLORS = {r"\sin 2x": NEW, "u": NEW, r"\,du": NEW}
    LIMS = (r"\int_{", (r"\frac{\pi}{6}", LIMIT), r"}^{", (r"\frac{\pi}{4}", LIMIT), r"}")
    LIMU = (r"\int_{", (r"\frac{\sqrt{3}}{2}", LIMIT), r"}^{", ("1", LIMIT), r"}")
    PROBLEM = eq(*LIMS, r"\frac{", N1, N2, r"}{", D1, D2, r"}", r"\,dx")
    PROBLEM_X = (-5.4, 3.6)     # a long line: give it room, clear of the badge
    CURVE_LABEL = None          # the fraction is far too big to sit beside the curve

    GRAPH = dict(x_range=[0.4, 0.9, 0.1], y_range=[0, 0.8, 0.2], a=P6, b=P4, size=(8, 4.2), plot_range=(0.45, P4),
                 x_labels={P6: r"\frac{\pi}{6}", P4: r"\frac{\pi}{4}"},
                 y_labels={0.2: "0.2", 0.4: "0.4", 0.6: "0.6"})

    HOOK = cap(r"A monster fraction, yet a gentle curve. What survives?")
    INTUITION = cap(r"Thin rectangles estimate the area; watch the gap shrink.")
    INSIGHT = dict(
        parts=[D2],
        label=cap(r"$e^{\ln w}=w$"),
        say=cap(r"$e$ undoes $\ln$. Every factor here shrinks on its own."),
    )

    STEPS = [
        dict(tex=eq(*LIMS, r"\frac{", r"\cos 2x", r"\sin^{2}x", r"}{", D1, D2, r"}", r"\,dx"),
             say=cap(r"Top: $\cos^{4}x-\sin^{4}x=\cos 2x$, and $(1-\cos x)(1+\cos x)=\sin^{2}x$."),
             rule=["pythagorean_identity", "double_angle"],
             mapping={"pythagorean_identity": [cap(r"A difference of squares leaves $\cos^{2}x+\sin^{2}x=1$.")],
                      "double_angle": [cap(r"Here $\cos^{2}x-\sin^{2}x=\cos 2x$.")]}),
        dict(tex=eq(*LIMS, r"\frac{", r"\cos 2x", r"\sin^{2}x", r"}{", r"\sin 2x", r"\cdot\,", r"\sin^{2}x", r"}", r"\,dx"),
             say=cap(r"Bottom: $(\sin x+\cos x)^{2}-1=\sin 2x$, and $e^{\ln(\sin^{2}x)}=\sin^{2}x$."),
             highlight=([r"\sin^{2}x"], cap(r"cancel")),
             side=UP,
             rule=["pythagorean_identity", "double_angle", "exp_log_inverse"]),
        dict(tex=eq(*LIMS, r"\frac{", r"\cos 2x", r"}{", r"\sin 2x", r"}", r"\,dx"),
             say=cap(r"Cancel $\sin^{2}x$: only $\frac{\cos 2x}{\sin 2x}$ is left."),
             highlight=([r"\cos 2x", r"\,dx"], cap(r"becomes $\frac{1}{2}\,du$")),
             side=UP,
             rule="algebra"),
        dict(tex=eq(r"\frac{1}{2}", *LIMU, r"\frac{1}{", "u", r"}", r"\,du"),
             say=cap(r"Let $u=\sin 2x$: the limits become $\frac{\sqrt{3}}{2}$ and $1$."),
             rule=["u_substitution", "chain_rule", "change_of_limits"],
             mapping={"u_substitution": [cap(r"Here $u=\sin 2x$, the bottom of the fraction.")],
                      "chain_rule": [cap(r"$du=2\cos 2x\,dx$: the inside $2x$ gives the $2$.")],
                      "change_of_limits": [cap(r"$\sin\frac{\pi}{3}=\frac{\sqrt{3}}{2}$ and $\sin\frac{\pi}{2}=1$.")]}),
        dict(tex=eq(r"\frac{1}{2}", r"\Big[", r"\ln|", "u", r"|", r"\Big]_{", (r"\frac{\sqrt{3}}{2}", LIMIT), r"}^{",
                    ("1", LIMIT), r"}"),
             say=cap(r"The integral of $\frac{1}{u}$ is $\ln|u|$."),
             rule="reciprocal_integral",
             mapping=[cap(r"Here the variable is $u$, and $u>0$ throughout.")]),
        dict(tex=eq(r"\frac{1}{2}", r"\Big(", "0", "-", r"\ln\frac{\sqrt{3}}{2}", r"\Big)"),
             say=cap(r"Upper limit minus lower limit, and $\ln 1=0$."),
             rule=["ftc", "absolute_value", "log_values"]),
        dict(tex=eq(r"\frac{1}{4}", r"\ln\frac{4}{3}"),
             say=cap(r"$-\ln\frac{\sqrt{3}}{2}=\ln\frac{2}{\sqrt{3}}=\frac{1}{2}\ln\frac{4}{3}$."),
             rule="log_laws"),
    ]

    ANSWER = eq(r"\frac{1}{4}", r"\ln\frac{4}{3}")
    ANSWER_VALUE = float(np.log(4 / 3) / 4)
    CLOSE_SAYS = (cap(r"Thin rectangles close in on $0.0719$."),
                  cap(r"Takeaway: simplify each factor alone before integrating anything."))
