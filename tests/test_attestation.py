from attestation_svc import AttestationService, RobotQuote


def test_happy_path_attestation():
    svc = AttestationService()
    nonce = svc.challenge("tb4-01")
    q = RobotQuote(
        robot_id="tb4-01",
        firmware_hash="fw-v1.5.0-signed",
        boot_components=(
            "bootloader-v3.1",
            "kernel-rt-6.6.20",
            "rootfs-immutable-2026.05",
            "ros2-jazzy-base",
        ),
        nonce=nonce,
    )
    token = svc.attest(q)
    claims = svc.ca.verify(token)
    assert claims["sub"] == "tb4-01"
    assert "nav.cmd_vel" in claims["caps"]


def test_replay_rejected():
    import pytest

    svc = AttestationService()
    svc.challenge("tb4-01")
    bad = RobotQuote(
        robot_id="tb4-01",
        firmware_hash="fw-v1.5.0-signed",
        boot_components=("bootloader-v3.1",),
        nonce="00" * 16,  # wrong nonce
    )
    with pytest.raises(PermissionError, match="nonce"):
        svc.attest(bad)


def test_tampered_firmware_rejected():
    import pytest

    svc = AttestationService()
    nonce = svc.challenge("tb4-01")
    bad = RobotQuote(
        robot_id="tb4-01",
        firmware_hash="fw-tampered-2026.06",
        boot_components=("bootloader-v3.1",),
        nonce=nonce,
    )
    with pytest.raises(PermissionError, match="firmware"):
        svc.attest(bad)
