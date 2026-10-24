import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import IntegralVideo, LIMIT, NEW, cap, eq

P2 = float(np.pi / 2)
P4 = float(np.pi / 4)


class HardIntegral(IntegralVideo):
    DIFFICULTY = "Hard"
    DATE = "2026-10-23"

    # 1 + s^4 = (1 + i s^2)(1 - i s^2) with s = sin x, so the integral is I(i) + I(-i), where
    # I(a) = int_0^{pi/2} ln(1 + a sin^2 x) dx. For real a > -1, I'(a) = (1/a)(pi/2 - pi/(2 sqrt(1+a)))
    # (t = tan x), so I(a) = pi ln((1 + sqrt(1+a))/2); both sides are analytic off (-inf, -1], so
    # a = +-i is allowed. The two factors are conjugates: |1 + sqrt(1+i)|^2 = 1 + sqrt2 + sqrt(2 + 2 sqrt2).
    @staticmethod
    def FUNC(x):
        return np.log(1 + np.sin(np.asarray(x, dtype=float)) ** 4)

    @classmethod
    def exact_integral(cls):
        return mp.quad(lambda x: mp.log(1 + mp.sin(x) ** 4), [0, mp.pi / 2])

    COLORS = {"I(i)": NEW, "I(-i)": NEW, "I'(a)": NEW, "I(a)": NEW}
    LIMS = (r"\int_{", ("0", LIMIT), r"}^{", (r"\frac{\pi}{2}", LIMIT), r"}")
    TLIMS = (r"\int_{", ("0", LIMIT), r"}^{", (r"\infty", LIMIT), r"}")
    PROBLEM = eq(*LIMS, r"\ln(1+", r"\sin^{4}x", ")", r"\,dx")
    CURVE_LABEL = eq("y", "=", r"\ln(1+", r"\sin^{4}x", ")")
    LABEL_AT = (0.1, 0.45)      # empty upper-left: the curve is below 0.1 for x < 0.6

    GRAPH = dict(x_range=[0, P2, P2 / 4], y_range=[0, 0.8, 0.2], a=0, b=P2, size=(8, 4.2),
                 x_labels={P4: r"\frac{\pi}{4}", P2: r"\frac{\pi}{2}"},
                 y_labels={0.2: "0.2", 0.4: "0.4", 0.6: "0.6"})

    HOOK = cap(r"No substitution tames this logarithm. Can the area be exact?")
    INTUITION = cap(r"Already at $4$ rectangles, the gap is tiny.")
    INSIGHT = dict(
        parts=[r"\sin^{4}x"],
        label=cap(r"$(\sin^{2}x)^{2}$"),
        say=cap(r"One plus a square factorises, once we allow $i$."),
    )

    # The family I(a) the method introduces, so verify.py can check the lines about I(a) and I'(a)
    # (as identities for real a in the sample range) and I(i)+I(-i) (against the website's value).
    DEFINITIONS = {"I": dict(of="a", tex=r"\int_{0}^{\frac{\pi}{2}}\ln(1+a\sin^{2}x)\,dx", sample=(-0.5, 3))}

    HALF = (r"\frac{1}{a}", r"\Big(", r"\frac{\pi}{2}", "-")

    STEPS = [
        dict(tex=eq(*LIMS, r"\ln(1+", r"i\sin^{2}x", ")", r"\,dx", "+", *LIMS, r"\ln(1-", r"i\sin^{2}x", ")",
                    r"\,dx"),
             say=cap(r"Allow $i$: $1+\sin^{4}x=(1+i\sin^{2}x)(1-i\sin^{2}x)$."),
             rule=["sum_of_squares_complex", "log_laws", "linearity"]),
        dict(tex=eq("I(i)", "+", "I(-i)"),
             say=cap(r"Call $I(a)=\int_{0}^{\pi/2}\ln(1+a\sin^{2}x)\,dx$: a whole family."),
             rule="algebra"),
        dict(tex=eq("I'(a)", "=", *LIMS, r"\frac{", r"\sin^{2}x", r"}{", r"1+a\sin^{2}x", r"}", r"\,dx"),
             say=cap(r"For real $a>-1$, differentiate with respect to $a$ inside."),
             rule=["differentiation_under_integral", "chain_rule", "ln_derivative"],
             mapping={"differentiation_under_integral": [
                 cap(r"Here $f=\ln(1+a\sin^{2}x)$, so $\frac{\partial f}{\partial a}=\frac{\sin^{2}x}{1+a\sin^{2}x}$.")]}),
        dict(tex=eq("I'(a)", "=", *HALF, *LIMS, r"\frac{", "1", r"}{", r"1+a\sin^{2}x", r"}", r"\,dx", r"\Big)"),
             say=cap(r"Split: $\frac{\sin^{2}x}{1+a\sin^{2}x}=\frac{1}{a}\Big(1-\frac{1}{1+a\sin^{2}x}\Big)$."),
             rule="linearity"),
        dict(tex=eq("I'(a)", "=", *HALF, *TLIMS, r"\frac{", "1", r"}{", r"1+(1+a)t^{2}", r"}", r"\,dt", r"\Big)"),
             say=cap(r"Divide by $\cos^{2}x$ and let $t=\tan x$, so $dt=\sec^{2}x\,dx$."),
             rule=["u_substitution", "pythagorean_identity", "change_of_limits", "improper_integral"]),
        dict(tex=eq("I'(a)", "=", *HALF, r"\frac{\pi}{2\sqrt{1+a}}", r"\Big)"),
             say=cap(r"The $\tan^{-1}$ climbs to $\frac{\pi}{2}$ as $t\to\infty$."),
             rule=["arctan_integral", "u_substitution", "improper_integral"],
             mapping={"arctan_integral": [
                 cap(r"With $u=\sqrt{1+a}\,t$ it is $\frac{1}{\sqrt{1+a}}\int_{0}^{\infty}\frac{du}{1+u^{2}}$.")]}),
        dict(tex=eq("I'(a)", "=", r"\frac{\pi}{2\sqrt{1+a}\,\big(1+\sqrt{1+a}\big)}"),
             say=cap(r"Factor $a=(\sqrt{1+a}-1)(\sqrt{1+a}+1)$ and cancel."),
             rule="algebra"),
        dict(tex=eq("I(a)", "=", r"\pi\ln\frac{1+\sqrt{1+a}}{2}"),
             say=cap(r"This has that derivative, and both sides are $0$ at $a=0$."),
             rule=["chain_rule", "ftc"]),
        dict(tex=eq(r"\pi\ln\frac{(1+\sqrt{1+i})(1+\sqrt{1-i})}{4}"),
             say=cap(r"Both sides are analytic in $a$, so put $a=\pm i$ and add."),
             rule=["analytic_continuation", "log_laws"],
             mapping={"analytic_continuation": [
                 cap(r"Here $f=I(a)$ and $g=\pi\ln\frac{1+\sqrt{1+a}}{2}$, both analytic.")]}),
        dict(tex=eq(r"\pi\ln\frac{|1+\sqrt{1+i}|^{2}}{4}"),
             say=cap(r"The factors are conjugates, so their product is a modulus squared."),
             rule="conjugate_product"),
        dict(tex=eq(r"\pi\ln\frac{1+\sqrt{2}+\sqrt{2+2\sqrt{2}}}{4}"),
             say=cap(r"With $\sqrt{1+i}=p+iq$: $p^{2}=\frac{1+\sqrt{2}}{2}$, $p^{2}+q^{2}=\sqrt{2}$."),
             rule="conjugate_product"),
    ]

    ANSWER = eq(r"\pi\ln\frac{1+\sqrt{2}+\sqrt{2+2\sqrt{2}}}{4}")
    ANSWER_VALUE = float(np.pi * np.log((1 + np.sqrt(2) + np.sqrt(2 + 2 * np.sqrt(2))) / 4))
    CLOSE_SAYS = (cap(r"Thin rectangles close in on $0.4470$."),
                  cap(r"Takeaway: give the integral a parameter, then differentiate in it."))
