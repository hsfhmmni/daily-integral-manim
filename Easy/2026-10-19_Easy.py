import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import (GRAPH_BOX, IntegralVideo, LIMIT, NEW, SAFE_TOP, _readout, build_graph, cap, caption, eq, fit_into,
                    mark, mt)

P2 = float(np.pi / 2)
N_START, N_END = 1.0, 0.001     # the hook shrinks n from 1 to (visually) 0


def g(x, n):
    """The integrand for a fixed n: cos x (cos x - cos(x + n)) / n (the top is cos x - cos(x + n))."""
    x = np.asarray(x, dtype=float)
    return np.cos(x) * (np.cos(x) - np.cos(x + n)) / n


class EasyIntegral(IntegralVideo):
    DIFFICULTY = "Easy"
    DATE = "2026-10-19"

    # The integral depends on n; the picture and the rectangles show its limit as n -> 0,
    # the area under sin(x)cos(x) from 0 to pi/2 (I(n) is 0.50382 at n = 0.01, 0.500039 at n = 1e-4).
    @staticmethod
    def FUNC(x):
        x = np.asarray(x, dtype=float)
        return np.sin(x) * np.cos(x)

    @classmethod
    def exact_integral(cls):
        return mp.quad(lambda x: mp.sin(x) * mp.cos(x), [0, mp.pi / 2])

    NUM = r"\cos(x)+\sin(x)\sin(n)-\cos(x)\cos(n)"
    GROUPED = r"\cos(x)(1-\cos n)+\sin(x)\sin n"
    SN, CN = r"\frac{\sin n}{n}", r"\frac{1-\cos n}{n}"
    COLORS = {SN: NEW, CN: NEW}
    LIM = r"\lim_{n\to 0}"
    INT = (r"\int_{", ("n", LIMIT), r"}^{", (r"\frac{\pi}{2}", LIMIT), r"}")
    INT0 = (r"\int_{", ("0", LIMIT), r"}^{", (r"\frac{\pi}{2}", LIMIT), r"}")
    PROBLEM = eq(LIM, *INT, r"\frac{", NUM, r"}{", r"n\sec(x)", r"}", r"\,dx")
    CURVE_LABEL = None          # the integrand depends on n; the curve is its limit
    PROBLEM_X = (-4.6, 3.6)

    GRAPH = dict(x_range=[0, P2, P2 / 4], y_range=[0, 0.75, 0.25], a=0, b=P2, size=(8, 4.2), plot_range=(0, P2),
                 x_labels={P2 / 2: r"\frac{\pi}{4}", P2: r"\frac{\pi}{2}"},
                 y_labels={0.25: "0.25", 0.5: "0.5"})

    HOOK = cap(r"As $n$ shrinks to $0$, the curve settles. What area remains?")
    INTUITION = cap(r"Thin rectangles estimate the limiting area; watch the gap shrink.")
    INSIGHT = dict(
        parts=[NUM],
        label=cap(r"group the $n$ terms"),
        side=UP,
        say=cap(r"Sort the top by $\sin n$ and $\cos n$: two famous limits appear."),
    )

    STEPS = [
        dict(tex=eq(LIM, *INT, r"\cos(x)", r"\cdot", r"\frac{", NUM, r"}{", "n", r"}", r"\,dx"),
             say=cap(r"Dividing by $\sec x$ is multiplying by $\cos x$."),
             rule="sec_reciprocal",
             mapping=[cap(r"Here $\frac{1}{n\sec x}=\frac{\cos x}{n}$.")]),
        dict(tex=eq(LIM, *INT, r"\cos(x)", r"\cdot", r"\frac{", GROUPED, r"}{", "n", r"}", r"\,dx"),
             say=cap(r"Group the top: $\cos x\,(1-\cos n)+\sin x\sin n$."),
             rule="algebra"),
        dict(tex=eq(LIM, r"\Big(", CN, *INT, r"\cos^{2}x", r"\,dx", "+", SN, *INT, r"\sin x\cos x", r"\,dx",
                    r"\Big)"),
             say=cap(r"Anything with only $n$ is a constant: pull it out."),
             rule="linearity"),
        dict(tex=eq("0", r"\cdot", *INT0, r"\cos^{2}x", r"\,dx", "+", "1", r"\cdot", *INT0, r"\sin x\cos x", r"\,dx"),
             say=cap(r"As $n\to 0$: the first term vanishes, the second keeps weight $1$."),
             rule="small_angle_limits",
             mapping=[cap(r"Here $\frac{1-\cos n}{n}\to 0$ and $\frac{\sin n}{n}\to 1$.")]),
        dict(tex=eq(*INT0, r"\tfrac{1}{2}\sin 2x", r"\,dx"),
             say=cap(r"Only one integral is left: write $\sin x\cos x=\frac{1}{2}\sin 2x$."),
             rule="double_angle",
             mapping=[cap(r"Here $\sin 2x=2\sin x\cos x$, so halve it.")]),
        dict(tex=eq(r"\Big[", r"-\tfrac{1}{4}\cos 2x", r"\Big]_{", ("0", LIMIT), r"}^{", (r"\frac{\pi}{2}", LIMIT), r"}"),
             say=cap(r"Integrate: $\int\sin 2x\,dx=-\frac{1}{2}\cos 2x$."),
             rule="sin_integral",
             mapping=[cap(r"With $2x$ inside, divide by $2$: $-\frac{1}{2}\cos 2x$.")]),
        dict(tex=eq(r"\tfrac{1}{4}", "+", r"\tfrac{1}{4}"),
             say=cap(r"$\cos\pi=-1$ and $\cos 0=1$: each end gives $\frac{1}{4}$."),
             rule="ftc"),
        dict(tex=eq(r"\frac{1}{2}"),
             say=cap(r"Exactly one half."),
             rule="algebra"),
    ]

    def hook(self):
        """The real integrand, drawn first at n = 1; then n shrinks towards 0 and the curve and its
        area settle onto the limit (the base hook would show the limit curve before it is earned)."""
        self._guard_section = "Hook"
        gr = build_graph(self.GRAPH, self.FUNC)
        t = ValueTracker(N_START)
        curve = always_redraw(lambda: gr.axes.plot(lambda x: g(x, t.get_value()),
                                                   x_range=[t.get_value(), P2, (P2 - t.get_value()) / 300],
                                                   color=gr.curve.get_color(), stroke_width=4))
        area = always_redraw(lambda: gr.axes.get_area(curve, x_range=(t.get_value(), P2),
                                                      color=gr.area.get_color(), opacity=gr.area.get_fill_opacity()))
        n_num = DecimalNumber(N_START, num_decimal_places=2, font_size=34)
        n_num.add_updater(lambda m: m.set_value(t.get_value()))
        readout = _readout([(r"n=", n_num)])
        self.play(FadeIn(gr.grid), Create(gr.axes, lag_ratio=0.02), FadeIn(gr.var_label), run_time=1.5)
        self.play(Create(curve), FadeIn(readout), run_time=1.5)
        self.play(FadeIn(area), run_time=1.0)
        mark(self, "hook: n=1")
        caption(self, self.HOOK, key="hook", wait=False)
        self.play(t.animate.set_value(N_END), run_time=4.0, rate_func=smooth)
        mark(self, "hook: n near 0")
        self.wait(1.0)
        curve.clear_updaters()
        area.clear_updaters()
        self.remove(curve, area)
        self.add(gr.curve, gr.area)
        problem = mt(self.PROBLEM, self.COLORS)
        fit_into(problem, *self.PROBLEM_X, GRAPH_BOX[3] + 0.1, SAFE_TOP - 0.05, center=True)
        self.play(Write(problem), FadeOut(readout), run_time=1.5)
        self.wait(1.0)
        return gr, None, problem

    ANSWER = eq(r"\frac{1}{2}")
    ANSWER_VALUE = 0.5
    CLOSE_SAYS = (cap(r"Thin rectangles close in on $\frac{1}{2}=0.5$."),
                  cap(r"Takeaway: pull out $\frac{\sin n}{n}$ before taking the limit."))
