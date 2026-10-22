import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
import common
from common import (AREA_COLOR, AREA_OPACITY, CAPTION_TOP, CURVE_COLOR, GRAPH_BOX, READOUT_BOX, SAFE_LEFT,
                    SAFE_RIGHT, TRAP_COLOR, IntegralVideo, LIMIT, NEW, add_watermark, build_graph, cap, caption,
                    clear_caption, draw_graph, eq, fit_into, install_frame_guard, intro_card, keep_watermark,
                    make_badge, mark, midpoint_sum, mt, riemann_rectangles, _now, _readout, _show_value)

# The 15 divisors of 2025 = 3^4 * 5^2: the only n where floor(2025/n) / (2025/n) reaches 1.
DIVISORS = [d for d in range(1, 2026) if 2025 % d == 0]


class _ThinEdges:
    """The graph's axes, but Riemann rectangles get thinner white edges as they multiply, so
    2025 of them still show green instead of a solid block of edge lines; a rectangle that
    lands on a spike gets a solid green edge, since at 1 wide it is far thinner than a pixel."""

    def __init__(self, axes):
        self._axes = axes

    def __getattr__(self, name):
        return getattr(self._axes, name)

    def get_riemann_rectangles(self, graph, x_range, dx, **kwargs):
        k = round((x_range[1] - x_range[0]) / dx + 0.5)
        kwargs["stroke_width"] = min(1.0, 16.0 / k)
        rects = self._axes.get_riemann_rectangles(graph, x_range=x_range, dx=dx, **kwargs)
        for r in rects:
            if r.height > 1e-3:
                r.set_stroke(AREA_COLOR, width=4, opacity=1)
        return rects


