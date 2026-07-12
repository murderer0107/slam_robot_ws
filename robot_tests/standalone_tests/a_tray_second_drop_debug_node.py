"""Debug node for A tray second soil drop joint path only."""

from __future__ import annotations

import rclpy

from robot_tests.dsr_runtime import bootstrap_dsr_python
from robot_tests.motion_primitives import move_j, normalize_pose
from robot_tests.node_common import ROBOT_ID, configure_dsr_init, setup_tool_and_tcp
from robot_tests.robot_motion_data import (
    A_TRAY_SOIL_DROP_CYCLES,
    A_TRAY_SOIL_DROP_PREP_JOINTS,
    A_TRAY_SOIL_DROP_TOP_JOINT,
    SOIL_SERVICE_TCP_NAME,
    SOIL_SERVICE_TOOL_NAME,
)
from robot_tests.tray_soil_service_common import go_home_with_gripper_held, import_soil_service_apis

bootstrap_dsr_python()

import DR_init

configure_dsr_init(DR_init)


def log_current_pose(node, apis, label: str) -> None:
    pose = normalize_pose(apis["get_current_posx"](ref=apis["DR_BASE"]))
    node.get_logger().info(f"{label} current pose={pose}")


def main(args=None):
    rclpy.init(args=args)
    node = rclpy.create_node("a_tray_second_drop_debug", namespace=ROBOT_ID)
    DR_init.__dsr__node = node
    returned_home = False

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

        node.get_logger().info("a_tray_second_drop_debug started")
        node.get_logger().info("Assumption: shovel is already gripped and soil is already scooped")

        for prep_index, prep_joint in enumerate(A_TRAY_SOIL_DROP_PREP_JOINTS, start=1):
            step_name = f"A_TRAY_PREP_DEBUG_{prep_index}"
            node.get_logger().info(f"{step_name} target_joint={prep_joint}")
            move_j(
                node,
                apis["movej"],
                apis["posj"],
                apis["wait"],
                step_name,
                prep_joint,
                vel=40.0,
                acc=40.0,
                check_motion=apis["check_motion"],
            )
            log_current_pose(node, apis, f"A_TRAY_PREP_DEBUG_{prep_index}")

        node.get_logger().info(f"A_TRAY_TOP_DEBUG target_joint={A_TRAY_SOIL_DROP_TOP_JOINT}")
        move_j(
            node,
            apis["movej"],
            apis["posj"],
            apis["wait"],
            "A_TRAY_TOP_DEBUG",
            A_TRAY_SOIL_DROP_TOP_JOINT,
            vel=40.0,
            acc=40.0,
            check_motion=apis["check_motion"],
        )
        log_current_pose(node, apis, "A_TRAY_TOP_DEBUG")

        cycle = A_TRAY_SOIL_DROP_CYCLES[1]
        node.get_logger().info(f"A_TRAY_DROP_2 cycle={cycle}")

        node.get_logger().info(f"A_TRAY_DROP_2_APPROACH_DEBUG target_joint={cycle['approach']}")
        move_j(
            node,
            apis["movej"],
            apis["posj"],
            apis["wait"],
            "A_TRAY_DROP_2_APPROACH_DEBUG",
            cycle["approach"],
            vel=20.0,
            acc=20.0,
            check_motion=apis["check_motion"],
        )
        log_current_pose(node, apis, "A_TRAY_DROP_2_APPROACH_DEBUG")

        node.get_logger().info(f"A_TRAY_DROP_2_DROP_DEBUG target_joint={cycle['drop']}")
        move_j(
            node,
            apis["movej"],
            apis["posj"],
            apis["wait"],
            "A_TRAY_DROP_2_DROP_DEBUG",
            cycle["drop"],
            vel=20.0,
            acc=20.0,
            check_motion=apis["check_motion"],
        )
        log_current_pose(node, apis, "A_TRAY_DROP_2_DROP_DEBUG")

        node.get_logger().info("a_tray_second_drop_debug finished")
        go_home_with_gripper_held(node, apis)
        returned_home = True
    except KeyboardInterrupt:
        node.get_logger().info("Stopped by user")
    except Exception as exc:
        node.get_logger().error(f"a_tray_second_drop_debug failed: {exc}")
        raise
    finally:
        if not returned_home:
            try:
                go_home_with_gripper_held(node, apis)
            except Exception as home_exc:
                node.get_logger().error(f"Failed to return home: {home_exc}")
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
