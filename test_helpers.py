"""Tiny test scenes, one per story helper in common.py.

Run them all as fast dry runs with the frame guard on (prints PASS/FAIL per helper):
    .venv\\Scripts\\python test_helpers.py
Render one to look at it:
    .venv\\Scripts\\manim -ql --media_dir _media test_helpers.py TestRiemann
"""
import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from manim import *
import common
from common import (LIMIT, NEW, Trail, build_graph, cap, caption, close, draw_graph, eq, highlight,
                    install_frame_guard, make_badge, morph_to, mt, parts_of, reflection_view,
                    riemann_rectangles, substitution_view, unzoom)

PARABOLA = dict(x_range=[0, 2, 0.5], y_range=[0, 4, 1], a=0, b=2, x_labels={1: "1", 2: "2"},
                y_labels={1: "1", 2: "2", 3: "3", 4: "4"})


def square(x):
    return x ** 2


class HelperTest(MovingCameraScene):
    """Sets up what IntegralVideo.construct normally sets up, then runs test()."""

    def __init__(self, *a, **k):
        config.background_color = common.BACKGROUND
        super().__init__(*a, **k)

    def construct(self):
        install_frame_guard(self)
        self._narration, self._keyframes, self._caption = [], [], None
        badge = make_badge(self, "Test", "1 Jan 2026")
        self._guard_reserved = [badge]
        self.add(badge)
        self.test()


class TestMt(HelperTest):
    """mt(): parts keep their colours (limits YELLOW, new variable ORANGE)."""
    def test(self):
        m = mt(eq(r"\int_{", ("0", LIMIT), "}^{", ("1", LIMIT), "}", "u", r"\,d", "u"), {"u": NEW})
        assert m.submobjects[1].get_fill_color().to_hex() == ManimColor(LIMIT).to_hex()
        assert parts_of(m, "u")[0].get_fill_color().to_hex() == ManimColor(NEW).to_hex()
        self.play(Write(m))


class TestCaption(HelperTest):
    """caption(): bottom of screen, 12-word limit, replaces the previous caption."""
    def test(self):
        caption(self, cap(r"A caption with maths: $\frac{\pi}{2}$."))
        caption(self, cap("A second caption replaces the first."))
        try:
            caption(self, "one two three four five six seven eight nine ten eleven twelve thirteen")
            raise AssertionError("13 words were accepted")
        except common.CaptionTooLong:
            pass


class TestBuildGraph(HelperTest):
    """build_graph() + draw_graph(): numbered axes, faint grid, BLUE curve, GREEN area."""
    def test(self):
        draw_graph(self, build_graph(PARABOLA, square))


class TestRiemann(HelperTest):
    """riemann_rectangles(): 4 -> 64 rectangles with a live estimate and gap."""
    def test(self):
        gr = build_graph(PARABOLA, square)
        draw_graph(self, gr)
        _, _, _, est = riemann_rectangles(self, gr, 0, 2, 8 / 3)
        assert abs(est - 8 / 3) < 0.01 * 8 / 3


class TestHighlight(HelperTest):
    """highlight() + unzoom(): box, arrow, label, camera zoom and back."""
    def test(self):
        m = mt(eq(r"\int_{0}^{2}", "x^{2}", r"\,dx"))
        self.add(m)
        extra = highlight(self, parts_of(m, "x^{2}"), cap("the curve"), context=m)
        unzoom(self, FadeOut(extra))


class TestMorph(HelperTest):
    """morph_to() + Trail: lines morph in place; old lines dim into the top-left trail."""
    def test(self):
        trail = Trail()
        line = mt(eq(r"\int_{0}^{2}", "x^{2}", r"\,dx"))
        self.add(line)
        line = morph_to(self, line, eq(r"\Big[", r"\frac{x^{3}}{3}", r"\Big]_{0}^{2}"), {}, trail)
        line = morph_to(self, line, eq(r"\frac{8}{3}"), {}, trail)
        assert len(trail.lines) == 2


class TestSubstitution(HelperTest):
    """substitution_view(): u = x^2 turns the area under 2x on [0, 2] into the area under 1 on [0, 4]."""
    def test(self):
        trail = Trail()
        line = mt(eq(r"\int_{0}^{4}", r"\,du"))
        self.add(line)
        g_x = dict(x_range=[0, 2, 0.5], y_range=[0, 4, 1], a=0, b=2, x_labels={1: "1", 2: "2"},
                   y_labels={2: "2", 4: "4"})
        g_u = dict(x_range=[0, 4, 1], y_range=[0, 1.5, 0.5], a=0, b=4, var="u",
                   x_labels={2: "2", 4: "4"}, y_labels={0.5: "0.5", 1: "1"})
        substitution_view(self, line, trail, g_x, lambda x: 2 * x, g_u, lambda u: 1.0 + 0 * u,
                          4.0, (cap("Area in $x$."), cap("Same area in $u$.")))


class TestReflection(HelperTest):
    """reflection_view(): point reflection (odd function) and mirror (weights adding to 1)."""
    def test(self):
        reflection_view(self, dict(x_range=[-1, 1, 0.5], y_range=[-1, 1, 0.5], x_labels={-1: "-1", 1: "1"},
                                   y_labels={1: "1"}), lambda x: x ** 3, "point",
                        (cap("Odd: mirror pieces."), cap("They cancel.")))
        reflection_view(self, dict(x_range=[-4, 4, 2], y_range=[0, 1.5, 0.5], color_limits=False, sum=1,
                                   x_labels={-2: "-2", 2: "2"}, y_labels={1: "1"}),
                        lambda x: 1 / (1 + np.exp(-x)), "mirror", (cap("Mirror it."), cap("They add to $1$.")))


class TestClose(HelperTest):
    """close(): the boxed answer once, then the estimate meeting it, then the takeaway."""
    def test(self):
        line = mt(eq(r"\frac{8}{3}"))
        self.add(line)
        close(self, line, Trail(), eq(r"\frac{8}{3}"), {}, square, (0, 2), 8 / 3, 64,
              (cap("Rectangles close in."), cap("Takeaway: test helpers.")))


TESTS = [TestMt, TestCaption, TestBuildGraph, TestRiemann, TestHighlight, TestMorph, TestSubstitution,
         TestReflection, TestClose]


def main():
    common.GUARD_MODE = "collect"
    failed = 0
    for cls in TESTS:
        common.GUARD_LOG.clear()
        try:
            with tempconfig({"dry_run": True, "disable_caching": True, "quality": "low_quality",
                             "media_dir": os.path.join(os.path.dirname(os.path.abspath(__file__)), "_media"),
                             "verbosity": "ERROR"}):
                cls().render()
            problems = sorted({m for _, _, m in common.GUARD_LOG})
            status = "PASS" if not problems else "FAIL"
        except Exception:
            problems, status = [traceback.format_exc().strip().splitlines()[-1]], "FAIL"
        failed += status == "FAIL"
        print(f"{status}  {cls.__name__:17s} {cls.__doc__.splitlines()[0]}")
        for p in problems:
            print(f"        {p}")
    print("HELPER TESTS:", "PASS" if not failed else f"FAIL ({failed})")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
