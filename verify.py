"""Independent checks: compare each day's script with the website's own TeX, not with itself.

Usage (from this folder, with the .venv):
    .venv\\Scripts\\python verify.py 2026-10-15              # all three levels
    .venv\\Scripts\\python verify.py 2026-10-15 Medium       # one level
    .venv\\Scripts\\python verify.py 2026-10-15 --log        # also append rows to verification_log.csv

The website's TeX, saved once by fetch_source.py in source/DATE_Level.json, is the one
source of truth. sympy reads it into an integrand and limits, and every check below
compares the script with THAT, not with something else in the same script:

  source_file                  source/DATE_Level.json exists and holds an integral
  source_unchanged             its SHA-256 still matches source/hashes.csv (never edited)
  date_matches                 the script's DATE is the date printed on the website
  problem_matches_source       PROBLEM (the integral shown on screen) has the same limits
                               and the same integrand at 20 random points
  func_matches_source          FUNC (used for the graph and rectangles) equals the
                               website's integrand at 20 random points
  exact_integral_matches_source  the function and interval that exact_integral() hands to
                               mpmath equal the website's integrand and limits
  answer_tex_matches_value     the boxed answer as shown (ANSWER, read by sympy) equals
                               ANSWER_VALUE to a relative error below 1e-10
  quadratures_agree            the website's integral done twice, by mpmath (tanh-sinh)
                               and scipy (QUADPACK), gives the same number
  answer_matches_reference     ANSWER_VALUE equals that reference
  exact_integral_matches_reference  exact_integral() equals that reference
  steps                        every line of STEPS that sympy can evaluate equals the line
                               before it; lines it cannot evaluate are listed as unchecked
  check_false_valid            check=False is only used on a line with a red TRAP part,
                               and always with a check_reason

Each check is "pass", "fail" or "unchecked" (it could not be done, with the reason).
A video is "flagged" if any check fails, otherwise "ready". Unchecked is never silent: it
is listed in the output, the review file and the log.

Tolerances (why each one, see README "Verification"):
  ANSWER vs ANSWER_VALUE: relative error below 1e-10; an exact 0 needs |value| < 1e-14
  numerical integrals (the two methods, references, steps): relative 1e-8, or an absolute
  1e-12 times the size of the integral (the area under |f|), so tiny answers stay strict

Reading TeX (normalise, to_sympy): spacing and sizing commands are dropped; a function
written without brackets takes only a plain argument (\\ln 2\\cdot\\ln 3 is ln 2 * ln 3,
\\tan\\theta(1+x) is tan(theta) * (1+x), \\ln\\cos(x) is ln(cos x)); each \\int ... dx is
bracketed so two integrals on one line stay apart; [F]_a^b is F(b) - F(a); \\pi, e and
x(...) are a number and a product, not functions. An expression ending in \\dots (a
continued fraction, a tower of logs) is its limit: the pattern written out twice before the
\\dots is the block that repeats, and the tail's value is the attracting solution of
u = block(u) (nested_pattern); at a solution with slope -1 the layers swing between two
values (as y = x/y does), and the value is the solution lying between them. \\cfrac is \\frac and \\ddots is
\\dots; a constant outside the integral (\\frac{1}{2}\\int ...) is moved inside it
(single_integral). A limit outside the integral (\\lim_{n\\to 0}\\int_{n}^{...}) is worked out
from the integral itself at points approaching the limit (limit_value: mpmath Richardson and
scipy with polynomial extrapolation, from both sides if two-sided), never by moving the limit
inside; FUNC and exact_integral() are compared with the integrand's pointwise limit, which
is what the video draws (from 2026-10-19). A line is about the video's integral,
named "I" unless PROBLEM starts "V = ..." (then "V"); a line naming another quantity, or
holding several statements, is unchecked.

Numerical integrals (integrate): split at the corners of |...| and where the inside of a
square root reaches 0; for an expression with \\dots, mpmath also halves the range wherever
its error estimate is large (corners it cannot find from the formula); an integral oscillating
to infinity uses mpmath.quadosc, and scipy over half-periods with repeated averaging.
A step fails only if both methods find it differs from the line before; if the two
methods disagree with each other, the step is unchecked instead.
"""
import csv
import datetime as dt
import hashlib
import importlib.util
import json
import math
import os
import random
import re
import sys
import warnings

import mpmath
import sympy as sp

ROOT = os.path.dirname(os.path.abspath(__file__))
LEVELS = ["Beginner", "Easy", "Medium"]
SOURCE_DIR = os.path.join(ROOT, "source")
LOG_PATH = os.path.join(ROOT, "verification_log.csv")

ANSWER_REL_TOL = 1e-10        # ANSWER (exact, from sympy) vs ANSWER_VALUE (a float in the script)
EXACT_ZERO_TOL = 1e-14        # only when the exact answer is 0, where relative error has no meaning
QUAD_REL_TOL = 1e-8           # anything that went through numerical integration
QUAD_ABS_TOL = 1e-12
POINT_REL_TOL = 1e-8          # FUNC (numpy, double precision) vs the website's integrand
POINT_ABS_TOL = 1e-10
SAME_REL_TOL = 1e-12          # two exact formulas for the same function (PROBLEM, exact_integral), compared
SAME_ABS_TOL = 1e-14          # after rounding to ordinary double precision (about 16 digits)
N_POINTS, MIN_POINTS, MAX_TRIES = 20, 10, 400
VARIABLES = ("x", "t", "u", "v", "y", "z", "theta", "phi")

CHECKS = ["source_file", "source_unchanged", "date_matches", "problem_matches_source",
          "func_matches_source", "exact_integral_matches_source", "answer_tex_matches_value",
          "quadratures_agree", "answer_matches_reference", "exact_integral_matches_reference",
          "steps", "check_false_valid"]
LOG_COLUMNS = (["date", "level", "attempt", "timestamp"] + CHECKS +
               ["check_text", "check_frame", "unchecked_steps", "check_false_lines",
                "script_sha256", "video_sha256", "final_status", "error_type"])

mpmath.mp.dps = 30


class Unparseable(Exception):
    """sympy could not turn this TeX into a number or an integral we can evaluate."""


# ---------------------------------------------------------------- reading TeX
def _group(s, i):
    """The {...} group (or single character) starting at s[i]; returns (content, next index)."""
    while i < len(s) and s[i] == " ":
        i += 1
    if i >= len(s):
        raise Unparseable("unexpected end of TeX")
    if s[i] != "{":
        return s[i], i + 1
    depth = 0
    for j in range(i, len(s)):
        depth += {"{": 1, "}": -1}.get(s[j], 0)
        if depth == 0:
            return s[i + 1:j], j + 1
    raise Unparseable("unbalanced braces")


def normalise(tex):
    """Remove spacing and sizing commands sympy does not need."""
    t = re.sub(r"\\(?:Big|big|Bigg|bigg|left|right)(?![a-zA-Z])", "", tex)
    t = re.sub(r"\\[tdc]frac", r"\\frac", t)          # \cfrac: a continued fraction's display form
    t = re.sub(r"\\(?:cdots|ldots|ddots|vdots)(?![a-zA-Z])", r"\\dots", t)
    t = re.sub(r"\\(?:,|;|!|:|quad|qquad|displaystyle)", " ", t)
    t = t.replace(r"\mathrm{d}", "d").replace(r"\operatorname{d}", "d")
    # \tan\theta(3-\tan^2\theta) means tan(theta) times (3 - ...), as a reader takes it;
    # sympy would otherwise read tan(theta(3 - ...)).
    t = FUNC_ARG.sub(lambda m: f"{m.group(1)}({m.group(2)})\\cdot(", t)
    # \ln 2\cdot\ln 3 means ln(2)*ln(3); sympy would read ln(2*ln 3). A bare argument made of
    # numbers, letters and Greek letters ends where something else starts.
    t = FUNC_ATOM.sub(lambda m: f"{m.group(1)}({m.group(2)})", t)
    return _wrap_integrals(t).strip()


