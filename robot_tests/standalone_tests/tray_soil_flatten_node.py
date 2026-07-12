"""Flatten tray surface by probing and pressing points without recording measurements."""

from __future__ import annotations

import rclpy

from robot_tests.compliance_common import extract_fz, safe_release_compliance
from robot_tests.dsr_runtime import bootstrap_dsr_python
from robot_tests.motion_primitives import normalize_pose
from robot_tests.node_common import (
    ROBOT_ID,
    configure_dsr_init,
    setup_tool_and_tcp,
)
from robot_tests.robot_motion_data import (
    TRAY_SOIL_TCP_NAME,
    TRAY_SOIL_TOOL_NAME,
    TRAY_CORNERS_XYZ,
    TRAY_SOIL_ACC,
    TRAY_SOIL_FLATTEN_ACC,
    TRAY_SOIL_FLATTEN_CONTACT_DELTA_FZ,
    TRAY_SOIL_FLATTEN_EXTRA_PRESS_MM,
    TRAY_SOIL_FLATTEN_HOLD_SEC,
    TRAY_SOIL_FLATTEN_VEL,
    TRAY_SOIL_MAX_DOWN_DISTANCE,
    TRAY_SOIL_PROBE_ACC,
    TRAY_SOIL_PROBE_VEL,
    TRAY_SOIL_TOP_POSES,
    TRAY_SOIL_VEL,
)
from robot_tests.tray_soil_service_common import (
    go_home_with_gripper_held,
    import_soil_service_apis,
    prompt_target_tray,
)

bootstrap_dsr_python()

import DR_init

configure_dsr_init(DR_init)


def make_pose(posx_fn, x: float, y: float, z: float, rx: float, ry: float, rz: float):
    return posx_fn(float(x), float(y), float(z), float(rx), float(ry), float(rz))


def make_corner_top_pose(posx_fn, base_top_pose: list[float], x: float, y: float, z: float):
    return make_pose(posx_fn, x, y, z, base_top_pose[3], base_top_pose[4], base_top_pose[5])


def run_tray_flatten_sequence(node, apis, tray_name: str) -> None:
    def move_line(name: str, target, vel: float = TRAY_SOIL_VEL, acc: float = TRAY_SOIL_ACC, sleep: float = 1.0):
        node.get_logger().info(f"Move start: {name} -> {target}")
        ret = apis["movel"](target, vel=vel, acc=acc)
        node.get_logger().info(f"Move ret: {name} = {ret}")
        apis["wait"](sleep)

    def return_to_pose(name: str, pose_values: list[float]) -> None:
        node.get_logger().info(f"Return to {name}")
        apis["movel"](apis["posx"](pose_values), vel=TRAY_SOIL_PROBE_VEL, acc=TRAY_SOIL_PROBE_ACC)
        apis["wait"](1.0)

    def compliance_press_down(corner_name: str, top_pose_values: list[float]) -> None:
        start_pose = normalize_pose(apis["get_current_posx"](ref=apis["DR_BASE"]))
        start_z = start_pose[2]
        limit_pose = start_pose.copy()
        limit_pose[2] = start_z - TRAY_SOIL_MAX_DOWN_DISTANCE

        node.get_logger().info(
            f"{tray_name}_{corner_name} flatten down start_z={start_z:.3f}, "
            f"delta_fz={TRAY_SOIL_FLATTEN_CONTACT_DELTA_FZ}"
        )

        apis["task_compliance_ctrl"]()
        apis["wait"](0.5)
        base_fz = extract_fz(apis["get_tool_force"](ref=apis["DR_BASE"]))
        contact_pose = None

        apis["amovel"](apis["posx"](limit_pose), vel=TRAY_SOIL_PROBE_VEL, acc=TRAY_SOIL_PROBE_ACC)

        while apis["check_motion"]() == 2:
            apis["wait"](0.05)
            current_pose = normalize_pose(apis["get_current_posx"](ref=apis["DR_BASE"]))
            current_fz = extract_fz(apis["get_tool_force"](ref=apis["DR_BASE"]))
            delta_fz = abs(current_fz - base_fz)

            if delta_fz >= TRAY_SOIL_FLATTEN_CONTACT_DELTA_FZ:
                contact_pose = current_pose
                node.get_logger().info(
                    f"{tray_name}_{corner_name} contact detected z={current_pose[2]:.3f}"
                )
                break

        if contact_pose is None:
            current_pose = normalize_pose(apis["get_current_posx"](ref=apis["DR_BASE"]))
            node.get_logger().warn(
                f"{tray_name}_{corner_name} contact failed, limit reached z={current_pose[2]:.3f}"
            )
            safe_release_compliance(node, apis["release_compliance_ctrl"])
            return_to_pose(f"{tray_name}_{corner_name}_TOP", top_pose_values)
            return

        safe_release_compliance(node, apis["release_compliance_ctrl"])

        press_pose = contact_pose.copy()
        press_pose[2] -= TRAY_SOIL_FLATTEN_EXTRA_PRESS_MM
        move_line(
            f"{tray_name}_{corner_name}_PRESS_EXTRA",
            apis["posx"](press_pose),
            vel=TRAY_SOIL_FLATTEN_VEL,
            acc=TRAY_SOIL_FLATTEN_ACC,
            sleep=0.2,
        )
        apis["wait"](TRAY_SOIL_FLATTEN_HOLD_SEC)
        return_to_pose(f"{tray_name}_{corner_name}_TOP", top_pose_values)

    tray_top_pose = normalize_pose(TRAY_SOIL_TOP_POSES[tray_name])
    move_line(f"{tray_name}_CENTER_TOP", apis["posx"](tray_top_pose))

    for corner_name, (x, y, z) in TRAY_CORNERS_XYZ[tray_name]:
        top_pose = normalize_pose(make_corner_top_pose(apis["posx"], tray_top_pose, x, y, z))
        move_line(
            f"{tray_name}_{corner_name}_TOP",
            apis["posx"](top_pose),
            vel=TRAY_SOIL_VEL,
            acc=TRAY_SOIL_ACC,
            sleep=0.5,
        )
        compliance_press_down(corner_name, top_pose)

    move_line(f"{tray_name}_CENTER_TOP_RETURN", apis["posx"](tray_top_pose))


def main(args=None):
    rclpy.init(args=args)
    node = rclpy.create_node("tray_soil_flatten", namespace=ROBOT_ID)
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
            TRAY_SOIL_TOOL_NAME,
            TRAY_SOIL_TCP_NAME,
        )
        go_home_with_gripper_held(node, apis)

        tray_name = prompt_target_tray()
        run_tray_flatten_sequence(node, apis, tray_name)

        go_home_with_gripper_held(node, apis)
        node.get_logger().info("tray_soil_flatten finished")
    except KeyboardInterrupt:
        node.get_logger().info("Stopped by user")
    except Exception as exc:
        node.get_logger().error(f"tray_soil_flatten failed: {exc}")
        raise
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
