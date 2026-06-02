"""High-level attestation service: takes a quote, returns a JWT or rejects."""
from __future__ import annotations

import secrets
from dataclasses import dataclass, field

from .ca import FleetCA
from .quote import RobotQuote, verify_quote


@dataclass
class AttestationService:
    ca: FleetCA = field(default_factory=FleetCA)
    _nonces: dict[str, str] = field(default_factory=dict)

    def challenge(self, robot_id: str) -> str:
        """Issue a one-time nonce the robot must include in its quote."""
        nonce = secrets.token_hex(16)
        self._nonces[robot_id] = nonce
        return nonce

    def attest(self, quote: RobotQuote) -> str:
        """Validate a quote and return a signed identity JWT."""
        expected = self._nonces.pop(quote.robot_id, None)
        if expected is None:
            raise PermissionError("no outstanding challenge for robot")
        ok, reason = verify_quote(quote, expected)
        if not ok:
            raise PermissionError(f"attestation failed: {reason}")
        return self.ca.issue(
            robot_id=quote.robot_id,
            capabilities=["nav.cmd_vel", "telemetry.publish"],
            pcr_digest=quote.pcr_digest(),
        )
