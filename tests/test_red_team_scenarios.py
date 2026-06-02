from red_team_agent import SCENARIOS
from scripts.record_trace import run_scenario


def test_every_adversarial_scenario_is_blocked():
    for s in SCENARIOS:
        if not s.is_adversarial:
            continue
        result = run_scenario(s.name)
        assert result["blocked"], f"{s.name} should be blocked by the envelope"
        kinds = {i["kind"] for i in result["interventions"]}
        assert s.expected_block_kind in kinds, (
            f"{s.name}: expected {s.expected_block_kind}, saw {kinds}"
        )


def test_benign_scenario_is_not_blocked():
    result = run_scenario("benign-patrol")
    assert not result["blocked"], "benign scenario should run clean"
    assert result["intervention_count"] == 0
