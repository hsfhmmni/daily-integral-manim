"""Write review/DATE_READY_FOR_REVIEW.md: what the user needs to decide GO or NO-GO.

Usage (from this folder, with the .venv):
    .venv\\Scripts\\python review.py 2026-10-15
    .venv\\Scripts\\python review.py 2026-10-15 --out somewhere\\test.md   (write elsewhere)
    .venv\\Scripts\\python review.py 2026-10-15 --log somewhere\\log.csv   (log elsewhere)

It never publishes anything. For each level of that day (levels.py: Medium and Hard from
2026-10-22) it:
  * finds the script and narration in <Level>/ and the finished video in pending/<Level>/
    (or in <Level>/ if it was already approved), and checks none is missing or empty
  * reads the video's real length with ffprobe
  * re-runs check_text.py and check_frame.py --frames on the finished files itself, instead
    of trusting what the daily run reported, and saves their full output in review/DATE_logs/
  * runs verify.py: every independent check against the website's own TeX (see verify.py),
    listing unchecked steps and check=False lines
  * appends one row per video to verification_log.csv (attempt number, every check's
    result, final status; error_type left blank for the publish review)
  * marks the video READY (every check passed) or FLAGGED (with the reasons)
It also lists what is NOT checked automatically, so the review knows what to look at.

The checks use the shared _media folder, so do not run this while another check or dry run
is using it. Exit code 0 when every video is READY, 1 otherwise.
"""
import glob
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import verify  # noqa: E402

from levels import levels_for  # noqa: E402
NOT_YET_CHECKED = [
    "Captions, mapping lines and Rule Cards contain no maths errors (only their wording and "
    "LaTeX are checked).",
    "The reasoning: a step can have the right value for the wrong reason.",
    "Every step listed above as unchecked, and every check=False line.",
    "That the video shows what the script says (watch it).",
]


def _short(result):
    """check_text / check_frame result for the log: pass, fail or not run."""
    r = result.lower()
    return "pass" if r.startswith("pass") else "fail" if r.startswith("fail") else "not run"


def _cell(text):
    return str(text).replace("|", "\\|").replace("\n", " ")[:160]


def env():
    """PATH with MiKTeX and the WinGet links first (the scheduled shell's PATH can be stale)."""
    local = os.environ.get("LOCALAPPDATA", "")
    extra = [os.path.join(local, "Programs", "MiKTeX", "miktex", "bin", "x64"),
             os.path.join(local, "Microsoft", "WinGet", "Links")]
    return dict(os.environ, PATH=os.pathsep.join(extra + [os.environ.get("PATH", "")]),
                PYTHONIOENCODING="utf-8")


def ffprobe():
    found = shutil.which("ffprobe", path=env()["PATH"])
    if found:
        return found
    hits = glob.glob(os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet", "Packages",
                                  "Gyan.FFmpeg*", "*", "bin", "ffprobe.exe"))
    return hits[0] if hits else None


