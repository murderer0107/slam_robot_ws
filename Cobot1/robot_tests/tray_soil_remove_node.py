"""Remove soil from tray when tray soil inspection says SOIL_HIGH."""

from __future__ import annotations

import rclpy

from robot_tests.dsr_runtime import bootstrap_dsr_python
from robot_tests.motion_primitives import set_outputs_compat
from robot_tests.node_common import (
    ROBOT_ID,
    configure_dsr_init,
    import_digital_output_apis,
    setup_tool_and_tcp,
)
from robot_tests.robot_motion_data import SOIL_SERVICE_TCP_NAME, SOIL_SERVICE_TOOL_NAME
from robot_tests.tray_soil_service_common import (
    go_home_with_gripper_held,
    import_soil_service_apis,
    inspect_tray_soil,
    prompt_target_tray,
    require_soil_state,
    run_soil_remove_action,
)

bootstrap_dsr_python()

import DR_init

configure_dsr_init(DR_init)


def main(args=None):
    rclpy.init(args=args)
    node = rclpy.create_node("tray_soil_remove", namespace=ROBOT_ID)
    DR_init.__dsr__node = node

    try:
        apis = import_soil_service_apis(node)
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

        setup_tool_and_tcp(node, apis["set_tool"], apis["set_tcp"], SOIL_SERVICE_TOOL_NAME, SOIL_SERVICE_TCP_NAME)
        go_home_with_gripper_held(node, apis)

        tray_name = prompt_target_tray()
        result = inspect_tray_soil(node, apis, tray_name)
        if require_soil_state(node, result, "SOIL_HIGH"):
            run_soil_remove_action(node, apis, set_digital_outputs, tray_name, result)

        go_home_with_gripper_held(node, apis)
        node.get_logger().info("tray_soil_remove finished")
    except KeyboardInterrupt:
        node.get_logger().info("Stopped by user")
    except Exception as exc:
        node.get_logger().error(f"tray_soil_remove failed: {exc}")
        raise
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
