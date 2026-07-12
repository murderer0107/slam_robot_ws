"""Test node for scooping soil supply with shovel already gripped."""

from __future__ import annotations

import rclpy

from robot_tests.dsr_runtime import bootstrap_dsr_python
from robot_tests.node_common import (
    ROBOT_ID,
    configure_dsr_init,
    setup_tool_and_tcp,
)
from robot_tests.robot_motion_data import SOIL_SERVICE_TCP_NAME, SOIL_SERVICE_TOOL_NAME
from robot_tests.tray_soil_service_common import fill_shovel_from_supply, import_soil_service_apis

bootstrap_dsr_python()

import DR_init

configure_dsr_init(DR_init)


def main(args=None):
    rclpy.init(args=args)
    node = rclpy.create_node("soil_supply_scoop_test", namespace=ROBOT_ID)
    DR_init.__dsr__node = node

    try:
        apis = import_soil_service_apis(node)
    except ImportError:
        node.destroy_node()
        rclpy.shutdown()
        return

    try:
        setup_tool_and_tcp(
            node,
            apis["set_tool"],
            apis["set_tcp"],
            SOIL_SERVICE_TOOL_NAME,
            SOIL_SERVICE_TCP_NAME,
        )

        node.get_logger().info("soil_supply_scoop_test started")
        node.get_logger().info("Assumption: shovel is already gripped before this node starts")
        fill_shovel_from_supply(node, apis)
        node.get_logger().info("soil_supply_scoop_test finished")
    except KeyboardInterrupt:
        node.get_logger().info("Stopped by user")
    except Exception as exc:
        node.get_logger().error(f"soil_supply_scoop_test failed: {exc}")
        raise
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
