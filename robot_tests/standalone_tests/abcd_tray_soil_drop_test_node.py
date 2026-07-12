"""Interactive test node for dropping scooped soil to a selected tray."""

from __future__ import annotations

import rclpy

from robot_tests.dsr_runtime import bootstrap_dsr_python
from robot_tests.node_common import (
    ROBOT_ID,
    configure_dsr_init,
    setup_tool_and_tcp,
)
from robot_tests.robot_motion_data import (
    A_TRAY_SOIL_DROP_CYCLES,
    B_TRAY_SOIL_DROP_CYCLES,
    D_TRAY_SOIL_DROP_CYCLES,
    SOIL_DROP_C_TRAY_CYCLES,
    SOIL_SERVICE_TCP_NAME,
    SOIL_SERVICE_TOOL_NAME,
)
from robot_tests.tray_soil_service_common import (
    drop_soil_to_a_tray_test,
    drop_soil_to_b_tray_test,
    drop_soil_to_c_tray_test,
    drop_soil_to_d_tray_test,
    fill_shovel_from_supply,
    go_home_with_gripper_held,
    import_soil_service_apis,
    prompt_target_tray,
)

bootstrap_dsr_python()

import DR_init

configure_dsr_init(DR_init)


TRAY_DROP_PLANS = {
    "A": {
        "cycles": A_TRAY_SOIL_DROP_CYCLES,
        "drop_fn": drop_soil_to_a_tray_test,
    },
    "B": {
        "cycles": B_TRAY_SOIL_DROP_CYCLES,
        "drop_fn": drop_soil_to_b_tray_test,
    },
    "C": {
        "cycles": SOIL_DROP_C_TRAY_CYCLES,
        "drop_fn": drop_soil_to_c_tray_test,
    },
    "D": {
        "cycles": D_TRAY_SOIL_DROP_CYCLES,
        "drop_fn": drop_soil_to_d_tray_test,
    },
}


def main(args=None):
    rclpy.init(args=args)
    node = rclpy.create_node("abcd_tray_soil_drop_test", namespace=ROBOT_ID)
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

        node.get_logger().info("abcd_tray_soil_drop_test started")
        node.get_logger().info("Assumption: shovel is already gripped before this node starts")

        while rclpy.ok():
            tray_name = prompt_target_tray()
            plan = TRAY_DROP_PLANS[tray_name]
            total_cycles = len(plan["cycles"])

            node.get_logger().info(f"Selected tray={tray_name}, total_cycles={total_cycles}")

            for cycle_index in range(total_cycles):
                node.get_logger().info(f"Cycle {cycle_index + 1}/{total_cycles}: scoop from supply")
                fill_shovel_from_supply(node, apis)
                node.get_logger().info(f"Cycle {cycle_index + 1}/{total_cycles}: drop to {tray_name} tray")
                try:
                    plan["drop_fn"](node, apis, cycle_index)
                except Exception as exc:
                    node.get_logger().error(
                        f"Drop failed at tray={tray_name}, cycle={cycle_index + 1}/{total_cycles}: {exc}"
                    )
                    raise

            node.get_logger().info(f"{tray_name} tray soil drop test finished")
            go_home_with_gripper_held(node, apis)
            returned_home = True
    except KeyboardInterrupt:
        node.get_logger().info("Stopped by user")
    except Exception as exc:
        node.get_logger().error(f"abcd_tray_soil_drop_test failed: {exc}")
        raise
    finally:
        if "apis" in locals() and not returned_home:
            try:
                go_home_with_gripper_held(node, apis)
            except Exception as home_exc:
                node.get_logger().error(f"Failed to return home: {home_exc}")
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
