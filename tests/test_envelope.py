from safety_envelope import EnvelopePolicy, SafetyEnvelope, Twist
from safety_envelope.core import InterventionKind


def make():
    return SafetyEnvelope(EnvelopePolicy())


def test_passthrough_when_safe():
    d = make().evaluate(
        command=Twist(0.2, 0.5),
        pose_xy=(0.0, 0.0),
        min_scan_range=10.0,
        authenticated=True,
    )
    assert not d.intervened
    assert d.allowed == Twist(0.2, 0.5)


def test_unauthenticated_blocked():
    d = make().evaluate(
        command=Twist(0.2, 0.0),
        pose_xy=(0.0, 0.0),
        min_scan_range=10.0,
        authenticated=False,
    )
    assert d.intervened
    assert d.kind == InterventionKind.UNAUTHENTICATED
    assert d.uca_id == "UCA-4"


def test_velocity_clamped():
    d = make().evaluate(
        command=Twist(1.5, 0.0),
        pose_xy=(0.0, 0.0),
        min_scan_range=10.0,
        authenticated=True,
    )
    assert d.intervened
    assert d.kind == InterventionKind.CLAMP_VELOCITY
    assert d.allowed.linear_x == 0.3


def test_workspace_breach_zeros_command():
    d = make().evaluate(
        command=Twist(0.25, 0.0),
        pose_xy=(0.95, 0.0),  # 0.95 + 0.25*1.0 = 1.20 > 1.0 boundary
        min_scan_range=10.0,
        authenticated=True,
    )
    assert d.intervened
    assert d.kind == InterventionKind.WORKSPACE_BREACH
    assert d.allowed.linear_x == 0.0


def test_obstacle_standoff_stops():
    d = make().evaluate(
        command=Twist(0.2, 0.0),
        pose_xy=(0.0, 0.0),
        min_scan_range=0.20,
        authenticated=True,
    )
    assert d.intervened
    assert d.kind == InterventionKind.OBSTACLE_STANDOFF
    assert d.uca_id == "UCA-3"
