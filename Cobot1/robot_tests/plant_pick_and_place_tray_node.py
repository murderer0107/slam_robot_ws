# 홈에서 출발해 모종을 집고 다른 트레이에 옮겨 심는 테스트 코드다.
"""Doosan M0609 plant pick route test node."""

from __future__ import annotations

import rclpy

from robot_tests.dsr_runtime import bootstrap_dsr_python
from robot_tests.motion_primitives import (
    set_outputs_compat,
)
from robot_tests.node_common import (
    ROBOT_ID,
    ROBOT_MODEL,
    configure_dsr_init,
    import_basic_motion_apis,
    import_digital_output_apis,
    setup_tool_and_tcp,
)
from robot_tests.plant_pick_and_place_common import (
    TARGET_TRAY_PLACE_JOINTS,
    TOOL_NAME,
    TCP_NAME,
    run_plant_pick_and_place_sequence,
)
from robot_tests.robot_motion_data import (
    PLANT_ACTIVE_PLANT as ACTIVE_PLANT,
    PLANT_ACTIVE_TARGET_TRAY as ACTIVE_TARGET_TRAY,
    PLANT_ACTIVE_TRAY as ACTIVE_TRAY,
)

bootstrap_dsr_python()

import DR_init

configure_dsr_init(DR_init)


def main(args=None):
    rclpy.init(args=args)

    node = rclpy.create_node("plant_pick_and_place_tray", namespace=ROBOT_ID)
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

        run_plant_pick_and_place_sequence(
            node=node,
            movej=motion_apis["movej"],
            movel=motion_apis["movel"],
            posj=motion_apis["posj"],
            posx=motion_apis["posx"],
            set_digital_outputs=set_digital_outputs,
            wait=motion_apis["wait"],
            get_current_posx=motion_apis["get_current_posx"],
            dr_base=motion_apis["DR_BASE"],
            source_tray=ACTIVE_TRAY,
            plant_index=ACTIVE_PLANT,
            target_tray=ACTIVE_TARGET_TRAY,
        )
        node.get_logger().info(
            "plant_pick_and_place_tray route test complete; "
            f"final place joint={TARGET_TRAY_PLACE_JOINTS[ACTIVE_TARGET_TRAY]['down']}"
        )

    except KeyboardInterrupt:
        node.get_logger().info("Stopped by user")
    except Exception as exc:
        node.get_logger().error(f"plant_pick_and_place_tray failed: {exc}")
        raise
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
