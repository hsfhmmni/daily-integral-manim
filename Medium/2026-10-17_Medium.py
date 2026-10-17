import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import (CAPTION_TOP, DIM_OPACITY, IntegralVideo, LIMIT, NEW, NEW_VAR_COLOR, SAFE_LEFT, SAFE_RIGHT,
                    build_graph, cap, caption, eq, mark)

P4 = float(np.pi / 4)
P2 = float(np.pi / 2)


def g(x):
    """The integrand once simplified: sin^2 2x / (8 - sin^2 2x), which is 0 at both ends."""
    s = np.sin(2 * np.asarray(x, dtype=float)) ** 2
    return s / (8 - s)


class MediumIntegral(IntegralVideo):
    DIFFICULTY = "Medium"
    DATE = "2026-10-17"

    @staticmethod
    def FUNC(x):
        return g(x)

    @classmethod
    def exact_integral(cls):
        f = lambda x: 1 / (mp.sin(x) ** 2 + mp.cos(x) ** 2 + mp.tan(x) ** 2 + mp.cot(x) ** 2
                           + mp.sec(x) ** 2 + mp.csc(x) ** 2)
        return mp.quad(f, [0, mp.pi / 4, mp.pi / 2])

    SC = r"\sin^{2}x+\cos^{2}x"
    S2 = r"\sin^{2}2x"
    COLORS = {"u": NEW, r"\,du": NEW, r"\tan^{2}2x": NEW}
    LIMS = (r"\int_{", ("0", LIMIT), r"}^{", (r"\frac{\pi}{2}", LIMIT), r"}")
    LIMH = (r"\int_{", ("0", LIMIT), r"}^{", (r"\frac{\pi}{4}", LIMIT), r"}")
    LIMU = (r"\int_{", ("0", LIMIT), r"}^{", (r"\infty", LIMIT), r"}")
    PROBLEM = eq(*LIMS, r"\frac{1}{", SC, "+", r"\tan^{2}x+\cot^{2}x", "+", r"\sec^{2}x+\csc^{2}x", r"}",
                 r"\,dx")
    PROBLEM_X = (-5.6, 3.0)     # a long line: give it room, clear of the badge
    CURVE_LABEL = None          # the denominator is far too long to sit beside the curve

    GRAPH = dict(x_range=[0, 1.75, 0.25], y_range=[0, 0.2, 0.05], a=0, b=P2, size=(8, 4.2), plot_range=(0, P2),
                 x_labels={P4: r"\frac{\pi}{4}", P2: r"\frac{\pi}{2}"},
                 y_labels={0.05: "0.05", 0.1: "0.1", 0.15: "0.15"})

    HOOK = cap(r"Four terms blow up at the ends. What survives?")
    INTUITION = cap(r"Thinner rectangles; watch the gap shrink.")
    INSIGHT = dict(
        parts=[SC],
        label=cap(r"$=1$"),
        say=cap(r"All tied to $\sin^{2}x+\cos^{2}x=1$."),
    )

    STEPS = [
        dict(tex=eq(*LIMS, r"\frac{1}{", "3", "+", r"2\tan^{2}x+2\cot^{2}x", r"}", r"\,dx"),
             say=cap(r"$\sec^{2}x=1+\tan^{2}x$ and $\csc^{2}x=1+\cot^{2}x$."),
             rule="pythagorean_identity",
             mapping=[cap(r"Divide by $\cos^{2}x$ or $\sin^{2}x$.")]),
        dict(tex=eq(*LIMS, r"\frac{1}{", r"\frac{8}{\sin^{2}2x}", "-", "1", r"}", r"\,dx"),
             say=cap(r"$\tan^{2}x+\cot^{2}x=\frac{1}{\sin^{2}x\cos^{2}x}-2=\frac{4}{\sin^{2}2x}-2$."),
             rule=["pythagorean_identity", "double_angle"],
             mapping={"double_angle": [cap(r"Here $\sin x\cos x=\frac{1}{2}\sin 2x$.")]}),
        dict(tex=eq(*LIMS, r"\frac{", S2, r"}{", "8", "-", S2, r"}", r"\,dx"),
             say=cap(r"Times $\sin^{2}2x$: both ends now give $0$."),
             rule="algebra"),
        dict(tex=eq(*LIMS, r"\Big(", r"\frac{8}{", "8", "-", S2, r"}", "-", "1", r"\Big)", r"\,dx"),
             say=cap(r"Top: $8-(8-\sin^{2}2x)$."),
             rule="algebra"),
        dict(tex=eq("2", *LIMH, r"\Big(", r"\frac{8}{", "8", "-", S2, r"}", "-", "1", r"\Big)", r"\,dx"),
             say=cap(r"$\tan 2x$ blows up at $\frac{\pi}{4}$: halve first."),
             rule="midpoint_symmetry",
             mapping=[cap(r"Here $\sin^{2}2(\frac{\pi}{2}-x)=\sin^{2}(\pi-2x)=\sin^{2}2x$.")],
             then="reflection"),
        dict(tex=eq("2", *LIMH, r"\frac{", r"8\sec^{2}2x", r"}{", "8", "+", r"7", r"\tan^{2}2x", r"}", r"\,dx", "-",
                    r"\frac{\pi}{2}"),
             say=cap(r"Divide by $\cos^{2}2x$: $8\sec^{2}2x-\tan^{2}2x=8+7\tan^{2}2x$."),
             highlight=([r"8\sec^{2}2x"], cap(r"$8\sec^{2}2x\,dx=4\,du$")),
             side=UP,
             rule=["pythagorean_identity", "linearity", "power_rule"]),
        dict(tex=eq(*LIMU, r"\frac{8}{", "8", "+", r"7", "u", "^{2}", r"}", r"\,du", "-", r"\frac{\pi}{2}"),
             say=cap(r"Let $u=\tan 2x$: the limits become $0$ and $\infty$."),
             rule=["u_substitution", "chain_rule", "sec2_integral", "change_of_limits", "improper_integral"],
             mapping={"u_substitution": [cap(r"Here $u=\tan 2x$, so $du=2\sec^{2}2x\,dx$.")],
                      "chain_rule": [cap(r"The inside $2x$ gives the $2$.")],
                      "change_of_limits": [cap(r"$x=0$ gives $u=0$; $x\to\frac{\pi}{4}$ gives $u\to\infty$.")],
                      "improper_integral": [cap(r"Integrate to $b$, then let $b\to\infty$.")]}),
        dict(tex=eq(r"\sqrt{\tfrac{8}{7}}", r"\Big[", r"\tan^{-1}\Big(", r"\sqrt{\tfrac{7}{8}}", "u", r"\Big)",
                    r"\Big]_{", ("0", LIMIT), r"}^{", (r"\infty", LIMIT), r"}", "-", r"\frac{\pi}{2}"),
             say=cap(r"$\frac{8}{8+7u^{2}}=\frac{1}{1+\frac{7}{8}u^{2}}$: an inverse tangent."),
             rule=["arctan_integral", "chain_rule", "linearity"],
             mapping={"arctan_integral": [cap(r"Here $x=\sqrt{\frac{7}{8}}\,u$.")]}),
        dict(tex=eq(r"\sqrt{\tfrac{8}{7}}", r"\cdot", r"\frac{\pi}{2}", "-", r"\frac{\pi}{2}"),
             say=cap(r"$\tan^{-1}u$ climbs from $0$ to $\frac{\pi}{2}$."),
             rule=["ftc", "improper_integral"]),
        dict(tex=eq(r"\frac{\pi\sqrt{14}}{7}", "-", r"\frac{\pi}{2}"),
             say=cap(r"$\sqrt{\frac{8}{7}}=\frac{2\sqrt{14}}{7}$."),
             rule="algebra"),
    ]

    REFLECTION = dict(says=(cap(r"Mirror the left half in $x=\frac{\pi}{4}$."),
                            cap(r"It lands on the right half.")))

    ANSWER = eq(r"\frac{\pi\sqrt{14}}{7}", "-", r"\frac{\pi}{2}")
    ANSWER_VALUE = float(np.pi * np.sqrt(14) / 7 - np.pi / 2)
    CLOSE_SAYS = (cap(r"Thin rectangles close in on $0.1085$."),
                  cap(r"Takeaway: identities first, then halve before $\tan$ explodes."))

    def _reflection(self, scene, current):
        """The left half of the area (ORANGE copy) flipped in x = pi/4 onto the right half."""
        current.save_state()
        lines = self._trail.lines
        self.play(current.animate.set_opacity(0), *[l.animate.set_opacity(0) for l in lines], run_time=0.6)
        self._guard_section = "Reflection"
        gs = dict(x_range=[0, P2, P4 / 2], y_range=[0, 0.2, 0.05], a=0, b=P2, size=(8, 3.6),
                  x_labels={P4: r"\frac{\pi}{4}", P2: r"\frac{\pi}{2}"},
                  y_labels={0.05: "0.05", 0.1: "0.1", 0.15: "0.15"}, color_limits=False)
        gr = build_graph(gs, g, (SAFE_LEFT, SAFE_RIGHT, CAPTION_TOP + 0.1, 1.0))
        self.play(FadeIn(gr.grid), Create(gr.axes, lag_ratio=0.02), FadeIn(gr.var_label), run_time=1.2)
        self.play(Create(gr.curve), run_time=1.2)
        left = gr.axes.get_area(gr.curve, x_range=(0, P4), color=NEW_VAR_COLOR, opacity=0.5)
        line = DashedLine(gr.axes.c2p(P4, 0), gr.axes.c2p(P4, 0.2), color=WHITE, dash_length=0.12)
        self.play(FadeIn(left), Create(line), run_time=1.0)
        caption(self, self.REFLECTION["says"][0])
        mirror = left.copy()
        mark(self, "reflection", offset=1.0)
        self.play(mirror.animate.flip(UP, about_point=gr.axes.c2p(P4, 0)), run_time=2.0)
        caption(self, self.REFLECTION["says"][1], key="reflection: result")
        self.play(FadeOut(VGroup(gr.group, line, left, mirror)), run_time=1.0)
        self.play(Restore(current), *[l.animate.set_opacity(DIM_OPACITY) for l in lines], run_time=0.6)
