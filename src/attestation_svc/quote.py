"""Simulated TPM-style quote produced by a robot agent at boot."""
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field


@dataclass(frozen=True)
class RobotQuote:
    """Pretend platform-measurement quote sent by a robot to attestation."""

    robot_id: str
    firmware_hash: str
    boot_components: tuple[str, ...]
    nonce: str
    timestamp: int = field(default_factory=lambda: int(time.time()))

    def pcr_digest(self) -> str:
        """Roll up boot components the way TPM PCR extend would."""
        h = hashlib.sha256()
        h.update(self.firmware_hash.encode())
        for c in self.boot_components:
            h.update(c.encode())
        return h.hexdigest()


# Reference allow-list — in real life this is an MAA / SCM policy.
ALLOWED_FIRMWARE_HASHES: set[str] = {
    "fw-v1.4.2-signed",
    "fw-v1.5.0-signed",
}
ALLOWED_BOOT_COMPONENTS: set[str] = {
    "bootloader-v3.1",
    "kernel-rt-6.6.20",
    "rootfs-immutable-2026.05",
    "ros2-jazzy-base",
}


def verify_quote(q: RobotQuote, expected_nonce: str) -> tuple[bool, str]:
    """Return (ok, reason). Reason is empty on success."""
    if q.nonce != expected_nonce:
        return False, "nonce mismatch (possible replay)"
    if q.firmware_hash not in ALLOWED_FIRMWARE_HASHES:
        return False, f"firmware not allow-listed: {q.firmware_hash}"
    unknown = [c for c in q.boot_components if c not in ALLOWED_BOOT_COMPONENTS]
    if unknown:
        return False, f"unknown boot components: {unknown}"
    return True, ""
