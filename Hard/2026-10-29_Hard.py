import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import (IntegralVideo, LIMIT, NEW, build_graph, cap, caption, clear_caption, eq, new_style,
                    riemann_rectangles, to_thumbnail)


class _ThinEdges:
    """The graph's axes, but Riemann rectangles get thinner white edges as they multiply, so
    2048 of them still show green instead of a solid block of edge lines."""

    def __init__(self, axes):
        self._axes = axes

    def __getattr__(self, name):
        return getattr(self._axes, name)

    def get_riemann_rectangles(self, graph, x_range, dx, **kwargs):
        k = round((x_range[1] - x_range[0]) / dx + 0.5)
        kwargs["stroke_width"] = min(1.0, 16.0 / k)
        return self._axes.get_riemann_rectangles(graph, x_range=x_range, dx=dx, **kwargs)


class HardIntegral(IntegralVideo):
    DIFFICULTY = "Hard"
    DATE = "2026-10-29"

    # t -> 1/t keeps (1+t^2)/(1+t)^4 dt and (1+t)/sqrt(1+t^2), and turns atan(t^2026) into
    # pi/2 - atan(t^2026); adding, I = (pi/4) int_0^inf (1+t^2)/(1+t)^4 atan((1+t)/sqrt(1+t^2)) dt.
    # y = (t-1)/(t+1): the weight becomes (1+y^2)/4 dy and the last factor atan(sqrt2/sqrt(1+y^2)),
    # on y from -1 to 1 (even), so I = (pi/8) int_0^1 (1+y^2) atan(sqrt2/sqrt(1+y^2)) dy. By parts
    # with v = y + y^3/3: (pi/8)(pi/3 + (sqrt2/3) int_0^1 y^2/sqrt(1+y^2) dy), and with y = sinh w
    # that integral is (sqrt2 - ln(1+sqrt2))/2. So I = pi(pi+1)/24 - sqrt2 pi ln(1+sqrt2)/48 = 0.460553.
    # The graph: atan(t^2026) is 0 below t = 1 and pi/2 above, so the curve switches on at t = 1.
    @staticmethod
    def FUNC(x):
        t = np.maximum(np.asarray(x, dtype=float), 1e-300)
        a = np.arctan(np.exp(np.clip(2026 * np.log(t), -745, 709)))
        return (1 + t * t) / (1 + t) ** 4 * a * np.arctan((1 + t) / np.sqrt(1 + t * t))

    @classmethod
    def exact_integral(cls):
        f = lambda t: (1 + t ** 2) / (1 + t) ** 4 * mp.atan(t ** 2026) * mp.atan((1 + t) / mp.sqrt(1 + t ** 2))
        return mp.quad(f, [0, mp.mpf("0.99"), 1, mp.mpf("1.01"), 2, mp.inf])

    COLORS = {r"\,du": NEW, r"\frac{1+u^{2}}{(1+u)^{4}}\,du": NEW, r"\frac{u+1}{\sqrt{u^{2}+1}}": NEW,
              r"\,dy": NEW, r"\,dw": NEW}
    LIMS = (r"\int_{", ("0", LIMIT), r"}^{", (r"\infty", LIMIT), r"}")
    LIMY = (r"\int_{", ("0", LIMIT), r"}^{", ("1", LIMIT), r"}")
    W = r"\frac{1+t^{2}}{(1+t)^{4}}"
    A = r"\tan^{-1}(t^{2026})"
    B = r"\tan^{-1}\left(\frac{1+t}{\sqrt{1+t^{2}}}\right)"
    ATY = r"\tan^{-1}\sqrt{\tfrac{2}{1+y^{2}}}"
    Y2 = r"\frac{y^{2}}{\sqrt{1+y^{2}}}"
    PROBLEM = eq(*LIMS, W, A, B, r"\,dt")
    CURVE_LABEL = None

    GRAPH = dict(x_range=[0, 5, 1], y_range=[0, 0.2, 0.05], a=0, b=5, size=(8.5, 4.2),
                 color_limits=False, var="t",
                 x_labels={1: "1", 2: "2", 3: "3", 4: "4", 5: "5"},
                 y_labels={0.1: "0.1", 0.2: "0.2"})
    WIDE = dict(x_range=[0, 512, 128], y_range=[0, 0.2, 0.05], a=0, b=512, size=(8.5, 4.2),
                color_limits=False, var="t",
                x_labels={128: "128", 256: "256", 384: "384", 512: "512"},
                y_labels={0.1: "0.1", 0.2: "0.2"})
    COUNTS = (8, 32, 128, 512, 2048)    # 2048 strips of width 1/4, so t = 1 is a strip edge
    WINDOW = (0, 512)                   # the tail beyond 512 adds about 0.0024
    CLOSE_WIDEN = (0, 4096)
    END_COUNT = 32768

    HOOK = cap(r"Why does the curve switch on at exactly $t=1$?")
    INTUITION = cap(r"Zoomed out to $512$: a thin tail holds $40\%$ of the area.")
    INSIGHT = dict(
        parts=[A],
        label=cap(r"$0$ below $t=1$, $\frac{\pi}{2}$ above"),
        say=cap(r"We want the $2026$ gone. Flipping $t$ to $\frac{1}{t}$ nearly does it."),
    )

    STEPS = [
        dict(tex=eq(r"\frac{1+t^{2}}{(1+t)^{4}}\,dt", "=", r"\frac{1+u^{-2}}{(1+u^{-1})^{4}}\,\frac{du}{u^{2}}", "=",
                    r"\frac{1+u^{2}}{(1+u)^{4}}\,du"),
             say=cap(r"Try $t=\frac{1}{u}$ on the weight: it comes back unchanged."),
             rule="u_substitution",
             highlight=([r"\frac{1+u^{2}}{(1+u)^{4}}\,du"], cap(r"same weight")), side=DOWN),
        dict(tex=eq(r"\frac{1+\frac{1}{u}}{\sqrt{1+\frac{1}{u^{2}}}}", "=", r"\frac{u+1}{\sqrt{u^{2}+1}}"),
             say=cap(r"Times $u$ on top and bottom: the last factor is unchanged too."),
             rule="algebra"),
        dict(tex=eq(*LIMS, W, r"\tan^{-1}(t^{-2026})", B, r"\,dt"),
             say=cap(r"The limits swap, the minus swaps them back; rename $u$ as $t$."),
             rule=["change_of_limits", "reversing_limits"]),
        dict(tex=eq(*LIMS, W, r"\Big(\frac{\pi}{2}-\tan^{-1}(t^{2026})\Big)", B, r"\,dt"),
             say=cap(r"For $a>0$, $\tan^{-1}\frac{1}{a}=\frac{\pi}{2}-\tan^{-1}a$."),
             rule="arctan_reciprocal"),
        dict(tex=eq("I", "=", r"\frac{\pi}{4}", *LIMS, W, B, r"\,dt"),
             say=cap(r"Add this to $I$ and halve: the $2026$ is gone."),
             rule="linearity"),
        dict(tex=eq(r"1+t=\frac{2}{1-y}", r",\quad", r"1+t^{2}=\frac{2(1+y^{2})}{(1-y)^{2}}", r",\quad",
                    r"dt=\frac{2\,dy}{(1-y)^{2}}"),
             say=cap(r"Now let $y=\frac{t-1}{t+1}$, so $t=\frac{1+y}{1-y}$."),
             rule="u_substitution"),
        dict(tex=eq("I", "=", r"\frac{\pi}{4}", r"\int_{", ("-1", LIMIT), r"}^{", ("1", LIMIT), r"}",
                    r"\frac{1+y^{2}}{4}", ATY, r"\,dy"),
             say=cap(r"Weight $\frac{1+y^{2}}{4}$; limits $0$ to $\infty$ become $-1$ to $1$."),
             rule="change_of_limits"),
        dict(tex=eq("I", "=", r"\frac{\pi}{8}", *LIMY, r"(1+y^{2})", ATY, r"\,dy"),
             say=cap(r"Even in $y$: twice the half from $0$ to $1$."),
             rule="odd_even_symmetry"),
        dict(tex=eq("I", "=", r"\frac{\pi}{8}", r"\Big(", r"\Big[\big(y+\tfrac{y^{3}}{3}\big)" + ATY + r"\Big]_{0}^{1}",
                    "+", r"\frac{\sqrt{2}}{3}", *LIMY, Y2, r"\,dy", r"\Big)"),
             say=cap(r"By parts with $v=y+\frac{y^{3}}{3}$: $3+y^{2}$ cancels top and bottom."),
             rule=["integration_by_parts", "arctan_derivative", "chain_rule"]),
        dict(tex=eq("I", "=", r"\frac{\pi}{8}", r"\Big(", r"\frac{\pi}{3}", "+", r"\frac{\sqrt{2}}{3}", *LIMY, Y2,
                    r"\,dy", r"\Big)"),
             say=cap(r"At $1$ the bracket is $\frac{4}{3}\cdot\frac{\pi}{4}=\frac{\pi}{3}$; at $0$ it is $0$."),
             rule="algebra"),
        dict(tex=eq("I", "=", r"\frac{\pi}{8}", r"\Big(", r"\frac{\pi}{3}", "+", r"\frac{\sqrt{2}}{3}",
                    r"\int_{0}^{\sinh^{-1}1}", r"\sinh^{2}w", r"\,dw", r"\Big)"),
             say=cap(r"Let $y=\sinh w$: $\sqrt{1+y^{2}}=\cosh w$ cancels $dy=\cosh w\,dw$."),
             rule=["u_substitution", "hyperbolic_identity"]),
        dict(tex=eq("I", "=", r"\frac{\pi}{8}", r"\Big(", r"\frac{\pi}{3}", "+", r"\frac{\sqrt{2}}{3}",
                    r"\Big[\frac{\sinh w\cosh w-w}{2}\Big]_{0}^{\sinh^{-1}1}", r"\Big)"),
             say=cap(r"$\sinh^{2}w=\frac{\cosh 2w-1}{2}$ integrates to $\frac{\sinh 2w}{4}-\frac{w}{2}$."),
             rule=["hyperbolic_double_angle", "ftc"]),
        dict(tex=eq("I", "=", r"\frac{\pi}{8}", r"\Big(", r"\frac{\pi}{3}", "+", r"\frac{\sqrt{2}}{3}",
                    r"\cdot\frac{\sqrt{2}-\ln(1+\sqrt{2})}{2}", r"\Big)"),
             say=cap(r"At the top $\sinh w=1$, $\cosh w=\sqrt{2}$, $w=\ln(1+\sqrt{2})$."),
             rule="arsinh_log"),
        dict(tex=eq("I", "=", r"\frac{\pi}{8}", r"\Big(", r"\frac{\pi}{3}", "+", r"\frac{1}{3}", "-",
                    r"\frac{\sqrt{2}}{6}\ln(1+\sqrt{2})", r"\Big)"),
             say=cap(r"Put it back: $\frac{\sqrt{2}}{3}\cdot\frac{\sqrt{2}}{2}=\frac{1}{3}$."),
             rule="algebra"),
        dict(tex=eq("I", "=", r"\frac{\pi(\pi+1)}{24}", "-", r"\frac{\sqrt{2}\,\pi}{48}\ln(1+\sqrt{2})"),
             say=cap(r"Multiply out the $\frac{\pi}{8}$."),
             rule="algebra"),
    ]

    ANSWER = eq(r"\frac{\pi(\pi+1)}{24}", "-", r"\frac{\sqrt{2}\,\pi}{48}\ln(1+\sqrt{2})")
    ANSWER_VALUE = float(mp.pi * (mp.pi + 1) / 24 - mp.sqrt(2) * mp.pi * mp.log(1 + mp.sqrt(2)) / 48)
    CLOSE_SAYS = (cap(r"Wider, thinner rectangles close in on $0.4606$."),
                  cap(r"At $t=1$ the factor switches on; $t\to\frac{1}{t}$ averages it to $\frac{\pi}{4}$."))

    def intuition(self, gr, label):
        """As IntegralVideo.intuition, but the picture first zooms out from [0, 5] to [0, 512]
        (40% of the area is in the tail), the rectangles get thinner edges, and the hook's
        graph comes back before it becomes the thumbnail."""
        self._guard_section = "Intuition"
        a, b = self.window()
        wide = build_graph(self.WIDE, self.FUNC)
        hook_copy = gr.group.copy()
        self.play(ReplacementTransform(gr.group, wide.group), run_time=1.5)
        caption(self, self.INTUITION, wait=False)
        shown = SimpleNamespace(**vars(wide))
        shown.axes = _ThinEdges(wide.axes)
        rects, readout, n, est = riemann_rectangles(self, shown, a, b, self.ANSWER_VALUE, self.COUNTS)
        self.wait(1.0)
        clear_caption(self)
        if new_style(self, "thumbnail"):
            self.play(FadeOut(rects), FadeOut(readout), ReplacementTransform(wide.group, hook_copy), run_time=1.2)
            back = build_graph(self.GRAPH, self.FUNC)
            self.remove(hook_copy)
            self.add(back.group)
            to_thumbnail(self, back)
        else:
            self.play(FadeOut(VGroup(wide.group, readout)), FadeOut(rects), run_time=1.0)
        return est
