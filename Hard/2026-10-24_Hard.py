import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import (IntegralVideo, LIMIT, NEW, _now, add_watermark, build_graph, cap, caption, clear_caption,
                    close, eq, install_frame_guard, intro_card, keep_watermark, make_badge, riemann_rectangles)


class _ThinEdges:
    """The graph's axes, but Riemann rectangles get thinner white edges as they multiply, so
    1250 of them still show green instead of a solid block of edge lines."""

    def __init__(self, axes):
        self._axes = axes

    def __getattr__(self, name):
        return getattr(self._axes, name)

    def get_riemann_rectangles(self, graph, x_range, dx, **kwargs):
        k = round((x_range[1] - x_range[0]) / dx + 0.5)
        kwargs["stroke_width"] = min(1.0, 16.0 / k)
        return self._axes.get_riemann_rectangles(graph, x_range=x_range, dx=dx, **kwargs)


def _tanhc_pair(x):
    """tanhc(x) tanhc(2x) = tanh(x) tanh(2x) / (2x^2), with its limit 1 at x = 0."""
    x = np.asarray(x, dtype=float)
    safe = np.where(np.abs(x) < 1e-6, 1.0, x)
    return np.where(np.abs(x) < 1e-6, 1.0, np.tanh(safe) * np.tanh(2 * safe) / (2 * safe ** 2))


