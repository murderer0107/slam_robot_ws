# 현재 TCP 위치에서 아래로 눌러 접촉을 확인한 뒤 다시 상승하는 테스트 코드다.
"""Doosan M0609 simple compliance down/up test from current TCP pose."""

from __future__ import annotations

import rclpy

from robot_tests.compliance_common import extract_fz, safe_release_compliance, safe_return_to_start
from robot_tests.dsr_runtime import bootstrap_dsr_python
from robot_tests.motion_primitives import normalize_pose
from robot_tests.node_common import ROBOT_ID, ROBOT_MODEL, configure_dsr_init
from robot_tests.robot_motion_data import (
    SIMPLE_COMPLIANCE_ACC as ACC,
    SIMPLE_COMPLIANCE_CONTACT_DELTA_FZ as CONTACT_DELTA_FZ,
    SIMPLE_COMPLIANCE_MAX_DOWN_DISTANCE as MAX_DOWN_DISTANCE,
    SIMPLE_COMPLIANCE_VEL as VEL,
)

bootstrap_dsr_python()

import DR_init

def log_force(node, get_tool_force, ref, label):
    try:
        force = get_tool_force(ref=ref)

        if isinstance(force, (list, tuple)) and len(force) >= 6:
            node.get_logger().info(
                f"{label} tool_force "
                f"fx={float(force[0]):.3f}, fy={float(force[1]):.3f}, fz={float(force[2]):.3f}, "
                f"tx={float(force[3]):.3f}, ty={float(force[4]):.3f}, tz={float(force[5]):.3f}"
            )
        else:
            node.get_logger().info(f"{label} tool_force={force}")

        return force

    except Exception as exc:
        node.get_logger().warn(f"{label} get_tool_force failed: {exc}")
        return None


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = rclpy.create_node("simple_compliance_down_up_test", namespace=ROBOT_ID)
    DR_init.__dsr__node = node
    configure_dsr_init(DR_init)

    try:
        from DSR_ROBOT2 import (
            DR_BASE,
            amovel,
            check_motion,
            get_current_posx,
            get_tool_force,
            movel,
            release_compliance_ctrl,
            task_compliance_ctrl,
            wait,
        )
        from DR_common2 import posx
    except ImportError as exc:
        node.get_logger().error(f"Failed to import Doosan API: {exc}")
        node.destroy_node()
        rclpy.shutdown()
        return

    start_pose: list[float] | None = None

    try:
        current_raw = get_current_posx(ref=DR_BASE)
        start_pose = normalize_pose(current_raw)
        start_z = start_pose[2]
        limit_z = start_z - MAX_DOWN_DISTANCE
        limit_pose = start_pose.copy()
        limit_pose[2] = limit_z

        node.get_logger().info(
            f"start_pose x={start_pose[0]:.3f}, y={start_pose[1]:.3f}, z={start_pose[2]:.3f}, "
            f"rx={start_pose[3]:.3f}, ry={start_pose[4]:.3f}, rz={start_pose[5]:.3f}"
        )
        node.get_logger().info(
            f"down config max_down_distance={MAX_DOWN_DISTANCE}, "
            f"contact_delta_fz={CONTACT_DELTA_FZ}, limit_z={limit_z:.3f}"
        )

        input("\nEnter 누르면 현재 위치에서 순응제어 하강/상승 테스트 시작: ")

        node.get_logger().info("Enable compliance control")
        task_compliance_ctrl()
        wait(0.5)
        base_force = get_tool_force(ref=DR_BASE)
        base_fz = extract_fz(base_force)
        node.get_logger().info(f"base_fz={base_fz:.3f}")

        contact_detected = False
        current_z = start_z

        node.get_logger().info(f"Move down {MAX_DOWN_DISTANCE}mm")
        amovel(posx(limit_pose), vel=VEL, acc=ACC)

        while check_motion() == 2:
            wait(0.05)
            current_pose = normalize_pose(get_current_posx(ref=DR_BASE))
            current_z = current_pose[2]
            force = get_tool_force(ref=DR_BASE)
            current_fz = extract_fz(force)
            delta_fz = abs(current_fz - base_fz)

            if delta_fz >= CONTACT_DELTA_FZ:
                node.get_logger().info(f"contact detected z={current_z:.3f}")
                contact_detected = True
                break

        if not contact_detected:
            current_pose = normalize_pose(get_current_posx(ref=DR_BASE))
            current_z = current_pose[2]
            node.get_logger().info(f"limit reached z={current_z:.3f}")

        safe_release_compliance(node, release_compliance_ctrl)
        node.get_logger().info("return to start_pose")
        movel(posx(start_pose), vel=VEL, acc=ACC)
        wait(1.0)
        node.get_logger().info("simple_compliance_down_up_test finished")

    except KeyboardInterrupt:
        node.get_logger().info("Stopped by user")
    except Exception as exc:
        node.get_logger().error(f"simple_compliance_down_up_test failed: {exc}")
        safe_release_compliance(node, release_compliance_ctrl)
        if all(name in locals() for name in ("movel", "posx", "wait")):
            safe_return_to_start(node, movel, posx, wait, start_pose, vel=VEL, acc=ACC)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
