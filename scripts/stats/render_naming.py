#!/usr/bin/env python
"""Render the naming figure to mp4 (1080p) + GIF + final-frame PNG in one go.

Runs the Manim scene three times with different output flags. Ensures an
`ffmpeg` binary is reachable (falls back to the one bundled with
imageio-ffmpeg). Outputs land under data/charts/ (Manim's media tree).

Run with the project venv's Python:
    .venv/Scripts/python scripts/stats/render_naming.py
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCENE = ROOT / "scripts" / "stats" / "scenes" / "naming.py"
MEDIA = ROOT / "data" / "charts"
# Per-artifact quality: crisp 1080p mp4 + poster, but a light 480p15 GIF
# (a 1080p60 GIF buffers every frame and OOMs, and would be enormous anyway).
Q_VIDEO = "-qh"   # 1080p60
Q_GIF = "-ql"     # 480p15
Q_PNG = "-qh"     # 1080p poster


def ensure_ffmpeg() -> None:
    """Manim shells out to `ffmpeg`; if it's not on PATH, expose the
    imageio-ffmpeg binary as `ffmpeg` next to the current interpreter."""
    if shutil.which("ffmpeg"):
        return
    try:
        import imageio_ffmpeg
    except ImportError:
        print("WARNING: no ffmpeg and imageio-ffmpeg not installed", file=sys.stderr)
        return
    src = Path(imageio_ffmpeg.get_ffmpeg_exe())
    dst = Path(sys.executable).parent / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")
    if not dst.exists():
        shutil.copy2(src, dst)
    os.environ["PATH"] = str(dst.parent) + os.pathsep + os.environ.get("PATH", "")


def run(quality: str, extra: list[str]) -> None:
    cmd = [sys.executable, "-m", "manim", quality, "--media_dir", str(MEDIA),
           *extra, str(SCENE), "NamingScene"]
    print("›", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main() -> None:
    ensure_ffmpeg()
    MEDIA.mkdir(parents=True, exist_ok=True)
    run(Q_VIDEO, [])                # mp4 1080p
    run(Q_GIF, ["--format", "gif"])  # gif 480p
    run(Q_PNG, ["-s"])             # final-frame PNG
    print(f"\nDone. Outputs under {MEDIA}")


if __name__ == "__main__":
    main()
