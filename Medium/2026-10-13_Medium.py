import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import (CAPTION_TOP, DIM_OPACITY, IntegralVideo, LIMIT, NEW, NEW_VAR_COLOR, SAFE_LEFT, SAFE_RIGHT,
                    build_graph, cap, caption, eq, mark)

Q4 = float(np.pi / 4)
Q8 = float(np.pi / 8)
S2 = float(np.sqrt(2))


def f(x):
    return np.log(1 + np.sin(2 * x)) / (4 * S2) - S2 / 4 * np.log(np.cos(x))


def shifted_log(x):
    """ln cos(x - pi/4): the mirror image of ln cos x in the line x = pi/8."""
    return np.log(np.cos(x - Q4))


class MediumIntegral(IntegralVideo):
    DIFFICULTY = "Medium"
    DATE = "2026-10-13"

    @staticmethod
    def FUNC(x):
        return f(x)

    @classmethod
    def exact_integral(cls):
        return mp.quad(lambda x: mp.log(1 + mp.sin(2 * x)) / (4 * mp.sqrt(2)) - mp.sqrt(2) / 4 * mp.log(mp.cos(x)),
                       [0, mp.pi / 4])

    COLORS = {r"2\ln\cos(x-\tfrac{\pi}{4})": NEW}
    LIMS = (r"\int_{", ("0", LIMIT), r"}^{", (r"\frac{\pi}{4}", LIMIT), r"}")
    PROBLEM = eq(*LIMS, r"\Big(", r"\tfrac{1}{4\sqrt{2}}", r"\ln(", r"1+\sin 2x", r")", "-", r"\tfrac{\sqrt{2}}{4}",
                 r"\ln(\cos x)", r"\Big)", r"\,dx")
    CURVE_LABEL = eq("y", "=", r"\tfrac{1}{4\sqrt{2}}", r"\ln(", r"1+\sin 2x", r")", "-", r"\tfrac{\sqrt{2}}{4}",
                     r"\ln(\cos x)")
    LABEL_AT = (0.1, 0.28)      # empty band above the curve, clear of the y-axis labels

    GRAPH = dict(x_range=[0, 1, 0.25], y_range=[0, 0.4, 0.1], a=0, b=Q4, size=(8, 4.2), plot_range=(0, 1),
                 x_labels={Q8: r"\frac{\pi}{8}", Q4: r"\frac{\pi}{4}", 1: "1"},
                 y_labels={0.1: "0.1", 0.2: "0.2", 0.3: "0.3"})

    HOOK = cap(r"Two unrelated-looking logarithms. Could most of them cancel?")
    INTUITION = cap(r"Thin rectangles estimate the area; watch the gap shrink.")
    INSIGHT = dict(
        parts=[r"1+\sin 2x"],
        label=cap(r"$(\cos x+\sin x)^{2}$"),
        say=cap(r"$1+\sin 2x$ is a perfect square in disguise."),
    )

    STEPS = [
        dict(tex=eq("I", "=", r"\tfrac{1}{4\sqrt{2}}", *LIMS, r"\Big(", r"\ln(", r"1+\sin 2x", r")", "-",
                    r"2\ln(\cos x)", r"\Big)", r"\,dx"),
             say=cap(r"$\frac{\sqrt{2}}{4}=\frac{2}{4\sqrt{2}}$, so pull out $\frac{1}{4\sqrt{2}}$."),
             rule="linearity"),
        dict(tex=eq("I", "=", r"\tfrac{1}{4\sqrt{2}}", *LIMS, r"\Big(", r"\ln(", r"(\cos x+\sin x)^{2}", r")", "-",
                    r"2\ln(\cos x)", r"\Big)", r"\,dx"),
             say=cap(r"$1+\sin 2x=(\cos x+\sin x)^{2}$."),
             rule=["pythagorean_identity", "double_angle"],
             mapping={"pythagorean_identity": [cap(r"Write the $1$ as $\cos^{2}x+\sin^{2}x$.")],
                      "double_angle": [cap(r"$\sin 2x=2\sin x\cos x$ is the cross term.")]}),
        dict(tex=eq("I", "=", r"\tfrac{1}{4\sqrt{2}}", *LIMS, r"\Big(", r"\ln(", r"2\cos^{2}(x-\tfrac{\pi}{4})", r")",
                    "-", r"2\ln(\cos x)", r"\Big)", r"\,dx"),
             say=cap(r"Merge into one cosine: $\cos x+\sin x=\sqrt{2}\cos(x-\frac{\pi}{4})$."),
             rule="compound_angle",
             mapping=[cap(r"Here $B=\frac{\pi}{4}$, and $\cos\frac{\pi}{4}=\sin\frac{\pi}{4}=\frac{1}{\sqrt{2}}$.")]),
        dict(tex=eq("I", "=", r"\tfrac{1}{4\sqrt{2}}", *LIMS, r"\Big(", r"\ln 2", "+", r"2\ln\cos(x-\tfrac{\pi}{4})",
                    "-", r"2\ln(\cos x)", r"\Big)", r"\,dx"),
             say=cap(r"Log laws split off $\ln 2$ and bring the square down."),
             rule="log_laws"),
        dict(tex=eq("I", "=", r"\tfrac{1}{4\sqrt{2}}", *LIMS, r"\Big(", r"\ln 2", "+", r"2\ln(\cos x)", "-",
                    r"2\ln(\cos x)", r"\Big)", r"\,dx"),
             say=cap(r"Mirror $x\to\frac{\pi}{4}-x$: the shifted term becomes $\ln(\cos x)$."),
             highlight=([r"2\ln(\cos x)"], cap(r"cancel")),
             rule="kings_rule",
             mapping=[cap(r"Here $a=\frac{\pi}{4}$, and cosine is even.")],
             then="reflection"),
        dict(tex=eq("I", "=", r"\tfrac{1}{4\sqrt{2}}", *LIMS, r"\ln 2", r"\,dx"),
             say=cap(r"The two terms cancel, leaving the constant $\ln 2$."),
             rule="algebra"),
        dict(tex=eq("I", "=", r"\tfrac{1}{4\sqrt{2}}", r"\cdot", r"\frac{\pi}{4}", r"\ln 2"),
             say=cap(r"Constant height $\ln 2$ over width $\frac{\pi}{4}$."),
             rule=["power_rule", "ftc"]),
        dict(tex=eq("I", "=", r"\frac{\pi\ln 2}{16\sqrt{2}}"),
             say=cap(r"Multiply: $4\sqrt{2}\cdot 4=16\sqrt{2}$."),
             rule="algebra"),
    ]

    REFLECTION = dict(says=(cap(r"Mirror $\ln\cos(x-\frac{\pi}{4})$ in the line $x=\frac{\pi}{8}$."),
                            cap(r"It lands on $\ln(\cos x)$: the same area.")))

    ANSWER = eq(r"\frac{\pi\ln 2}{16\sqrt{2}}")
    ANSWER_VALUE = float(np.pi * np.log(2) / (16 * S2))
    CLOSE_SAYS = (cap(r"Thin rectangles close in on $0.09624$."),
                  cap(r"Takeaway: on $0$ to $a$, try swapping $x$ for $a-x$."))

    def _reflection(self, scene, current):
        """ln cos(x - pi/4) (BLUE) and its mirror in x = pi/8 (ORANGE), which is ln cos x."""
        current.save_state()
        lines = self._trail.lines
        self.play(current.animate.set_opacity(0), *[l.animate.set_opacity(0) for l in lines], run_time=0.6)
        self._guard_section = "Reflection"
        g = dict(x_range=[0, Q4, Q8], y_range=[-0.4, 0.1, 0.1], a=0, b=Q4, size=(8, 3.6),
                 x_labels={Q8: r"\frac{\pi}{8}", Q4: r"\frac{\pi}{4}"},
                 y_labels={-0.2: "-0.2", -0.4: "-0.4"}, color_limits=False)
        gr = build_graph(g, shifted_log, (SAFE_LEFT, SAFE_RIGHT, CAPTION_TOP + 0.1, 1.0))
        self.play(FadeIn(gr.grid), Create(gr.axes, lag_ratio=0.02), FadeIn(gr.var_label), run_time=1.2)
        self.play(Create(gr.curve), run_time=1.2)
        self.play(FadeIn(gr.area), run_time=0.8)
        line = DashedLine(gr.axes.c2p(Q8, -0.4), gr.axes.c2p(Q8, 0), color=WHITE, dash_length=0.12)
        self.play(Create(line), run_time=0.8)
        caption(self, self.REFLECTION["says"][0])
        mirror = VGroup(gr.curve.copy(), gr.area.copy()).set_color(NEW_VAR_COLOR)
        mark(self, "reflection", offset=1.0)
        self.play(mirror.animate.flip(UP, about_point=gr.axes.c2p(Q8, 0)), run_time=2.0)
        caption(self, self.REFLECTION["says"][1], key="reflection: result")
        self.play(FadeOut(VGroup(gr.group, line, mirror)), run_time=1.0)
        self.play(Restore(current), *[l.animate.set_opacity(DIM_OPACITY) for l in lines], run_time=0.6)
