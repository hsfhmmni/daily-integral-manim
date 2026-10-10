"""Check that nothing in a day's videos leaves the safe area, overlaps text, or is unreadably small.

Usage (from this folder, with the .venv):
    .venv\\Scripts\\python check_frame.py 2026-10-07                  # all three difficulties
    .venv\\Scripts\\python check_frame.py 2026-10-07 Easy             # just one
    .venv\\Scripts\\python check_frame.py 2026-10-07 --frames         # also grab still frames

It runs each scene as a fast low-quality dry run (same layout, no video written) with
the frame guard from common.py switched to "collect" mode, so instead of stopping at
the first problem it lists every one. The guard checks, after every animation:
  * every object stays inside the safe area (0.4 from each frame edge)
  * no text block overlaps text from another block
  * nothing touches the corner badge or the problem line at the top
  * no text was shrunk below a readable size
During a real render the same guard runs in "raise" mode and stops the render.

With --frames it also pulls one still from the rendered DATE_Difficulty.mp4 at the end of
every pause, into _media/frames/<Difficulty>/, plus 2x2 contact sheets, so a person
(or Claude) can look at them. Run this after rendering.

Exit code is 0 when every checked video passes, 1 otherwise.
"""
import glob
import importlib.util
import json
import os
import shutil
import stat
import subprocess
import sys

from manim import *

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import common  # noqa: E402

DIFFICULTIES = ["Beginner", "Easy", "Medium", "Hard"]


def check_scene(date, diff):
    """Dry-run one scene and return (passed, list of (pause time, section))."""
    script = os.path.join(ROOT, diff, f"{date}_{diff}.py")
    spec = importlib.util.spec_from_file_location(f"{date}_{diff}", script)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    base = getattr(mod, f"{diff}Integral")

    common.GUARD_MODE = "collect"
    common.GUARD_LOG.clear()
    pauses = []

    class Measured(base):
        def wait(self, *a, **k):
            super().wait(*a, **k)
            pauses.append((round(self.renderer.time - 0.1, 2), getattr(self, "_guard_section", "Intro")))

    scene = None
    with tempconfig({"dry_run": True, "disable_caching": True, "quality": "low_quality",
                     "media_dir": os.path.join(ROOT, "_media")}):
        scene = Measured()
        scene.render()

    unique = {}
    for section, n, msg in common.GUARD_LOG:
        unique.setdefault(msg, (section, n))
    length = scene.renderer.time
    print(f"\n=== {diff} ({date}): {getattr(scene, '_guard_count', 0)} animations checked, "
          f"length {length:.1f} s ===")
    print(f"Layout problems: {len(unique)}")
    for msg, (section, n) in sorted(unique.items(), key=lambda kv: kv[1][1]):
        print(f"  [{section}] after animation #{n}: {msg}")
    passed = not unique and getattr(scene, "_guard_installed", False)
    if not getattr(scene, "_guard_installed", False):
        print("  The frame guard was not installed (scene does not call solve()).")
    if isinstance(scene, common.IntegralVideo):     # the new story format also has a length target
        lo, hi = common.TARGET_LENGTH
        if not lo <= length <= hi:
            print(f"  Length {length:.1f} s is outside the target {lo}-{hi} s.")
            passed = False
        keys = getattr(scene, "_keyframes", [])
        if keys:
            pauses = keys                            # key moments: hook, rectangles, insight, morph, answer
    print("RESULT:", "PASS" if passed else "FAIL")
    return passed, pauses


def _ffmpeg():
    found = shutil.which("ffmpeg")
    if found:
        return found
    pattern = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet",
                           "Packages", "Gyan.FFmpeg*", "*", "bin", "ffmpeg.exe")
    hits = glob.glob(pattern)
    return hits[0] if hits else None


def _force_remove(func, path, _exc):
    """rmtree helper: folders here can carry the read-only flag, which blocks deletion."""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def extract_frames(date, diff, pauses, low=False):
    """Stills at each key moment (or pause), plus labelled contact sheets.

    low=True reads the -ql review render in _media/videos/<name>/480p15/.
    """
    name = f"{date}_{diff}"
    video = (os.path.join(ROOT, "_media", "videos", name, "480p15", f"{name}.mp4") if low
             else os.path.join(ROOT, diff, f"{name}.mp4"))
    ff = _ffmpeg()
    if not os.path.exists(video) or ff is None:
        print(f"  (skipping frames: {'no video yet at ' + video if ff else 'ffmpeg not found'})")
        return
    out = os.path.join(ROOT, "_media", "frames", diff)
    if os.path.isdir(out):
        shutil.rmtree(out, onerror=_force_remove)
    os.makedirs(out)
    font = "C\\:/Windows/Fonts/arial.ttf"
    for i, (t, label) in enumerate(pauses, 1):
        text = f"{i:02d}  {label}  t={t:.1f}s".replace(":", "\\:").replace("'", "")
        subprocess.run([ff, "-v", "error", "-y", "-ss", str(t), "-i", video, "-frames:v", "1",
                        "-vf", f"drawtext=fontfile='{font}':text='{text}':x=8:y=8:fontsize=h/22:"
                               "fontcolor=white:box=1:boxcolor=black@0.6",
                        os.path.join(out, f"{i:02d}.png")], check=True)
    tile = "3x3" if len(pauses) > 4 else "2x2"
    subprocess.run([ff, "-v", "error", "-y", "-start_number", "1", "-i",
                    os.path.join(out, "%02d.png"), "-vf", f"pad=iw+8:ih+8:4:4:red,tile={tile}",
                    os.path.join(out, "sheet_%d.png")], check=True)
    with open(os.path.join(out, "frames.json"), "w") as fh:
        json.dump([{"file": f"{i:02d}.png", "time": t, "section": s}
                   for i, (t, s) in enumerate(pauses, 1)], fh, indent=1)
    print(f"  {len(pauses)} frames + contact sheets saved in {out}")


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    date, wanted = args[0], args[1:]
    if not wanted:
        wanted = [d for d in DIFFICULTIES
                  if os.path.exists(os.path.join(ROOT, d, f"{date}_{d}.py"))]
    if not wanted:
        print(f"No scripts found for {date}. Check the date (YYYY-MM-DD).")
        return 1
    all_ok = True
    for diff in wanted:
        ok, pauses = check_scene(date, diff)
        all_ok &= ok
        if "--frames" in argv:
            extract_frames(date, diff, pauses, low="--low" in argv)
    print("\nOVERALL:", "PASS" if all_ok else "FAIL")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
