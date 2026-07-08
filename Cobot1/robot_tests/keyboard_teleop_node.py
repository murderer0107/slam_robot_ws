# 키보드 입력으로 TCP를 수동 조그 이동시키는 텔레옵 코드다.
"""Keyboard teleop node for Doosan collaborative robot TCP jogging."""

from __future__ import annotations

import select
import sys
import termios
import tty
from typing import Any

import rclpy

from robot_tests.dsr_runtime import bootstrap_dsr_python
from robot_tests.motion_primitives import normalize_pose
from robot_tests.robot_motion_data import (
    KEYBOARD_DEFAULT_ACC,
    KEYBOARD_DEFAULT_STEP,
    KEYBOARD_DEFAULT_VEL,
)

bootstrap_dsr_python()

import DR_init
from robot_tests.node_common import ROBOT_ID, ROBOT_MODEL, configure_dsr_init

DEFAULT_STEP = KEYBOARD_DEFAULT_STEP
DEFAULT_VEL = KEYBOARD_DEFAULT_VEL
DEFAULT_ACC = KEYBOARD_DEFAULT_ACC

configure_dsr_init(DR_init)


class KeyboardTeleopNode:
    def __init__(self, node, get_current_posx, movel, set_digital_outputs, dr_base, posx) -> None:
        self.node = node
        self._get_current_posx = get_current_posx
        self._movel = movel
        self._set_digital_outputs = set_digital_outputs
        self.dr_base = dr_base
        self._posx = posx
        self.step = float(self.node.declare_parameter("step_mm", DEFAULT_STEP).value)
        self.vel = float(self.node.declare_parameter("velocity", DEFAULT_VEL).value)
        self.acc = float(self.node.declare_parameter("acceleration", DEFAULT_ACC).value)

    def print_help(self) -> None:
        help_text = [
            "",
            "[Keyboard Teleop]",
            f"STEP={self.step:.1f} mm, VEL={self.vel:.1f}, ACC={self.acc:.1f}, REF=DR_BASE",
            "w/s : x+ / x-",
            "a/d : y+ / y-",
            "z/c : z- / z+",
            "r/f/g : gripper open / close / strong close(0010)",
            "i/o/p : print x / y / z",
            "h : print x, y, z",
            "q or Ctrl+C : quit",
            "",
        ]
        for line in help_text:
            self.node.get_logger().info(line)

    def get_key(self) -> str:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            select.select([sys.stdin], [], [])
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def get_xyz(self) -> tuple[float, float, float]:
        pose = normalize_pose(self._get_current_posx(ref=self.dr_base))
        return pose[0], pose[1], pose[2]

    def move_relative(self, dx: float = 0.0, dy: float = 0.0, dz: float = 0.0) -> None:
        before_pose = normalize_pose(self._get_current_posx(ref=self.dr_base))
        target_pose = before_pose.copy()
        target_pose[0] += float(dx)
        target_pose[1] += float(dy)
        target_pose[2] += float(dz)

        self.node.get_logger().info(
            f"Move command: dx={dx:.3f}, dy={dy:.3f}, dz={dz:.3f} -> "
            f"x={target_pose[0]:.3f}, y={target_pose[1]:.3f}, z={target_pose[2]:.3f}"
        )

        self._movel(
            self._posx(target_pose),
            vel=self.vel,
            acc=self.acc,
            ref=self.dr_base,
        )

    def print_position(self, mode: str = "all") -> None:
        x, y, z = self.get_xyz()

        if mode == "x":
            self.node.get_logger().info(f"Current x: {x:.3f}")
            return
        if mode == "y":
            self.node.get_logger().info(f"Current y: {y:.3f}")
            return
        if mode == "z":
            self.node.get_logger().info(f"Current z: {z:.3f}")
            return

        self.node.get_logger().info(f"Current xyz: x={x:.3f}, y={y:.3f}, z={z:.3f}")

    def gripper_open(self) -> None:
        # Wiring may differ on real hardware. Swap open/close outputs if operation is reversed.
        self._set_digital_outputs([-1, 2, -3])
        self.node.get_logger().info("Gripper open command sent")

    def gripper_close(self) -> None:
        # Wiring may differ on real hardware. Swap open/close outputs if operation is reversed.
        self._set_digital_outputs([1, -2, -3])
        self.node.get_logger().info("Gripper close command sent")

    def gripper_strong_close(self) -> None:
        self._set_digital_outputs([-1, -2, 3, -4])
        self.node.get_logger().info("Gripper strong close command sent (0010)")

    def run(self) -> None:
        self.print_help()

        while rclpy.ok():
            try:
                key = self.get_key()
            except KeyboardInterrupt:
                self.node.get_logger().info("Ctrl+C received. Shutting down.")
                break
            except Exception as exc:
                self.node.get_logger().error(f"Key read failed: {exc}")
                continue

            if key in ("\x03", "q"):
                self.node.get_logger().info("Exit requested. Shutting down.")
                break

            try:
                if key == "w":
                    self.move_relative(dx=self.step)
                elif key == "s":
                    self.move_relative(dx=-self.step)
                elif key == "a":
                    self.move_relative(dy=self.step)
                elif key == "d":
                    self.move_relative(dy=-self.step)
                elif key == "z":
                    self.move_relative(dz=-self.step)
                elif key == "c":
                    self.move_relative(dz=self.step)
                elif key == "r":
                    self.gripper_open()
                elif key == "f":
                    self.gripper_close()
                elif key == "g":
                    self.gripper_strong_close()
                elif key == "i":
                    self.print_position(mode="x")
                elif key == "o":
                    self.print_position(mode="y")
                elif key == "p":
                    self.print_position(mode="z")
                elif key == "h":
                    self.print_position(mode="all")
                else:
                    self.node.get_logger().info(f"Unknown key: {repr(key)}")
            except Exception as exc:
                self.node.get_logger().error(f"Command failed for key {repr(key)}: {exc}")


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    ros_node = rclpy.create_node("keyboard_teleop_node", namespace=ROBOT_ID)
    DR_init.__dsr__node = ros_node
    node: KeyboardTeleopNode | None = None

    try:
        from DSR_ROBOT2 import DR_BASE, get_current_posx, movel
        from DR_common2 import posx

        try:
            from DSR_ROBOT2 import set_digital_outputs
        except ImportError:
            from DSR_ROBOT2 import set_digital_output

            def set_digital_outputs(channels: list[int]) -> None:
                for channel in channels:
                    index = abs(int(channel))
                    value = 1 if int(channel) > 0 else 0
                    set_digital_output(index, value)

        node = KeyboardTeleopNode(
            node=ros_node,
            get_current_posx=get_current_posx,
            movel=movel,
            set_digital_outputs=set_digital_outputs,
            dr_base=DR_BASE,
            posx=posx,
        )
        node.run()
    except KeyboardInterrupt:
        if node is not None:
            node.node.get_logger().info("Stopped by user")
        else:
            ros_node.get_logger().info("Stopped by user")
    except Exception as exc:
        if node is not None:
            node.node.get_logger().error(f"Node failed: {exc}")
        else:
            ros_node.get_logger().error(f"Node failed before init: {exc}")
    finally:
        ros_node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
