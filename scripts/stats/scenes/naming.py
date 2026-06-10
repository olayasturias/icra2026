"""Manim scene: "How ICRA 2026 names things".

One sequenced video stepping through five panels built from
data/stats/naming.json (produced by scripts/stats/naming_stats.py):

    title card -> title patterns -> title length -> how titles open
               -> most-reused acronyms -> domain themes

Style mirrors the cvpr2026 dashboard (accent blue on white). Uses Text only
(no LaTeX). Render:

    python -m manim -qh --media_dir data/charts scripts/stats/scenes/naming.py NamingScene
    (+ --format gif  for the GIF, + -s  for a final-frame PNG)
"""

from __future__ import annotations

import json
from pathlib import Path

from manim import (
    BOLD, DOWN, LEFT, RIGHT, UP, Create, FadeIn, FadeOut, GrowFromEdge,
    LaggedStart, Line, Rectangle, Scene, Succession, Text, VGroup,
    ValueTracker, Write, always_redraw,
)

# scripts/stats/scenes/naming.py -> repo root is three parents up.
ROOT = Path(__file__).resolve().parents[3]
STATS = json.loads((ROOT / "data" / "stats" / "naming.json").read_text(encoding="utf-8"))

# Palette (mirrors cvpr2026 build_dashboard.py).
BG = "#ffffff"
TEXT = "#20242b"
MUTED = "#6a7079"
RULE = "#e7e7e4"
ACCENT = "#0b5fb0"
ACCENT2 = "#3a7ec0"

TOTAL = STATS["total"]

# Plot area for horizontal-bar panels.
BAR_X0 = -3.0       # left edge of every bar (x units)
BAR_MAX_W = 6.3     # width of the longest bar
TOP_Y = 2.4         # y of the top row
AREA_H = 5.0        # vertical span used by the rows


def _fmt_value(cur: float, show_pct: bool) -> str:
    """Label text for the current (animated) value: integer count, plus a
    percentage of the corpus when show_pct (1 decimal under 1%)."""
    n = int(round(cur))
    if not show_pct:
        return f"{n}"
    pct = 100 * cur / TOTAL
    return f"{n}  ({pct:.0f}%)" if pct >= 1 else f"{n}  ({pct:.1f}%)"


