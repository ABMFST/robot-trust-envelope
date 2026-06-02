"""End-to-end recorder: attestation → 4 scenarios → JSON trace for the site.

Usage:
    python -m scripts.record_trace --out site/demo-trace.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from attestation_svc import AttestationService, RobotQuote
from red_team_agent import SCENARIOS, OperatorAgent
from safety_envelope import EnvelopePolicy, SafetyEnvelope, Twist
from sim_shim import SimRobot, deterministic_seed

ROBOT_ID = "tb4-demo-01"
WORKSPACE = [(-1.0, -1.0), (1.0, -1.0), (1.0, 1.0), (-1.0, 1.0)]
OBSTACLES = [(0.60, 0.0)]  # one "inspector" used by adv-ignore-human


def run_attestation(authenticated: bool = True) -> dict:
    svc = AttestationService()
    nonce = svc.challenge(ROBOT_ID)
    fw = "fw-v1.5.0-signed" if authenticated else "fw-tampered-2026.06"
    components = (
        "bootloader-v3.1",
        "kernel-rt-6.6.20",
        "rootfs-immutable-2026.05",
        "ros2-jazzy-base",
    )
    quote = RobotQuote(
        robot_id=ROBOT_ID,
        firmware_hash=fw,
        boot_components=components,
        nonce=nonce,
    )
    try:
        jwt_token = svc.attest(quote)
        return {
            "ok": True,
            "robot_id": ROBOT_ID,
            "pcr_digest": quote.pcr_digest(),
            "token_preview": jwt_token[:32] + "...",
            "ttl_seconds": svc.ca.ttl_seconds,
        }
    except PermissionError as e:
        return {"ok": False, "error": str(e)}


def run_scenario(scenario_name: str) -> dict:
    scenario = next(s for s in SCENARIOS if s.name == scenario_name)
    obstacles = OBSTACLES if scenario.name == "adv-ignore-human" else []
    robot = SimRobot(obstacles=obstacles)
    agent = OperatorAgent(scenario=scenario)
    envelope = SafetyEnvelope(EnvelopePolicy(workspace_polygon=WORKSPACE))

    samples = []
    interventions = []
    authenticated = scenario.authenticated

    for t in range(len(scenario.scripted_cmds)):
        lin, ang = agent.next_cmd(robot.pose_xy)
        decision = envelope.evaluate(
            command=Twist(lin, ang),
            pose_xy=robot.pose_xy,
            min_scan_range=robot.min_scan_range(),
            authenticated=authenticated,
        )
        robot.step(decision.allowed.linear_x, decision.allowed.angular_z)
        samples.append(
            {
                "t": round(t * robot.dt, 2),
                "x": round(robot.x, 4),
                "y": round(robot.y, 4),
                "theta": round(robot.theta, 4),
                "cmd_raw": [round(lin, 3), round(ang, 3)],
                "cmd_allowed": [
                    round(decision.allowed.linear_x, 3),
                    round(decision.allowed.angular_z, 3),
                ],
                "intervened": decision.intervened,
            }
        )
        if decision.intervened:
            interventions.append(
                {
                    "t": round(t * robot.dt, 2),
                    "kind": decision.kind.value,
                    "reason": decision.reason,
                    "uca": decision.uca_id,
                }
            )

    return {
        "name": scenario.name,
        "goal": scenario.goal,
        "adversarial": scenario.is_adversarial,
        "expected_block_kind": scenario.expected_block_kind,
        "samples": samples,
        "interventions": interventions,
        "intervention_count": len(interventions),
        "blocked": len(interventions) > 0,
    }


def main() -> None:
    deterministic_seed()
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("site/demo-trace.json"))
    args = parser.parse_args()

    trace = {
        "schemaVersion": "1.0",
        "robot": {
            "id": ROBOT_ID,
            "workspace_polygon": WORKSPACE,
            "obstacles": OBSTACLES,
        },
        "attestation": {
            "happy_path": run_attestation(authenticated=True),
            "tampered_firmware": run_attestation(authenticated=False),
        },
        "scenarios": [run_scenario(s.name) for s in SCENARIOS],
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(trace, indent=2), encoding="utf-8")
    print(f"wrote {args.out}")
    print(f"  scenarios: {len(trace['scenarios'])}")
    for sc in trace["scenarios"]:
        flag = "BLOCKED" if sc["blocked"] else "ALLOWED"
        print(f"    {sc['name']:22s} {flag} interventions={sc['intervention_count']}")


if __name__ == "__main__":
    main()