FUNCS = r"\\(?:sinh|cosh|tanh|sin|cos|tan|sec|csc|cot|ln|log|arcsin|arccos|arctan)(?![a-zA-Z])"
GREEK = r"\\(?:theta|phi|varphi|alpha|beta|pi)(?![a-zA-Z])"
# the argument of a function written without brackets: numbers, single letters and Greek
# letters only (never another function: \ln\cos(x) is ln(cos(x)))
FUNC_ARG = re.compile(r"(" + FUNCS + r"(?:\^\{[^{}]*\}|\^\d)?)\s*"
                      r"((?:\d+(?:\.\d+)?|[a-zA-Z](?![a-zA-Z])|" + GREEK + r")++)\s*\(")
FUNC_ATOM = re.compile(r"(" + FUNCS + r"(?:\^\{[^{}]*\}|\^\d)?)\s*"
                       r"((?:\d+(?:\.\d+)?|[a-zA-Z](?![a-zA-Z])|" + GREEK + r")++)"
                       r"(?![\(\^_{\[])")
DIFFERENTIAL = re.compile(r"d(?:[a-zA-Z]|\\(?:theta|phi|varphi))(?![a-zA-Z])")


def _wrap_integrals(t):
    """Put each \\int ... dx in brackets, so two integrals on one line stay apart
    (sympy otherwise reads the first \\int up to the last dx)."""
    out, i = "", 0
    while True:
        k = t.find(r"\int", i)
        if k < 0:
            return out + t[i:]
        depth, j, end = 0, k + 4, None
        while j < len(t):
            c = t[j]
            if c in "{([":
                depth += 1
            elif c in "})]":
                depth -= 1
                if depth < 0:
                    break
            elif depth == 0 and c == "d" and (j == 0 or not t[j - 1].isalpha() or t[j - 2:j] == "\\,"):
                m = DIFFERENTIAL.match(t, j)
                if m:
                    end = m.end()
                    break
            j += 1
        if end is None:                                  # no differential found: leave it as it is
            return out + t[i:]
        out += t[i:k] + "(" + t[k:end] + ")"
        i = end


def _fix(expr):
    """Undo two misreadings: the letter e means Euler's number, and x(3-x^2) means x*(3-x^2)
    for a real variable name (an unknown function such as g(x) is left alone)."""
    from sympy.core.function import AppliedUndef
    expr = expr.replace(lambda e: isinstance(e, AppliedUndef) and e.func.__name__ in VARIABLES + ("pi", "e")
                        and len(e.args) == 1, lambda e: sp.Symbol(e.func.__name__) * e.args[0])
    expr = expr.subs({sp.Symbol("e"): sp.E, sp.Symbol("pi"): sp.pi})
    expr = expr.replace(lambda e: isinstance(e, sp.log) and len(e.args) == 2,
                        lambda e: sp.log(e.args[0]) / sp.log(e.args[1]))
    return expr


def _bars(t):
    """Replace each evaluation bar [F]_{a}^{b} with a placeholder; returns (tex, {name: value})."""
    values = {}
    while True:
        m = re.search(r"\]\s*_", t)
        if not m:
            return t, values
        close = m.start()
        depth, start = 0, None
        for j in range(close, -1, -1):                    # the matching [
            depth += {"]": 1, "[": -1}.get(t[j], 0)
            if depth == 0:
                start = j
                break
        if start is None:
            raise Unparseable("unmatched ] in an evaluation bar")
        lo, i = _group(t, m.end())
        while i < len(t) and t[i] == " ":
            i += 1
        if i >= len(t) or t[i] != "^":
            raise Unparseable("evaluation bar without an upper limit")
        hi, i = _group(t, i + 1)
        inner = to_sympy(t[start + 1:close])
        var = list(inner.free_symbols)
        if len(var) != 1:                                # several letters: prefer a usual variable name
            var = [s for s in var if s.name in VARIABLES]
        if len(var) != 1:
            raise Unparseable("cannot tell the variable of an evaluation bar")
        a, b = to_sympy(lo), to_sympy(hi)
        name = f"Xi_{{{len(values)}}}"                  # parse_latex reads \Xi_{0} as Symbol("Xi_{0}")
        values[name] = inner.subs(var[0], b) - inner.subs(var[0], a)
        t = t[:start] + " \\" + name + " " + t[i:]


def to_sympy(tex):
    """TeX -> sympy expression (integrals stay as sympy Integral objects)."""
    from sympy.parsing.latex import parse_latex
    t, bars = _bars(normalise(tex))
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            expr = parse_latex(t)
    except Exception as exc:                             # sympy raises several error types
        raise Unparseable(f"sympy could not read it ({type(exc).__name__})") from None
    expr = _fix(expr)
    for name, value in bars.items():
        expr = expr.subs(sp.Symbol(name), value)
    return expr


def single_integral(expr):
    r"""expr as one sympy Integral: an Integral, or a constant times one (\frac{1}{2}\int ...),
    with the constant moved inside. Anything else is not a single integral."""
    if isinstance(expr, sp.Integral):
        return expr
    if isinstance(expr, sp.Mul):
        ints = [f for f in expr.args if isinstance(f, sp.Integral)]
        rest = [f for f in expr.args if not isinstance(f, sp.Integral)]
        if len(ints) == 1 and not any(f.free_symbols or f.has(sp.Integral) for f in rest):
            return sp.Integral(sp.Mul(*rest) * ints[0].function, *ints[0].limits)
    raise Unparseable("not a single integral")


def split_top_level(tex, ch="="):
    """Split on ch outside braces and brackets."""
    parts, depth, cur = [], 0, ""
    for c in tex:
        depth += {"{": 1, "}": -1, "(": 1, ")": -1, "[": 1, "]": -1}.get(c, 0)
        if c == ch and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += c
    return parts + [cur]


# ---------------------------------------------------------------- numbers
def to_mp(v):
    if v == sp.oo:
        return mpmath.inf
    if v == -sp.oo:
        return -mpmath.inf
    z = complex(sp.N(v, 30))
    if abs(z.imag) > 1e-20 * max(1.0, abs(z.real)):
        raise Unparseable("a limit is not a real number")
    return mpmath.mpf(str(sp.N(sp.re(v), 30)))


DOTS = sp.Symbol("dots")       # parse_latex reads \dots as this symbol
NEST_ITERATIONS = 200
NEST_STARTS = (0, 1, 10, 100)


def _path_to(expr, sym):
    """The nodes from the root of expr down to sym, each with a key describing it apart from
    the branch that leads on to sym (its type and its other arguments)."""
    nodes = []
    while expr != sym:
        branch = [i for i, a in enumerate(expr.args) if a.has(sym)]
        if len(branch) != 1:
            raise Unparseable(r"\dots appears more than once")
        others = sorted(sp.srepr(a) for i, a in enumerate(expr.args) if i != branch[0])
        nodes.append((expr, (expr.func, tuple(others))))
        expr = expr.args[branch[0]]
    return nodes