class HardIntegral(IntegralVideo):
    DIFFICULTY = "Hard"
    DATE = "2026-10-24"

    # tanh x tanh 2x = 2 sinh^2 x / cosh 2x = 1 - sech 2x, and t = 2x gives J = int_0^inf (1 - sech t)/t^2 dt.
    # sech t = int_0^inf sech(pi w/2) cos(w t) dw (sech is self-dual under the Fourier transform), so
    # 1 - sech t = int_0^inf sech(pi w/2)(1 - cos w t) dw; swap (all positive), int_0^inf (1 - cos w t)/t^2 dt
    # = pi w/2, then v = pi w/2: J = (2/pi) int_0^inf v sech v dv = (2/pi)(2G) = 4G/pi.
    @staticmethod
    def FUNC(x):
        return _tanhc_pair(x)

    @classmethod
    def exact_integral(cls):
        f = lambda x: mp.tanh(x) * mp.tanh(2 * x) / (2 * x ** 2) if x != 0 else mp.mpf(1)     # noqa: E731
        return mp.quad(f, [0, 1, mp.inf])

    COLORS = {r"t^{2}": NEW, r"\,dt": NEW, r"1-\operatorname{sech}t": NEW, "v": NEW, r"\operatorname{sech}v": NEW,
              r"\,dv": NEW}
    LIMS = (r"\int_{", ("0", LIMIT), r"}^{", (r"\infty", LIMIT), r"}")
    TC1 = r"\operatorname{tanhc}(x)"
    TC2 = r"\operatorname{tanhc}(2x)"
    SW = r"\operatorname{sech}\frac{\pi\omega}{2}"
    PROBLEM = eq(*LIMS, TC1, TC2, r"\,dx")
    CURVE_LABEL = eq("y", "=", TC1, TC2)
    LABEL_AT = (1.4, 0.55)      # empty space above the falling curve (y is about 0.25 at x = 1.4)

    GRAPH = dict(x_range=[0, 6, 1], y_range=[0, 1.25, 0.25], a=0, b=6, size=(8, 4.2), color_limits=False,
                 x_labels={1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6"},
                 y_labels={0.5: "0.5", 1: "1"})
    WIDE = dict(x_range=[0, 50, 10], y_range=[0, 1.25, 0.25], a=0, b=50, size=(8, 4.2), color_limits=False,
                x_labels={10: "10", 20: "20", 30: "30", 40: "40", 50: "50"},
                y_labels={0.5: "0.5", 1: "1"})
    WINDOW = (0, 50)            # the tail beyond 50 adds about 0.01
    CLOSE_WIDEN = (0, 10000)    # and beyond 10000 about 0.00005
    END_COUNT = 65536           # strips about 0.15 wide over the widened window
    COUNTS = (5, 25, 125, 625, 1250)

    HOOK = cap(r"$\operatorname{tanhc}(x)=\frac{\tanh x}{x}$. Is this endless area exact?")
    INTUITION = cap(r"Zoomed out: the thin tail beyond $50$ still adds about $0.01$.")
    INSIGHT = dict(
        parts=[TC1, TC2],
        label=cap(r"$\dfrac{1-\operatorname{sech}2x}{2x^{2}}$"),
        say=cap(r"The two $\tanh$ factors merge into a single $\operatorname{sech}$."),
    )

    STEPS = [
        dict(tex=eq(*LIMS, r"\frac{", r"1-\operatorname{sech}2x", r"}{", r"2x^{2}", r"}", r"\,dx"),
             say=cap(r"Unfold $\operatorname{tanhc}$; then $\tanh x\tanh 2x=\frac{2\sinh^{2}x}{\cosh 2x}=1-\operatorname{sech}2x$."),
             rule="hyperbolic_double_angle"),
        dict(tex=eq(*LIMS, r"\frac{", r"1-\operatorname{sech}t", r"}{", r"t^{2}", r"}", r"\,dt"),
             say=cap(r"Let $t=2x$: then $\frac{dx}{2x^{2}}=\frac{dt}{t^{2}}$, and the limits stay."),
             rule=["u_substitution", "change_of_limits"]),
        dict(tex=eq(*LIMS, r"\frac{1}{t^{2}}", *LIMS, SW, r"(1-\cos\omega t)", r"\,d\omega", r"\,dt"),
             say=cap(r"Write $\operatorname{sech}t$ as a blend of cosine waves $\cos\omega t$."),
             rule="sech_cosine_transform",
             mapping=[cap(r"At $t=0$ it gives $1$; subtract to get $1-\cos\omega t$.")]),
        dict(tex=eq(*LIMS, SW, *LIMS, r"\frac{", r"1-\cos\omega t", r"}{", r"t^{2}", r"}", r"\,dt", r"\,d\omega"),
             say=cap(r"Everything is positive, so swap the order."),
             rule="swap_order",
             mapping=[cap(r"Here $f=\operatorname{sech}\frac{\pi\omega}{2}\cdot\frac{1-\cos\omega t}{t^{2}}\ge 0$.")]),
        dict(tex=eq(*LIMS, SW, r"\cdot", r"\frac{\pi\omega}{2}", r"\,d\omega"),
             say=cap(r"The inner integral is just $\frac{\pi\omega}{2}$."),
             rule=["one_minus_cos_integral", "improper_integral"],
             mapping={"one_minus_cos_integral": [cap(r"Here $a=\omega\ge 0$, so the inner integral is $\frac{\pi\omega}{2}$.")]}),
        dict(tex=eq(r"\frac{2}{\pi}", *LIMS, "v", r"\operatorname{sech}v", r"\,dv"),
             say=cap(r"Let $v=\frac{\pi\omega}{2}$, so $d\omega=\frac{2}{\pi}\,dv$."),
             rule="u_substitution"),
        dict(tex=eq(r"\frac{2}{\pi}", *LIMS, "v", r"\cdot 2\sum_{n=0}^{\infty}(-1)^{n}e^{-(2n+1)v}", r"\,dv"),
             say=cap(r"$\operatorname{sech}v=\frac{2e^{-v}}{1+e^{-2v}}$: a geometric series in $-e^{-2v}$."),
             rule="geometric_series"),
        dict(tex=eq(r"\frac{4}{\pi}", r"\sum_{n=0}^{\infty}\frac{(-1)^{n}}{(2n+1)^{2}}"),
             say=cap(r"Each term: $\int_{0}^{\infty}ve^{-kv}\,dv=\frac{1}{k^{2}}$, with $k=2n+1$."),
             rule=["swap_order", "integration_by_parts", "linearity"]),
        dict(tex=eq(r"\frac{4G}{\pi}"),
             say=cap(r"So the answer is $\frac{4G}{\pi}$."),
             rule="catalan_constant",
             mapping=[cap(r"Our sum is exactly $G$, about $0.9160$.")]),
    ]

    CONSTANTS = {"G": "catalan"}    # verify.py reads G as Catalan's constant (its value from sympy)
    ANSWER = eq(r"\frac{4G}{\pi}")
    ANSWER_VALUE = float(4 * mp.catalan / mp.pi)
    CLOSE_SAYS = (cap(r"Wider, thinner rectangles close in on $1.1662$."),
                  cap(r"Takeaway: write a function as a blend of waves, then swap."))

    def intuition(self, gr, label):
        """As IntegralVideo.intuition, but first the picture zooms out from [0, 6] to [0, 50]
        (the tail is too long for the hook's graph), and the rectangles get thinner edges."""
        self._guard_section = "Intuition"
        a, b = self.window()
        if label is not None:
            self.play(FadeOut(label), run_time=0.5)
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
        window: the tail falls like 1/(2x^2), so 2048 rectangles on [0, 400] stop 0.00125 short."""
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
