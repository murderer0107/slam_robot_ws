"""Standalone fixed-route rock pick-and-discard test."""

from __future__ import annotations

import argparse
import subprocess
import sys

import rclpy

from robot_tests.dsr_runtime import bootstrap_dsr_python
from robot_tests.motion_primitives import (
    move_j,
    normalize_pose,
    set_outputs_compat,
)
from robot_tests.node_common import (
    ROBOT_ID,
    configure_dsr_init,
    import_basic_motion_apis,
    import_digital_output_apis,
    setup_tool_and_tcp,
)
from robot_tests.robot_motion_data import (
    HOME_JOINT,
    PRESS_TCP_NAME,
    PRESS_TOOL_NAME,
)
from robot_tests.tray_soil_service_common import run_rock_remove_action

bootstrap_dsr_python()

import DR_init

configure_dsr_init(DR_init)

HOME_TOLERANCE_DEG = 1.0
TOOL_PUTDOWN_NODES = {
    "press": "press_plate_putdown_node",
    "shovel": "shovel_putdown_node",
}


def parse_args(argv: list[str] | None = None) -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(description="Standalone fixed-route rock removal test")
    parser.add_argument(
        "--held-tool",
        choices=("press", "shovel", "none"),
        help="tool currently held by the gripper",
    )
    return parser.parse_known_args(argv)


def prompt_held_tool() -> str:
    choices = {
        "1": "press",
        "2": "shovel",
        "3": "none",
        "press": "press",
        "shovel": "shovel",
        "none": "none",
    }
    while True:
        value = input("현재 그리퍼 상태 [1:누름판 / 2:삽 / 3:비어있음]: ").strip().lower()
        if value in choices:
            return choices[value]
        print("1, 2, 3 중 하나를 입력하세요.")


def put_down_held_tool(held_tool: str) -> None:
    node_name = TOOL_PUTDOWN_NODES.get(held_tool)
    if node_name is None:
        return

    print(f"현재 tool={held_tool}: {node_name} 실행")
    subprocess.run(["ros2", "run", "robot_tests", node_name], check=True)


def is_home(current_joint: list[float]) -> bool:
    return all(
        abs(current - target) <= HOME_TOLERANCE_DEG
        for current, target in zip(current_joint, HOME_JOINT)
    )


def run_sequence(node, apis, set_digital_outputs, get_current_posj) -> None:
    current_joint = normalize_pose(get_current_posj())
    if is_home(current_joint):
        node.get_logger().info("Already at HOME; skip initial home move")
    else:
        move_j(node, apis["movej"], apis["posj"], apis["wait"], "HOME", HOME_JOINT)

    run_rock_remove_action(node, apis, set_digital_outputs, "fixed", {})


def main(args: list[str] | None = None) -> None:
    parsed, ros_args = parse_args(sys.argv[1:] if args is None else args)
    held_tool = parsed.held_tool or prompt_held_tool()
    put_down_held_tool(held_tool)

    rclpy.init(args=ros_args)
    node = rclpy.create_node("tray_rock_remove", namespace=ROBOT_ID)
    DR_init.__dsr__node = node

    try:
        apis = import_basic_motion_apis(node)
        from DSR_ROBOT2 import get_current_posj

        set_digital_outputs_fn, set_digital_output_fn = import_digital_output_apis()
        set_digital_outputs = set_outputs_compat(
            node,
            set_digital_outputs_fn=set_digital_outputs_fn,
            set_digital_output_fn=set_digital_output_fn,
        )
        setup_tool_and_tcp(
            node,
            apis["set_tool"],
            apis["set_tcp"],
            PRESS_TOOL_NAME,
            PRESS_TCP_NAME,
        )
        run_sequence(node, apis, set_digital_outputs, get_current_posj)
        node.get_logger().info("tray_rock_remove fixed-route test complete")
    except KeyboardInterrupt:
        node.get_logger().info("Stopped by user")
    except Exception as exc:
        node.get_logger().error(f"tray_rock_remove failed: {exc}")
        raise
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
