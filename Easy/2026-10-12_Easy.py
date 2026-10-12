import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath as mp
import numpy as np
from manim import *
import common
from common import AREA_COLOR, CURVE_COLOR, IntegralVideo, LIMIT, NEW, cap, caption, clear_caption, eq, mark


def y(x):
    """The curve that is spun: y = e^{-x} cos x."""
    return np.exp(-x) * np.cos(x)


class EasyIntegral(IntegralVideo):
    DIFFICULTY = "Easy"
    DATE = "2026-10-12"

    @staticmethod
    def FUNC(x):
        """The area of the disc at x: pi y^2."""
        return np.pi * np.exp(-2 * x) * np.cos(x) ** 2

    @classmethod
    def exact_integral(cls):
        return mp.pi * mp.quad(lambda x: mp.exp(-2 * x) * mp.cos(x) ** 2, [0, mp.inf])

    COLORS = {"I": NEW}
    LIMS = (r"\int_{", ("0", LIMIT), r"}^{", (r"\infty", LIMIT), r"}")
    PROBLEM = eq("V", "=", r"\pi", *LIMS, r"y^{2}", r"\,dx")
    CURVE_LABEL = eq("A", "=", r"\pi", r"y^{2}")
    LABEL_AT = (1.0, 1.6)       # empty space above the curve, which is below 0.4 for x > 1

    GRAPH = dict(x_range=[0, 3.5, 0.5], y_range=[0, 3.5, 1], a=0, b=3.5, size=(8, 4.2),
                 x_labels={1: "1", np.pi / 2: r"\frac{\pi}{2}", 2: "2", 3: "3"},
                 y_labels={1: "1", 2: "2", 3: "3"})
    WINDOW = (0, 3.5)           # the tail beyond 3.5 adds less than 0.001
    CLOSE_WIDEN = (0, 8)

    HOOK = cap(r"Plot each disc's area $\pi y^{2}$: the volume becomes an area.")
    INTUITION = cap(r"Thin rectangles estimate the area; watch the gap shrink.")
    INSIGHT = dict(
        parts=[r"y^{2}"],
        label=cap(r"$y^{2}=e^{-2x}\cos^{2}x$"),
        say=cap(r"Squaring makes $\cos^{2}x$; a double angle will flatten it."),
    )

    STEPS = [
        dict(tex=eq("V", "=", r"\pi", *LIMS, r"e^{-2x}", r"\cos^{2}x", r"\,dx"),
             say=cap(r"Square the curve: $y^{2}=e^{-2x}\cos^{2}x$."),
             rule=["volume_of_revolution", "exponent_laws"],
             mapping={"volume_of_revolution": [cap(r"Here $y=e^{-x}\cos x$, from $x=0$ to $\infty$.")]}),
        dict(tex=eq("V", "=", r"\frac{\pi}{2}", *LIMS, r"\big(", r"e^{-2x}", "+", r"e^{-2x}", r"\cos 2x", r"\big)",
                    r"\,dx"),
             say=cap(r"Swap $\cos^{2}x$ for $\frac{1+\cos 2x}{2}$, and pull out $\frac{1}{2}$."),
             rule=["double_angle", "pythagorean_identity", "linearity"],
             mapping={"double_angle": [cap(r"$\cos 2x=\cos^{2}x-\sin^{2}x$, with our angle $x$.")],
                      "pythagorean_identity": [cap(r"$\sin^{2}x=1-\cos^{2}x$, so $\cos 2x=2\cos^{2}x-1$.")]}),
        dict(tex=eq("V", "=", r"\frac{\pi}{2}", r"\Big(", r"\frac{1}{2}", "+", "I", r"\Big)", r",\quad", "I", "=",
                    *LIMS, r"e^{-2x}", r"\cos 2x", r"\,dx"),
             say=cap(r"The plain piece gives $\frac{1}{2}$; call the other piece $I$."),
             rule=["improper_integral", "exp_integral"],
             mapping={"improper_integral": [cap(r"Integrate to $b$; $e^{-2b}\to 0$ as $b\to\infty$.")],
                      "exp_integral": [cap(r"$\int_{0}^{b} e^{-2x}\,dx=\frac{1}{2}-\frac{1}{2}e^{-2b}\to\frac{1}{2}$.")]}),
        dict(tex=eq("I", "=", r"\frac{1}{2}", "-", *LIMS, r"e^{-2x}", r"\sin 2x", r"\,dx"),
             say=cap(r"Parts with $u=\cos 2x$: the boundary term gives $\frac{1}{2}$."),
             rule=["integration_by_parts", "chain_rule"],
             mapping={"integration_by_parts": [cap(r"$u=\cos 2x$ and $dv=e^{-2x}\,dx$, so $v=-\frac{1}{2}e^{-2x}$.")],
                      "chain_rule": [cap(r"$\frac{d}{dx}\cos 2x=-2\sin 2x$: the inside $2x$ gives $2$.")]}),
        dict(tex=eq("I", "=", r"\frac{1}{2}", "-", "I"),
             say=cap(r"Parts again on $e^{-2x}\sin 2x$ brings back $I$ itself."),
             rule=["integration_by_parts", "chain_rule"]),
        dict(tex=eq("I", "=", r"\frac{1}{4}"),
             say=cap(r"So $2I=\frac{1}{2}$, giving $I=\frac{1}{4}$."),
             rule="algebra"),
        dict(tex=eq("V", "=", r"\frac{3\pi}{8}"),
             say=cap(r"$V=\frac{\pi}{2}\big(\frac{1}{2}+\frac{1}{4}\big)=\frac{3\pi}{8}$."),
             rule="algebra"),
    ]

    ANSWER = eq(r"\frac{3\pi}{8}")
    ANSWER_VALUE = float(3 * np.pi / 8)
    CLOSE_SAYS = (cap(r"Rectangles under $\pi y^{2}$ close in on $\frac{3\pi}{8}\approx 1.178$."),
                  cap(r"Takeaway: square first, then a double angle tames $\cos^{2}x$."))

    def hook(self):
        self.solid_sketch()
        return super().hook()

    def solid_sketch(self):
        """The curve, its mirror below the axis and thin discs: the solid seen side-on."""
        self._guard_section = "Solid"
        axes = Axes(x_range=[0, 3.5, 0.5], y_range=[-1.1, 1.1, 0.5], x_length=8.5, y_length=4.2,
                     tips=False, axis_config=dict(stroke_opacity=0.6, include_ticks=False))
        axes.move_to([0, 0.15, 0])
        x_label = MathTex("x", font_size=34).next_to(axes.x_axis.get_right(), RIGHT, buff=0.15)
        top = axes.plot(y, x_range=[0, 3.5], color=CURVE_COLOR)
        bottom = axes.plot(lambda t: -y(t), x_range=[0, 3.5], color=CURVE_COLOR, stroke_opacity=0.5)
        unit_y = axes.c2p(0, 1)[1] - axes.c2p(0, 0)[1]
        discs = VGroup(*[
            Ellipse(width=0.16, height=2 * abs(y(t)) * unit_y).move_to(axes.c2p(t, 0))
            .set_stroke(AREA_COLOR, 2).set_fill(AREA_COLOR, 0.3)
            for t in np.arange(0.1, 3.4, 0.2) if abs(y(t)) > 0.03])
        self.play(Create(axes), FadeIn(x_label), run_time=1.0)
        self.play(Create(top), run_time=1.2)
        caption(self, cap(r"Spin $y=e^{-x}\cos x$ about the $x$-axis. What volume?"), key="hook: solid")
        self.play(TransformFromCopy(top, bottom), run_time=1.2)
        self.play(LaggedStart(*[GrowFromCenter(d) for d in discs], lag_ratio=0.08), run_time=2.0)
        mark(self, "discs")
        caption(self, cap(r"Slice the solid into thin discs, each of area $\pi y^{2}$."))
        clear_caption(self)
        self.play(FadeOut(VGroup(axes, x_label, top, bottom, discs)), run_time=0.8)