class NamingScene(Scene):
    def construct(self):
        self.camera.background_color = BG
        self._title_card()
        self._hbars("Title patterns (of %d)" % TOTAL, STATS["patterns"],
                    ACCENT, show_pct=True)
        self._histogram()
        self._hbars("How titles open", STATS["first_words"], ACCENT2,
                    show_pct=False, cap=12)
        self._hbars("Most-reused acronyms / tech terms", STATS["acronyms"],
                    ACCENT2, show_pct=False)
        self._hbars("Domain themes in titles", STATS["themes"], ACCENT,
                    show_pct=True, hold=True)
        self.wait(1.5)

    # --- panels ------------------------------------------------------------

    def _title_card(self):
        title = Text("How ICRA 2026 names things", font_size=52,
                     color=TEXT, weight=BOLD)
        sub = Text(f"{TOTAL} papers · title linguistics", font_size=28,
                   color=MUTED)
        sub.next_to(title, DOWN, buff=0.4)
        rule = Line(LEFT * 3, RIGHT * 3, color=ACCENT, stroke_width=3)
        rule.next_to(sub, DOWN, buff=0.5)
        self.play(Write(title), run_time=1.4)
        self.play(FadeIn(sub, shift=UP * 0.2), Create(rule), run_time=1.0)
        self.wait(1.2)
        self.play(FadeOut(VGroup(title, sub, rule)), run_time=0.7)

    def _hbars(self, title, mapping, color, show_pct, cap=None, hold=False):
        items = sorted(mapping.items(), key=lambda kv: kv[1], reverse=True)
        if cap:
            items = items[:cap]
        heading = Text(title, font_size=32, color=TEXT, weight=BOLD)
        heading.to_edge(UP, buff=0.55).to_edge(LEFT, buff=0.8)

        maxv = max((v for _, v in items), default=1) or 1
        n = len(items)
        gap = AREA_H / max(n, 1)
        bar_h = min(0.34, gap * 0.62)
        fs = 24 if n <= 9 else (21 if n <= 12 else 18)
        vfs = max(fs - 2, 16)

        labels, bars, values, rows = VGroup(), VGroup(), VGroup(), []
        for i, (label, val) in enumerate(items):
            y = TOP_Y - i * gap
            lab = Text(label, font_size=fs, color=TEXT)
            lab.next_to([BAR_X0, y, 0], LEFT, buff=0.22)
            labels.add(lab)

            # One tracker per row drives width, label position, and the count.
            # A row's bar/count stay hidden (tracker at 0) until the row's turn.
            tr = ValueTracker(0.0)

            def bar_redraw(tr=tr, y=y):
                w = max(BAR_MAX_W * tr.get_value() / maxv, 1e-3)
                return Rectangle(width=w, height=bar_h, fill_color=color,
                                 fill_opacity=0.0 if tr.get_value() <= 0 else 1.0,
                                 stroke_width=0).move_to([BAR_X0 + w / 2, y, 0])

            def val_redraw(tr=tr, y=y):
                w = max(BAR_MAX_W * tr.get_value() / maxv, 1e-3)
                t = Text(_fmt_value(tr.get_value(), show_pct),
                         font_size=vfs, color=MUTED)
                t.next_to([BAR_X0 + w, y, 0], RIGHT, buff=0.16)
                return t.set_opacity(0.0 if tr.get_value() <= 0 else 1.0)

            bars.add(always_redraw(bar_redraw))
            values.add(always_redraw(val_redraw))
            rows.append((lab, tr, val))

        self.play(FadeIn(heading, shift=DOWN * 0.2), run_time=0.7)
        self.add(bars, values)  # invisible until each row's tracker moves
        # Per row: the name appears, then its bar loads 0->value (count riding
        # the tip). LaggedStart staggers rows so the next name comes in shortly
        # after the previous bar has started loading.
        seqs = [Succession(FadeIn(lab, run_time=0.28),
                           tr.animate(run_time=0.95).set_value(val))
                for lab, tr, val in rows]
        self.play(LaggedStart(*seqs, lag_ratio=0.42))
        # Freeze redraws so the held/poster frame is stable and cheap to render.
        for m in (*bars, *values):
            m.clear_updaters()
        self.wait(1.4)
        if not hold:  # keep the last panel on screen for the poster frame
            self.play(FadeOut(VGroup(heading, labels, bars, values)), run_time=0.6)

    def _histogram(self):
        heading = Text("Title length (words)", font_size=32, color=TEXT,
                       weight=BOLD)
        heading.to_edge(UP, buff=0.55).to_edge(LEFT, buff=0.8)
        hist = {int(k): v for k, v in STATS["length"]["hist"].items()}
        lo, hi = min(hist), max(hist)
        xs = list(range(lo, hi + 1))
        vals = [hist.get(x, 0) for x in xs]
        maxv = max(vals) or 1
        n = len(xs)
        plot_w, plot_h = 11.0, 4.2
        x0 = -plot_w / 2
        base_y = -2.6
        slot = plot_w / n
        bw = slot * 0.8

        axis = Line([x0, base_y, 0], [x0 + plot_w, base_y, 0],
                    color=RULE, stroke_width=2)
        bars, ticks = VGroup(), VGroup()
        for i, (x, v) in enumerate(zip(xs, vals)):
            h = plot_h * v / maxv
            cx = x0 + slot * (i + 0.5)
            bar = Rectangle(width=bw, height=max(h, 0.02), fill_color=ACCENT,
                            fill_opacity=1.0, stroke_width=0)
            bar.move_to([cx, base_y + h / 2, 0])
            bars.add(bar)
            if x % 2 == 0:  # label every other bin to avoid crowding
                t = Text(str(x), font_size=16, color=MUTED)
                t.next_to([cx, base_y, 0], DOWN, buff=0.15)
                ticks.add(t)
        med = STATS["length"]["median"]
        cap = Text(f"median {med} words", font_size=22, color=MUTED)
        cap.to_edge(RIGHT, buff=1.0).set_y(2.0)

        self.play(FadeIn(heading, shift=DOWN * 0.2), Create(axis), run_time=0.8)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars],
                              lag_ratio=0.03), run_time=1.8)
        self.play(FadeIn(ticks), FadeIn(cap), run_time=0.7)
        self.wait(1.6)
        self.play(FadeOut(VGroup(heading, axis, bars, ticks, cap)), run_time=0.6)
