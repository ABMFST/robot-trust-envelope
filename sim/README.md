# sim/ — TurtleBot4 + Gazebo Harmonic launch (weekend bring-up)

This directory holds the Gazebo bring-up for the demo. The repo runs
end-to-end **without** any of this installed (everything in `src/` plus
`scripts/record_trace.py` produces the same `site/demo-trace.json` that
drives the website), so this is optional polish for a live walk-through.

## Prerequisites (WSL2 Ubuntu 24.04)

```bash
# ROS2 Jazzy
sudo apt update && sudo apt install -y software-properties-common
sudo add-apt-repository universe
sudo apt install -y curl
curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
  -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" \
  | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
sudo apt update
sudo apt install -y ros-jazzy-desktop ros-dev-tools
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc

# TurtleBot4 sim
sudo apt install -y ros-jazzy-turtlebot4-simulator ros-jazzy-irobot-create-nodes
```

## Launch

```bash
# Terminal 1 — sim
ros2 launch turtlebot4_ignition_bringup turtlebot4_ignition.launch.py world:=warehouse

# Terminal 2 — the envelope node from this repo
cd robot-trust-envelope
pip install -e .
ros2 run safety_envelope envelope_node --ros-args -p authenticated:=true

# Terminal 3 — the red-team agent (live LLM mode)
OPENAI_API_KEY=... python -m red_team_agent.agent --scenario adv-leave-cell --live-llm
```

The envelope subscribes to `/cmd_vel_raw` (renamed from `/cmd_vel` upstream so
the envelope sits in front of the planner) and publishes the allowed
`/cmd_vel` plus a `/safety/intervention` event topic. Record the topic
with `ros2 bag record /tf /odom /scan /cmd_vel /safety/intervention` and
re-export to the website trace format with `scripts/bag_to_trace.py`
(left as a TODO past the weekend).

## envelope.yaml

```yaml
safety_envelope:
  ros__parameters:
    authenticated: true
    v_max_linear: 0.3
    v_max_angular: 1.0
    d_min_obstacle: 0.40
    workspace_polygon: [-1.0,-1.0, 1.0,-1.0, 1.0,1.0, -1.0,1.0]
```
