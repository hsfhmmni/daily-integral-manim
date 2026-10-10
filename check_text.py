"""Stop maths from being drawn as plain words, and catch LaTeX mistakes in seconds.

Usage (from this folder, with the .venv):
    .venv\\Scripts\\python check_text.py              # every script + common.py
    .venv\\Scripts\\python check_text.py 2026-10-08   # only that day's scripts (+ common.py)
    .venv\\Scripts\\python check_text.py --no-latex   # skip the LaTeX compile step

It reads the scripts without running them and checks:
  (a) Text / Paragraph / MarkupText strings must not contain maths
      (pi, sqrt, sin, x^2, 3/4, ->, u = ..., -1, ...): Text prints characters literally.
  (b) sentences shown with rich() - IDEA, CHECK, the graph caption, each step's
      "what" and "why", and any rich("...") call - must keep all maths inside $...$.
  (c) every rich() sentence and every MathTex string is compiled with LaTeX, so an
      escaping mistake fails here instead of halfway through a render.

Exit code is 0 when everything passes, 1 otherwise.
"""
import ast
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
FOLDERS = ["Beginner", "Easy", "Medium", "Hard"]
TEXT_CALLS = {"Text", "Paragraph", "MarkupText", "_paragraph"}
MATHTEX_CALLS = {"MathTex"}

# Each pattern finds maths written as plain characters. They run on prose only
# (for rich() strings, everything between $...$ is removed first).
MATH_PATTERNS = [
    (r"\b(?:pi|sqrt|theta|sigma|sin|cos|tan|sec|csc|cot|ln|log|exp|arcsin|arccos|arctan|infty)\b",
     "maths word"),
    (r"\^", "power written with ^"),
    (r"\d\s*/\s*\d|\b[a-z]\s*/\s*[a-z0-9(]|\)\s*/\s*\w", "fraction written with /"),
    (r"->|=>|<=|>=", "arrow or inequality"),
    (r"=", "equation"),
    (r"(?<![\w'’])\d*[xut]\b", "variable x, u or t"),
    (r"(?<![\w$)])-\s?\d", "negative number with a hyphen"),
]


def maths_in_prose(s):
    """Return the descriptions of every maths pattern found in s."""
    found = []
    for pat, what in MATH_PATTERNS:
        m = re.search(pat, s)
        if m:
            found.append(f'{what} "{m.group(0).strip()}"')
    return found


def split_math(s):
    """Split on unescaped $: even items are prose, odd items are maths."""
    return re.split(r"(?<!\\)\$", s)


