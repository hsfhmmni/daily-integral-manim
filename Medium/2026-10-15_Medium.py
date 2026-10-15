import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import (IntegralVideo, LIMIT, NEW, TRAP, cap, eq, mt, fit_into, highlight, parts_of, caption,
                    unzoom, SAFE_LEFT, SAFE_RIGHT, STAGE)

PI = float(np.pi)
P2 = float(np.pi / 2)


class MediumIntegral(IntegralVideo):
    DIFFICULTY = "Medium"
    DATE = "2026-10-15"

    @staticmethod
    def FUNC(x):
        # the limit of the continued fraction: y = (sqrt(1 + cos 2x) - 1) / 2
        return (np.sqrt(1 + np.cos(2 * np.asarray(x, dtype=float))) - 1) / 2

    @classmethod
    def exact_integral(cls):
        # the continued fraction's limit, the root of 4y^2 + 4y - cos 2x = 0 with y = 0 at cos 2x = 0
        # (layer-by-layer convergents agree to 1e-5; they converge slowly at x = pi/2)
        return mp.quad(lambda x: (mp.sqrt(1 + mp.cos(2 * x)) - 1) / 2, [0, mp.pi / 2, mp.pi])

    REPEAT = r"\frac{\cos 2x}{4+\frac{\cos 2x}{1+\dots}}"
    COLORS = {REPEAT: NEW, "y": NEW, r"4y^{2}": NEW, r"4y": NEW}
    LIMS = (r"\int_{", ("0", LIMIT), r"}^{", (r"\pi", LIMIT), r"}")
    TOP = (r"\frac{", r"\cos 2x", r"}{4+\frac{", r"\cos 2x", r"}{1+")
    PROBLEM = eq(*LIMS, *TOP, REPEAT, r"}}", r"\,dx")
    # the same fraction with \dfrac on the second level, for the insight and the first step:
    # room between that numerator and the boxed tail (too tall for the band above the hook's graph)
    ROOMY = (r"\frac{", r"\cos 2x", r"}{4+\dfrac{", r"\cos 2x", r"}{1+")
    PROBLEM_X = (-5.6, 3.3)     # a tall line: give it room, clear of the badge
    CURVE_LABEL = None          # the continued fraction is too big to sit beside the curve

    GRAPH = dict(x_range=[0, PI, PI / 4], y_range=[-0.6, 0.4, 0.2], a=0, b=PI, size=(8, 4.2), plot_range=(0, PI),
                 x_labels={P2: r"\frac{\pi}{2}", PI: r"\pi"},
                 y_labels={-0.4: "-0.4", 0.2: "0.2"})

    HOOK = cap(r"A fraction that never ends. Mostly below the axis: how far?")
    INTUITION = cap(r"Thin rectangles estimate the signed area; watch the gap shrink.")
    INSIGHT = dict(
        parts=[REPEAT],
        label=cap(r"the start again"),
        say=cap(r"After one $4$ and one $1$, the whole fraction restarts."),
    )

    STEPS = [
        dict(tex=eq("y", "=", *ROOMY, "y", r"}}"),
             say=cap(r"Call the fraction $y$: the tail after $4$ and $1$ is $y$."),
             rule="nested_fixed_point",
             mapping=[cap(r"Here $g(y)=\frac{\cos 2x}{4+\frac{\cos 2x}{1+y}}$.")]),
        dict(tex=eq(r"4y^{2}", "+", r"4y", "-", r"\cos 2x", "=", "0"),
             say=cap(r"Clear the fractions: a quadratic in $y$."),
             rule="algebra"),
        dict(tex=eq("y", "=", r"\frac{", "-1+", r"\sqrt{1+\cos 2x}", r"}{2}"),
             say=cap(r"Quadratic formula, $+$ root: when $\cos 2x=0$, $y=0$."),
             rule=["quadratic_formula", "nested_fixed_point"]),
        dict(tex=eq(*LIMS, r"\frac{", r"\sqrt{1+\cos 2x}", "-1", r"}{2}", r"\,dx"),
             say=cap(r"That root is the integrand."),
             rule="algebra"),
        dict(tex=eq(*LIMS, r"\frac{", r"\sqrt{2}", (r"\cos x", TRAP), "-1", r"}{2}", r"\,dx"),
             say=cap(r"$1+\cos 2x=2\cos^{2}x$. But is $\sqrt{\cos^{2}x}$ really $\cos x$?"),
             rule=["double_angle", "pythagorean_identity"],
             mapping={"double_angle": [cap(r"Here $\cos 2x=\cos^{2}x-\sin^{2}x$.")],
                      "pythagorean_identity": [cap(r"$\sin^{2}x=1-\cos^{2}x$, so $\cos 2x=2\cos^{2}x-1$.")]},
             check=False,
             check_reason="trap: sqrt(cos^2 x) is |cos x|, not cos x, because cos x < 0 on (pi/2, pi)"),
        dict(tex=eq(*LIMS, r"\frac{", r"\sqrt{2}", r"|\cos x|", "-1", r"}{2}", r"\,dx"),
             say=cap(r"No: past $\frac{\pi}{2}$, $\cos x<0$. The root is $|\cos x|$."),
             rule="absolute_value"),
        dict(tex=eq(r"\frac{\sqrt{2}}{2}", r"\Big(", r"\int_{0}^{\frac{\pi}{2}}\cos x\,dx", "-",
                    r"\int_{\frac{\pi}{2}}^{\pi}\cos x\,dx", r"\Big)", "-", r"\frac{\pi}{2}"),
             say=cap(r"Split at $\frac{\pi}{2}$, where $\cos x$ changes sign."),
             rule=["interval_additivity", "linearity"],
             mapping={"interval_additivity": [cap(r"Here $b=\frac{\pi}{2}$: $|\cos x|=\cos x$, then $-\cos x$.")]}),
        dict(tex=eq(r"\frac{\sqrt{2}}{2}", r"\Big(", "1", "-", "(-1)", r"\Big)", "-", r"\frac{\pi}{2}"),
             say=cap(r"$\sin x$ goes $0\to 1$, then $1\to 0$."),
             rule=["cos_integral", "ftc"]),
        dict(tex=eq(r"\sqrt{2}", "-", r"\frac{\pi}{2}"),
             say=cap(r"So the signed area is about $-0.157$."),
             rule="algebra"),
    ]

    def insight(self, problem):
        """As IntegralVideo.insight, but the line grows into its ROOMY form, so the box around
        the repeating tail clears the numerator just above it."""
        self._guard_section = "Insight"
        target = mt(eq(*self.LIMS, *self.ROOMY, self.REPEAT, r"}}", r"\,dx"), self.COLORS)
        fit_into(target, SAFE_LEFT, SAFE_RIGHT, STAGE[2], STAGE[3])
        target.move_to([0, 0.2, 0])
        self.play(ReplacementTransform(problem, target), run_time=1.2)
        extra = highlight(self, parts_of(target, *self.INSIGHT["parts"]), self.INSIGHT["label"],
                          side=self.INSIGHT.get("side", DOWN), context=target)
        caption(self, self.INSIGHT["say"])
        unzoom(self, FadeOut(extra))
        return target

    ANSWER = eq(r"\sqrt{2}", "-", r"\frac{\pi}{2}")
    ANSWER_VALUE = float(np.sqrt(2) - np.pi / 2)
    CLOSE_SAYS = (cap(r"Thin rectangles close in on $-0.1566$."),
                  cap(r"Takeaway: name the repeating tail, solve for it, mind $\sqrt{\cos^{2}x}$."))
