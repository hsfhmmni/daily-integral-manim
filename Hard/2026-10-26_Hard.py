import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
import common
from common import AREA_COLOR, AREA_OPACITY, CURVE_COLOR, IntegralVideo, LIMIT, NEW, cap, eq

JUMPS = [2.0 ** -k for k in range(1, 10)]      # where the floor steps down (finer ones are too small to see)


class HardIntegral(IntegralVideo):
    DIFFICULTY = "Hard"
    DATE = "2026-10-26"

    # On [2^-n, 2^(1-n)) the floor of log2 x is -n, so the integral is -sum n (ln cos 2^-n - ln cos 2^(1-n)).
    # Summing by parts (N ln cos 2^-N -> 0), every ln cos 2^-n, n >= 0, is left once: ln prod cos 2^-n.
    # cos t = sin 2t / (2 sin t) telescopes: prod_{n>=1} cos 2^-n = sin 1 / lim 2^N sin 2^-N = sin 1,
    # so the integral is ln(cos 1 sin 1) = ln(sin 2 / 2) = -0.78823.
    @staticmethod
    def FUNC(x):
        x = np.asarray(x, dtype=float)
        # at x = 1 the floor is 0; draw the left-hand limit there (one point, no area); at 0 the limit is 0
        xs = np.clip(x, 1e-300, np.nextafter(1.0, 0.0))
        return np.where(x > 0, np.floor(np.log2(xs)) * np.tan(xs), 0.0)

    @classmethod
    def exact_integral(cls):
        f = lambda x: mp.floor(mp.log(x, 2)) * mp.tan(x)      # noqa: E731
        return mp.quad(f, [0] + [mp.mpf(2) ** -k for k in range(60, -1, -1)])     # split at every jump

    COLORS = {r"\sum_{n=1}^{\infty}": NEW, r"\sum_{n=0}^{\infty}": NEW, "n": NEW}
    LIMS = (r"\int_{", ("0", LIMIT), r"}^{", ("1", LIMIT), r"}")
    NLIMS = (r"\int_{", (r"2^{-n}", LIMIT), r"}^{", (r"2^{1-n}", LIMIT), r"}")
    FL = r"\lfloor\log_{2}(x)\rfloor"
    PROBLEM = eq(*LIMS, FL, r"\tan(x)", r"\,dx")
    CURVE_LABEL = eq("y", "=", FL, r"\tan(x)")
    LABEL_AT = (0.03, -1.9)     # empty space bottom-left, below the shallow steps near 0

    GRAPH = dict(x_range=[0, 1, 0.125], y_range=[-2, 0.5, 0.5], a=0, b=1, size=(8, 4.2),
                 x_labels={0.125: r"\frac{1}{8}", 0.25: r"\frac{1}{4}", 0.5: r"\frac{1}{2}", 1: "1"},
                 y_labels={-1: "-1", -2: "-2"})

    HOOK = cap(r"Infinitely many steps crowd towards $0$. Can we add them all?")
    INTUITION = cap(r"All of this area is below the axis, so negative.")
    INSIGHT = dict(
        parts=[FL],
        label=cap(r"$-1,\,-2,\,-3,\,\dots$"),
        say=cap(r"Each halving towards $0$ drops the floor one more step."),
    )

    STEPS = [
        dict(tex=eq("-", r"\sum_{n=1}^{\infty}", "n", *NLIMS, r"\tan x", r"\,dx"),
             say=cap(r"On $[2^{-n},2^{1-n})$ the floor is $-n$: split there."),
             rule=["interval_additivity", "floor_function", "linearity"]),
        dict(tex=eq("-", r"\sum_{n=1}^{\infty}", "n", r"\Big(", r"\ln\cos 2^{-n}", "-", r"\ln\cos 2^{1-n}", r"\Big)"),
             say=cap(r"$\int\tan x\,dx=-\ln\cos x$, as $\cos x>0$ on $[0,1]$."),
             rule=["tan_integral", "ftc", "absolute_value"]),
        dict(tex=eq(r"\sum_{n=0}^{\infty}", r"\ln\cos 2^{-n}"),
             say=cap(r"Sum by parts; $N\ln\cos 2^{-N}\to 0$, so each term counts once."),
             rule="summation_by_parts"),
        dict(tex=eq(r"\ln", r"\Big(", r"\cos 1", r"\cdot", r"\prod_{n=1}^{\infty}\cos 2^{-n}", r"\Big)"),
             say=cap(r"Add the $\ln$ terms: it is $\ln$ of the product."),
             rule="log_laws"),
        dict(tex=eq(r"\ln", r"\Big(", r"\cos 1", r"\cdot", r"\lim_{N\to\infty}\frac{\sin 1}{2^{N}\sin 2^{-N}}", r"\Big)"),
             say=cap(r"$\cos t=\frac{\sin 2t}{2\sin t}$: each bottom cancels the next top."),
             rule=["double_angle", "telescoping_product"]),
        dict(tex=eq(r"\ln", r"\Big(", r"\cos 1", r"\cdot", r"\sin 1", r"\Big)"),
             say=cap(r"$2^{N}\sin 2^{-N}=\frac{\sin h}{h}\to 1$, with $h=2^{-N}$."),
             rule="small_angle_limits"),
        dict(tex=eq(r"\ln", r"\frac{\sin 2}{2}"),
             say=cap(r"Double angle again: $\sin 1\cos 1=\frac{1}{2}\sin 2$."),
             rule="double_angle"),
    ]

    ANSWER = eq(r"\ln", r"\frac{\sin 2}{2}")
    ANSWER_VALUE = float(mp.log(mp.sin(2) / 2))
    CLOSE_SAYS = (cap(r"Thin rectangles close in on $-0.7882$."),
                  cap(r"Takeaway: halving angles telescope, since $\sin 2t=2\sin t\cos t$."))

    def _jump_graph(self, g, func, *args, **kwargs):
        """common.build_graph, but the curve breaks at each jump 2^-k instead of joining the
        steps with steep lines."""
        gr = self._plain_build_graph(g, func, *args, **kwargs)
        ax = gr.axes
        curve = ax.plot(func, x_range=[0, 1, 1 / 2000], discontinuities=JUMPS, dt=1e-5,
                        color=CURVE_COLOR, stroke_width=4)
        area = ax.get_area(curve, x_range=(0, 1), color=AREA_COLOR, opacity=AREA_OPACITY)
        group = VGroup(gr.grid, ax, area, curve, gr.var_label)
        return SimpleNamespace(**{**vars(gr), "curve": curve, "area": area, "group": group})

    def hook(self):
        """As IntegralVideo.hook, with the graph broken at the jumps (see _jump_graph)."""
        self._plain_build_graph = common.build_graph
        common.build_graph = self._jump_graph
        try:
            return super().hook()
        finally:
            common.build_graph = self._plain_build_graph