def video_length(path):
    exe = ffprobe()
    if exe is None:
        return None
    r = subprocess.run([exe, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return None


def run_check(args, log_path):
    """Run a check script, save its full output, return (exit code, output)."""
    r = subprocess.run([sys.executable] + args, cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=env())
    out = (r.stdout or "") + (("\n--- stderr ---\n" + r.stderr) if r.stderr.strip() else "")
    with open(log_path, "w", encoding="utf-8") as fh:
        fh.write(out)
    return r.returncode, out


def files_for(date, level):
    """(script, narration, video, where): where says which folder the video was found in."""
    script = os.path.join(ROOT, level, f"{date}_{level}.py")
    narration = os.path.join(ROOT, level, f"{date}_{level}_narration.txt")
    video = os.path.join(ROOT, "pending", level, f"{date}_{level}.mp4")
    where = "pending (waiting for review)"
    if not os.path.exists(video) and os.path.exists(os.path.join(ROOT, level, f"{date}_{level}.mp4")):
        video = os.path.join(ROOT, level, f"{date}_{level}.mp4")
        where = "level folder (already approved or published)"
    return script, narration, video, where


def size_ok(path):
    return os.path.exists(path) and os.path.getsize(path) > 0


def text_problems_for(output, date, level):
    """check_text problem lines about this level's script, plus lines about shared files."""
    mine, shared = [], []
    for line in output.splitlines():
        s = line.strip()
        if re.match(r"^[\w.\\/-]+:\d+\s+\([a-e]\)", s) or re.match(r"^[\w.\\/-]+\s+\([a-e]\)", s):
            if re.search(rf"{level}[\\/]{date}_{level}\.py", s):
                mine.append(s)
            elif s.startswith(("rules.py", "common.py")):
                shared.append(s)
        elif "LaTeX failed" in s:
            if re.search(rf"{level}[\\/]{date}_{level}\.py", s):
                mine.append(s)
            elif s.startswith(("rules.py", "common.py")):
                shared.append(s)
    return mine, shared


def numeric_line(output, date, level):
    for line in output.splitlines():
        if re.search(rf"{level}[\\/]{date}_{level}\.py: numerical integral", line):
            return line.strip()
    return None


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if not args or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args[0]):
        print(__doc__)
        return 2
    date = args[0]
    out_path = os.path.join(ROOT, "review", f"{date}_READY_FOR_REVIEW.md")
    if "--out" in argv:
        out_path = os.path.abspath(argv[argv.index("--out") + 1])
    log_dir = os.path.join(os.path.dirname(out_path), f"{date}_logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = verify.LOG_PATH
    if "--log" in argv:
        log_path = os.path.abspath(argv[argv.index("--log") + 1])

    print(f"Running check_text.py {date} ...")
    text_code, text_out = run_check(["check_text.py", date], os.path.join(log_dir, "check_text.txt"))
    text_pass = text_code == 0 and "CHECK_TEXT: PASS" in text_out

    LEVELS = levels_for(date)
    results = {}
    for level in LEVELS:
        script, narration, video, where = files_for(date, level)
        flags, info = [], []
        for label, path in (("script", script), ("narration", narration), ("video", video)):
            if not size_ok(path):
                flags.append(f"The {label} is missing or empty: `{os.path.relpath(path, ROOT)}`")
        length = video_length(video) if size_ok(video) else None
        if size_ok(video):
            info.append(f"Video: `{os.path.relpath(video, ROOT)}` ({os.path.getsize(video) / 1e6:.1f} MB, "
                        f"{f'{length:.1f} s' if length else 'length unknown'}), in the {where}")

        mine, shared = text_problems_for(text_out, date, level)
        num = numeric_line(text_out, date, level)
        if num:
            info.append(f"Numbers: {num.split(': ', 1)[1]}")
        if not size_ok(script):
            text_result = "not run (no script)"
        elif mine or shared or not text_pass and not num:
            text_result = "FAIL"
            flags += [f"check_text: `{p}`" for p in mine + shared] or ["check_text did not pass (see the log)"]
        elif not text_pass:
            text_result = "PASS for this video (another file failed; see the log)"
        else:
            text_result = "PASS"

        if size_ok(script) and size_ok(video):
            print(f"Running check_frame.py {date} {level} --frames ...")
            code, out = run_check(["check_frame.py", date, level, "--frames"],
                                  os.path.join(log_dir, f"check_frame_{level}.txt"))
            frame_pass = code == 0 and "OVERALL: PASS" in out
            frame_result = "PASS" if frame_pass else "FAIL"
            m = re.search(r"length ([\d.]+) s", out)
            hold = re.search(r"Hold times: .*", out)
            wm = re.search(r"Watermark.*|.*watermark.*score.*", out, re.I)
            cached = re.search(r"\(cached: identical inputs to the dry run of ([^;]+);", out)
            for x in (m and f"Planned length (dry run): {m.group(1)} s", hold and hold.group(0),
                      cached and f"Dry run: result reused from {cached.group(1)} (script, project code, "
                                 f"settings, package and LaTeX versions all unchanged)",
                      wm and wm.group(0).strip()):
                if x:
                    info.append(x)
            if not frame_pass:
                bad = [l.strip() for l in out.splitlines()
                       if l.startswith("  ") and any(w in l for w in ("outside", "held", "overlap", "missing",
                                                                      "covered", "No watermark", "Length"))]
                flags += [f"check_frame: `{b}`" for b in bad[:10]] or ["check_frame did not pass (see the log)"]
        else:
            frame_result = "not run (script or video missing)"

        # independent checks against the website's TeX, then one row in verification_log.csv
        ver, row = None, None
        if size_ok(script):
            print(f"Running verify.py {date} {level} ...")
            ver = verify.check_video(date, level)
            for name in verify.CHECKS:
                c = ver["checks"][name]
                if c["result"] == "fail":
                    flags.append(f"verify {name}: {c['detail']}")
            if ver.get("error"):
                flags.append(f"verify: {ver['error']}")
            row = verify.append_log(ver, check_text=_short(text_result), check_frame=_short(frame_result),
                                    log_path=log_path)

        results[level] = dict(status="READY" if not flags else "FLAGGED", flags=flags, info=info,
                              text=text_result, frame=frame_result, verify=ver, row=row,
                              files=[os.path.relpath(p, ROOT) for p in (video, script, narration)])

    approved = [lv for lv in LEVELS if results[lv]["files"][0].startswith(lv)]
    if len(approved) == len(LEVELS):
        top = ("**All the videos are already in the level folders (approved or published before "
               "this review).** Nothing here is waiting for a decision.")
    elif approved:
        top = (f"**Already in the level folder (approved or published before this review): "
               f"{', '.join(approved)}.** The rest are waiting for your decision.")
    else:
        top = "**Nothing has been published.** These videos are waiting for your decision."
    lines = [f"# Ready for review: {date}", "",
             top + " Only you publish, by running `publish.py` yourself after watching them.", "",
             "| Level | Status | check_text | check_frame |", "|---|---|---|---|"]
    for level in LEVELS:
        r = results[level]
        lines.append(f"| {level} | **{r['status']}** | {r['text']} | {r['frame']} |")
    for level in LEVELS:
        r = results[level]
        lines += ["", f"## {level}: {r['status']}", ""]
        lines += [f"- `{f}`" for f in r["files"]]
        lines += [f"- {i}" for i in r["info"]]
        if r["flags"]:
            lines += ["", "**Flagged:**"] + [f"- {f}" for f in r["flags"]]
        v = r["verify"]
        if v:
            lines += ["", "**Independent checks (verify.py, against the website's TeX):**", "",
                      "| Check | Result | Detail |", "|---|---|---|"]
            for name in verify.CHECKS:
                c = v["checks"][name]
                lines.append(f"| {name} | {c['result']} | {_cell(c['detail'])} |")
            lines += ["", f"Steps: " + ", ".join(f"{e['n']} {e['result']}" for e in v["steps"])]
            if v["unchecked_steps"]:
                lines += ["", "**Unchecked steps (the computer could not evaluate these; check them yourself):**"]
                lines += [f"- `{u}`" for u in v["unchecked_steps"]]
            if v["check_false_lines"]:
                lines += ["", "**Lines marked check=False (shown as wrong on purpose, in red):**"]
                lines += [f"- `{u}`" for u in v["check_false_lines"]]
            if r["row"]:
                lines += ["", f"Logged in `verification_log.csv` as attempt {r['row']['attempt']} "
                              f"({r['row']['final_status']})."]
    lines += ["", "## Not checked automatically (look at these yourself)", ""]
    lines += [f"- {x}" for x in NOT_YET_CHECKED]
    lines += ["", f"Full check output: `{os.path.relpath(log_dir, ROOT)}`. "
              f"Contact sheets: `_media/frames/<Level>/sheet_*.png`.", ""]
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))

    for level in LEVELS:
        print(f"  {level}: {results[level]['status']}")
    print(f"Review file: {out_path}")
    all_ready = all(r["status"] == "READY" for r in results.values())
    print("REVIEW:", "ALL READY" if all_ready else "SOME FLAGGED")
    return 0 if all_ready else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
