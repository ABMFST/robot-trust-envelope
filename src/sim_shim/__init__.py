"""Pure-Python toy sim. Lets the whole pipeline run without ROS2/Gazebo.

The shim mirrors the ROS2 surface area the safety envelope cares about:
    - apply a Twist (linear_x, angular_z) for one step
    - report pose (x, y) and a single min-scan range
That is enough to exercise every code path in `safety_envelope.core`.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass


@dataclass
class SimRobot:
    x: float = 0.0
    y: float = 0.0
    theta: float = 0.0
    dt: float = 0.1  # 10 Hz
    obstacles: list[tuple[float, float]] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.obstacles is None:
            self.obstacles = []

    def step(self, linear_x: float, angular_z: float) -> None:
        self.theta += angular_z * self.dt
        self.x += linear_x * math.cos(self.theta) * self.dt
        self.y += linear_x * math.sin(self.theta) * self.dt

    @property
    def pose_xy(self) -> tuple[float, float]:
        return (self.x, self.y)

    def min_scan_range(self) -> float:
        if not self.obstacles:
            return float("inf")
        return min(math.hypot(ox - self.x, oy - self.y) for ox, oy in self.obstacles)


def deterministic_seed(seed: int = 42) -> None:
    random.seed(seed)
