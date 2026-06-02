# STPA worksheet — Robot Trust Envelope (toy system)

Method: [STPA — Leveson, MIT](https://psas.scripts.mit.edu/home/get_file.php?name=STPA_handbook.pdf).
Applied to the toy single-robot system in this repo. This is a **learning
exercise** to demonstrate the analytical method, not a certification-grade
safety case.

---

## Step 1 — Purpose of the analysis

Identify safety-critical control failures in a Microsoft-Robotics-style
cyber-physical system where (a) the robot is remotely commandable, (b)
the command source may include an LLM-driven autonomous agent, and (c) a
cloud control plane is in the loop for identity and policy.

## Step 2 — Losses

| ID | Loss |
|----|------|
| L-1 | Human in the workspace is struck or pinned by the robot |
| L-2 | Robot leaves the authorized workspace (property / collateral damage) |
| L-3 | Compromised / spoofed command source drives the robot to unsafe behavior |
| L-4 | Robot continues to operate on revoked / expired credentials |

## Step 3 — System-level hazards

| ID | Hazard | Linked losses |
|----|--------|---------------|
| H-1 | Robot velocity exceeds the safe limit for the operating context | L-1, L-2 |
| H-2 | Robot crosses the workspace polygon boundary | L-2 |
| H-3 | Robot comes within < D-min of a detected human/obstacle | L-1 |
| H-4 | Robot accepts a command from an unattested or expired identity | L-3, L-4 |

## Step 4 — Control structure

```
+--------------------+     attest()/JWT      +----------------------+
| Operator (human/AI)| --------------------> | Attestation Service  |
+--------------------+                       +----------------------+
          | /cmd_vel + JWT                            |
          v                                           v
+--------------------+   sub /cmd_vel        +----------------------+
|  Robot Control     | <-------------------- | Safety Envelope Node |
|  (TurtleBot4)      |  pub override+event   +----------------------+
+--------------------+                                ^
          |                                           |
          | /odom /scan                               |
          +-------------------------------------------+
```

## Step 5 — Unsafe Control Actions (UCAs)

| UCA ID | Controller        | Control Action  | Type             | Context | Hazard |
|--------|-------------------|-----------------|------------------|---------|--------|
| UCA-1  | Operator          | /cmd_vel (high) | Provided unsafe  | Speed > V-max for context | H-1 |
| UCA-2  | Operator          | /cmd_vel        | Provided unsafe  | Heading exits workspace | H-2 |
| UCA-3  | Operator          | /cmd_vel        | Provided unsafe  | Human within D-min | H-3 |
| UCA-4  | Robot Control     | execute(cmd)    | Provided unsafe  | JWT absent / expired | H-4 |
| UCA-5  | Safety Envelope   | override = stop | Not provided     | Required but missed (deadline miss) | H-1, H-3 |
| UCA-6  | Safety Envelope   | override = stop | Wrong timing     | Triggered after collision | H-1 |

## Step 6 — Loss scenarios (informal, pruned to the three driving design)

- **Scenario A (drives UCA-1):** an LLM operator infers a productivity
  bonus from going faster and emits `/cmd_vel.linear.x` above V-max. The
  envelope must clamp.
- **Scenario B (drives UCA-2):** an LLM operator is instructed to "find
  the exit" and computes a path through the workspace boundary. The
  envelope must zero `/cmd_vel` once the projected pose crosses the
  polygon.
- **Scenario C (drives UCA-3):** an LLM operator ignores the obstacle
  cost map. The envelope must zero `/cmd_vel` when `/scan` reports a
  return inside D-min.

## Step 7 — Derived runtime constraints (what the envelope enforces)

| Constraint | Parameter | Default |
|------------|-----------|---------|
| C-1: bounded linear speed | `v_max_linear` | 0.3 m/s |
| C-2: bounded angular speed | `v_max_angular` | 1.0 rad/s |
| C-3: workspace polygon | `workspace_polygon` | unit square |
| C-4: minimum standoff distance | `d_min_obstacle` | 0.40 m |
| C-5: command authorization | `require_attested_jwt` | true |

These map 1:1 to the parameters in `src/safety_envelope/policy.py`.

## What this worksheet is not

- It is not formally validated against ISO 13482 or ISO 10218.
- It does not exhaustively enumerate UCAs for multi-robot or
  human-in-the-loop teaming.
- It does not include a software hazard analysis (FMEA-D) on the envelope
  itself.

If I take this further past the weekend, the next steps are: layer a
`FMEA` on the envelope's own failure modes, add the cloud control plane
as an explicit controller in Step 4, and enumerate UCAs around
JWT rotation / revocation.
