# FMEA worksheet - Safety Envelope (toy system)

Method: [Failure Mode and Effects Analysis (FMEA)](https://www.iqasystem.com/news/fmea-failure-modes-and-effects-analysis/).
Applied to the safety envelope *itself*, as the complement to the STPA
worksheet in `stpa-worksheet.md`. STPA focuses on unsafe control actions
the robot or operator might take; FMEA focuses on **what happens when
the safety envelope, the thing meant to prevent those actions, itself
fails**. Together they give the breadth of methods the Microsoft
Robotics JD asks for (FMEA, FTA, HAZOP, STPA).

This is a **learning exercise** on a toy system, not a
certification-grade design FMEA. Scores are 1-5 (low to high). RPN =
Severity x Occurrence x Detection. Items above RPN 30 deserve attention
first.

## Scoring legend

| Score | Severity | Occurrence | Detection |
|-------|----------|------------|-----------|
| 1 | No safety impact | Implausible | Always caught immediately |
| 2 | Minor degradation | Unlikely | Usually caught by tests / monitoring |
| 3 | Brief unsafe window | Possible | Sometimes caught |
| 4 | Likely injury / property loss | Likely | Rarely caught before incident |
| 5 | Severe injury / catastrophic loss | Frequent | Not detectable today |

## Failure modes

| ID | Failure mode | Effect | S | O | D | RPN | Mitigation in repo today | Gap / next step |
|----|--------------|--------|---|---|---|-----|--------------------------|-----------------|
| F-1 | Envelope event loop misses its deadline (GIL stall, GC pause, slow scan callback) | Stale pose / scan; intervention fires late or never | 5 | 3 | 4 | 60 | None - pure Python, no real-time guarantees | Move hot path to C++ rclcpp node; add watchdog timer; budget per-callback time |
| F-2 | JWT verification raises an exception (malformed token, key rotation race, library bug) | Envelope crashes; without supervisor, robot keeps last command | 5 | 2 | 3 | 30 | Exception escapes today | Wrap in try/except, fail-closed to Twist(0,0); add `safety_envelope.crashes` metric |
| F-3 | Workspace polygon mis-configured (empty list, degenerate polygon, wrong frame) | Every projection looks "inside", workspace breach never fires | 5 | 3 | 5 | 75 | Default polygon hard-coded in `policy.py` | Schema-validate the YAML; reject empty / non-convex / <3-vertex polygons on load |
| F-4 | `/scan` topic stops publishing (sensor failure, transport flake) | `min_scan_range` returns last value or `inf`; obstacle standoff bypassed | 5 | 3 | 4 | 60 | None - stale data treated as safe | Track scan age; treat scan older than 200 ms as 0.0 m (fail-closed) |
| F-5 | Clock drift breaks JWT `exp` check | Expired tokens accepted; UCA-4 gate bypassed | 4 | 2 | 4 | 32 | None today | Require monotonic clock + NTP discipline; alert on drift > 1 s |
| F-6 | Safety envelope itself is compromised (supply-chain attack, code injection) | Override authority becomes the attack vector | 5 | 1 | 5 | 25 | None - envelope runs unattested | Run envelope in attested enclave / measured boot of its own; sign envelope binary in CI |
| F-7 | Policy YAML reload races with in-flight evaluation | Envelope uses half-applied policy (e.g., new V-max with old polygon) | 4 | 2 | 3 | 24 | None - no hot reload implemented | Atomic policy swap (read-copy-update); reject load on validation error |
| F-8 | Multiple intervention conditions race; only one event is logged | Audit trail under-counts; harder to diagnose | 2 | 3 | 3 | 18 | First-match short-circuit in `core.evaluate()` | Already documented in code; consider logging all-conditions for audit |
| F-9 | Operator floods `/cmd_vel_raw` faster than the envelope can keep up | Backpressure; some commands evaluated against stale pose | 4 | 3 | 3 | 36 | None - unbounded queue | Bounded queue + drop-oldest; rate-limit per JWT `sub` |
| F-10 | LLM red-team scenario file is itself adversarial (e.g., crafted to cause an exception in the agent) | Agent crashes; scenario doesn't run; false sense of coverage | 3 | 2 | 2 | 12 | Deterministic mode is total; LLM mode catches parse failures | Add fuzzing on the scenario loader; treat unparseable scenarios as failures, not skips |

## Top 3 by RPN

1. **F-3 (RPN 75)** - misconfigured workspace polygon. The fix is cheap
   (schema validation on policy load) and the consequence is total: the
   most-important geometric guardrail silently disabled.
2. **F-1 (RPN 60)** - missed envelope deadline. The Python implementation
   here is not real-time. In production the envelope belongs in a C++
   rclcpp node with a watchdog.
3. **F-4 (RPN 60)** - stale `/scan`. Treating absent sensor data as "safe"
   is the classic instrumentation failure pattern; fail-closed is
   straightforward.

## What this worksheet is not

- It is not a complete FMEA - I haven't enumerated failure modes for the
  attestation service, the robot controller, or the operator network.
- It does not include criticality analysis (FMECA) or fault-tree linkage.
- Mitigations are sketched, not implemented. The repo today is a
  prototype, not a production safety system.

If I take this further the next steps are: implement the top three
mitigations (F-3 schema validation first, F-1 watchdog next, F-4
fail-closed scan staleness), add an FMECA criticality column, and link
each failure mode to the STPA UCA it corresponds to.
