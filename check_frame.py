"""Check that nothing in a day's videos leaves the safe area, overlaps text, or is unreadably small.

Usage (from this folder, with the .venv):
    .venv\\Scripts\\python check_frame.py 2026-10-07                  # all three difficulties
    .venv\\Scripts\\python check_frame.py 2026-10-07 Easy             # just one
    .venv\\Scripts\\python check_frame.py 2026-10-07 --frames         # also grab still frames
    .venv\\Scripts\\python check_frame.py 2026-10-07 --fresh          # never reuse a cached dry run
    .venv\\Scripts\\python check_frame.py 2026-10-10 Medium --dir _upgrade_test --name 2026-10-10_Medium_v2
        (a script in another folder; --name is the -o name of its review render)

It runs each scene as a fast low-quality dry run (same layout, no video written) with
the frame guard from common.py switched to "collect" mode, so instead of stopping at
the first problem it lists every one. The guard checks, after every animation:
  * every object stays inside the safe area (0.4 from each frame edge)
  * no text block overlaps text from another block
  * nothing touches the corner badge or the problem line at the top
  * no text was shrunk below a readable size
  * the watermark is on screen, in the foreground, and nothing touches it
It also checks the length (Beginner 90-180 s, Easy 90-180 s, Medium 90-210 s) and that
every caption and Rule Card beat stayed on screen for its read time.
During a real render the same guard runs in "raise" mode and stops the render.

With --frames it also pulls one still from the rendered DATE_Difficulty.mp4 at the end of
every pause, into _media/frames/<Difficulty>/, plus 2x2 contact sheets, so a person
(or Claude) can look at them, and samples a frame every 2 s to confirm the watermark
is visible in each (compared with a reference crop rendered from common.make_watermark).
Run this after rendering.

The dry run is deterministic, so its result is saved in _media/dryrun_cache.json under a
fingerprint of everything that can change it: the script, every .py file and manim.cfg in
this folder, the Python and package versions and the LaTeX version. While none of these has
changed, the same report is printed again with a "(cached: ...)" line instead of a new dry
run (about 1-2 minutes per video saved each time). --fresh always runs it. --frames always
reads the video itself and checks the watermark again.

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


# ---- result cache: the dry run is deterministic, so identical inputs give an identical result
CACHE_PATH = os.path.join(ROOT, "_media", "dryrun_cache.json")
CACHE_KEEP = 300                                   # newest entries kept
PACKAGES = ("manim", "numpy", "scipy", "sympy", "mpmath", "pycairo", "manimpango", "pillow", "networkx",
            "skia-pathops", "svgelements", "watchdog", "decorator", "isosurfaces", "moderngl", "srt", "typing-extensions")


def fingerprint(date, diff, script):
    """SHA-256 of everything that can change a dry run's result: the script, every .py file in
    the project folder (common.py, rules.py, this file, ...), manim.cfg, the Python and package
    versions, and the LaTeX version. Any change to any of them gives a new fingerprint."""
    import hashlib
    import importlib.metadata as md
    h = hashlib.sha256()

    def add(label, data):
        data = data if isinstance(data, bytes) else data.encode()
        h.update(f"{label}:{len(data)}:".encode() + data)       # length-prefixed: no two inputs can blur
    add("job", f"{date}|{diff}|{os.path.relpath(script, ROOT)}")
    add("script", open(script, "rb").read())
    for path in sorted(glob.glob(os.path.join(ROOT, "*.py")) + glob.glob(os.path.join(ROOT, "*.cfg"))):
        add(os.path.basename(path), open(path, "rb").read())
    add("python", sys.version)
    for pkg in PACKAGES:
        try:
            add(pkg, md.version(pkg))
        except md.PackageNotFoundError:
            add(pkg, "-")
    try:
        latex = subprocess.run(["latex", "--version"], capture_output=True, text=True).stdout.splitlines()[:2]
    except OSError:
        latex = ["no latex"]
    add("latex", " / ".join(latex))
    return h.hexdigest()


def _read_cache():
    try:
        return json.load(open(CACHE_PATH, encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _write_cache(cache):
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    newest = sorted(cache.items(), key=lambda kv: kv[1]["saved_at"])[-CACHE_KEEP:]
    tmp = CACHE_PATH + ".part"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(dict(newest), fh, indent=1)
    os.replace(tmp, CACHE_PATH)


def check_scene(date, diff, folder=None, fresh=False):
    """Dry-run one scene and return (passed, list of (pause time, section)).

    The dry run is deterministic, so its result is saved under fingerprint() and reused while
    nothing that could change it has changed: the same report is printed again, with a line
    saying it was reused. fresh=True (--fresh) always runs it."""
    import datetime as dt
    script = os.path.join(folder or os.path.join(ROOT, diff), f"{date}_{diff}.py")
    key = fingerprint(date, diff, script)
    cache = _read_cache()
    hit = None if fresh else cache.get(key)
    if hit is not None:
        lines = hit["lines"]
        for i, line in enumerate(lines):
            print(line)
            if i == 0:
                print(f"(cached: identical inputs to the dry run of {hit['saved_at']}; use --fresh to re-run)")
        return hit["passed"], [tuple(p) for p in hit["pauses"]]
    lines = []

    def say(*parts):
        text = " ".join(str(p) for p in parts)      # like print(): say("RESULT:", "PASS")
        print(text)
        lines.append(text)
    passed, pauses = _dry_run(date, diff, folder, say)
    cache = _read_cache()                         # re-read: another check may have saved meanwhile
    cache[key] = dict(lines=lines, passed=bool(passed), pauses=[list(p) for p in pauses],
                      saved_at=dt.datetime.now().astimezone().isoformat(timespec="seconds"))
    _write_cache(cache)
    return passed, pauses


def _dry_run(date, diff, folder, say):
    """Dry-run one scene, reporting through say(); returns (passed, list of (pause time, section))."""
    script = os.path.join(folder or os.path.join(ROOT, diff), f"{date}_{diff}.py")
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
    say(f"\n=== {diff} ({date}): {getattr(scene, '_guard_count', 0)} animations checked, "
          f"length {length:.1f} s ===")
    say(f"Layout problems: {len(unique)}")
    for msg, (section, n) in sorted(unique.items(), key=lambda kv: kv[1][1]):
        say(f"  [{section}] after animation #{n}: {msg}")
    passed = not unique and getattr(scene, "_guard_installed", False)
    if not getattr(scene, "_guard_installed", False):
        say("  The frame guard was not installed (scene does not call solve()).")
    if isinstance(scene, common.IntegralVideo):     # the new story format also has a length target
        lo, hi = common.TARGET_LENGTHS.get(diff, common.TARGET_LENGTH)
        if not lo <= length <= hi:
            say(f"  Length {length:.1f} s is outside the target {lo}-{hi} s.")
            passed = False
        short = [(t, a, b, need) for t, a, b, need in getattr(scene, "_caption_log", [])
                 if b is not None and b - a < need - 0.05]
        log = getattr(scene, "_caption_log", [])
        say(f"Hold times: {len(log) - len(short)} of {len(log)} captions and card beats held "
              f"for their read time")
        for t, a, b, need in short:
            say(f"  held {b - a:.1f} s < {need:.1f} s at t={a:.1f}: {t[:70]!r}")
            passed = False
        if getattr(scene, "_watermark", None) is None:
            say("  No watermark: IntegralVideo.construct must call add_watermark().")
            passed = False
        keys = getattr(scene, "_keyframes", [])
        if keys:
            pauses = keys                            # key moments: hook, rectangles, insight, morph, answer
    say("RESULT:", "PASS" if passed else "FAIL")
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


def _watermark_reference(width, height):
    """The watermark alone on the background, rendered at the video's size: (gray image,
    pixel box left, top, right, bottom)."""
    import numpy as np
    with tempconfig({"pixel_width": width, "pixel_height": height,
                     "background_color": common.BACKGROUND, "media_dir": os.path.join(ROOT, "_media")}):
        cam = Camera()
        wm = common.make_watermark()
        cam.capture_mobject(wm)
        img = np.asarray(cam.get_image().convert("L"), dtype=float)
    l, r, b, t = common.watermark_box()
    fw, fh = config.frame_width, config.frame_height
    px = lambda x: int(round((x + fw / 2) / fw * width))
    py = lambda y: int(round((fh / 2 - y) / fh * height))
    return img, (px(l), py(t), px(r), py(b))


def check_watermark(video, out, every=2.0):
    """Sample one frame every `every` seconds and compare the watermark corner with a
    reference crop. Returns (number of frames, list of failing times)."""
    import numpy as np
    from PIL import Image
    ff = _ffmpeg()
    probe = os.path.join(out, "_probe.png")
    subprocess.run([ff, "-v", "error", "-y", "-i", video, "-frames:v", "1", probe], check=True)
    width, height = Image.open(probe).size
    os.remove(probe)
    ref, (l, t, r, b) = _watermark_reference(width, height)
    pad, slack = max(4, width // 240), max(3, width // 480)
    x0, y0 = max(0, l - pad - slack), max(0, t - pad - slack)
    x1, y1 = min(width, r + pad + slack), min(height, b + pad + slack)
    ref_crop = ref[t - pad:b + pad, l - pad:r + pad]
    wm_dir = os.path.join(out, "watermark")
    os.makedirs(wm_dir, exist_ok=True)
    subprocess.run([ff, "-v", "error", "-y", "-i", video, "-vf",
                    f"fps=1/{every},crop={x1 - x0}:{y1 - y0}:{x0}:{y0}",
                    os.path.join(wm_dir, "wm_%04d.png")], check=True)
    rz = (ref_crop - ref_crop.mean()) / (ref_crop.std() + 1e-9)
    files = sorted(glob.glob(os.path.join(wm_dir, "wm_*.png")))
    bad, scores = [], []
    for i, f in enumerate(files):
        crop = np.asarray(Image.open(f).convert("L"), dtype=float)
        best = -1.0
        for dy in range(0, 2 * slack + 1):
            for dx in range(0, 2 * slack + 1):
                w = crop[dy:dy + ref_crop.shape[0], dx:dx + ref_crop.shape[1]]
                if w.shape != ref_crop.shape:
                    continue
                wz = (w - w.mean()) / (w.std() + 1e-9)
                best = max(best, float((wz * rz).mean()))
        scores.append(best)
        if best < 0.6:
            bad.append((round(i * every, 1), round(best, 2)))
    Image.fromarray(ref_crop.astype("uint8")).save(os.path.join(wm_dir, "reference.png"))
    print(f"  Watermark: {len(files) - len(bad)} of {len(files)} sampled frames (every {every:g} s) match "
          f"the reference (lowest score {min(scores) if scores else 0:.2f}, pass >= 0.60)")
    for t_, sc in bad:
        print(f"    missing or covered at t={t_} s (score {sc})")
    return len(files), bad


def extract_frames(date, diff, pauses, low=False, folder=None, name=None):
    """Stills at each key moment (or pause), plus labelled contact sheets, plus the
    watermark check on a frame every 2 s. Returns False if the watermark check fails.

    low=True reads the -ql review render in _media_<Difficulty>/videos/<script name>/480p15/
    (each difficulty renders into its own media folder so the three can run in parallel),
    falling back to the older shared _media/ folder.
    folder: where the script and final video live (default the difficulty folder, then
    pending/<Difficulty>/ for a final video that is not approved yet);
    name: the -o name of the review render (default DATE_Difficulty).
    """
    script_name = f"{date}_{diff}"
    name = name or script_name
    if low:
        video = os.path.join(ROOT, f"_media_{diff}", "videos", script_name, "480p15", f"{name}.mp4")
        if not os.path.exists(video):
            video = os.path.join(ROOT, "_media", "videos", script_name, "480p15", f"{name}.mp4")
    else:
        video = os.path.join(folder or os.path.join(ROOT, diff), f"{script_name}.mp4")
        if folder is None and not os.path.exists(video):       # not approved yet: waiting in pending/
            video = os.path.join(ROOT, "pending", diff, f"{script_name}.mp4")
    ff = _ffmpeg()
    if not os.path.exists(video) or ff is None:
        print(f"  (skipping frames: {'no video yet at ' + video if ff else 'ffmpeg not found'})")
        return False
    out = os.path.join(ROOT, "_media", "frames", diff if folder is None
                       else os.path.basename(os.path.normpath(folder)) + "_" + diff)
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
    n, bad = check_watermark(video, out)
    return n > 0 and not bad


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    folder = name = None
    if "--dir" in argv:
        folder = os.path.join(ROOT, argv[argv.index("--dir") + 1])
        args = [a for a in args if os.path.join(ROOT, a) != folder]
    if "--name" in argv:
        name = argv[argv.index("--name") + 1]
        args = [a for a in args if a != name]
    date, wanted = args[0], args[1:]
    if not wanted:
        wanted = [d for d in DIFFICULTIES
                  if os.path.exists(os.path.join(folder or os.path.join(ROOT, d), f"{date}_{d}.py"))]
    if not wanted:
        print(f"No scripts found for {date}. Check the date (YYYY-MM-DD).")
        return 1
    all_ok = True
    for diff in wanted:
        ok, pauses = check_scene(date, diff, folder, fresh="--fresh" in argv)
        all_ok &= ok
        if "--frames" in argv:
            all_ok &= extract_frames(date, diff, pauses, low="--low" in argv, folder=folder, name=name)
    print("\nOVERALL:", "PASS" if all_ok else "FAIL")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
