import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import (CAPTION_TOP, IntegralVideo, LIMIT, NEW, SAFE_LEFT, SAFE_RIGHT, SAFE_TOP, STAGE, build_graph,
                    cap, caption, clear_caption, draw_graph, eq, fit_into, highlight, mt, parts_of,
                    riemann_rectangles, unzoom)

PI = float(np.pi)
Y_TOP = 3.0


class _ThinEdges:
    """The graph's axes, but Riemann rectangles get thinner white edges as they multiply, so
    1024 of them still show green instead of a solid block of edge lines."""

    def __init__(self, axes):
        self._axes = axes

    def __getattr__(self, name):
        return getattr(self._axes, name)

    def get_riemann_rectangles(self, graph, x_range, dx, **kwargs):
        k = round((x_range[1] - x_range[0]) / dx + 0.5)
        kwargs["stroke_width"] = min(1.0, 16.0 / k)
        return self._axes.get_riemann_rectangles(graph, x_range=x_range, dx=dx, **kwargs)


class MediumIntegral(IntegralVideo):
    DIFFICULTY = "Medium"
    DATE = "2026-10-19"

    # The continued fraction's limit is sqrt(x) for x >= 1 (checked layer by layer to 30 digits).
    # For 0 <= x < 1 the floor is 0 and the fraction never settles (x, 1, x, 1, ...); the video
    # takes its fixed point sqrt(x) there too, as the problem intends.
    @staticmethod
    def FUNC(x):
        return 0.5 / np.sqrt(np.asarray(x, dtype=float))

    @classmethod
    def exact_integral(cls):
        return mp.quad(lambda x: 0.5 / mp.sqrt(x), [0, 1, mp.pi])

    A = r"\lfloor\sqrt{x}\rfloor"
    R = r"x-\lfloor\sqrt{x}\rfloor^{2}"
    REP = r"\cfrac{x-\lfloor\sqrt{x}\rfloor^{2}}{2\lfloor\sqrt{x}\rfloor+\cfrac{x-\lfloor\sqrt{x}\rfloor^{2}}{\ddots}}"
    COLORS = {REP: NEW, "y": NEW, "k+y": NEW, r"y^{2}": NEW}
    LIMS = (r"\int_{", ("0", LIMIT), r"}^{", (r"\pi", LIMIT), r"}")
    PROBLEM = eq(r"\frac{1}{2}", *LIMS, r"\Bigg(", A, "+", r"\cfrac{", R, r"}{2", A, "+", REP, r"}",
                 r"\Bigg)^{-1}", r"\,dx")
    PROBLEM_X = (-5.6, 3.3)     # a tall line: give it room, clear of the badge
    CURVE_LABEL = None          # the continued fraction is too big to sit beside the curve

    GRAPH = dict(x_range=[0, 3.5, 0.5], y_range=[0, Y_TOP, 0.5], a=0.03, b=PI, size=(8, 4.2), plot_range=(0.03, PI),
                 x_labels={1: "1", 2: "2", PI: r"\pi"},
                 y_labels={1: "1", 2: "2", 3: "3"})
    WINDOW = (0, PI)            # the shading starts at 0.03, where the curve leaves the picture
    COUNTS = (4, 16, 64, 256, 1024)     # the spike at 0 makes rectangles converge slowly

    HOOK = cap(r"Floors inside an endless fraction, yet the curve is smooth. Why?")
    INTUITION = cap(r"Near $0$ the curve shoots up; the gap shrinks slowly.")
    INSIGHT = dict(
        parts=[REP],
        label=cap(r"the same fraction again"),
        say=cap(r"Below each $2\lfloor\sqrt{x}\rfloor$, the same fraction starts over."),
    )

    STEPS = [
        dict(tex=eq("y", "=", "k", "+", r"\cfrac{", "x-k^{2}", r"}{2k+", r"\cfrac{", "x-k^{2}", r"}{2k+", r"\ddots",
                    r"}}"),
             say=cap(r"Call the fraction $y$, and write $k=\lfloor\sqrt{x}\rfloor$."),
             rule="algebra"),
        dict(tex=eq("y", "=", "k", "+", r"\cfrac{", "x-k^{2}", r"}{", "k+y", r"}"),
             say=cap(r"The tail after $2k$ is $y-k$, so the bottom is $k+y$."),
             rule="nested_fixed_point",
             mapping=[cap(r"Here $g(y)=k+\frac{x-k^{2}}{k+y}$.")]),
        dict(tex=eq(r"y^{2}", "+", "ky", "=", "ky", "+", "k^{2}", "-k^{2}", "+", "x"),
             say=cap(r"Multiply both sides by $k+y$ and expand."),
             highlight=(["ky", "k^{2}", "-k^{2}"], cap(r"these cancel")),
             side=UP,
             rule="algebra"),
        dict(tex=eq(r"y^{2}", "=", "x"),
             say=cap(r"The $ky$ terms and the $k^{2}$ terms cancel."),
             rule="algebra"),
        dict(tex=eq("y", "=", r"\sqrt{x}"),
             say=cap(r"Take the positive root: the floor has vanished completely."),
             rule="nested_fixed_point"),
        dict(tex=eq(r"\frac{1}{2}", *LIMS, r"\frac{1}{", r"\sqrt{x}", r"}", r"\,dx"),
             say=cap(r"For $x<1$, $k=0$ and the fraction never settles."),
             rule="algebra"),
        dict(tex=eq(r"\frac{1}{2}", *LIMS, r"x^{-\frac{1}{2}}", r"\,dx"),
             say=cap(r"On $[0,1)$ we take its fixed point $\sqrt{x}$ too."),
             rule=["exponent_laws", "improper_integral"],
             mapping={"improper_integral": [cap(r"Here $x^{-\frac{1}{2}}$ blows up at the lower limit $0$.")]}),
        dict(tex=eq(r"\frac{1}{2}", r"\Big[", r"2\sqrt{x}", r"\Big]_{", ("0", LIMIT), r"}^{", (r"\pi", LIMIT), r"}"),
             say=cap(r"Power rule: $\int x^{-\frac{1}{2}}\,dx=2\sqrt{x}$."),
             rule=["power_rule", "linearity"]),
        dict(tex=eq(r"\sqrt{\pi}", "-", "0"),
             say=cap(r"As $x\to 0$, $2\sqrt{x}\to 0$: the area is finite."),
             rule=["ftc", "improper_integral"]),
        dict(tex=eq(r"\sqrt{\pi}"),
             say=cap(r"About $1.7725$."),
             rule="algebra"),
    ]

    GRAPH_TOP = 1.45            # the graph sits lower than usual, so the tall problem gets a taller band

    def hook(self):
        """As IntegralVideo.hook (no curve label), but with the graph lowered to GRAPH_TOP: the
        three-level fraction needs about twice the usual band above the graph to stay readable."""
        self._guard_section = "Hook"
        gr = build_graph(self.GRAPH, self.FUNC, (SAFE_LEFT, 3.0, CAPTION_TOP + 0.1, self.GRAPH_TOP))
        draw_graph(self, gr)
        caption(self, self.HOOK, key="hook")
        problem = mt(self.PROBLEM, self.COLORS)
        fit_into(problem, *self.PROBLEM_X, self.GRAPH_TOP + 0.1, SAFE_TOP - 0.05, center=True)
        self.play(Write(problem), run_time=1.5)
        self.wait(1.0)
        return gr, None, problem

    def intuition(self, gr, label):
        """As IntegralVideo.intuition, but the rectangles are drawn no taller than the graph
        (the spike at 0 is unbounded); the estimate and gap use the true heights."""
        self._guard_section = "Intuition"
        a, b = self.window()
        if label is not None:
            self.play(FadeOut(label), run_time=0.5)
        caption(self, self.INTUITION, wait=False)
        capped = gr.axes.plot(lambda x: min(float(self.FUNC(x)), Y_TOP), x_range=[1e-6, PI, PI / 600])
        shown = SimpleNamespace(**vars(gr))
        shown.curve = capped
        shown.axes = _ThinEdges(gr.axes)
        rects, readout, n, est = riemann_rectangles(self, shown, a, b, self.ANSWER_VALUE, self.COUNTS)
        self.wait(1.0)
        clear_caption(self)
        self.play(FadeOut(VGroup(gr.group, readout)), FadeOut(rects), run_time=1.0)
        return est

    def insight(self, problem):
        """The continued fraction alone, as large as the stage allows (the whole line is too
        tall to read at the stage's height), with its repeating tail boxed."""
        self._guard_section = "Insight"
        target = mt(eq(self.A, "+", r"\cfrac{", self.R, r"}{2", self.A, "+", self.REP, r"}"), self.COLORS)
        fit_into(target, SAFE_LEFT, SAFE_RIGHT, STAGE[2], STAGE[3])
        target.move_to([0, (STAGE[2] + STAGE[3]) / 2, 0])
        self.play(ReplacementTransform(problem, target), run_time=1.2)
        extra = highlight(self, parts_of(target, *self.INSIGHT["parts"]), self.INSIGHT["label"],
                          side=RIGHT, context=target)
        caption(self, self.INSIGHT["say"])
        unzoom(self, FadeOut(extra))
        return target

    ANSWER = eq(r"\sqrt{\pi}")
    ANSWER_VALUE = float(np.sqrt(np.pi))
    CLOSE_SAYS = (cap(r"Even $2048$ rectangles fall short: the spike at $0$ resists."),
                  cap(r"Takeaway: call the endless tail $y$, then solve $y=g(y)$."))
