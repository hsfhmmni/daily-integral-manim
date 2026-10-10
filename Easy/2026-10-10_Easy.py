import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import (IntegralVideo, LIMIT, NEW, cap, eq, build_graph, caption, mark, CAPTION_TOP, SAFE_LEFT,
                    SAFE_RIGHT, DIM_OPACITY, AREA_COLOR, AREA_OPACITY)

PI2 = float(np.pi / 2)
PI4 = float(np.pi / 4)


def mirror_func(x):
    return np.sin(x) ** 2 * np.cos(x) / (np.sin(x) + np.cos(x))


class EasyIntegral(IntegralVideo):
    DIFFICULTY = "Easy"
    DATE = "2026-10-10"

    @staticmethod
    def FUNC(x):
        # cos x / (sec x + csc x), multiplied top and bottom by sin x cos x (fills the end points with 0)
        return np.sin(x) * np.cos(x) ** 2 / (np.sin(x) + np.cos(x))

    @classmethod
    def exact_integral(cls):
        return mp.quad(lambda x: mp.cos(x) / (mp.sec(x) + mp.csc(x)), [0, mp.pi / 2])

    COLORS = {r"\sin^{2}x\cos x": NEW}
    PROBLEM = eq(r"\int_{", ("0", LIMIT), r"}^{", (r"\frac{\pi}{2}", LIMIT), r"}", r"\frac{", r"\cos x", r"}{",
                 r"\sec x+\csc x", r"}", r"\,dx")
    CURVE_LABEL = eq("y", "=", r"\frac{", r"\cos x", r"}{", r"\sec x+\csc x", r"}")
    LABEL_AT = (0.95, 0.3)      # empty space above the falling right half of the curve

    GRAPH = dict(x_range=[0, 1.75, 0.25], y_range=[0, 0.4, 0.1], a=0, b=PI2, size=(8, 4.2), plot_range=(0, PI2),
                 x_labels={PI4: r"\frac{\pi}{4}", PI2: r"\frac{\pi}{2}"},
                 y_labels={0.1: "0.1", 0.2: "0.2", 0.3: "0.3", 0.4: "0.4"})

    HOOK = cap(r"How big is the green area from $0$ to $\frac{\pi}{2}$?")
    HOOK_NOTE = cap(r"At each end one term blows up, so the curve $\to 0$.")
    INTUITION = cap(r"Thin rectangles estimate the area; watch the gap shrink.")
    INSIGHT = dict(
        before=cap(r"Look at the bottom: swap $\sec$ and $\csc$ and nothing changes."),
        parts=[r"\sec x+\csc x"],
        label=cap(r"$=\frac{\sin x+\cos x}{\sin x\cos x}$"),
        say=cap(r"Swapping $x$ for $\frac{\pi}{2}-x$ swaps $\sin$ and $\cos$."),
    )

    STEPS = [
        dict(tex=eq("I", "=", r"\int_{", ("0", LIMIT), r"}^{", (r"\frac{\pi}{2}", LIMIT), r"}", r"\frac{",
                    r"\sin x\cos^{2}x", r"}{", r"\sin x+\cos x", r"}", r"\,dx"),
             say=cap(r"Multiply top and bottom by $\sin x\cos x$; call it $I$.")),
        dict(tex=eq("I", "=", r"\int_{", ("0", LIMIT), r"}^{", (r"\frac{\pi}{2}", LIMIT), r"}", r"\frac{",
                    r"\sin^{2}x\cos x", r"}{", r"\sin x+\cos x", r"}", r"\,dx"),
             say=cap(r"Replace $x$ by $\frac{\pi}{2}-x$: same limits, $\sin$ and $\cos$ swap."),
             then="reflection"),
        dict(tex=eq("2I", "=", r"\int_{", ("0", LIMIT), r"}^{", (r"\frac{\pi}{2}", LIMIT), r"}", r"\frac{",
                    r"\sin x\cos x", r"(\sin x+\cos x)", r"}{", r"\sin x+\cos x", r"}", r"\,dx"),
             say=cap(r"Add the two forms of $I$, then factor the top.")),
        dict(tex=eq("2I", "=", r"\int_{", ("0", LIMIT), r"}^{", (r"\frac{\pi}{2}", LIMIT), r"}", r"\sin x\cos x",
                    r"\,dx"),
             say=cap(r"The bracket cancels with the bottom.")),
        dict(tex=eq("2I", "=", r"\Big[", r"\frac{\sin^{2}x}{2}", r"\Big]_{", ("0", LIMIT), r"}^{",
                    (r"\frac{\pi}{2}", LIMIT), r"}"),
             say=cap(r"The derivative of $\frac{\sin^{2}x}{2}$ is $\sin x\cos x$.")),
        dict(tex=eq("2I", "=", r"\frac{1}{2}"),
             say=cap(r"Upper limit minus lower limit: $\frac{1}{2}-0$.")),
        dict(tex=eq("I", "=", r"\frac{1}{4}"),
             say=cap(r"Halve both sides.")),
    ]

    REFLECTION = dict(
        spec=dict(x_range=[0, 1.75, 0.25], y_range=[0, 0.6, 0.2], a=0, b=PI2, size=(7, 3.2), plot_range=(0, PI2),
                  x_labels={PI4: r"\frac{\pi}{4}", PI2: r"\frac{\pi}{2}"}, y_labels={0.2: "0.2", 0.4: "0.4"}),
        says=(cap(r"Mirror the curve in $x=\frac{\pi}{4}$: same area, $\sin$ and $\cos$ swapped."),
              cap(r"Stacked, the two curves make $\sin x\cos x$, area $\frac{1}{2}$.")),
    )

    def _reflection(self, scene, current):
        """Mirror the curve in x = pi/4 (ORANGE copy), then stack the two: the sum is sin x cos x."""
        r = self.REFLECTION
        current.save_state()
        lines = self._trail.lines
        self.play(current.animate.set_opacity(0), *[l.animate.set_opacity(0) for l in lines], run_time=0.6)
        self._guard_section = "Reflection"
        gr = build_graph(r["spec"], self.FUNC, (SAFE_LEFT, SAFE_RIGHT, CAPTION_TOP + 0.1, 1.0))
        ax = gr.axes
        self.play(FadeIn(gr.grid), Create(ax, lag_ratio=0.02), FadeIn(gr.var_label), run_time=1.2)
        self.play(Create(gr.curve), run_time=1.2)
        axis_line = DashedLine(ax.c2p(PI4, 0), ax.c2p(PI4, 0.6), color=GREY_B, dash_length=0.1)
        self.play(Create(axis_line), run_time=0.8)
        mirror = gr.curve.copy().set_color(NEW)
        caption(self, r["says"][0])
        mark(self, "reflection", offset=1.0)
        # morph into the mirror image (an animated flip squashes the curve to a spike halfway)
        mirrored = ax.plot(mirror_func, x_range=[0, PI2, PI2 / 600], color=NEW, stroke_width=4)
        self.play(Transform(mirror, mirrored), run_time=2.0)
        # stack: the orange curve rides on top of the blue one, giving sin x cos x
        stacked = ax.plot(lambda x: self.FUNC(x) + mirror_func(x), x_range=[0, PI2, PI2 / 600], color=NEW,
                          stroke_width=4)
        total = ax.get_area(stacked, x_range=(0, PI2), color=AREA_COLOR, opacity=AREA_OPACITY)
        self.play(Transform(mirror, stacked), FadeOut(axis_line), run_time=1.5)
        self.play(FadeIn(total), run_time=1.0)
        caption(self, r["says"][1], key="reflection: result")
        self.play(FadeOut(VGroup(gr.grid, ax, gr.var_label, gr.curve, mirror, total)), run_time=1.0)
        self.play(Restore(current), *[l.animate.set_opacity(DIM_OPACITY) for l in lines], run_time=0.6)

    ANSWER = eq(r"\frac{1}{4}")
    ANSWER_VALUE = 0.25
    CLOSE_SAYS = (cap(r"More, thinner rectangles close in on $\frac{1}{4}=0.25$."),
                  cap(r"Takeaway: on $[0,\frac{\pi}{2}]$, try $x\to\frac{\pi}{2}-x$ and add."))
