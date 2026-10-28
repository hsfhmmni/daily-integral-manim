import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import (GRAPH_BOX, SAFE_TOP, IntegralVideo, LIMIT, NEW, _now, add_watermark, build_graph, cap,
                    caption, clear_caption, close, draw_graph, eq, fit_into, install_frame_guard, intro_card,
                    keep_watermark, make_badge, mt, riemann_rectangles)


class _ThinEdges:
    """The graph's axes, but Riemann rectangles get thinner white edges as they multiply, so
    255 of them still show green instead of a solid block of edge lines."""

    def __init__(self, axes):
        self._axes = axes

    def __getattr__(self, name):
        return getattr(self._axes, name)

    def get_riemann_rectangles(self, graph, x_range, dx, **kwargs):
        k = round((x_range[1] - x_range[0]) / dx + 0.5)
        kwargs["stroke_width"] = min(1.0, 16.0 / k)
        return self._axes.get_riemann_rectangles(graph, x_range=x_range, dx=dx, **kwargs)


def _stretched(k):
    """The k-th integrand stretched by sqrt(k): 1 - (sqrt(k) t sin(1/(sqrt(k) t)))^k; its area is the k-th term."""
    def g(t):
        y = np.sqrt(k) * np.where(np.abs(t) < 1e-9, 1e-9, t)
        return 1 - (y * np.sin(1 / y)) ** k
    return g


