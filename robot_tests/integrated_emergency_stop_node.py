# 통합본 전용 긴급정지 노드다. MoveStop 서비스로 즉시 정지를 요청한다.
from __future__ import annotations

import rclpy

from robot_tests.dsr_runtime import bootstrap_dsr_python
from robot_tests.node_common import ROBOT_ID, configure_dsr_init

bootstrap_dsr_python()

import DR_init

configure_dsr_init(DR_init)

DEFAULT_QSTOP = 1


def main(args=None):
    rclpy.init(args=args)
    node = rclpy.create_node("integrated_emergency_stop", namespace=ROBOT_ID)
    DR_init.__dsr__node = node

    try:
        try:
            from dsr_msgs2.srv import MoveStop
        except ImportError as exc:
            raise RuntimeError(f"Failed to import MoveStop service: {exc}") from exc

        stop_mode = DEFAULT_QSTOP
        try:
            from DSR_ROBOT2 import DR_QSTOP

            stop_mode = DR_QSTOP
        except ImportError:
            node.get_logger().warn("DR_QSTOP import failed, fallback to stop_mode=1")

        client = node.create_client(MoveStop, f"/{ROBOT_ID}/motion/move_stop")
        if not client.wait_for_service(timeout_sec=1.0):
            raise RuntimeError("MoveStop service unavailable")

        request = MoveStop.Request()
        request.stop_mode = int(stop_mode)

        future = client.call_async(request)
        rclpy.spin_until_future_complete(node, future, timeout_sec=2.0)

        if not future.done():
            raise TimeoutError("MoveStop service response timeout")
        response = future.result()
        if response is None or not response.success:
            raise RuntimeError("MoveStop service call rejected")

        node.get_logger().info(f"Emergency stop requested stop_mode={stop_mode}")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
