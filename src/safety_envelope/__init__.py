"""safety_envelope — STPA-derived runtime monitor.

The `core` module is pure Python (no ROS2 dependency) so it can be unit
tested and driven by the sim_shim on any platform. `ros2_node` is a thin
adapter that subscribes to /cmd_vel, /odom, /scan and republishes
overrides + /safety/intervention events when running against Gazebo.
"""
from .core import EnvelopeDecision, SafetyEnvelope, Twist
from .policy import EnvelopePolicy

__all__ = ["EnvelopeDecision", "SafetyEnvelope", "Twist", "EnvelopePolicy"]
