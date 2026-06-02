"""Envelope policy = the STPA-derived constraints, made data."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EnvelopePolicy:
    v_max_linear: float = 0.3            # m/s - STPA C-1
    v_max_angular: float = 1.0           # rad/s - STPA C-2
    workspace_polygon: list[tuple[float, float]] = field(
        default_factory=lambda: [(-1.0, -1.0), (1.0, -1.0), (1.0, 1.0), (-1.0, 1.0)]
    )  # STPA C-3
    d_min_obstacle: float = 0.40         # m - STPA C-4
    require_attested_jwt: bool = True    # STPA C-5
