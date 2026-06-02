"""OperatorAgent: emits Twist commands from a scenario.

Two modes:
- deterministic (default) — replays the scripted_cmds list from Scenario.
  This is what tests and the trace recorder use so runs are reproducible.
- live LLM (optional) — calls the configured LLM with the goal + current
  pose to produce the next Twist. Used for ad-hoc showcase runs.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from .scenarios import Scenario


@dataclass
class OperatorAgent:
    scenario: Scenario
    use_llm: bool = False
    _step: int = 0

    def next_cmd(self, pose_xy: tuple[float, float]) -> tuple[float, float]:
        if self.use_llm:
            return self._llm_cmd(pose_xy)
        if self._step < len(self.scenario.scripted_cmds):
            cmd = self.scenario.scripted_cmds[self._step]
            self._step += 1
            return cmd
        return (0.0, 0.0)

    def _llm_cmd(self, pose_xy: tuple[float, float]) -> tuple[float, float]:
        """Optional: call an OpenAI-compatible API. Keeps deps soft."""
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - optional dep
            raise RuntimeError("install with [agent] extra to use live LLM") from exc

        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))
        msg = (
            f"You are operating a small differential-drive robot. Goal: "
            f"{self.scenario.goal!r}. Current pose: x={pose_xy[0]:.2f}, "
            f"y={pose_xy[1]:.2f}. Respond with two floats separated by a "
            f"space: linear_x angular_z."
        )
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": msg}],
        )
        text = (resp.choices[0].message.content or "0 0").strip().split()
        try:
            return float(text[0]), float(text[1])
        except (ValueError, IndexError):
            return (0.0, 0.0)
