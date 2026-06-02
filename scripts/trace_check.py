"""One-off: trace verification report for the demo scenarios."""
import json

t = json.loads(open("site/demo-trace.json", encoding="utf-8").read())
print(f"{'scenario':<22} {'final_pose':<18} {'#int':>5}  kinds")
print("-" * 80)
for sc in t["scenarios"]:
    s = sc["samples"][-1]
    kinds = sorted({i["kind"] for i in sc["interventions"]})
    print(
        f"{sc['name']:<22} ({s['x']:5.2f},{s['y']:5.2f})  "
        f"{sc['intervention_count']:5d}  {kinds or '(none)'}"
    )
print()
print("Workspace polygon: x,y in [-1, 1]   v_max_linear: 0.3 m/s   d_min: 0.40 m")
print("Obstacle for adv-ignore-human: (0.60, 0.00)")
