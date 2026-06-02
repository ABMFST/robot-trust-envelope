"""Toy fleet CA. Generates an Ed25519 keypair on first use and signs JWTs."""
from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


@dataclass
class FleetCA:
    """Issues short-lived JWTs for attested robots.

    In production this is the equivalent of the Microsoft Azure
    Attestation (MAA) service signing key paired with a fleet-scoped
    policy. Here we use a single Ed25519 key for the toy.
    """

    issuer: str = "robot-trust-envelope/FleetCA"
    audience: str = "robot-trust-envelope/control-plane"
    ttl_seconds: int = 300
    _private_key: Ed25519PrivateKey | None = None

    def __post_init__(self) -> None:
        if self._private_key is None:
            self._private_key = Ed25519PrivateKey.generate()

    @classmethod
    def from_seed_file(cls, path: Path) -> FleetCA:
        """Load (or create) a deterministic key from disk. Test convenience."""
        if path.exists():
            data = path.read_bytes()
            key = serialization.load_pem_private_key(data, password=None)
            assert isinstance(key, Ed25519PrivateKey)
        else:
            key = Ed25519PrivateKey.generate()
            path.write_bytes(
                key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )
        ca = cls()
        ca._private_key = key
        return ca

    @property
    def public_key(self) -> Ed25519PublicKey:
        assert self._private_key is not None
        return self._private_key.public_key()

    @property
    def public_pem(self) -> bytes:
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

    def issue(self, robot_id: str, capabilities: list[str], pcr_digest: str) -> str:
        """Issue a short-lived attestation JWT for a robot."""
        now = int(time.time())
        payload = {
            "iss": self.issuer,
            "aud": self.audience,
            "sub": robot_id,
            "iat": now,
            "nbf": now,
            "exp": now + self.ttl_seconds,
            "caps": capabilities,
            "pcr": pcr_digest,
        }
        assert self._private_key is not None
        key_pem = self._private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        return jwt.encode(payload, key_pem, algorithm="EdDSA")

    def verify(self, token: str) -> dict:
        return jwt.decode(
            token,
            self.public_pem,
            algorithms=["EdDSA"],
            audience=self.audience,
            issuer=self.issuer,
        )
