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

## What this prototype *isn't*

So you don't have to read the code to find out:

- **Not a real-time system.** Pure Python on no specific runtime
  guarantees. A production envelope belongs in a C++ `rclcpp` node with
  a watchdog.
- **Not safety-certified.** STPA and FMEA worksheets are learning
  exercises on a toy system, not certification-grade safety cases.
- **No Gazebo in the embedded demo video.** The video renders a recorded
  scenario trace through matplotlib. The ROS2 adapter
  (`safety_envelope/ros2_node.py`) and `sim/` launch instructions
  describe how to run the same envelope against a TurtleBot4 in real
  Gazebo Harmonic, but bringing that up needs WSL2 + Ubuntu 24.04 +
  ROS2 Jazzy.
- **Live LLM is opt-in.** The recorded trace and tests use
  deterministic scripted commands so runs are reproducible. Live-LLM
  mode (`OPENAI_API_KEY`) lives in `red_team_agent/agent.py` and works,
  but it isn't what the demo video shows.
- **No multi-robot, no human-in-the-loop teaming, no FMECA criticality
  on top of the FMEA, no software-FMEA on the envelope itself.** All
  reasonable next steps; none done here.

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

Prototype. Not safety-certified, not production. STPA worksheet is
a learning exercise on a toy system.
