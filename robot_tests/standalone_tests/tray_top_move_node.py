# 홈에서 출발해 선택한 트레이의 기본 상단 조인트로만 이동하는 테스트 코드다.
"""Move to selected tray top joint."""

from __future__ import annotations

import rclpy

from robot_tests.dsr_runtime import bootstrap_dsr_python
from robot_tests.motion_primitives import HOME_JOINT, move_j, prepare_home_joint, set_outputs_compat
from robot_tests.node_common import (
    ROBOT_ID,
    ROBOT_MODEL,
    configure_dsr_init,
    import_basic_motion_apis,
    import_digital_output_apis,
    setup_tool_and_tcp,
)
from robot_tests.plant_pick_and_place_common import TARGET_TRAY_PLACE_JOINTS, TCP_NAME, TOOL_NAME

bootstrap_dsr_python()

import DR_init

configure_dsr_init(DR_init)


def prompt_choice(prompt: str, valid_values: list[str]) -> str:
    valid_map = {value.upper(): value for value in valid_values}
    while True:
        raw = input(prompt).strip()
        if not raw:
            print("입력이 비었습니다. 다시 입력하세요.")
            continue
        if raw.lower() == "q":
            raise KeyboardInterrupt
        key = raw.upper()
        if key not in valid_map:
            print(f"잘못된 입력입니다. 가능한 값: {', '.join(valid_values)}")
            continue
        return valid_map[key]


def prompt_target_tray() -> str:
    return prompt_choice("\n이동할 트레이 선택 [A/B/C/D], 종료 [q]: ", ["A", "B", "C", "D"]).upper()


def main(args=None):
    rclpy.init(args=args)

    node = rclpy.create_node("tray_top_move", namespace=ROBOT_ID)
    DR_init.__dsr__node = node

    try:
        motion_apis = import_basic_motion_apis(node)
    except ImportError:
        node.destroy_node()
        rclpy.shutdown()
        return

    set_digital_outputs_fn, set_digital_output_fn = import_digital_output_apis()

    try:
        set_digital_outputs = set_outputs_compat(
            node,
            set_digital_outputs_fn=set_digital_outputs_fn,
            set_digital_output_fn=set_digital_output_fn,
        )

        setup_tool_and_tcp(node, motion_apis["set_tool"], motion_apis["set_tcp"], TOOL_NAME, TCP_NAME)

        tray_map = {
            "A": "tray_a",
            "B": "tray_b",
            "C": "tray_c",
            "D": "tray_d",
        }

        while rclpy.ok():
            target_tray_label = prompt_target_tray()
            target_tray = tray_map[target_tray_label]
            top_joint = TARGET_TRAY_PLACE_JOINTS[target_tray]["top"]

            node.get_logger().info(f"Selected target tray={target_tray_label} top={top_joint}")
            prepare_home_joint(node, set_digital_outputs, motion_apis["wait"])
            move_j(node, motion_apis["movej"], motion_apis["posj"], motion_apis["wait"], "HOME", HOME_JOINT)
            move_j(
                node,
                motion_apis["movej"],
                motion_apis["posj"],
                motion_apis["wait"],
                f"{target_tray}_top",
                top_joint,
            )

    except KeyboardInterrupt:
        node.get_logger().info("Stopped by user")
    except Exception as exc:
        node.get_logger().error(f"tray_top_move failed: {exc}")
        raise
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
