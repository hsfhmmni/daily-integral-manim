import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import IntegralVideo, LIMIT, NEW, cap, eq

LN2 = float(np.log(2))


class MediumIntegral(IntegralVideo):
    DIFFICULTY = "Medium"
    DATE = "2026-10-18"

    @staticmethod
    def FUNC(x):
        x = np.asarray(x, dtype=float)
        return (np.sqrt(np.exp(x) + 1) + np.sqrt(np.exp(x) - 1)) / np.sqrt(np.exp(2 * x) - 1)

    @classmethod
    def exact_integral(cls):
        return mp.quad(lambda x: (mp.sqrt(mp.exp(x) + 1) + mp.sqrt(mp.exp(x) - 1)) / mp.sqrt(mp.exp(2 * x) - 1),
                       [mp.log(2), 5, mp.inf])

    A = r"\sqrt{e^{x}+1}"
    B = r"\sqrt{e^{x}-1}"
    BOT = r"\sqrt{e^{2x}-1}"
    U1, U2 = r"\frac{1}{u}", r"\frac{2u}{u^{2}+1}"
    V1, V2 = r"\frac{1}{v}", r"\frac{2v}{v^{2}-1}"
    COLORS = {U1: NEW, U2: NEW, r"\frac{2}{u^{2}+1}": NEW, "u": NEW, r"\,du": NEW,
              V1: NEW, V2: NEW, r"\,dv": NEW}
    LIMS = (r"\int_{", (r"\ln 2", LIMIT), r"}^{", (r"\infty", LIMIT), r"}")
    LIMU = (r"\int_{", ("1", LIMIT), r"}^{", (r"\infty", LIMIT), r"}")
    LIMV = (r"\int_{", (r"\sqrt{3}", LIMIT), r"}^{", (r"\infty", LIMIT), r"}")
    PROBLEM = eq(*LIMS, r"\frac{", A, "+", B, r"}{", BOT, r"}", r"\,dx")
    CURVE_LABEL = eq("y", "=", r"\frac{", A, "+", B, r"}{", BOT, r"}")
    LABEL_AT = (4.0, 0.9)       # empty space above the tail, which is below 0.3 for x > 4

    GRAPH = dict(x_range=[0, 14, 2], y_range=[0, 2, 0.5], a=LN2, b=14, size=(8, 4.2), plot_range=(LN2, 14),
                 x_labels={LN2: r"\ln 2", 4: "4", 8: "8", 12: "12"},
                 y_labels={0.5: "0.5", 1: "1", 1.5: "1.5"})
    WINDOW = (LN2, 14)          # the tail beyond 14 adds about 0.0036
    CLOSE_WIDEN = (LN2, 24)

    HOOK = cap(r"Out to $\infty$, a tangle of roots. Does the area settle?")
    INTUITION = cap(r"Thin rectangles estimate the area; watch the gap shrink.")
    INSIGHT = dict(
        parts=[BOT],
        label=cap(r"$\sqrt{e^{x}-1}\,\sqrt{e^{x}+1}$"),
        say=cap(r"The bottom factors, so the fraction splits in two."),
    )

    REST_X = (*LIMS, r"\frac{1}{", A, r"}", r"\,dx")
    STEPS = [
        dict(tex=eq(*LIMS, r"\frac{", A, "+", B, r"}{", B, A, r"}", r"\,dx"),
             say=cap(r"$e^{2x}-1=(e^{x}-1)(e^{x}+1)$, a difference of squares."),
             rule="exponent_laws"),
        dict(tex=eq(*LIMS, r"\frac{1}{", B, r"}", r"\,dx", "+", *REST_X),
             say=cap(r"Each root cancels once; both pieces converge, so split."),
             rule=["linearity", "improper_integral"],
             mapping={"improper_integral": [cap(r"Each piece shrinks like $e^{-\frac{x}{2}}$, so each converges.")]}),
        dict(tex=eq(*LIMU, U1, r"\cdot", U2, r"\,du", "+", *REST_X),
             say=cap(r"Let $u=\sqrt{e^{x}-1}$: then $e^{x}=u^{2}+1$."),
             highlight=([U1, U2], cap(r"$u$ cancels")),
             side=UP,
             rule=["u_substitution", "change_of_limits", "exp_log_inverse"],
             mapping={"u_substitution": [cap(r"Here $u=\sqrt{e^{x}-1}$, so $dx=\frac{2u}{u^{2}+1}\,du$.")],
                      "change_of_limits": [cap(r"$x=\ln 2$ gives $u=1$; $x\to\infty$ gives $u\to\infty$.")]}),
        dict(tex=eq(*LIMU, r"\frac{2}{u^{2}+1}", r"\,du", "+", *REST_X),
             say=cap(r"The $u$ cancels, leaving $\frac{2}{u^{2}+1}$."),
             rule="algebra"),
        dict(tex=eq(*LIMU, r"\frac{2}{u^{2}+1}", r"\,du", "+", *LIMV, V1, r"\cdot", V2, r"\,dv"),
             say=cap(r"Likewise $v=\sqrt{e^{x}+1}$: the limits become $\sqrt{3}$ and $\infty$."),
             highlight=([V1, V2], cap(r"$v$ cancels")),
             side=UP,
             rule=["u_substitution", "change_of_limits", "exp_log_inverse"]),
        dict(tex=eq(*LIMU, r"\frac{2}{u^{2}+1}", r"\,du", "+", *LIMV, r"\Big(", r"\frac{1}{v-1}", "-",
                    r"\frac{1}{v+1}", r"\Big)", r"\,dv"),
             say=cap(r"$v^{2}-1=(v-1)(v+1)$: split into partial fractions."),
             rule="partial_fractions",
             mapping=[cap(r"Here $\frac{2}{(v-1)(v+1)}=\frac{1}{v-1}-\frac{1}{v+1}$.")]),
        dict(tex=eq(r"\Big[", r"2\tan^{-1}", "u", r"\Big]_{", ("1", LIMIT), r"}^{", (r"\infty", LIMIT), r"}", "+",
                    r"\Big[", r"\ln\frac{v-1}{v+1}", r"\Big]_{", (r"\sqrt{3}", LIMIT), r"}^{", (r"\infty", LIMIT), r"}"),
             say=cap(r"An inverse tangent, then two logs combined into one."),
             rule=["arctan_integral", "reciprocal_integral", "log_laws", "linearity"],
             mapping={"arctan_integral": [cap(r"Here the variable is $u$, times the constant $2$.")]}),
        dict(tex=eq(r"2\Big(\frac{\pi}{2}-\frac{\pi}{4}\Big)", "+", r"\Big(0-\ln\frac{\sqrt{3}-1}{\sqrt{3}+1}\Big)"),
             say=cap(r"As they grow, $\tan^{-1}u\to\frac{\pi}{2}$ and $\frac{v-1}{v+1}\to 1$."),
             rule=["ftc", "improper_integral", "log_values"]),
        dict(tex=eq(r"\frac{\pi}{2}", "+", r"\ln(2+\sqrt{3})"),
             say=cap(r"$\frac{\sqrt{3}+1}{\sqrt{3}-1}=\frac{(\sqrt{3}+1)^{2}}{2}=2+\sqrt{3}$."),
             rule="log_laws"),
    ]

    ANSWER = eq(r"\frac{\pi}{2}", "+", r"\ln(2+\sqrt{3})")
    ANSWER_VALUE = float(np.pi / 2 + np.log(2 + np.sqrt(3)))
    CLOSE_SAYS = (cap(r"Thin rectangles close in on $2.8878$."),
                  cap(r"Takeaway: factor the bottom, split, then substitute each root."))
