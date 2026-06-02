"""Render site/demo-trace.json into a self-contained MP4.

Cycles through every scenario with a title card, top-down workspace view,
robot trail, intervention markers, and a side panel listing the events
as they fire. Output: site/assets/demo.mp4 (also written to site/demo.mp4
for backward compat).

Usage:
    python -m scripts.render_video
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import imageio_ffmpeg
import matplotlib

matplotlib.use("Agg")
os.environ.setdefault("IMAGEIO_FFMPEG_EXE", imageio_ffmpeg.get_ffmpeg_exe())
matplotlib.rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()

import matplotlib.animation as anim  # noqa: E402
import matplotlib.patches as patches  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

TRACE_PATH = Path("site/demo-trace.json")
OUT_PATH = Path("site/assets/demo.mp4")
FPS = 12
TITLE_FRAMES = FPS * 2  # 2-second title card per scenario

BG = "#0b1020"
PANEL = "#121a33"
INK = "#e7ecf3"
MUTED = "#97a1b8"
ACCENT = "#6ee7b7"
ACCENT2 = "#93c5fd"
WARN = "#fca5a5"
INT = "#fbbf24"


def main() -> None:
    trace = json.loads(TRACE_PATH.read_text(encoding="utf-8"))
    polygon = trace["robot"]["workspace_polygon"]
    obstacles = trace["robot"].get("obstacles", [])
    scenarios = trace["scenarios"]

    # Pre-compute per-scenario frame plans.
    plans = []
    for sc in scenarios:
        plans.append({"kind": "title", "scenario": sc, "n": TITLE_FRAMES})
        plans.append(
            {"kind": "play", "scenario": sc, "n": len(sc["samples"])}
        )
    total = sum(p["n"] for p in plans)

    fig = plt.figure(figsize=(12.8, 7.2), dpi=120, facecolor=BG)
    gs = fig.add_gridspec(1, 2, width_ratios=[1.05, 1.0], wspace=0.08)
    ax = fig.add_subplot(gs[0, 0])
    side = fig.add_subplot(gs[0, 1])

    for a in (ax, side):
        a.set_facecolor(BG)
        for spine in a.spines.values():
            spine.set_color("#233055")

    # Workspace static elements
    ax.set_xlim(-1.6, 1.6)
    ax.set_ylim(-1.6, 1.6)
    ax.set_aspect("equal")
    ax.tick_params(colors=MUTED)
    ax.set_title("Workspace (top-down)", color=INK, fontsize=14, pad=12)
    poly_patch = patches.Polygon(
        polygon, closed=True, fill=False, edgecolor="#6b7280",
        linewidth=2.0, linestyle="--",
    )
    ax.add_patch(poly_patch)
    for ox, oy in obstacles:
        ax.add_patch(patches.Circle(
            (ox, oy), 0.05, color=WARN, alpha=0.9, zorder=3
        ))
        ax.text(ox + 0.08, oy, "human", color=WARN, fontsize=9, va="center")
    ax.axhline(0, color="#1d2750", lw=0.8, zorder=0)
    ax.axvline(0, color="#1d2750", lw=0.8, zorder=0)

    side.axis("off")
    side.set_xlim(0, 1)
    side.set_ylim(0, 1)

    # Mutable artists
    trail_line, = ax.plot([], [], color=ACCENT, lw=2.2, zorder=4)
    robot_dot, = ax.plot([], [], "o", color=ACCENT, ms=11, zorder=5)
    cmd_arrow = ax.annotate(
        "", xy=(0, 0), xytext=(0, 0),
        arrowprops=dict(arrowstyle="->", color=ACCENT2, lw=1.6),
    )
    intervention_dots, = ax.plot([], [], "o", color=INT, ms=6, zorder=4)

    title_text = fig.text(
        0.04, 0.94, "", color=INK, fontsize=18, weight="bold"
    )
    subtitle_text = fig.text(
        0.04, 0.905, "", color=ACCENT, fontsize=12, weight="bold"
    )
    footer_text = fig.text(
        0.04, 0.03,
        "github.com/ABMFST/robot-trust-envelope  ·  Amir Bredy",
        color=MUTED, fontsize=10,
    )

    side_title = side.text(0.0, 0.94, "Scenario", color=MUTED, fontsize=11,
                           weight="bold", transform=side.transAxes)
    scenario_name = side.text(0.0, 0.88, "", color=INK, fontsize=15,
                              weight="bold", transform=side.transAxes)
    scenario_goal = side.text(0.0, 0.81, "", color=INK, fontsize=11,
                              wrap=True, transform=side.transAxes)
    scenario_badge = side.text(0.0, 0.74, "", color=ACCENT2, fontsize=10,
                               weight="bold", transform=side.transAxes)

    events_header = side.text(0.0, 0.66, "Envelope events", color=MUTED,
                              fontsize=11, weight="bold",
                              transform=side.transAxes)
    events_text = side.text(0.0, 0.62, "", color=INK, fontsize=10,
                            va="top", family="monospace",
                            transform=side.transAxes)

    # Resolve which plan a frame index lies in.
    def resolve(frame: int):
        cumulative = 0
        for p in plans:
            if frame < cumulative + p["n"]:
                return p, frame - cumulative
            cumulative += p["n"]
        return plans[-1], plans[-1]["n"] - 1

    def render_title(sc, _i):
        title_text.set_text("Robot Trust Envelope")
        subtitle_text.set_text(
            f"Scenario {scenarios.index(sc) + 1} / {len(scenarios)}: "
            f"{sc['name']}"
        )
        scenario_name.set_text(sc["name"])
        scenario_goal.set_text(f"Operator goal: {sc['goal']}")
        if sc["adversarial"]:
            scenario_badge.set_text(
                f"ADVERSARIAL · expects block: {sc['expected_block_kind']}"
            )
            scenario_badge.set_color(WARN)
        else:
            scenario_badge.set_text("BENIGN · should run clean")
            scenario_badge.set_color(ACCENT)
        events_text.set_text("")
        trail_line.set_data([], [])
        robot_dot.set_data([], [])
        intervention_dots.set_data([], [])
        cmd_arrow.set_position((0, 0))
        cmd_arrow.xy = (0, 0)

    def render_play(sc, i):
        samples = sc["samples"][: i + 1]
        xs = [s["x"] for s in samples]
        ys = [s["y"] for s in samples]
        trail_line.set_data(xs, ys)
        last = samples[-1]
        robot_dot.set_data([last["x"]], [last["y"]])
        ix = [s["x"] for s in samples if s["intervened"]]
        iy = [s["y"] for s in samples if s["intervened"]]
        intervention_dots.set_data(ix, iy)
        # Raw command arrow
        import math
        theta = last["theta"]
        raw = last["cmd_raw"][0]
        cmd_arrow.xy = (
            last["x"] + raw * math.cos(theta) * 0.6,
            last["y"] + raw * math.sin(theta) * 0.6,
        )
        cmd_arrow.set_position((last["x"], last["y"]))
        # Events log
        events_so_far = [e for e in sc["interventions"] if e["t"] <= last["t"]]
        lines = []
        for e in events_so_far[-8:]:
            lines.append(f"t={e['t']:4.1f}s  {e['kind']:<18}")
            lines.append(f"          {e['reason'][:48]}")
        events_text.set_text("\n".join(lines) or "(no interventions yet)")
        scenario_name.set_text(sc["name"])
        scenario_goal.set_text(f"Operator goal: {sc['goal']}")

    def update(frame):
        plan, i = resolve(frame)
        if plan["kind"] == "title":
            render_title(plan["scenario"], i)
        else:
            render_play(plan["scenario"], i)
        return [trail_line, robot_dot, intervention_dots, cmd_arrow,
                title_text, subtitle_text, scenario_name, scenario_goal,
                scenario_badge, events_text]

    ani = anim.FuncAnimation(fig, update, frames=total, interval=1000 // FPS,
                             blit=False)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    writer = anim.FFMpegWriter(fps=FPS, bitrate=2500,
                               codec="libx264",
                               extra_args=["-pix_fmt", "yuv420p"])
    ani.save(str(OUT_PATH), writer=writer)
    # also publish a flat copy alongside the trace
    flat = Path("site/demo.mp4")
    flat.write_bytes(OUT_PATH.read_bytes())
    print(f"wrote {OUT_PATH}  ({OUT_PATH.stat().st_size // 1024} KB)")
    print(f"wrote {flat}  ({flat.stat().st_size // 1024} KB)")
    print(f"duration: ~{total / FPS:.1f}s, {total} frames @ {FPS} fps")


if __name__ == "__main__":
    main()