def nested_pattern(expr):
    """For an expression ending in \\dots (a continued fraction, a tower of logs, ...):
    the block that repeats on the way down to \\dots, as (block, start). The \\dots stands
    for the infinite tail that starts where the pattern next begins, so its value u solves
    u = block(u), and the expression's value is expr with \\dots = u.

    The pattern must be written out at least twice in full before the \\dots, so it is
    read from the TeX itself, never guessed."""
    if expr.count(DOTS) != 1:
        raise Unparseable(r"\dots appears more than once")
    nodes = _path_to(expr, DOTS)
    keys = [k for _, k in nodes]
    m = len(keys)                                        # depth of \dots
    for p in range(1, m // 2 + 1):                       # shortest period first, then earliest start
        for s in range(0, m - 2 * p + 1):
            if all(keys[i] == keys[i + p] for i in range(s, m - p)):
                r = s + (m - s) % p                      # the depth where the tail restarts the pattern
                # one period: the subtree at depth r, with its copy one period down replaced by \dots
                block = nodes[r][0].xreplace({nodes[r + p][0]: DOTS})
                return block, r
    raise Unparseable(r"no repeating pattern before \dots (it must be written out twice)")


def _nested_value(block_f, x):
    """The value u of the infinite tail at x: the attracting solution of u = block(x, u),
    reached by iterating from several starts (NEST_STARTS). Starts that leave the real
    numbers (e.g. ln 0) are dropped; if the others lead to different values, or the
    solution is not attracting, it is not a clear limit."""
    with mpmath.workdps(2 * mpmath.mp.dps):          # spare digits for where two solutions meet
        found = _nested_values(block_f, x)
    if not found:
        raise ValueError(rf"the expression with \dots has no clear limit at x = {mpmath.nstr(x, 6)}")
    if any(not close(v, found[0], 1e-12, 1e-14) for v in found[1:]):
        raise ValueError(r"the expression with \dots has two different limits here")
    return found[0]


def _nested_values(block_f, x):
    """The limit of the iteration u -> block(x, u) from each start that works (see _nested_value)."""
    found = []
    for u in map(mpmath.mpf, NEST_STARTS):
        try:
            seq = [u]
            for _ in range(NEST_ITERATIONS):
                u = block_f(x, u)
                if isinstance(u, mpmath.mpc):
                    if abs(u.imag) > 1e-20 * max(1, abs(u.real)):
                        raise ValueError("complex value")
                    u = u.real
                if not mpmath.isfinite(u):
                    raise ValueError("not a finite number")
                seq.append(u)
                if abs(seq[-1] - seq[-2]) <= mpmath.mpf(10) ** (-mpmath.mp.dps + 5):
                    break                                # converged
            # iteration converges slowly where two solutions meet (a double root): finish with
            # Newton's method for repeated roots, started from the last iterate so it keeps to
            # the solution being approached
            tiny = mpmath.mpf(10) ** (-mpmath.mp.dps + 5)
            swing = None
            if (abs(seq[-1] - seq[-2]) > tiny and len(seq) > 3 and abs(seq[-1] - seq[-3]) <= tiny):
                # stuck swinging between two values p, q (block(p) = q, block(q) = p): block(v) - v
                # changes sign between them, so bracket the solution there
                swing = tuple(sorted(seq[-2:]))
                u = _bisect(lambda v: block_f(x, v) - v, *swing)
            elif abs(seq[-1] - seq[-2]) > tiny:
                # (at a double root, rounding can split it into a complex pair a hair apart:
                # accept the root when it solves u = block(u) to a third of the working digits)
                u = mpmath.findroot(lambda v: block_f(x, v) - v, u, solver="mnewton", verify=False)
                if abs(block_f(x, u) - u) > mpmath.mpf(10) ** (-(mpmath.mp.dps // 3)):
                    raise ValueError("no root found")
                u = mpmath.re(u)
            d = mpmath.diff(lambda v: block_f(x, v), u)
            if abs(d) > 1 + 1e-6:
                raise ValueError("a repelling solution")
            # slope -1: the layers swing between two values and never settle (y = x/y gives
            # x, 1, x, 1, ...). Read as the solution lying strictly between the two values they
            # swing between (+sqrt(x) for x/(x/(x/...)), never -sqrt(x)); a start whose swing
            # does not surround that solution is dropped (user, 2026-10-19). Slope +1, where two
            # solutions meet, still converges slowly and needs nothing extra.
            if d < -1 + 1e-6 and (swing is None or not swing[0] < u < swing[1]):
                raise ValueError("an oscillating solution outside the swing")
            if not mpmath.isfinite(u):
                raise ValueError("not a finite number")
            found.append(mpmath.mpf(mpmath.re(u)))
        except (ValueError, ZeroDivisionError, TypeError):
            continue                                     # e.g. ln(0) from the start 0: try the next start
    return found


def _bisect(h, lo, hi):
    """A root of h between lo and hi, where h changes sign, by bisection: halving at the
    geometric mean when lo and hi have the same sign (so a swing from 1e-22 to 1 is resolved
    in about 200 steps), at the midpoint otherwise. mpmath's bracketing solvers give up on
    such lopsided ranges (2026-10-19)."""
    h_lo = h(lo)
    if h_lo == 0:
        return lo
    if mpmath.sign(h_lo) == mpmath.sign(h(hi)):
        raise ValueError("no sign change in the swing")
    tiny = mpmath.mpf(10) ** (-mpmath.mp.dps + 5)
    for _ in range(4 * mpmath.mp.prec):
        if hi - lo <= tiny * max(abs(lo), abs(hi)):
            break
        mid = (mpmath.sign(lo) * mpmath.sqrt(lo * hi)) if lo * hi > 0 else (lo + hi) / 2
        h_mid = h(mid)
        if h_mid == 0:
            return mid
        if mpmath.sign(h_mid) == mpmath.sign(h_lo):
            lo, h_lo = mid, h_mid
        else:
            hi = mid
    return (lo + hi) / 2


def mp_function(expr, var):
    if expr.has(DOTS):
        block, _ = nested_pattern(expr)
        outer = sp.lambdify((var, DOTS), expr, modules="mpmath")
        block_f = sp.lambdify((var, DOTS), block, modules="mpmath")
        f = lambda x: outer(x, _nested_value(block_f, x))      # noqa: E731
    else:
        f = sp.lambdify(var, expr, modules="mpmath")

    def g(x):
        y = f(x)
        if isinstance(y, mpmath.mpc):
            if abs(y.imag) > 1e-20 * max(1, abs(y.real)):
                raise ValueError("complex value")
            y = y.real
        return mpmath.mpf(y)
    return g


def _no_unknown_functions(expr):
    """Notation such as g(x), defined only in the video, has no value we can compute."""
    from sympy.core.function import AppliedUndef
    names = sorted({f.func.__name__ for f in expr.atoms(AppliedUndef)})
    if names:
        raise Unparseable(f"uses functions defined only in the video: {', '.join(names)}")


def breakpoints(expr, var, a, b):
    r"""Points inside (a, b) where |...| switches sign, or where the inside of a square root
    (or another fractional power) reaches 0 (\sqrt{1+\cos 2x} is \sqrt{2}|\cos x|): corners
    that numerical methods should not have to step across."""
    pts = set()
    roots = [p.base for p in expr.atoms(sp.Pow)
             if p.exp.is_Rational and not p.exp.is_integer and p.base.has(var)]
    for inside in [ab.args[0] for ab in expr.atoms(sp.Abs)] + roots:
        try:
            sol = sp.solveset(inside, var, domain=sp.Interval(a, b, True, True))
            if isinstance(sol, sp.FiniteSet):
                for s in sol:
                    pts.add(to_mp(s))
        except Exception:                                  # anything sympy cannot solve: no extra points
            pass
    return sorted(pts)


def oscillation(expr, var, a, b):
    """For an infinite range with sin/cos of (c*var + d): the largest |c|, else None."""
    if a not in (-mpmath.inf, mpmath.inf) and b not in (-mpmath.inf, mpmath.inf):
        return None
    freqs = []
    for f in expr.atoms(sp.sin, sp.cos):
        poly = sp.Poly(f.args[0], var) if f.args[0].is_polynomial(var) else None
        if poly is not None and poly.degree() == 1:
            freqs.append(abs(float(poly.all_coeffs()[0])))
    return max(freqs) if freqs else None


def integrate(expr, var, a, b, method="mpmath", scale=1.0):
    """The definite integral of expr from a to b (mpmath numbers, may be infinite).
    method "mpmath": tanh-sinh (mpmath.quad), or mpmath.quadosc for endless oscillation.
    method "scipy":  QUADPACK (scipy.integrate.quad); for endless oscillation, scipy over
                     each half-period, then repeated averaging of the partial sums.
    Both split the range at the corners found by breakpoints()."""
    f = mp_function(expr, var)
    pts = [a] + breakpoints(expr, var, a, b) + [b]
    omega = oscillation(expr, var, a, b)
    total = mpmath.mpf(0)
    for lo, hi in zip(pts[:-1], pts[1:]):
        if omega and (lo == -mpmath.inf or hi == mpmath.inf):
            pieces = [(lo, mpmath.mpf(0)), (mpmath.mpf(0), hi)] if lo == -mpmath.inf and hi == mpmath.inf else [(lo, hi)]
            for p, q in pieces:
                total += _oscillating(f, p, q, omega, method)
        elif method == "mpmath" and expr.has(DOTS) and mpmath.isfinite(lo) and mpmath.isfinite(hi):
            total += _adaptive_quad(f, lo, hi)
        elif method == "mpmath":
            total += mpmath.quad(f, [lo, hi])
        else:
            total += mpmath.mpf(_scipy_quad(f, lo, hi, epsabs=1e-13 * max(scale, 1e-300))[0])
    return total


def _adaptive_quad(f, lo, hi, tol=mpmath.mpf("1e-20"), depth=0):
    r"""tanh-sinh, halving the range wherever its error estimate is too large. Used for an
    expression with \dots: its corners (e.g. where a hidden |cos x| turns) cannot be found
    from the formula, so they are isolated by bisection instead of split at in advance."""
    value, err = mpmath.quad(f, [lo, hi], error=True, maxdegree=6)
    if err <= tol or depth >= 40:
        return value
    mid = (lo + hi) / 2
    return (_adaptive_quad(f, lo, mid, tol / 2, depth + 1) +
            _adaptive_quad(f, mid, hi, tol / 2, depth + 1))


def _oscillating(f, lo, hi, omega, method):
    """An integral to +-infinity of an oscillating function."""
    if method == "mpmath":
        return mpmath.quadosc(f, [lo, hi], omega=omega)
    from scipy import integrate as si
    sign, start = (1, float(lo)) if hi == mpmath.inf else (-1, float(hi))
    step = math.pi / omega
    g = lambda x: float(f(mpmath.mpf(x)))                  # noqa: E731
    sums, s = [], 0.0
    for k in range(400):                                   # 400 half-periods, then accelerate
        x0, x1 = start + sign * k * step, start + sign * (k + 1) * step
        s += si.quad(g, min(x0, x1), max(x0, x1), limit=200, epsabs=1e-15, epsrel=1e-13)[0]
        sums.append(s)
    seq = sums[-60:]
    for _ in range(40):                                    # repeated averaging (Euler) of the tail
        seq = [(p + q) / 2 for p, q in zip(seq[:-1], seq[1:])]
        if len(seq) == 1:
            break
    return mpmath.mpf(seq[-1])


def quad_integral(integral, method="mpmath"):
    """Numerical value of a definite sympy Integral (one variable)."""
    if len(integral.limits) != 1 or len(integral.limits[0]) != 3:
        raise Unparseable("not a definite integral in one variable")
    var, a, b = integral.limits[0]
    _no_unknown_functions(integral.function)
    extra = integral.function.free_symbols - {var, DOTS}
    if extra:
        raise Unparseable(f"unknown symbols {sorted(s.name for s in extra)}")
    return integrate(integral.function, var, to_mp(a), to_mp(b), method)


def value_of(expr, method="mpmath"):
    """A real number for an expression with no free symbols (integrals done numerically).
    Returns (value, exact) where exact says no numerical integration was needed."""
    _no_unknown_functions(expr)
    expr = expr.replace(lambda e: isinstance(e, sp.Derivative), lambda e: e.doit())
    if expr.has(sp.Limit):                       # \lim_{n\to 0} ... : done numerically (limit_value)
        expr = expr.replace(lambda e: isinstance(e, sp.Limit),
                            lambda e: sp.Float(mpmath.nstr(limit_value(e, method), 28), 30))
        if not expr.has(sp.Integral):
            return value_of(expr, method)[0], False
    exact = not expr.has(sp.Integral)
    if not exact:
        expr = expr.replace(lambda e: isinstance(e, sp.Integral),
                            lambda e: sp.Float(mpmath.nstr(quad_integral(e, method), 28), 30))
    if expr.free_symbols:
        raise Unparseable(f"unknown symbols {sorted(s.name for s in expr.free_symbols)}")
    z = complex(sp.N(expr, 30))
    if not math.isfinite(z.real) or abs(z.imag) > 1e-20 * max(1.0, abs(z.real)):
        raise Unparseable("not a finite real number")
    return mpmath.mpf(str(sp.N(sp.re(expr), 30))), exact


LIMIT_STEP = mpmath.mpf("0.1")      # mpmath: the expression at z0 + 0.1/2^k (mpmath.limit, exp=True)
SCIPY_LIMIT_STEPS = 6               # scipy: at z0 + 0.02/2^k, k = 0..5, then a polynomial through them at 0


def limit_value(lim, method="mpmath"):
    r"""The value of a sympy Limit such as \lim_{n\to 0}\int_{n}^{\pi/2} f(x, n)\,dx, from the
    expression itself at points approaching the limit point: never by moving the limit inside
    an integral, which is not always allowed.
    method "mpmath": mpmath.limit with exp=True (Richardson extrapolation from z0 + 0.1/2^k;
                     the plain 0.1/k points were only good to 5 digits on 2026-10-19 Easy),
                     each value with mpmath.quad at 30 digits.
    method "scipy":  values with scipy at z0 + 0.02/2^k (k = 0..5), extrapolated to z0 by the
                     polynomial through them (Neville).
    A two-sided limit is done from both sides, which must agree."""
    body, z, z0, direction = lim.args
    if z0 in (sp.oo, -sp.oo):
        raise Unparseable("a limit at infinity")
    z0 = to_mp(z0)

    def at(h):                                   # the expression at z0 + h
        return value_of(body.subs(z, sp.Float(mpmath.nstr(z0 + h, 40), 40)), method)[0]

    sides = {"+": [1], "-": [-1]}.get(str(direction), [1, -1])
    values = []
    for s in sides:
        if method == "mpmath":
            values.append(mpmath.limit(at, 0, direction=s * LIMIT_STEP, exp=True))
        else:
            hs = [s * mpmath.mpf("0.02") / 2 ** k for k in range(SCIPY_LIMIT_STEPS)]
            values.append(_extrapolate_to_zero(hs, [at(h) for h in hs]))
    if len(values) == 2 and not close(values[0], values[1], QUAD_REL_TOL, QUAD_ABS_TOL):
        raise ValueError(f"the limits from the two sides differ ({mpmath.nstr(values[0], 10)}, "
                         f"{mpmath.nstr(values[1], 10)})")
    return values[0]


LIMIT_SAMPLES = ("0.3", "0.1", "0.03")      # distances from the limit point where two limits are compared


def compare_limit_problems(src, p):
    """Compare two limits of integrals (the website's and PROBLEM): the same limit point and
    direction, and at each distance in LIMIT_SAMPLES (on each side the limit uses) the same
    limits of integration and the same integrand at random points. Returns a list of problems."""
    if not isinstance(p, sp.Limit):
        return ["PROBLEM is not a limit of an integral, but the website's is"]
    (sb, sz, sz0, sd), (pb, pz, pz0, pd) = src.args, p.args
    if sz0 != pz0:
        return [f"limit point {pz0}, website {sz0}"]
    if str(sd) != str(pd):
        return [f"limit from side {pd}, website {sd}"]
    si, pi_ = single_integral(sb), single_integral(pb)
    if len(si.limits) != 1 or len(pi_.limits) != 1 or len(si.limits[0]) != 3 or len(pi_.limits[0]) != 3:
        return ["not a definite integral in one variable"]
    (svar, sa, sb_), (pvar, pa, pb_) = si.limits[0], pi_.limits[0]
    problems = []
    for side in {"+": [1], "-": [-1]}.get(str(sd), [1, -1]):
        for h in LIMIT_SAMPLES:
            zv = sp.Float(mpmath.nstr(to_mp(sz0) + side * mpmath.mpf(h), 40), 40)
            lo, hi = to_mp(sa.subs(sz, zv)), to_mp(sb_.subs(sz, zv))
            plo, phi = to_mp(pa.subs(pz, zv)), to_mp(pb_.subs(pz, zv))
            if not (close(plo, lo, 1e-15, 1e-15) and close(phi, hi, 1e-15, 1e-15)):
                problems.append(f"at {sz} = {mpmath.nstr(zv, 4)}: limits {mpmath.nstr(plo, 8)} to "
                                f"{mpmath.nstr(phi, 8)}, website {mpmath.nstr(lo, 8)} to {mpmath.nstr(hi, 8)}")
                continue
            r, d = compare_on_points(mp_function(si.function.subs(sz, zv), svar),
                                     mp_function(pi_.function.subs(pz, zv), pvar), lo, hi,
                                     rel=SAME_REL_TOL, abs_tol=SAME_ABS_TOL)
            if r != "pass":
                problems.append(f"at {sz} = {mpmath.nstr(zv, 4)}: integrand: {d}")
    return problems


def _extrapolate_to_zero(hs, vs):
    """The polynomial through the points (hs[i], vs[i]), evaluated at 0 (Neville's scheme)."""
    p = list(vs)
    for m in range(1, len(hs)):
        p = [(hs[i + m] * p[i] - hs[i] * p[i + 1]) / (hs[i + m] - hs[i]) for i in range(len(p) - 1)]
    return p[0]


def close(x, y, rel, abs_tol=0.0):
    x, y = mpmath.mpf(x), mpmath.mpf(y)
    if mpmath.isinf(x) or mpmath.isinf(y):     # inf - inf is nan: infinities match only themselves
        return x == y
    return abs(x - y) <= max(rel * max(abs(x), abs(y)), abs_tol)


def sample_points(a, b, rng):
    """A random point strictly inside (a, b); handles infinite limits."""
    u = mpmath.mpf(rng.uniform(0.002, 0.998))
    if a != -mpmath.inf and b != mpmath.inf:
        return a + (b - a) * u
    if a != -mpmath.inf:
        return a + u / (1 - u)
    if b != mpmath.inf:
        return b - u / (1 - u)
    return mpmath.tan(mpmath.pi * (u - mpmath.mpf(0.5)))


def compare_on_points(ref, test, a, b, rel=POINT_REL_TOL, abs_tol=POINT_ABS_TOL, seed=1):
    """Compare two functions at N_POINTS random points of (a, b) where ref is defined.
    Returns (result, detail)."""
    rng = random.Random(seed)
    used, tries = 0, 0
    while used < N_POINTS and tries < MAX_TRIES:
        tries += 1
        x = sample_points(a, b, rng)
        try:
            r = ref(x)
        except (ValueError, ZeroDivisionError, OverflowError, TypeError):
            continue                                    # the website's integrand is undefined here
        if not mpmath.isfinite(r):
            continue
        try:
            y = test(x)
            y = complex(y)
            if abs(y.imag) > 1e-12 * max(1.0, abs(y.real)):
                return "fail", f"value is complex at x = {mpmath.nstr(x, 8)}"
            y = y.real
        except Exception as exc:
            return "fail", f"undefined at x = {mpmath.nstr(x, 8)} ({type(exc).__name__}), where the website's integrand is {mpmath.nstr(r, 10)}"
        if not math.isfinite(y) or not close(y, r, rel, abs_tol):
            return "fail", f"at x = {mpmath.nstr(x, 8)}: {y!r} but the website's integrand gives {mpmath.nstr(r, 12)}"
        used += 1
    if used < MIN_POINTS:
        return "unchecked", f"only {used} usable points (need {MIN_POINTS})"
    return "pass", f"equal at {used} random points"


# ---------------------------------------------------------------- the script
def load_class(date, level, folder=None):
    path = os.path.join(folder or os.path.join(ROOT, level), f"{date}_{level}.py")
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    name = f"_verify_{date}_{level}_{abs(hash(path))}"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return getattr(mod, f"{level}Integral"), path


def spec_tex(spec):
    return "".join(p[0] if isinstance(p, tuple) else p for p in spec)


def trap_parts(spec, colors):
    import common
    out = []
    for p in spec:
        tex, colour = (p[0], p[1]) if isinstance(p, tuple) else (p, (colors or {}).get(p))
        if colour is not None and colour == common.TRAP_COLOR:
            out.append(tex)
    return out


def capture_exact(cls):
    """Call exact_integral() while recording what it passes to mpmath.quad."""
    calls, orig, orig_ctx = [], mpmath.quad, mpmath.mp.quad

    def spy(f, *args, **kwargs):
        calls.append((f, args[0] if args else kwargs.get("intervals")))
        return orig(f, *args, **kwargs)
    mpmath.quad = spy
    mpmath.mp.quad = spy
    try:
        value = cls.exact_integral()
    finally:
        mpmath.quad = orig
        mpmath.mp.quad = orig_ctx
    return value, calls


def sha256(path):
    if not path or not os.path.exists(path):
        return ""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def video_path(date, level, root=ROOT):
    for p in (os.path.join(root, "pending", level, f"{date}_{level}.mp4"),
              os.path.join(root, level, f"{date}_{level}.mp4")):
        if os.path.exists(p):
            return p
    return None


# ---------------------------------------------------------------- the checks
def line_values(tex, main="I", method="mpmath"):
    """The value of the integral that one line states, from each side of its = signs.
    A side "I" or "2I" (main: the name the video gives the integral) names it; every other
    side is evaluated. A line about another named quantity (a side that is a different
    single letter, e.g. a helper integral J) or with several statements is not compared.
    Returns (values, unread) where unread lists what could not be evaluated."""
    if len(split_top_level(normalise(tex), ",")) > 1:
        return [], ["several statements on one line"]
    sides = [s.strip() for s in split_top_level(tex, "=")]
    if len(sides) > 1:
        # an equation whose sides still hold letters (4y^2+4y-\cos 2x=0) relates other
        # quantities; it does not state a value of the integral
        letters = set()
        for s in sides:
            if re.fullmatch(r"(\d*)\s*([A-Za-z])", s):
                continue
            try:
                letters |= {v.name for v in to_sympy(s).free_symbols if v != DOTS}
            except Unparseable:
                pass
        if letters:
            return [], [f"an equation in {', '.join(sorted(letters))}, not a value of the integral"]
    coeff = 1
    values, unread = [], []
    for s in sides:
        m = re.fullmatch(r"(\d*)\s*([A-Za-z])", s)
        if m and m.group(2) == main:
            coeff = int(m.group(1) or 1)
            continue
        if m and len(sides) > 1:
            return [], [f"the line is about another quantity, {m.group(2)}"]
        try:
            v, _ = value_of(to_sympy(s), method)
            values.append(v)
        except (Unparseable, ValueError, ZeroDivisionError, TypeError, ArithmeticError) as exc:
            unread.append(f"{s[:60]} ({exc})")
    return [v / coeff for v in values], unread


def check_video(date, level, folder=None, source_dir=None, root=ROOT):
    """Run every check for one video. Returns a dict with checks, status and details."""
    checks = {c: dict(result="unchecked", detail="not run") for c in CHECKS}
    out = dict(date=date, level=level, checks=checks, unchecked_steps=[], check_false_lines=[],
               steps=[], script_sha256="", video_sha256="")

    def set_(name, result, detail):
        checks[name] = dict(result=result, detail=detail)

    source_dir = source_dir or os.path.join(root, "source")
    src_path = os.path.join(source_dir, f"{date}_{level}.json")
    try:
        cls, script = load_class(date, level, folder)
    except Exception as exc:
        set_("source_file", "fail" if not os.path.exists(src_path) else "pass", "")
        out["error"] = f"could not load the script: {type(exc).__name__}: {exc}"
        for c in CHECKS[1:]:
            set_(c, "fail", "the script could not be loaded")
        return _finish(out)
    out["script_sha256"] = sha256(script)
    out["video_sha256"] = sha256(video_path(date, level, root))
    out["script"] = script

    # --- the website's integral
    integrand = var = a = b = src_limit = None
    if not os.path.exists(src_path):
        set_("source_file", "fail", f"{os.path.relpath(src_path, root)} is missing (run fetch_source.py)")
        source = None
    else:
        source = json.load(open(src_path, encoding="utf-8"))
        try:
            expr = to_sympy(source["problem_tex"])
            if isinstance(expr, sp.Limit):               # a limit outside the integral, e.g. lim n->0 of int_n^(pi/2) f(x, n) dx
                src_limit = expr
                expr = single_integral(expr.args[0])
            expr = single_integral(expr)                 # a constant factor outside moves inside
            if len(expr.limits) != 1:
                raise Unparseable("not a single integral")
            integrand, lim = expr.function, expr.limits[0]
            var = lim[0]
            note = ""
            if src_limit is not None:
                # the value is the limit of the integral (limit_value). FUNC and exact_integral()
                # are compared with the integrand's pointwise limit on the limiting interval,
                # which is what the video draws; if sympy cannot find it, those are unchecked
                if len(lim) != 3:
                    raise Unparseable("a limit of an indefinite integral")
                z, z0, zdir = src_limit.args[1], src_limit.args[2], str(src_limit.args[3])
                a = to_mp(sp.limit(lim[1], z, z0, dir=zdir))
                b = to_mp(sp.limit(lim[2], z, z0, dir=zdir))
                try:
                    g = sp.limit(integrand, z, z0, dir=zdir)
                    if g.has(z, sp.Limit, sp.nan, sp.zoo, sp.oo, -sp.oo):
                        raise ValueError
                    integrand = g
                    note = f" (as {z} -> {z0}: integrand {g}, from {lim[1]} to {lim[2]} -> {a} to {b})"
                except Exception:                        # sympy raises several error types
                    integrand = None
                    note = f" (as {z} -> {z0}: the integrand's pointwise limit could not be found)"
            elif len(lim) == 3:
                a, b = to_mp(lim[1]), to_mp(lim[2])
            set_("source_file", "pass", f"{source['problem_tex']}{note}")
        except Unparseable as exc:
            set_("source_file", "fail", f"the website's TeX could not be read: {exc}")
            source = None
        hashes = os.path.join(source_dir, "hashes.csv")
        want = None
        if os.path.exists(hashes):
            for row in csv.DictReader(open(hashes, encoding="utf-8")):
                if row["file"] == os.path.basename(src_path):
                    want = row["sha256"]
        got = sha256(src_path)
        if want is None:
            set_("source_unchanged", "fail", "no fingerprint recorded in source/hashes.csv")
        elif got != want:
            set_("source_unchanged", "fail", "the file was changed after it was saved")
        else:
            set_("source_unchanged", "pass", f"sha256 {got[:12]}... as saved")

    if source is not None:
        set_("date_matches", "pass" if cls.DATE == source["date"] else "fail",
             f"script DATE {cls.DATE}, website {source['date']} ({source.get('page_date_text')})")
    else:
        set_("date_matches", "unchecked", "no readable source")

    definite = a is not None
    ref_f = mp_function(integrand, var) if integrand is not None else None
    lo_hi = (a, b) if definite else _graph_range(cls)
    # the name the video gives the integral: "V" in PROBLEM = "V=\pi\int...", otherwise "I"
    problem_sides = split_top_level(spec_tex(cls.PROBLEM), "=")
    m = re.fullmatch(r"\s*([A-Za-z])\s*", problem_sides[0]) if len(problem_sides) > 1 else None
    main_name = m.group(1) if m else "I"

    # --- PROBLEM (what the viewer sees) vs the website
    if src_limit is not None:
        try:
            problems = compare_limit_problems(src_limit, to_sympy(problem_sides[-1]))
            set_("problem_matches_source", "fail" if problems else "pass",
                 "; ".join(problems) or "same limit; same limits of integration and integrand at "
                                        f"{len(LIMIT_SAMPLES)} values of {src_limit.args[1]}")
        except Unparseable as exc:
            set_("problem_matches_source", "unchecked", f"PROBLEM could not be read: {exc}")
        if ref_f is not None:
            r, d = compare_on_points(ref_f, lambda x: cls.FUNC(float(x)), *lo_hi)
            set_("func_matches_source", r, d + " (with the integrand's pointwise limit)")
        else:
            set_("func_matches_source", "unchecked", "the integrand's pointwise limit could not be found")
    elif ref_f is not None:
        try:
            p = single_integral(to_sympy(problem_sides[-1]))
            if len(p.limits) != 1:
                raise Unparseable("PROBLEM is not a single integral")
            pvar, plim = p.limits[0][0], p.limits[0]
            problems = []
            if definite != (len(plim) == 3):
                problems.append("one has limits and the other does not")
            elif definite and not (close(to_mp(plim[1]), a, 1e-15, 1e-15) and close(to_mp(plim[2]), b, 1e-15, 1e-15)):
                problems.append(f"limits {plim[1]} to {plim[2]}, website {mpmath.nstr(a, 10)} to {mpmath.nstr(b, 10)}")
            if not problems:
                r, d = compare_on_points(ref_f, mp_function(p.function, pvar), *lo_hi, rel=SAME_REL_TOL, abs_tol=SAME_ABS_TOL)
                if r != "pass":
                    problems.append(f"integrand: {d}")
            set_("problem_matches_source", "fail" if problems else "pass",
                 "; ".join(problems) or "same limits, same integrand at 20 random points")
        except Unparseable as exc:
            set_("problem_matches_source", "unchecked", f"PROBLEM could not be read: {exc}")
        r, d = compare_on_points(ref_f, lambda x: cls.FUNC(float(x)), *lo_hi)
        set_("func_matches_source", r, d)

    # --- exact_integral(): its function and interval
    try:
        exact_value, calls = capture_exact(cls)
        exact_value = mpmath.mpf(exact_value)
    except Exception as exc:
        exact_value, calls = None, []
        set_("exact_integral_matches_source", "fail", f"exact_integral() raised {type(exc).__name__}: {exc}")
    if exact_value is not None and ref_f is not None:
        if not calls:
            set_("exact_integral_matches_source", "unchecked", "exact_integral() does not call mpmath.quad")
        else:
            f, intervals = calls[0]
            pts = [mpmath.mpf(x) if x not in (mpmath.inf, -mpmath.inf) else x for x in (intervals or [])]
            problems = []
            if definite and pts and not (close(pts[0], a, 1e-15, 1e-15) and close(pts[-1], b, 1e-15, 1e-15)):
                problems.append(f"interval {[mpmath.nstr(x, 8) for x in pts]}, website {mpmath.nstr(a, 10)} to {mpmath.nstr(b, 10)}")
            if len(calls) > 1:
                problems.append(f"{len(calls)} calls to mpmath.quad; only the first was compared")
            r, d = compare_on_points(ref_f, f, *lo_hi, rel=SAME_REL_TOL, abs_tol=SAME_ABS_TOL)
            if r == "fail":
                problems.insert(0, f"integrand: {d}")
            bad = r == "fail" or (definite and pts and problems and problems[0].startswith("interval"))
            set_("exact_integral_matches_source", "fail" if bad else r,
                 "; ".join(problems) or d)

    # --- the boxed answer as shown, and ANSWER_VALUE
    answer_exact = None
    try:
        if definite or source is None:
            answer_exact, _ = value_of(to_sympy(spec_tex(cls.ANSWER)))
            is_zero = abs(answer_exact) < mpmath.mpf("1e-25")
            ok = (abs(cls.ANSWER_VALUE) < EXACT_ZERO_TOL) if is_zero else close(cls.ANSWER_VALUE, answer_exact, ANSWER_REL_TOL)
            rel_err = (abs(cls.ANSWER_VALUE - answer_exact) / abs(answer_exact)) if not is_zero else None
            set_("answer_tex_matches_value", "pass" if ok else "fail",
                 f"ANSWER = {mpmath.nstr(answer_exact, 15)}, ANSWER_VALUE = {cls.ANSWER_VALUE!r}"
                 + (f", relative error {mpmath.nstr(rel_err, 3)}" if rel_err is not None else " (exact 0)"))
        else:                                            # indefinite: d/dx of the answer = integrand
            ans = to_sympy(re.sub(r"\+\s*C\s*$", "", spec_tex(cls.ANSWER)))
            avar = [s for s in ans.free_symbols if s.name in VARIABLES]
            if len(avar) != 1:
                raise Unparseable("cannot tell the answer's variable")
            r, d = compare_on_points(ref_f, mp_function(sp.diff(ans, avar[0]), avar[0]), *lo_hi,
                                     rel=1e-12, abs_tol=1e-15)
            set_("answer_tex_matches_value", r, f"derivative of ANSWER vs the integrand: {d}")
    except Unparseable as exc:
        set_("answer_tex_matches_value", "unchecked", f"ANSWER could not be read: {exc}")

    # --- the reference value, two independent ways, from the website's integrand only
    ref_value = None
    abs_tol = QUAD_ABS_TOL
    if definite and src_limit is not None:
        # the limit of the integral itself, two ways (limit_value); never the integral of the
        # pointwise limit, since swapping a limit and an integral is not always allowed
        try:
            v_mp = limit_value(src_limit, "mpmath")
            if integrand is not None:
                lo_s, hi_s = max(a, mpmath.mpf(-50)), min(b, mpmath.mpf(50))
                size = abs(integrate(sp.Abs(integrand), var, lo_s, hi_s, "mpmath"))
            else:
                size = abs(v_mp)
            abs_tol = QUAD_ABS_TOL * size
            v_sp = limit_value(src_limit, "scipy")
            agree = close(v_mp, v_sp, QUAD_REL_TOL, abs_tol)
            set_("quadratures_agree", "pass" if agree else "fail",
                 f"limit of the integral: mpmath {mpmath.nstr(v_mp, 15)} (Richardson), "
                 f"scipy {mpmath.nstr(v_sp, 15)} (polynomial extrapolation)")
            if agree:
                ref_value = v_mp
        except Exception as exc:
            set_("quadratures_agree", "fail", f"the limit could not be computed: {type(exc).__name__}: {exc}")
    elif definite and ref_f is not None:
        try:
            # the absolute allowance scales with the size of the integral (the area under |f|),
            # so a very small integral gets a very small allowance and cannot slip through
            # (over at most [-50, 50]: an oscillating integrand such as sin(x)/x has no finite
            # area under |f| on an infinite range)
            lo_s, hi_s = max(a, mpmath.mpf(-50)), min(b, mpmath.mpf(50))
            size = abs(integrate(sp.Abs(integrand), var, lo_s, hi_s, "mpmath"))
            abs_tol = QUAD_ABS_TOL * size
            v_mp = integrate(integrand, var, a, b, "mpmath")
            v_sp = integrate(integrand, var, a, b, "scipy", scale=float(size))
            agree = close(v_mp, v_sp, QUAD_REL_TOL, abs_tol)
            how = []
            if breakpoints(integrand, var, a, b):
                how.append("split at the corners of |...|")
            if oscillation(integrand, var, a, b):
                how.append("oscillating to infinity: mpmath quadosc, scipy per half-period")
            set_("quadratures_agree", "pass" if agree else "fail",
                 f"mpmath {mpmath.nstr(v_mp, 15)}, scipy {mpmath.nstr(v_sp, 15)}"
                 + (f" ({'; '.join(how)})" if how else ""))
            if agree:
                ref_value = v_mp
        except Exception as exc:
            set_("quadratures_agree", "fail", f"numerical integration failed: {type(exc).__name__}: {exc}")
    elif not definite and ref_f is not None:
        set_("quadratures_agree", "unchecked", "indefinite integral: no single value")

    if ref_value is not None:
        set_("answer_matches_reference",
             "pass" if close(cls.ANSWER_VALUE, ref_value, QUAD_REL_TOL, abs_tol) else "fail",
             f"ANSWER_VALUE {cls.ANSWER_VALUE!r}, reference {mpmath.nstr(ref_value, 15)}")
        if exact_value is not None:
            set_("exact_integral_matches_reference",
                 "pass" if close(exact_value, ref_value, QUAD_REL_TOL, abs_tol) else "fail",
                 f"exact_integral() {mpmath.nstr(exact_value, 15)}, reference {mpmath.nstr(ref_value, 15)}")
    elif not definite and ref_f is not None:
        for c in ("answer_matches_reference", "exact_integral_matches_reference"):
            set_(c, "unchecked", "indefinite integral: no single value")
    else:
        for c in ("answer_matches_reference", "exact_integral_matches_reference"):
            if checks[c]["detail"] == "not run":
                set_(c, "unchecked", "no reference value (see quadratures_agree)")

    # --- the method, line by line
    _check_steps(cls, out, ref_value if definite else None, set_, abs_tol, main_name)
    return _finish(out)


def _graph_range(cls):
    g = getattr(cls, "GRAPH", {}) or {}
    xr = g.get("x_range", [0.1, 1])
    return mpmath.mpf(xr[0]), mpmath.mpf(xr[1])


def _scipy_quad(f, a, b, epsabs=1e-13):
    from scipy import integrate
    from scipy.integrate import IntegrationWarning

    def g(x):
        return float(f(mpmath.mpf(x)))
    lo = -math.inf if a == -mpmath.inf else float(a)
    hi = math.inf if b == mpmath.inf else float(b)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", IntegrationWarning)
        value, err = integrate.quad(g, lo, hi, limit=500, epsabs=epsabs, epsrel=1e-11)
    note = f" (scipy error estimate {err:.1e})"
    if caught:
        note += f"; scipy warned: {str(caught[0].message).splitlines()[0][:80]}"
    return value, note


def _check_steps(cls, out, reference, set_, abs_tol=QUAD_ABS_TOL, main="I"):
    """Each evaluable line must equal the last line that passed (starting from the
    website's own value). check=False lines must carry a red TRAP part and a reason."""
    steps = list(getattr(cls, "STEPS", []))
    colors = getattr(cls, "COLORS", {})
    prev, prev_label = reference, "the website's integral"
    any_fail, misuse, checked = False, [], 0
    for i, step in enumerate(steps, 1):
        tex = spec_tex(step["tex"])
        entry = dict(n=i, tex=tex)
        if step.get("check") is False:
            traps = trap_parts(step["tex"], colors)
            reason = step.get("check_reason")
            out["check_false_lines"].append(f"step {i}: {tex[:70]} | reason: {reason or '(none)'}")
            if not traps:
                misuse.append(f"step {i} uses check=False but no part of it is red (TRAP)")
            if not reason:
                misuse.append(f"step {i} uses check=False without a check_reason")
            entry.update(result="not checked (check=False)", detail=reason or "")
            out["steps"].append(entry)
            continue
        if reference is None:
            entry.update(result="unchecked", detail="no reference value")
            out["unchecked_steps"].append(f"step {i}: {tex[:70]} (no reference value)")
            out["steps"].append(entry)
            continue
        values, unread = line_values(tex, main)
        bad = [v for v in values if not close(v, prev, QUAD_REL_TOL, abs_tol)]
        if bad:
            # before calling a line wrong, do it again the other way: a line fails only if
            # scipy agrees that it differs; if the two methods disagree, it is unchecked
            values2, _ = line_values(tex, main, method="scipy")
            if values2 and not [v for v in values2 if not close(v, prev, QUAD_REL_TOL, abs_tol)]:
                values, unread = [], [f"mpmath gives {mpmath.nstr(bad[0], 12)} but scipy agrees with "
                                      f"{prev_label} ({mpmath.nstr(prev, 12)}): numerical integration unreliable here"]
                bad = []
        if not values:
            entry.update(result="unchecked", detail="; ".join(unread) or "nothing to evaluate")
            out["unchecked_steps"].append(f"step {i}: {tex[:70]} ({entry['detail'][:90]})")
        else:
            if bad:
                any_fail = True
                entry.update(result="fail", detail=f"value {mpmath.nstr(bad[0], 12)} but {prev_label} "
                                                   f"is {mpmath.nstr(prev, 12)}")
            else:
                checked += 1
                entry.update(result="pass", detail=f"= {mpmath.nstr(values[0], 12)}"
                             + (f" (also unread: {'; '.join(unread)})" if unread else ""))
                prev, prev_label = values[0], f"step {i}"
        out["steps"].append(entry)
    if misuse:
        set_("check_false_valid", "fail", "; ".join(misuse))
    else:
        set_("check_false_valid", "pass", f"{len(out['check_false_lines'])} check=False lines, all on red trap lines with reasons")
    if any_fail:
        set_("steps", "fail", "; ".join(f"step {e['n']}: {e['detail']}" for e in out["steps"] if e["result"] == "fail"))
    elif checked == 0:
        set_("steps", "unchecked", f"no line could be evaluated ({len(steps)} lines)")
    else:
        set_("steps", "pass", f"{checked} of {len(steps)} lines checked, {len(out['unchecked_steps'])} unchecked")


def _finish(out):
    out["status"] = "flagged" if any(c["result"] == "fail" for c in out["checks"].values()) else "ready"
    return out


# ---------------------------------------------------------------- the log
def append_log(result, check_text="not run", check_frame="not run", log_path=LOG_PATH):
    """Append one row to verification_log.csv. The attempt number counts earlier rows for
    the same date and level. error_type is left blank (filled in at the publish review)."""
    rows = read_log(log_path)
    attempt = 1 + sum(1 for r in rows if r["date"] == result["date"] and r["level"] == result["level"])
    row = dict(date=result["date"], level=result["level"], attempt=attempt,
               timestamp=dt.datetime.now().astimezone().isoformat(timespec="seconds"))
    for c in CHECKS:
        row[c] = result["checks"][c]["result"]
    row.update(check_text=check_text, check_frame=check_frame,
               unchecked_steps=" || ".join(result["unchecked_steps"]),
               check_false_lines=" || ".join(result["check_false_lines"]),
               script_sha256=result["script_sha256"], video_sha256=result["video_sha256"], error_type="")
    failed = [c for c in CHECKS if row[c] == "fail"] + [c for c in ("check_text", "check_frame") if row[c] == "fail"]
    row["final_status"] = "flagged" if failed else "ready"
    new = not os.path.exists(log_path)
    with open(log_path, "a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=LOG_COLUMNS)
        if new:
            w.writeheader()
        w.writerow(row)
    return row


def read_log(log_path=LOG_PATH):
    if not os.path.exists(log_path):
        return []
    with open(log_path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


# ---------------------------------------------------------------- printing
def report(result):
    lines = [f"=== {result['level']} ({result['date']}): {result['status'].upper()} ==="]
    if result.get("error"):
        lines.append(f"  {result['error']}")
    for c in CHECKS:
        r = result["checks"][c]
        lines.append(f"  {r['result']:9s} {c}: {r['detail']}")
    for e in result["steps"]:
        lines.append(f"    step {e['n']}: {e['result']}  {e['tex'][:60]}  {e.get('detail', '')[:100]}")
    if result["unchecked_steps"]:
        lines.append("  Unchecked steps:")
        lines += [f"    - {u}" for u in result["unchecked_steps"]]
    if result["check_false_lines"]:
        lines.append("  check=False lines:")
        lines += [f"    - {u}" for u in result["check_false_lines"]]
    return "\n".join(lines)


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if not args or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args[0]):
        print(__doc__)
        return 2
    date, levels = args[0], [a for a in args[1:] if a in LEVELS] or LEVELS
    all_ok = True
    for level in levels:
        if not os.path.exists(os.path.join(ROOT, level, f"{date}_{level}.py")):
            print(f"=== {level} ({date}): no script ===")
            all_ok = False
            continue
        res = check_video(date, level)
        print(report(res))
        if "--log" in argv:
            append_log(res)
        all_ok &= res["status"] == "ready"
    print("VERIFY:", "PASS" if all_ok else "FAIL")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
