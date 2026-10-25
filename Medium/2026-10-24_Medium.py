import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
import common
from common import (AREA_COLOR, AREA_OPACITY, BACKGROUND, CURVE_COLOR, TRAP_COLOR, IntegralVideo, LIMIT, _now,
                    add_watermark, cap, close, eq, install_frame_guard, intro_card, keep_watermark, make_badge)


class MediumIntegral(IntegralVideo):
    DIFFICULTY = "Medium"
    DATE = "2026-10-24"

    # x - floor(x) is x + 1 on [-1/2, 0) and x on (0, 1), so the integrand is x/(x+1), then 1:
    # [x - ln|x+1|] from -1/2 to 0 is 1/2 + ln(1/2), plus 1, giving 3/2 - ln 2.
    # At the whole numbers 0 and 1 the bottom is 0: single points carry no area.
    @staticmethod
    def FUNC(x):
        x = np.asarray(x, dtype=float)
        frac = x - np.floor(x)
        # at a whole number n the bottom is 0; draw the left-hand limit n there (one point, no area)
        return np.where(frac > 0, x / np.where(frac > 0, frac, 1.0), x)

    @classmethod
    def exact_integral(cls):
        return mp.quad(lambda x: x / (x - mp.floor(x)), [-0.5, 0, 1])

    L1 = (r"\int_{", (r"-\frac{1}{2}", LIMIT), r"}^{", ("0", LIMIT), r"}")
    L2 = (r"\int_{", ("0", LIMIT), r"}^{", ("1", LIMIT), r"}")
    LIMS = (r"\int_{", (r"-\frac{1}{2}", LIMIT), r"}^{", ("1", LIMIT), r"}")
    FLOOR = r"\lfloor x\rfloor"
    PROBLEM = eq(*LIMS, r"\frac{", "x", r"}{", "x-", FLOOR, r"}", r"\,dx")
    CURVE_LABEL = eq("y", "=", r"\frac{", "x", r"}{", "x-", FLOOR, r"}")
    LABEL_AT = (0.2, -1.3)      # empty space below the axis, right of the jump

    GRAPH = dict(x_range=[-0.5, 1, 0.25], y_range=[-1.5, 1.5, 0.5], a=-0.5, b=1, size=(8, 4.2),
                 x_labels={-0.5: r"-\frac{1}{2}", 0.5: r"\frac{1}{2}", 1: "1"},
                 y_labels={-1: "-1", 1: "1"})
    COUNTS = (3, 6, 12, 24, 48)     # multiples of 3: the jump at 0 always falls on a strip edge
    END_COUNT = 3072                # the close ends on a multiple of 3 as well

    HOOK = cap(r"The bottom is $0$ at every whole number. What breaks there?")
    HOOK_NOTE = cap(r"At $x=0$ the curve jumps from $0$ up to $1$.")
    INTUITION = cap(r"Area below the axis counts as negative.")
    INSIGHT = dict(
        parts=[FLOOR],
        label=cap(r"$-1$, then $0$"),
        say=cap(r"$\lfloor x\rfloor$ is $-1$ left of $0$, and $0$ right of it."),
    )

    STEPS = [
        dict(tex=eq(*L1, r"\frac{", "x", r"}{", "x-", FLOOR, r"}", r"\,dx", "+",
                    *L2, r"\frac{", "x", r"}{", "x-", FLOOR, r"}", r"\,dx"),
             say=cap(r"Split the interval at $0$, where $\lfloor x\rfloor$ jumps."),
             rule=["interval_additivity", "floor_function"],
             mapping={"interval_additivity": [cap(r"Split $[-\frac{1}{2},1]$ at $0$, into two pieces.")],
                      "floor_function": [cap(r"For $-1\le x<0$, $\lfloor x\rfloor=-1$; for $0\le x<1$, it is $0$.")]}),
        dict(tex=eq(*L1, r"\frac{", "x", r"}{", "x+1", r"}", r"\,dx", "+",
                    *L2, r"\frac{", "x", r"}{", "x", r"}", r"\,dx"),
             say=cap(r"Left of $0$: $x-(-1)=x+1$. Right of $0$: $x-0=x$."),
             rule="floor_function"),
        dict(tex=eq(*L1, r"\Big(", "1", "-", r"\frac{1}{x+1}", r"\Big)", r"\,dx", "+", *L2, "1", r"\,dx"),
             say=cap(r"$\frac{x}{x+1}=1-\frac{1}{x+1}$, and $\frac{x}{x}=1$ for $x>0$."),
             rule="algebra"),
        dict(tex=eq(r"\Big[", "x", "-", r"\ln|x+1|", r"\Big]_{", (r"-\frac{1}{2}", LIMIT), r"}^{", ("0", LIMIT), r"}",
                    "+", r"\Big[", "x", r"\Big]_{", ("0", LIMIT), r"}^{", ("1", LIMIT), r"}"),
             say=cap(r"$\int\frac{1}{x+1}\,dx=\ln|x+1|$, and $\int 1\,dx=x$."),
             rule=["reciprocal_integral", "absolute_value", "power_rule", "linearity"]),
        dict(tex=eq(r"\Big(", "0", "-", r"\big(-\frac{1}{2}-\ln\frac{1}{2}\big)", r"\Big)", "+", "1"),
             say=cap(r"At $0$: $0-\ln 1=0$. At $-\frac{1}{2}$: $-\frac{1}{2}-\ln\frac{1}{2}$."),
             rule=["ftc", "log_values"]),
        dict(tex=eq(r"\frac{1}{2}", "+", r"\ln\frac{1}{2}", "+", "1"),
             say=cap(r"Clear the brackets: the two minus signs make plus."),
             rule="algebra"),
        dict(tex=eq(r"\frac{3}{2}", "-", r"\ln 2"),
             say=cap(r"$\ln\frac{1}{2}=-\ln 2$, and $\frac{1}{2}+1=\frac{3}{2}$."),
             rule="log_laws"),
    ]

    ANSWER = eq(r"\frac{3}{2}", "-", r"\ln 2")
    ANSWER_VALUE = float(1.5 - np.log(2))
    CLOSE_SAYS = (cap(r"Thin rectangles close in on $0.8069$."),
                  cap(r"Takeaway: split a floor at its jumps; each piece is ordinary."))

    def _jump_graph(self, g, func, *args, **kwargs):
        """common.build_graph, but the curve is drawn in two pieces with a break at the jump
        (x = 0), and hollow dots where the integrand is undefined: (0, 0), (0, 1) and (1, 1)."""
        gr = self._plain_build_graph(g, func, *args, **kwargs)
        ax = gr.axes
        curve = ax.plot(func, x_range=[-0.5, 1, 1.5 / 600], discontinuities=[0], dt=0.002,
                        color=CURVE_COLOR, stroke_width=4)
        area = ax.get_area(curve, x_range=(-0.5, 1), color=AREA_COLOR, opacity=AREA_OPACITY)
        holes = VGroup(*[Circle(radius=0.09).set_stroke(TRAP_COLOR, 3).set_fill(BACKGROUND, 1).move_to(ax.c2p(x, y))
                         for x, y in ((0, 0), (0, 1), (1, 1))])
        group = VGroup(gr.grid, ax, area, curve, gr.var_label, holes)
        return SimpleNamespace(**{**vars(gr), "curve": curve, "area": area, "hole": holes, "group": group})

    def hook(self):
        """As IntegralVideo.hook, with the graph broken at the jump (see _jump_graph)."""
        self._plain_build_graph = common.build_graph
        common.build_graph = self._jump_graph
        try:
            return super().hook()
        finally:
            common.build_graph = self._plain_build_graph

    def construct(self):
        """As IntegralVideo.construct, but the close ends on END_COUNT rectangles (a multiple of
        3, so the jump at 0 sits on a strip edge and the last estimate does not wobble)."""
        install_frame_guard(self)
        self._narration, self._keyframes, self._caption, self._caption_log = [], [], None, []
        self._rules_seen = set()
        add_watermark(self)
        intro_card(self, self.DIFFICULTY, self.date_long(), self.PROBLEM, self.COLORS)
        badge = make_badge(self, self.DIFFICULTY, self.date_short())
        self._badge = badge
        self._guard_reserved = [badge, self._watermark]
        self.add(badge)
        keep_watermark(self)
        gr, label, problem = self.hook()
        self.intuition(gr, label)
        problem = self.insight(problem)
        current, trail = self.method(problem)
        close(self, current, trail, self.ANSWER, self.COLORS, self.FUNC, self.window(), self.ANSWER_VALUE,
              self.COUNTS[-1], self.CLOSE_SAYS, widen_to=self.CLOSE_WIDEN, end_count=self.END_COUNT)
        if self._caption_log and self._caption_log[-1][2] is None:
            self._caption_log[-1][2] = _now(self)
        self.write_narration()
