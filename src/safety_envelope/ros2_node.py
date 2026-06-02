"""Thin ROS2 adapter around `core.SafetyEnvelope`.

Imported only when running inside a ROS2 environment - keeping it in a
separate module means the rest of the package and the test suite have no
ROS2 dependency. Run as:

    ros2 run safety_envelope envelope_node --params-file sim/envelope.yaml

This file is intentionally minimal: all decisions live in core.py.
"""
from __future__ import annotations

try:
    import rclpy
    from geometry_msgs.msg import Twist as RosTwist
    from nav_msgs.msg import Odometry
    from rclpy.node import Node
    from sensor_msgs.msg import LaserScan
    from std_msgs.msg import String
except ImportError as exc:  # pragma: no cover - ROS2 not present on dev box
    raise SystemExit(
        "ros2_node imported without rclpy on PYTHONPATH; source your ROS2 setup first."
    ) from exc

import json

from .core import EnvelopeDecision, SafetyEnvelope, Twist
from .policy import EnvelopePolicy


class EnvelopeNode(Node):  # pragma: no cover - exercised only under ROS2
    def __init__(self) -> None:
        super().__init__("safety_envelope")
        self.envelope = SafetyEnvelope(EnvelopePolicy())
        self.authenticated = self.declare_parameter("authenticated", True).value
        self.pose_xy = (0.0, 0.0)
        self.min_scan = float("inf")

        self.create_subscription(RosTwist, "/cmd_vel_raw", self._on_cmd, 10)
        self.create_subscription(Odometry, "/odom", self._on_odom, 10)
        self.create_subscription(LaserScan, "/scan", self._on_scan, 10)
        self.cmd_pub = self.create_publisher(RosTwist, "/cmd_vel", 10)
        self.event_pub = self.create_publisher(String, "/safety/intervention", 10)

    def _on_odom(self, msg: Odometry) -> None:
        p = msg.pose.pose.position
        self.pose_xy = (p.x, p.y)

    def _on_scan(self, msg: LaserScan) -> None:
        self.min_scan = min((r for r in msg.ranges if r > 0.0), default=float("inf"))

    def _on_cmd(self, msg: RosTwist) -> None:
        decision: EnvelopeDecision = self.envelope.evaluate(
            command=Twist(linear_x=msg.linear.x, angular_z=msg.angular.z),
            pose_xy=self.pose_xy,
            min_scan_range=self.min_scan,
            authenticated=self.authenticated,
        )
        out = RosTwist()
        out.linear.x = decision.allowed.linear_x
        out.angular.z = decision.allowed.angular_z
        self.cmd_pub.publish(out)
        if decision.intervened:
            self.event_pub.publish(
                String(
                    data=json.dumps(
                        {
                            "kind": decision.kind.value,
                            "reason": decision.reason,
                            "uca": decision.uca_id,
                        }
                    )
                )
            )


def main() -> None:  # pragma: no cover
    rclpy.init()
    node = EnvelopeNode()
    rclpy.spin(node)
    rclpy.shutdown()
