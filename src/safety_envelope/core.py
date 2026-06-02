"""Core safety envelope logic. No ROS2, no I/O - pure decision function."""
from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum

from .policy import EnvelopePolicy


@dataclass(frozen=True)
class Twist:
    linear_x: float
    angular_z: float


class InterventionKind(str, Enum):
    NONE = "none"
    CLAMP_VELOCITY = "clamp_velocity"
    WORKSPACE_BREACH = "workspace_breach"
    OBSTACLE_STANDOFF = "obstacle_standoff"
    UNAUTHENTICATED = "unauthenticated"


@dataclass(frozen=True)
class EnvelopeDecision:
    allowed: Twist
    intervened: bool
    kind: InterventionKind
    reason: str
    uca_id: str  # which STPA UCA this addresses


def _point_in_polygon(x: float, y: float, poly: list[tuple[float, float]]) -> bool:
    """Standard ray-cast point-in-polygon."""
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        intersect = ((yi > y) != (yj > y)) and (
            x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-12) + xi
        )
        if intersect:
            inside = not inside
        j = i
    return inside


class SafetyEnvelope:
    """Decision function: given pose + scan + command, return safe command."""

    def __init__(self, policy: EnvelopePolicy | None = None) -> None:
        self.policy = policy or EnvelopePolicy()

    def evaluate(
        self,
        *,
        command: Twist,
        pose_xy: tuple[float, float],
        min_scan_range: float,
        authenticated: bool,
        # Look-ahead horizon (seconds) for workspace projection.
        horizon_s: float = 1.0,
    ) -> EnvelopeDecision:
        # C-5: unauthenticated → reject everything.
        if self.policy.require_attested_jwt and not authenticated:
            return EnvelopeDecision(
                allowed=Twist(0.0, 0.0),
                intervened=True,
                kind=InterventionKind.UNAUTHENTICATED,
                reason="command refused: no valid attestation token",
                uca_id="UCA-4",
            )

        # C-4: obstacle standoff.
        if min_scan_range < self.policy.d_min_obstacle:
            return EnvelopeDecision(
                allowed=Twist(0.0, 0.0),
                intervened=True,
                kind=InterventionKind.OBSTACLE_STANDOFF,
                reason=(
                    f"obstacle at {min_scan_range:.2f}m < "
                    f"D-min {self.policy.d_min_obstacle:.2f}m"
                ),
                uca_id="UCA-3",
            )

        # C-1 + C-2: clamp velocity first so workspace projection uses the
        # safe velocity, not the raw (potentially over-limit) command.
        v_lin = math.copysign(
            min(abs(command.linear_x), self.policy.v_max_linear), command.linear_x
        )
        v_ang = math.copysign(
            min(abs(command.angular_z), self.policy.v_max_angular), command.angular_z
        )
        clamped = (v_lin != command.linear_x) or (v_ang != command.angular_z)
        safe = Twist(v_lin, v_ang)

        # C-3: project pose forward using the clamped velocity and check
        # workspace polygon. Workspace breach always wins over clamping
        # (stop is strictly safer than clamp).
        projected = (
            pose_xy[0] + safe.linear_x * horizon_s,
            pose_xy[1],
        )
        if not _point_in_polygon(*projected, self.policy.workspace_polygon):
            return EnvelopeDecision(
                allowed=Twist(0.0, 0.0),
                intervened=True,
                kind=InterventionKind.WORKSPACE_BREACH,
                reason=(
                    f"projected pose {projected} leaves workspace polygon"
                ),
                uca_id="UCA-2",
            )

        if clamped:
            return EnvelopeDecision(
                allowed=safe,
                intervened=True,
                kind=InterventionKind.CLAMP_VELOCITY,
                reason=(
                    f"velocity clamped: cmd=({command.linear_x:.2f},"
                    f"{command.angular_z:.2f}) -> "
                    f"({v_lin:.2f},{v_ang:.2f})"
                ),
                uca_id="UCA-1",
            )

        return EnvelopeDecision(
            allowed=command,
            intervened=False,
            kind=InterventionKind.NONE,
            reason="",
            uca_id="",
        )
