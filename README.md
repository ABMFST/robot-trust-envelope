# robot-trust-envelope

> Trusted Launch patterns + STPA-derived safety envelopes for robot fleets.

A working demo that ports the hardware-root-of-trust / attestation / fleet-
policy patterns Microsoft already ships in Azure (Trusted Launch, vTPM,
Confidential VMs, regulated/air-gapped cloud rollouts) onto a simulated
robot fleet, then adds two layers the cloud doesn't have to think about:

1. **STPA-derived runtime safety envelopes** - bounded velocity, workspace
   polygons, standoff distance - enforced as a ROS2 control-plane node
   that can override `/cmd_vel` and emit `/safety/intervention` events.
2. **AI red-team scenarios** - an LLM-driven "operator" agent given the
   robot command API and adversarial natural-language goals; the envelope
   intercepts every prohibited command.

The project runs end-to-end **without ROS2 or Gazebo installed** thanks to
a pure-Python sim shim used by the test suite and the trace recorder. The
ROS2 adapter in `safety-envelope/ros2_node.py` wraps the same core logic
for use against a real TurtleBot4 Gazebo sim (`sim/`).

## Why this exists

Built as a working artifact for the [Microsoft Robotics - Robot Security &
Safety](https://apply.careers.microsoft.com/careers/job/1970393556868893)
opening. I currently run Trusted Launch (vTPM + Secure Boot) for Azure
Local and own the Security Benchmarks program for our public and
regulated cloud environments; see `docs/trusted-launch-mapping.md` for
the explicit mapping between that work and the robotics security domain.

## Quick start (no ROS2 required)

```bash
python -m pip install -e .[dev,agent]
make test
make demo            # writes site/demo-trace.json
```

Open `site/index.html` to see the dashboard replay the recorded trace.

## With ROS2 + Gazebo

See `sim/README.md` for the TurtleBot4 launch. The safety envelope runs as
a normal ROS2 node:

```bash
ros2 run safety_envelope envelope_node --params-file sim/envelope.yaml
```

## Layout

```
src/
  attestation_svc/    # fake-TPM-quote → JWT identity service
  safety_envelope/    # STPA-derived runtime monitor (core + ROS2 adapter)
  red_team_agent/     # LLM-driven adversarial operator
  sim_shim/           # tiny pure-Python robot sim used by tests + recorder
scripts/
  record_trace.py     # runs end-to-end scenario, emits demo-trace.json
docs/
  architecture.svg
  stpa-worksheet.md
  trusted-launch-mapping.md
sim/                  # docker-compose + TurtleBot4 ROS2 launch
site/                 # static site, deployed to Azure SWA from main
tests/                # pytest
```

## Status

Weekend prototype. Not safety-certified, not production. STPA worksheet is
a learning exercise on a toy system.
