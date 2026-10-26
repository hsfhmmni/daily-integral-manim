import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
from common import (IntegralVideo, LIMIT, NEW, build_graph, cap, caption, clear_caption, eq, riemann_rectangles)


class _ThinEdges:
    """The graph's axes, but Riemann rectangles get thinner white edges as they multiply, so
    the strips still show green instead of a solid block of edge lines."""

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
    DATE = "2026-10-25"

    # x = tan(theta), then times cos^2: the log of (3 + 2cos 2t + 2sin 2t)/(3 + 2cos 2t - 2sin 2t); t = 2 theta and
    # 2cos t +- 2sin t = 2 sqrt2 cos(t -+ pi/4). With 3 + 2 sqrt2 cos psi = 2(1 + 2r cos psi + r^2), r = 1/sqrt2, the
    # Fourier series of the log and int_0^pi t sin nt dt = (-1)^(n+1) pi/n give pi sum r^n sin(n pi/4)/n^2
    # = pi Im Li2((1+i)/2). Landen with z/(z-1) = -i: Im Li2((1+i)/2) = G - (pi/8) ln 2.
    @staticmethod
    def FUNC(x):
        x = np.asarray(x, dtype=float)
        return (np.log(x ** 2 + 4 * x + 5) - np.log(x ** 2 - 4 * x + 5)) * np.arctan(x) / (x ** 2 + 1)

    @classmethod
    def exact_integral(cls):
        f = lambda x: (mp.log(x ** 2 + 4 * x + 5) - mp.log(x ** 2 - 4 * x + 5)) * mp.atan(x) / (x ** 2 + 1)  # noqa: E731
        return mp.quad(f, [0, 1, 2, 4, 10, mp.inf])

    COLORS = {r"\theta": NEW, r"\,d\theta": NEW, "t": NEW, r"\,dt": NEW}
    LIMS = (r"\int_{", ("0", LIMIT), r"}^{", (r"\infty", LIMIT), r"}")
    TH = (r"\int_{", ("0", LIMIT), r"}^{", (r"\frac{\pi}{2}", LIMIT), r"}")
    PI_ = (r"\int_{", ("0", LIMIT), r"}^{", (r"\pi", LIMIT), r"}")
    LOGS = r"\big(\ln(x^{2}+4x+5)-\ln(x^{2}-4x+5)\big)"
    ATAN = r"\tan^{-1}x"
    DEN = r"x^{2}+1"
    PROBLEM = eq(*LIMS, r"\frac{", ATAN, r"}{", DEN, r"}", LOGS, r"\,dx")
    PROBLEM_X = (-5.6, 3.3)     # a long line: give it room, clear of the badge
    CURVE_LABEL = None          # the integrand is too long to sit beside the curve

    GRAPH = dict(x_range=[0, 8, 1], y_range=[0, 0.8, 0.2], a=0, b=8, size=(8, 4.2), color_limits=False,
                 x_labels={2: "2", 4: "4", 6: "6", 8: "8"},
                 y_labels={0.4: "0.4", 0.8: "0.8"})
    WIDE = dict(x_range=[0, 30, 5], y_range=[0, 0.8, 0.2], a=0, b=30, size=(8, 4.2), color_limits=False,
                x_labels={10: "10", 20: "20", 30: "30"},
                y_labels={0.4: "0.4", 0.8: "0.8"})
    WINDOW = (0, 30)            # the tail beyond 30 adds about 0.007
    CLOSE_WIDEN = (0, 400)      # and beyond 400 about 0.00004
    COUNTS = (8, 16, 32, 64, 128)

    HOOK = cap(r"Two logs and $\tan^{-1}x$ over an endless tail. Exact area?")
    INTUITION = cap(r"Zoomed out: the tail beyond $30$ adds under $0.01$.")
    INSIGHT = dict(
        parts=[ATAN, DEN],
        label=cap(r"$\theta\,d\theta$"),
        say=cap(r"With $x=\tan\theta$, the $\tan^{-1}x$ and $x^{2}+1$ become $\theta\,d\theta$."),
    )

    STEPS = [
        dict(tex=eq(*TH, r"\theta", r"\ln\frac{\tan^{2}\theta+4\tan\theta+5}{\tan^{2}\theta-4\tan\theta+5}", r"\,d\theta"),
             say=cap(r"Let $x=\tan\theta$: $\frac{dx}{x^{2}+1}=d\theta$, and $\infty$ becomes $\frac{\pi}{2}$."),
             rule=["tan_substitution", "change_of_limits", "improper_integral", "log_laws"]),
        dict(tex=eq(*TH, r"\theta", r"\ln\frac{3+2\cos 2\theta+2\sin 2\theta}{3+2\cos 2\theta-2\sin 2\theta}", r"\,d\theta"),
             say=cap(r"Times $\cos^{2}\theta$: $\sin^{2}\theta+5\cos^{2}\theta=3+2\cos 2\theta$."),
             rule=["double_angle", "pythagorean_identity"]),
        dict(tex=eq(r"\frac{1}{4}", *PI_, "t",
                    r"\ln\frac{3+2\sqrt{2}\cos(t-\frac{\pi}{4})}{3+2\sqrt{2}\cos(t+\frac{\pi}{4})}", r"\,dt"),
             say=cap(r"Let $t=2\theta$; then $2\cos t\pm 2\sin t=2\sqrt{2}\cos(t\mp\frac{\pi}{4})$."),
             rule=["u_substitution", "change_of_limits", "compound_angle"]),
        dict(tex=eq(r"\frac{1}{2}", *PI_, "t",
                    r"\sum_{n=1}^{\infty}\frac{(-1)^{n+1}}{n\,2^{n/2}}"
                    r"\Big(\cos(nt-\tfrac{n\pi}{4})-\cos(nt+\tfrac{n\pi}{4})\Big)", r"\,dt"),
             say=cap(r"Expand each logarithm as a cosine series; the $\ln 2$ terms cancel."),
             rule=["log_cosine_series", "log_laws"],
             mapping={"log_cosine_series": [cap(r"Here $3+2\sqrt{2}\cos\psi=2(1+2r\cos\psi+r^{2})$, $r=\frac{1}{\sqrt{2}}$.")]}),
        dict(tex=eq(*PI_, "t", r"\sum_{n=1}^{\infty}\frac{(-1)^{n+1}\sin\frac{n\pi}{4}}{n\,2^{n/2}}\sin nt", r"\,dt"),
             say=cap(r"$\cos(A-B)-\cos(A+B)=2\sin A\sin B$, with $A=nt$, $B=\frac{n\pi}{4}$."),
             rule="compound_angle"),
        dict(tex=eq(r"\pi", r"\sum_{n=1}^{\infty}\frac{\sin\frac{n\pi}{4}}{n^{2}\,2^{n/2}}"),
             say=cap(r"Swap, then by parts: $\int_{0}^{\pi}t\sin nt\,dt=\frac{(-1)^{n+1}\pi}{n}$."),
             rule=["swap_order", "integration_by_parts"],
             mapping={"swap_order": [cap(r"A sum over $n$ is an integral too; $\sum\frac{1}{n2^{n/2}}$ converges.")]}),
        dict(tex=eq(r"\pi", r"\,\mathrm{Im}\,", r"\mathrm{Li}_{2}\Big(\frac{1+i}{2}\Big)"),
             say=cap(r"$\frac{\sin\frac{n\pi}{4}}{2^{n/2}}$ is the imaginary part of $\big(\frac{1+i}{2}\big)^{n}$."),
             rule=["euler_formula", "dilogarithm"],
             mapping={"dilogarithm": [cap(r"Here $z=\frac{1+i}{2}$, so $z^{n}=2^{-n/2}e^{in\pi/4}$.")]}),
        dict(tex=eq(r"\pi", r"\,\mathrm{Im}\,", r"\Big(-\mathrm{Li}_{2}(-i)-\frac{1}{2}\ln^{2}\frac{1-i}{2}\Big)"),
             say=cap(r"Landen's identity: $\frac{z}{z-1}=-i$ and $1-z=\frac{1-i}{2}$."),
             rule="dilogarithm"),
        dict(tex=eq(r"\pi G", "-", r"\frac{\pi^{2}}{8}\ln 2"),
             say=cap(r"$\ln\frac{1-i}{2}=-\frac{1}{2}\ln 2-\frac{i\pi}{4}$; keep the imaginary parts."),
             rule=["catalan_constant", "euler_formula", "log_laws"],
             mapping={"catalan_constant": [cap(r"$\mathrm{Im}\,\mathrm{Li}_{2}(-i)=-1+\frac{1}{9}-\frac{1}{25}+\cdots=-G$.")]}),
    ]

    CONSTANTS = {"G": "catalan"}    # verify.py reads G as Catalan's constant (its value from sympy)
    ANSWER = eq(r"\pi G", "-", r"\frac{\pi^{2}}{8}\ln 2")
    ANSWER_VALUE = float(mp.pi * mp.catalan - mp.pi ** 2 / 8 * mp.log(2))
    CLOSE_SAYS = (cap(r"Wider, thinner rectangles close in on $2.0225$."),
                  cap(r"Takeaway: a logarithm of cosines has a Fourier series; sum it."))

    def intuition(self, gr, label):
        """As IntegralVideo.intuition, but first the picture zooms out from [0, 8] to [0, 30]
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
