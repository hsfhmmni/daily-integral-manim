import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import IntegralVideo, LIMIT, NEW, cap, eq

LO = float(np.arctan(1 / np.e))     # the lower limit as written, about 0.3525 (the larger number)
HI = float(np.arctan(1 / np.pi))    # the upper limit as written, about 0.3082
UE = float(1 / np.e)
UP = float(1 / np.pi)


class EasyIntegral(IntegralVideo):
    DIFFICULTY = "Easy"
    DATE = "2026-10-15"

    @staticmethod
    def FUNC(x):
        return 1 / (np.sin(x) * np.cos(x))

    @classmethod
    def exact_integral(cls):
        return mp.quad(lambda x: 1 / (mp.sin(x) * mp.cos(x)), [mp.atan(1 / mp.e), mp.atan(1 / mp.pi)])

    COLORS = {r"\tan x": NEW, "u": NEW, r"\,du": NEW, r"\sec^{2}x": NEW}
    LIMS = (r"\int_{", (r"\tan^{-1}\frac{1}{e}", LIMIT), r"}^{", (r"\tan^{-1}\frac{1}{\pi}", LIMIT), r"}")
    LIMU = (r"\int_{", (r"\frac{1}{e}", LIMIT), r"}^{", (r"\frac{1}{\pi}", LIMIT), r"}")
    PROBLEM = eq(*LIMS, r"\frac{1}{", r"\sin x\cos x", r"}", r"\,dx")
    CURVE_LABEL = eq("y", "=", r"\frac{1}{", r"\sin x\cos x", r"}")
    LABEL_AT = (0.285, 4.0)     # empty space above the curve (which stays below 3.7)

    GRAPH = dict(x_range=[0.28, 0.38, 0.02], y_range=[0, 5, 1], a=HI, b=LO, size=(8, 4.2), plot_range=(0.28, 0.38),
                 x_labels={HI: r"\tan^{-1}\frac{1}{\pi}", LO: r"\tan^{-1}\frac{1}{e}"},
                 y_labels={1: "1", 2: "2", 3: "3"})
    WINDOW = (LO, HI)           # the integral runs from tan^-1(1/e) down to tan^-1(1/pi)

    HOOK = cap(r"The limits run backwards. Is the answer positive or negative?")
    INTUITION = cap(r"Backwards limits flip the sign: the estimate is negative.")
    INSIGHT = dict(
        parts=[r"\sin x\cos x"],
        label=cap(r"$\div\cos^{2}x$"),
        say=cap(r"Divide top and bottom by $\cos^{2}x$: $\tan x$ appears."),
    )

    STEPS = [
        dict(tex=eq(*LIMS, r"\frac{", r"\sec^{2}x", r"}{", r"\tan x", r"}", r"\,dx"),
             say=cap(r"$\frac{1}{\cos^{2}x}=\sec^{2}x$ and $\frac{\sin x}{\cos x}=\tan x$."),
             highlight=([r"\sec^{2}x", r"\,dx"], cap(r"becomes $du$")),
             rule="algebra"),
        dict(tex=eq(*LIMU, r"\frac{1}{", "u", r"}", r"\,du"),
             say=cap(r"Let $u=\tan x$: then $du=\sec^{2}x\,dx$ replaces the top."),
             rule=["u_substitution", "sec2_integral", "change_of_limits"],
             mapping={"u_substitution": [cap(r"Here $u=\tan x$, the bottom of the fraction.")],
                      "sec2_integral": [cap(r"So $\frac{d}{dx}\tan x=\sec^{2}x$, giving $du=\sec^{2}x\,dx$.")],
                      "change_of_limits": [cap(r"$\tan\big(\tan^{-1}\frac{1}{e}\big)=\frac{1}{e}$; likewise $\frac{1}{\pi}$.")]},
             then="substitution"),
        dict(tex=eq(r"\Big[", r"\ln|", "u", r"|", r"\Big]_{", (r"\frac{1}{e}", LIMIT), r"}^{",
                    (r"\frac{1}{\pi}", LIMIT), r"}"),
             say=cap(r"The integral of $\frac{1}{u}$ is $\ln|u|$."),
             rule="reciprocal_integral",
             mapping=[cap(r"Here the variable is $u$, and $u>0$ throughout.")]),
        dict(tex=eq(r"\ln\frac{1}{\pi}", "-", r"\ln\frac{1}{e}"),
             say=cap(r"Upper limit minus lower limit."),
             rule=["ftc", "absolute_value"]),
        dict(tex=eq(r"-\ln\pi", "+", "1"),
             say=cap(r"$\ln\frac{1}{a}=-\ln a$, and $\ln e=1$."),
             rule=["log_laws", "log_values"]),
        dict(tex=eq("1", "-", r"\ln\pi"),
             say=cap(r"Negative, because $\pi>e$ makes $\ln\pi>1$."),
             rule="algebra"),
    ]

    SUBSTITUTION = dict(
        u_graph=dict(x_range=[0.3, 0.38, 0.02], y_range=[0, 4, 1], a=UP, b=UE, var="u", size=(8, 4.2),
                     plot_range=(0.3, 0.38), x_labels={UP: r"\frac{1}{\pi}", UE: r"\frac{1}{e}"},
                     y_labels={1: "1", 2: "2", 3: "3"}),
        u_func=lambda u: 1 / u,
        says=(cap(r"In $x$: the signed area is about $-0.145$."),
              cap(r"In $u$: the curve $\frac{1}{u}$, with exactly the same area.")),
    )

    ANSWER = eq("1", "-", r"\ln\pi")
    ANSWER_VALUE = float(1 - np.log(np.pi))
    CLOSE_SAYS = (cap(r"Thin rectangles close in on $-0.1447$."),
                  cap(r"Takeaway: $\frac{1}{\sin x\cos x}$ is $\frac{\sec^{2}x}{\tan x}$, giving $\ln|\tan x|$."))
