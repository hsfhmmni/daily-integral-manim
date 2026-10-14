import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import IntegralVideo, LIMIT, NEW, cap, eq

S32 = float(np.sqrt(3) / 2)     # the lower limit, about 0.866
P3 = float(np.pi / 3)
P2 = float(np.pi / 2)


class EasyIntegral(IntegralVideo):
    DIFFICULTY = "Easy"
    DATE = "2026-10-14"

    @staticmethod
    def FUNC(x):
        x = np.asarray(x, dtype=float)
        return 1 / (1 - np.sqrt(np.maximum(0.0, 1 - x ** 2)))

    @classmethod
    def exact_integral(cls):
        return mp.quad(lambda x: 1 / (1 - mp.sqrt(1 - x ** 2)), [mp.sqrt(3) / 2, 1])

    COLORS = {r"\sqrt{1-x^{2}}": NEW, r"\cos\theta": NEW, r"\,d\theta": NEW, r"\theta": NEW}
    LIMS = (r"\int_{", (r"\frac{\sqrt{3}}{2}", LIMIT), r"}^{", ("1", LIMIT), r"}")
    LIMT = (r"\int_{", (r"\frac{\pi}{3}", LIMIT), r"}^{", (r"\frac{\pi}{2}", LIMIT), r"}")
    PROBLEM = eq(*LIMS, r"\frac{1}{1-", r"\sqrt{1-x^{2}}", r"}", r"\,dx")
    CURVE_LABEL = eq("y", "=", r"\frac{1}{1-", r"\sqrt{1-x^{2}}", r"}")
    LABEL_AT = (0.92, 2.1)      # empty space above the falling right half of the curve (below 1.7 there)

    GRAPH = dict(x_range=[0.8, 1.05, 0.05], y_range=[0, 3, 0.5], a=S32, b=1, size=(8, 4.2), plot_range=(0.8, 1),
                 x_labels={0.8: "0.8", S32: r"\frac{\sqrt{3}}{2}", 1: "1"},
                 y_labels={1: "1", 2: "2", 3: "3"})

    HOOK = cap(r"A root inside a fraction. How big is this thin sliver?")
    INTUITION = cap(r"Thin rectangles estimate the area; watch the gap shrink.")
    INSIGHT = dict(
        parts=[r"\sqrt{1-x^{2}}"],
        label=cap(r"$x=\sin\theta$"),
        say=cap(r"$\sqrt{1-x^{2}}$ is a circle's height: let $x=\sin\theta$."),
    )

    STEPS = [
        dict(tex=eq(*LIMT, r"\frac{", r"\cos\theta", r"}{1-", r"\cos\theta", r"}", r"\,d\theta"),
             say=cap(r"Let $x=\sin\theta$: then $\sqrt{1-x^{2}}=\cos\theta$ and $dx=\cos\theta\,d\theta$."),
             rule=["trig_substitution", "pythagorean_identity", "change_of_limits"],
             mapping={"trig_substitution": [cap(r"Here $a=1$, so $x=\sin\theta$ and $dx=\cos\theta\,d\theta$.")],
                      "pythagorean_identity": [cap(r"$1-\sin^{2}\theta=\cos^{2}\theta$, and $\cos\theta\ge 0$ here.")],
                      "change_of_limits": [cap(r"$x=\frac{\sqrt{3}}{2}$ gives $\frac{\pi}{3}$; $x=1$ gives $\frac{\pi}{2}$.")]},
             then="substitution"),
        dict(tex=eq(*LIMT, r"\Big(", r"\frac{1}{1-", r"\cos\theta", r"}", "-", "1", r"\Big)", r"\,d\theta"),
             say=cap(r"Write the top as $1-(1-\cos\theta)$, then split."),
             rule="algebra"),
        dict(tex=eq(*LIMT, r"\Big(", r"\tfrac{1}{2}", r"\csc^{2}\tfrac{\theta}{2}", "-", "1", r"\Big)",
                    r"\,d\theta"),
             say=cap(r"$1-\cos\theta=2\sin^{2}\frac{\theta}{2}$, so the fraction is $\frac{1}{2}\csc^{2}\frac{\theta}{2}$."),
             rule=["double_angle", "pythagorean_identity"],
             mapping={"double_angle": [cap(r"With $x=\frac{\theta}{2}$: $\cos\theta=1-2\sin^{2}\frac{\theta}{2}$.")]}),
        dict(tex=eq(r"\Big[", r"-\cot\tfrac{\theta}{2}", "-", r"\theta", r"\Big]_{", (r"\frac{\pi}{3}", LIMIT),
                    r"}^{", (r"\frac{\pi}{2}", LIMIT), r"}"),
             say=cap(r"$\frac{1}{2}\csc^{2}\frac{\theta}{2}$ integrates to $-\cot\frac{\theta}{2}$."),
             rule=["csc2_integral", "linearity"],
             mapping={"csc2_integral": [cap(r"The inner $\frac{\theta}{2}$ supplies the $\frac{1}{2}$ by the chain rule.")]}),
        dict(tex=eq(r"\big(", "-1", "-", r"\frac{\pi}{2}", r"\big)", "-", r"\big(", r"-\sqrt{3}", "-",
                    r"\frac{\pi}{3}", r"\big)"),
             say=cap(r"$\cot\frac{\pi}{4}=1$ and $\cot\frac{\pi}{6}=\sqrt{3}$."),
             rule="ftc"),
        dict(tex=eq(r"\sqrt{3}", "-", "1", "-", r"\frac{\pi}{6}"),
             say=cap(r"Collect the angles: $\frac{\pi}{3}-\frac{\pi}{2}=-\frac{\pi}{6}$."),
             rule="algebra"),
    ]

    SUBSTITUTION = dict(
        u_graph=dict(x_range=[1.0, 1.7, 0.1], y_range=[0, 1.4, 0.2], a=P3, b=P2, var=r"\theta", size=(8, 4.2),
                     plot_range=(1.0, P2), x_labels={P3: r"\frac{\pi}{3}", P2: r"\frac{\pi}{2}"},
                     y_labels={0.4: "0.4", 0.8: "0.8", 1.2: "1.2"}),
        u_func=lambda t: np.cos(t) / (1 - np.cos(t)),
        says=(cap(r"In $x$: the green area is about $0.208$."),
              cap(r"In $\theta$: a wider, flatter curve with the same area.")),
    )

    ANSWER = eq(r"\sqrt{3}", "-", "1", "-", r"\frac{\pi}{6}")
    ANSWER_VALUE = float(np.sqrt(3) - 1 - np.pi / 6)
    CLOSE_SAYS = (cap(r"Thin rectangles close in on $0.2085$."),
                  cap(r"Takeaway: $\sqrt{1-x^{2}}$ suggests $x=\sin\theta$, a circle's angle."))