class HardIntegral(IntegralVideo):
    DIFFICULTY = "Hard"
    DATE = "2026-10-28"

    # x = sqrt(k) t: dx = sqrt(k) dt cancels 1/sqrt(k), and with u = 1/(sqrt(k) t) the base is
    # sin(u)/u = 1 - 1/(6 k t^2) + O(1/k^2), so its k-th power tends to exp(-1/(6 t^2)). The
    # integrands stay below min(2, 1/(6 t^2)) (1 - a^k <= k(1 - a) and 1 - sin(u)/u <= u^2/6 for
    # |u| < pi; |sin(u)/u| <= 1/pi otherwise), so the limit moves inside (dominated convergence).
    # Then 2 int_0^inf (1 - e^{-1/(6t^2)}) dt, s = 1/(sqrt6 t): (2/sqrt6) int_0^inf (1 - e^{-s^2})/s^2 ds,
    # by parts (4/sqrt6) int_0^inf e^{-s^2} ds = (4/sqrt6)(sqrt(pi)/2) = sqrt(2 pi / 3) = 1.447203.
    # The graph is the limit shape in t (the k-th integral is exactly the area under the
    # k-th stretched curve), so its area is the answer.
    @staticmethod
    def FUNC(x):
        x = np.asarray(x, dtype=float)
        return -np.expm1(-1 / (6 * np.maximum(x * x, 1e-300)))

    @classmethod
    def exact_integral(cls):
        return mp.quad(lambda t: 1 - mp.exp(-1 / (6 * t ** 2)), [-mp.inf, -1, 0, 1, mp.inf])

    COLORS = {r"\sqrt{k}\,t\sin\frac{1}{\sqrt{k}\,t}": NEW, r"\,dt": NEW, r"\frac{1-e^{-s^{2}}}{s^{2}}": NEW,
              r"\,ds": NEW}
    LIM = r"\lim_{k\to\infty}"
    PRE = r"\frac{1}{\sqrt{k}}"
    LIMS = (r"\int_{", (r"-\infty", LIMIT), r"}^{", (r"\infty", LIMIT), r"}")
    HALF = (r"\int_{", ("0", LIMIT), r"}^{", (r"\infty", LIMIT), r"}")
    XS = r"x\sin\frac{1}{x}"
    TS = r"\sqrt{k}\,t\sin\frac{1}{\sqrt{k}\,t}"
    G = r"e^{-\frac{1}{6t^{2}}}"
    PROBLEM = eq(LIM, PRE, *LIMS, r"\Big(", "1-", r"\big(", XS, r"\big)^{k}", r"\Big)", r"\,dx")
    CURVE_LABEL = None

    GRAPH = dict(x_range=[-3, 3, 1], y_range=[0, 1.25, 0.25], a=-3, b=3, size=(8.5, 4.2),
                 color_limits=False, var="t",
                 x_labels={-2: "-2", -1: "-1", 1: "1", 2: "2"},
                 y_labels={0.5: "0.5", 1: "1"})
    WIDE = dict(x_range=[-30, 30, 10], y_range=[0, 1.25, 0.25], a=-30, b=30, size=(8.5, 4.2),
                color_limits=False, var="t",
                x_labels={-20: "-20", -10: "-10", 10: "10", 20: "20"},
                y_labels={0.5: "0.5", 1: "1"})
    GHOSTS = (2, 8)                     # finite k, drawn faintly in the hook
    COUNTS = (5, 15, 45, 135, 255)      # odd, so one strip always sits on the spike at 0
    WINDOW = (-30, 30)                  # the tails beyond 30 add about 0.011
    CLOSE_WIDEN = (-3000, 3000)         # and beyond 3000 about 0.00011
    END_COUNT = 65535                   # strips about 0.09 wide over the widened window

    HOOK = cap(r"The power $k$ grows, the factor $\frac{1}{\sqrt{k}}$ shrinks. Who wins?")
    HOOK_NOTE = cap(r"White: $k=2$ and $k=8$, stretched by $\sqrt{k}$. Nearly the limit already.")
    INTUITION = cap(r"Zoomed out: the tails beyond $3$ still hold about $0.11$.")
    INSIGHT = dict(
        parts=[PRE, r"\,dx"],
        label=cap(r"$x=\sqrt{k}\,t$"),
        say=cap(r"Stretch $x$ by $\sqrt{k}$ and the $\frac{1}{\sqrt{k}}$ disappears."),
    )

    STEPS = [
        dict(tex=eq(LIM, *LIMS, r"\Big(", "1-", r"\big(", TS, r"\big)^{k}", r"\Big)", r"\,dt"),
             say=cap(r"Let $x=\sqrt{k}\,t$; $dx=\sqrt{k}\,dt$ cancels the $\frac{1}{\sqrt{k}}$."),
             rule="u_substitution",
             highlight=([r"\,dt"], cap(r"$dx=\sqrt{k}\,dt$")), side=UP),
        dict(tex=eq(r"\big(", TS, r"\big)^{k}", "=", r"\big(", "1", r"-\frac{1}{6kt^{2}}", r"+\cdots",
                    r"\big)^{k}"),
             say=cap(r"With $u=\frac{1}{\sqrt{k}\,t}$ this is $\frac{\sin u}{u}=1-\frac{u^{2}}{6}+\cdots$."),
             rule="maclaurin_series"),
        dict(tex=eq(r"\big(", "1", r"-\frac{1}{6kt^{2}}", r"+\cdots", r"\big)^{k}", r"\to", G),
             say=cap(r"The $k$-th power tends to $e^{a}$, with $a=-\frac{1}{6t^{2}}$."),
             rule="exp_limit"),
        dict(tex=eq(*LIMS, r"\Big(", "1-", G, r"\Big)", r"\,dt"),
             say=cap(r"One bound with finite area lets the limit move inside."),
             rule="dominated_convergence",
             mapping=[cap(r"Here every $f_{k}\le\min\big(2,\frac{1}{6t^{2}}\big)$, a finite area.")]),
        dict(tex=eq("2", *HALF, r"\Big(", "1-", G, r"\Big)", r"\,dt"),
             say=cap(r"The integrand is even in $t$: take twice the right half."),
             rule="odd_even_symmetry"),
        dict(tex=eq(r"\frac{2}{\sqrt{6}}", *HALF, r"\frac{1-e^{-s^{2}}}{s^{2}}", r"\,ds"),
             say=cap(r"Let $s=\frac{1}{\sqrt{6}\,t}$: the ends swap; the minus sign swaps them back."),
             rule=["u_substitution", "change_of_limits", "reversing_limits"],
             highlight=([r"\,ds"], cap(r"$dt=-\frac{ds}{\sqrt{6}\,s^{2}}$")), side=UP),
        dict(tex=eq(r"\frac{2}{\sqrt{6}}", r"\Big(", r"\Big[-\frac{1-e^{-s^{2}}}{s}\Big]_{0}^{\infty}", "+",
                    *HALF, r"\frac{2se^{-s^{2}}}{s}", r"\,ds", r"\Big)"),
             say=cap(r"By parts with $v=-\frac{1}{s}$; the chain rule gives $2se^{-s^{2}}$."),
             rule=["integration_by_parts", "chain_rule", "exp_derivative"]),
        dict(tex=eq(r"\frac{4}{\sqrt{6}}", *HALF, r"e^{-s^{2}}", r"\,ds"),
             say=cap(r"The bracket is $0$ at both ends, and the $s$ cancels."),
             rule="linearity"),
        dict(tex=eq(r"\frac{4}{\sqrt{6}}", r"\cdot", r"\frac{\sqrt{\pi}}{2}"),
             say=cap(r"Half a bell curve: $\int_{0}^{\infty}e^{-s^{2}}\,ds=\frac{\sqrt{\pi}}{2}$."),
             rule="gaussian_integral",
             mapping=[cap(r"Here only the right half, so $\frac{\sqrt{\pi}}{2}$.")]),
        dict(tex=eq(r"\sqrt{\frac{2\pi}{3}}"),
             say=cap(r"$\frac{2\sqrt{\pi}}{\sqrt{6}}=\sqrt{\frac{4\pi}{6}}=\sqrt{\frac{2\pi}{3}}$."),
             rule="algebra"),
    ]

    ANSWER = eq(r"\sqrt{\frac{2\pi}{3}}")
    ANSWER_VALUE = float(mp.sqrt(2 * mp.pi / 3))
    CLOSE_SAYS = (cap(r"Wider, thinner rectangles close in on $1.4472$."),
                  cap(r"Takeaway: rescale until the limit has a shape, then integrate it."))

    def hook(self):
        """As IntegralVideo.hook, but after the question two finite-k integrands, stretched the
        same way, are drawn faintly over the limit shape: the picture is what the problem tends to."""
        self._guard_section = "Hook"
        gr = build_graph(self.GRAPH, self.FUNC)
        draw_graph(self, gr, None)
        caption(self, self.HOOK, key="hook")
        ghosts = VGroup(*[gr.axes.plot(_stretched(k), x_range=[-3, 3, 0.001], color=WHITE, stroke_width=2.5,
                                       stroke_opacity=0.85) for k in self.GHOSTS])
        self.play(Create(ghosts), run_time=1.5)
        caption(self, self.HOOK_NOTE)
        self.play(FadeOut(ghosts), run_time=0.8)
        problem = mt(self.PROBLEM, self.COLORS)
        fit_into(problem, *self.PROBLEM_X, GRAPH_BOX[3] + 0.1, SAFE_TOP - 0.05, center=True)
        self.play(Write(problem), run_time=1.5)
        self.wait(1.0)
        return gr, None, problem

    def intuition(self, gr, label):
        """As IntegralVideo.intuition, but first the picture zooms out from [-3, 3] to [-30, 30]
        (the tails are too long for the hook's graph), and the rectangles get thinner edges."""
        self._guard_section = "Intuition"
        a, b = self.window()
        wide = build_graph(self.WIDE, self.FUNC)
        self.play(ReplacementTransform(gr.group, wide.group), run_time=1.5)
        caption(self, self.INTUITION, wait=False)
        shown = SimpleNamespace(**vars(wide))
        shown.axes = _ThinEdges(wide.axes)
        rects, readout, n, est = riemann_rectangles(self, shown, a, b, self.ANSWER_VALUE, self.COUNTS)
        self.wait(1.0)
        clear_caption(self)
        self.play(FadeOut(VGroup(wide.group, readout)), FadeOut(rects), run_time=1.0)
        return est

    def construct(self):
        """As IntegralVideo.construct, but the close ends on END_COUNT rectangles over the widened
        window: the tails fall like 1/(6t^2), so 2048 rectangles on [-3000, 3000] miss the spike."""
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