class MediumIntegral(IntegralVideo):
    DIFFICULTY = "Medium"
    DATE = "2026-10-22"

    # With n = floor(x), floor(2025/n) / (2025/n) <= 1, with equality exactly when n divides 2025,
    # so the integrand is x on [n, n+1) for the 15 divisors n and 0 elsewhere:
    # sum (n + 1/2) = sigma(2025) + 15/2 = 121 * 31 + 15/2 = 7517/2.
    @staticmethod
    def FUNC(x):
        n = np.floor(np.asarray(x, dtype=float))
        return x * np.floor(np.floor(2025 / n) / (2025 / n))

    @classmethod
    def exact_integral(cls):
        f = lambda x: x * mp.floor(mp.floor(2025 / mp.floor(x)) / (2025 / mp.floor(x)))     # noqa: E731
        return mp.quad(f, list(range(1, 2027)))         # one call, split at every jump of floor(x)

    COLORS = {r"\sum_{n=1}^{2025}": NEW, r"\sum_{n\mid 2025}": NEW}
    LIMS = (r"\int_{", ("1", LIMIT), r"}^{", ("2026", LIMIT), r"}")
    NLIMS = (r"\int_{", ("n", LIMIT), r"}^{", ("n+1", LIMIT), r"}")
    TOP = r"\big\lfloor\frac{2025}{\lfloor x\rfloor}\big\rfloor"
    BOTTOM = r"\frac{2025}{\lfloor x\rfloor}"
    PROBLEM = eq(*LIMS, "x", r"\Bigg\lfloor", r"\frac{", TOP, r"}{", BOTTOM, r"}", r"\Bigg\rfloor", r"\,dx")
    CURVE_LABEL = None

    GRAPH = dict(x_range=[0, 2100, 300], y_range=[0, 2100, 700], a=1, b=2026, size=(8, 4.2),
                 x_labels={405: "405", 675: "675", 2026: "2026"},
                 y_labels={700: "700", 1400: "1400", 2100: "2100"})
    COUNTS = (5, 25, 135, 675, 2025)        # strips of width 1 land exactly on every spike

    HOOK = cap(r"Zero almost everywhere, with thin spikes. Where are they?")
    INTUITION = cap(r"Rectangles miss the spikes until each strip is $1$ wide.")
    INSIGHT = dict(
        parts=[TOP, BOTTOM],
        label=cap(r"$\frac{\lfloor y\rfloor}{y}\le 1$"),
        say=cap(r"It is $1$ only when $\lfloor x\rfloor$ divides $2025$; otherwise $0$."),
    )

    STEPS = [
        dict(tex=eq(r"\sum_{n=1}^{2025}", *NLIMS, "x", r"\Bigg\lfloor", r"\frac{",
                    r"\big\lfloor\frac{2025}{n}\big\rfloor", r"}{", r"\frac{2025}{n}", r"}", r"\Bigg\rfloor", r"\,dx"),
             say=cap(r"Cut at each whole number: on $[n,n+1)$, $\lfloor x\rfloor=n$."),
             rule=["interval_additivity", "floor_function"],
             mapping={"interval_additivity": [cap(r"Split $[1,2026]$ into $2025$ pieces of width $1$.")],
                      "floor_function": [cap(r"For $n\le x<n+1$, $\lfloor x\rfloor=n$ stays constant.")]}),
        dict(tex=eq(r"\sum_{n\mid 2025}", *NLIMS, "x", r"\,dx"),
             say=cap(r"Keep only the pieces where $n$ divides $2025$."),
             rule="floor_function"),
        dict(tex=eq(r"\sum_{n\mid 2025}", r"\Big(", "n", "+", r"\frac{1}{2}", r"\Big)"),
             say=cap(r"Each piece gives $\Big[\frac{x^{2}}{2}\Big]_{n}^{n+1}=n+\frac{1}{2}$."),
             rule=["power_rule", "ftc"]),
        dict(tex=eq(r"\sum_{n\mid 2025}", "n", "+", r"\frac{15}{2}"),
             say=cap(r"$2025=3^{4}\cdot 5^{2}$ has $5\cdot 3=15$ divisors."),
             rule=["divisor_sum", "linearity"],
             mapping={"divisor_sum": [cap(r"Here $2025=3^{4}\cdot 5^{2}$: $p=3$, $a=4$, $q=5$, $b=2$.")]}),
        dict(tex=eq(r"(1+3+9+27+81)", r"(1+5+25)", "+", r"\frac{15}{2}"),
             say=cap(r"Expanding this product lists every divisor exactly once."),
             rule="divisor_sum"),
        dict(tex=eq("121", r"\cdot", "31", "+", r"\frac{15}{2}"),
             say=cap(r"$1+3+9+27+81=121$ and $1+5+25=31$."),
             rule="algebra"),
        dict(tex=eq(r"\frac{7517}{2}"),
             say=cap(r"$3751+\frac{15}{2}=\frac{7517}{2}$."),
             rule="algebra"),
    ]

    ANSWER = eq(r"\frac{7517}{2}")
    ANSWER_VALUE = 3758.5
    CLOSE_SAYS = (cap(r"Any whole multiple of $2025$ strips gives exactly $3758.5$."),
                  cap(r"Takeaway: a floor is constant between integers, so split there."))

    def hook(self):
        """As IntegralVideo.hook, but the curve is drawn as its 15 spikes: a plot sampled 600
        times across [1, 2026] would step over strips only 1 wide."""
        self._guard_section = "Hook"
        base = build_graph(self.GRAPH, lambda x: 0.0 * x)
        ax = base.axes
        spikes = VGroup(*[Line(ax.c2p(d + 0.5, 0), ax.c2p(d + 0.5, d + 0.5)) for d in DIVISORS])
        spikes.set_stroke(CURVE_COLOR, width=4)
        area = VGroup(*[Polygon(ax.c2p(d, 0), ax.c2p(d, d), ax.c2p(d + 1, d + 1), ax.c2p(d + 1, 0))
                        for d in DIVISORS])
        area.set_stroke(width=0).set_fill(AREA_COLOR, AREA_OPACITY)
        ghost = DashedLine(ax.c2p(1, 1), ax.c2p(2026, 2026), dash_length=0.12)
        ghost.set_stroke(GREY_B, width=2, opacity=0.5)
        gr = SimpleNamespace(axes=ax, grid=base.grid, curve=spikes, area=area, hole=None,
                             var_label=base.var_label, spec=self.GRAPH, func=self.FUNC,
                             group=VGroup(base.grid, ax, ghost, area, spikes, base.var_label))
        draw_graph(self, gr)
        self.play(Create(ghost), run_time=1.0)
        caption(self, self.HOOK, key="hook")
        problem = mt(self.PROBLEM, self.COLORS)
        fit_into(problem, *self.PROBLEM_X, GRAPH_BOX[3] + 0.1, config.frame_height / 2 - 0.45, center=True)
        self.play(Write(problem), run_time=1.5)
        self.wait(1.0)
        return gr, None, problem

    def intuition(self, gr, label):
        """As IntegralVideo.intuition, with the true integrand behind the rectangles (sampled at
        each midpoint) and thinner edges as they multiply."""
        self._guard_section = "Intuition"
        a, b = self.window()
        caption(self, self.INTUITION, wait=False)
        shown = SimpleNamespace(**vars(gr))
        shown.curve = gr.axes.plot(self.FUNC, x_range=[a, b, (b - a) / 600])
        shown.axes = _ThinEdges(gr.axes)
        # The estimate grows from 0 to 3758.5000 after the readout is fitted, so fit it into a
        # narrower box (same left edge) to leave room for the longer row.
        wide = common._readout
        common._readout = lambda rows, box=READOUT_BOX: wide(rows, box=(box[0], box[1] - 0.5, box[2], box[3]))
        try:
            rects, readout, n, est = riemann_rectangles(self, shown, a, b, self.ANSWER_VALUE, self.COUNTS)
        finally:
            common._readout = wide
        self.wait(1.0)
        clear_caption(self)
        self.play(FadeOut(VGroup(gr.group, readout)), FadeOut(rects), run_time=1.0)
        return est

    def construct(self):
        """As IntegralVideo.construct, but with the close below."""
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
        self.close_exact(current, trail)
        if self._caption_log and self._caption_log[-1][2] is None:
            self._caption_log[-1][2] = _now(self)
        self.write_narration()

    def close_exact(self, current, trail, multiples=4):
        """As common.close, but the rectangle count steps through whole multiples of 2025
        (2025, 4050, 6075, 8100): then every spike is covered by whole strips, and since the
        integrand is linear on each spike, each midpoint sum is exact. A count in between
        (common.close ramps smoothly to 2048) would cut spikes and wobble."""
        self._guard_section = "Close"
        clear_caption(self)
        answer = mt(eq(r"\text{Answer}", "=", *self.ANSWER), self.COLORS).scale(1.3)
        answer.set_color(AREA_COLOR)
        fit_into(answer, SAFE_LEFT, SAFE_RIGHT, 0.4, 2.6, center=True)
        self.play(TransformMatchingTex(current, answer), *trail.fade(), run_time=1.5)
        trail.lines = []
        self.play(Create(SurroundingRectangle(answer, color=AREA_COLOR, buff=0.25)), run_time=0.8)
        mark(self, "answer")
        t = ValueTracker(1)
        a, b = self.window()
        base = self.COUNTS[-1]

        def count():
            return base * int(round(t.get_value()))

        def estimate():
            return midpoint_sum(self.FUNC, a, b, count())

        n_num = Integer(base, font_size=34, group_with_commas=False)
        est = DecimalNumber(estimate(), num_decimal_places=5, font_size=34)
        gap = DecimalNumber(abs(estimate() - self.ANSWER_VALUE), num_decimal_places=5, font_size=34,
                            color=TRAP_COLOR)
        readout = _readout([(r"\text{rectangles}=", n_num), (r"\text{estimate}\approx", est),
                            (r"\text{gap}=", gap)], box=(-3.5, 3.5, CAPTION_TOP + 0.15, -0.1))
        n_num.add_updater(lambda m: _show_value(m, count()))
        est.add_updater(lambda m: _show_value(m, estimate()))
        gap.add_updater(lambda m: _show_value(m, abs(estimate() - self.ANSWER_VALUE)))
        self.play(FadeIn(readout, lag_ratio=0.2), run_time=1.0)
        self.play(t.animate.set_value(multiples), run_time=2.5, rate_func=linear)
        caption(self, self.CLOSE_SAYS[0], key="estimate meets answer")
        caption(self, self.CLOSE_SAYS[1], color=YELLOW)
        self.wait(1.0)