def _str(node):
    """The literal string in node, or None (implicit concatenation is already one Constant)."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _call_name(node):
    f = node.func
    return f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else None


def _eq_parts(node):
    """The tex strings of an eq(...) call: plain strings or the first item of (tex, COLOUR) tuples."""
    parts = []
    for a in node.args:
        if _str(a) is not None:
            parts.append(_str(a))
        elif isinstance(a, ast.Tuple) and a.elts and _str(a.elts[0]) is not None:
            parts.append(_str(a.elts[0]))
        else:
            return None                                   # computed part: cannot check statically
    return tuple(parts)


def collect(path):
    """Return (text, rich, mathtex, captions): lists of (line, string); mathtex items may
    be tuples of parts (from eq(...)); captions are the cap(...) sentences."""
    tree = ast.parse(open(path, encoding="utf-8").read(), path)
    text, rich, mathtex, captions = [], [], [], []

    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and node.args:
            name = _call_name(node)
            arg = node.args[0]
            if name == "cap" and _str(arg) is not None:
                rich.append((node.lineno, _str(arg)))
                captions.append((node.lineno, _str(arg)))
            elif name == "eq":
                parts = _eq_parts(node)
                if parts:
                    mathtex.append((node.lineno, parts))
            elif name in TEXT_CALLS:
                if isinstance(arg, ast.JoinedStr):          # f-string: check its literal parts
                    s = "".join(v.value for v in arg.values if isinstance(v, ast.Constant))
                    text.append((node.lineno, s))
                elif _str(arg) is not None:
                    text.append((node.lineno, _str(arg)))
            elif name == "rich" and _str(arg) is not None:
                rich.append((node.lineno, _str(arg)))
            elif name in MATHTEX_CALLS:
                for a in node.args:
                    if _str(a) is not None:
                        mathtex.append((node.lineno, _str(a)))

    for node in tree.body:                                   # module-level data of a day's script
        if not isinstance(node, ast.Assign) or not isinstance(node.targets[0], ast.Name):
            continue
        name, val = node.targets[0].id, node.value
        if name in ("IDEA", "CHECK") and _str(val) is not None:
            rich.append((node.lineno, _str(val)))
        elif name in ("PROBLEM", "ANSWER") and _str(val) is not None:
            mathtex.append((node.lineno, _str(val)))
        elif name == "GRAPH":
            pairs = []
            if isinstance(val, ast.Call):
                pairs = [(k.arg, k.value) for k in val.keywords]
            elif isinstance(val, ast.Dict):
                pairs = [(_str(k), v) for k, v in zip(val.keys, val.values)]
            for key, v in pairs:
                if key == "caption" and _str(v) is not None:
                    rich.append((v.lineno, _str(v)))
                elif key in ("a_label", "b_label") and _str(v) is not None:
                    mathtex.append((v.lineno, _str(v)))
        elif name == "STEPS" and isinstance(val, (ast.List, ast.Tuple)):
            for step in val.elts:
                if isinstance(step, ast.Tuple) and len(step.elts) == 3:
                    what, why, tex = step.elts
                    for part in (what, why):
                        if _str(part) is not None:
                            rich.append((part.lineno, _str(part)))
                    if _str(tex) is not None:
                        mathtex.append((tex.lineno, _str(tex)))
    return text, rich, mathtex, captions


def caption_words(text):
    """Same rule as common.caption_words: each $...$ chunk is one word; punctuation is not."""
    tokens = re.sub(r"(?<!\\)\$[^$]*\$", " M ", text).split()
    return sum(1 for t in tokens if re.search(r"\w", t))


def numeric_checks(files):
    """(d) For story-format scripts: the answer matches an mpmath integral, and the final
    rectangle estimate shown in the video is within 1% of it. Returns a list of problems."""
    import importlib.util
    sys.path.insert(0, ROOT)
    import common
    problems = []
    for path in files:
        base = os.path.basename(path)
        m = re.match(r"(\d{4}-\d{2}-\d{2})_(\w+)\.py$", base)
        if not m:
            continue
        spec = importlib.util.spec_from_file_location(base[:-3], path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        cls = getattr(mod, f"{m.group(2)}Integral", None)
        if cls is None or not issubclass(cls, common.IntegralVideo):
            continue                                       # older format: no numeric data
        rel = os.path.relpath(path, ROOT)
        exact = float(cls.exact_integral())
        answer = float(cls.ANSWER_VALUE)
        a, b = cls.window()
        n = cls.COUNTS[-1]
        estimate = common.midpoint_sum(cls.FUNC, a, b, n)
        rel_ans = abs(exact - answer) / max(1.0, abs(exact))
        rel_est = abs(estimate - answer) / abs(answer)
        print(f"  {rel}: numerical integral {exact:.10f}, stated answer {answer:.10f} "
              f"(diff {rel_ans:.1e}); {n}-rectangle estimate {estimate:.6f} ({rel_est * 100:.3f}% off)")
        if rel_ans > 1e-8:
            problems.append(f"{rel}  (d) answer {answer} does not match the numerical integral {exact}")
        if rel_est > 0.01:
            problems.append(f"{rel}  (d) final rectangle estimate {estimate:.6f} is more than 1% from {answer}")
    return problems


def main(argv):
    flags = [a for a in argv if a.startswith("--")]
    dates = [a for a in argv if not a.startswith("--")]
    files = [os.path.join(ROOT, "common.py")]
    for folder in FOLDERS:
        for f in sorted(glob.glob(os.path.join(ROOT, folder, "*.py"))):
            if not dates or any(os.path.basename(f).startswith(d) for d in dates):
                files.append(f)

    problems, to_compile = [], []
    for path in files:
        rel = os.path.relpath(path, ROOT)
        text, rich, mathtex, captions = collect(path)
        for line, s in captions:
            if caption_words(s) > 12:
                problems.append(f"{rel}:{line}  (b) caption has {caption_words(s)} words (max 12): {s[:70]!r}")
        for line, s in text:
            for what in maths_in_prose(s):
                problems.append(f"{rel}:{line}  (a) Text with maths, {what}: {s[:70]!r}")
        for line, s in rich:
            parts = split_math(s)
            if len(parts) % 2 == 0:
                problems.append(f"{rel}:{line}  (b) unbalanced $ in: {s[:70]!r}")
                continue
            prose = " ".join(parts[0::2])
            for what in maths_in_prose(prose):
                problems.append(f"{rel}:{line}  (b) maths outside $...$, {what}: {s[:70]!r}")
            to_compile.append((rel, line, "rich", s))
        for line, s in mathtex:
            to_compile.append((rel, line, "MathTex", s))

    print(f"Scanned {len(files)} files: {len(to_compile)} strings to typeset.")
    for p in problems:
        print("  " + p)

    compile_errors = 0
    if "--no-latex" not in flags:
        sys.path.insert(0, ROOT)
        from manim import MathTex, config, logger
        config.media_dir = os.path.join(ROOT, "_media")
        logger.setLevel("ERROR")
        try:
            from common import rich
        except ImportError:
            rich = None
            problems.append("common.py has no rich() helper")
        for rel, line, kind, s in to_compile:
            try:
                if kind == "rich" and rich is not None:
                    rich(s)
                elif kind == "MathTex":
                    MathTex(*s) if isinstance(s, tuple) else MathTex(s)
            except Exception as exc:                 # LaTeX errors arrive as ValueError
                compile_errors += 1
                shown = "".join(s) if isinstance(s, tuple) else s
                print(f"  {rel}:{line}  (c) LaTeX failed for {kind} {shown[:70]!r}\n      {str(exc).strip()[:300]}")
        print(f"LaTeX compile: {len(to_compile) - compile_errors} ok, {compile_errors} failed")

    if "--no-numeric" not in flags:
        print("Numeric checks:")
        numeric = numeric_checks(files[1:])
        for p in numeric:
            print("  " + p)
        problems += numeric

    ok = not problems and not compile_errors
    print("CHECK_TEXT:", "PASS" if ok else f"FAIL ({len(problems)} text problems, {compile_errors} LaTeX failures)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
