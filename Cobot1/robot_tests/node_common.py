"""Common ROS/Doosan node helpers for robot test nodes."""

from __future__ import annotations

from typing import Any

ROBOT_ID = "dsr01"
ROBOT_MODEL = "m0609"


def configure_dsr_init(dr_init_module: Any) -> None:
    dr_init_module.__dsr__id = ROBOT_ID
    dr_init_module.__dsr__model = ROBOT_MODEL


def import_basic_motion_apis(node):
    try:
        from DSR_ROBOT2 import DR_BASE, get_current_posx, movej, movel, set_tcp, set_tool, wait
        from DR_common2 import posj, posx
    except ImportError as exc:
        node.get_logger().error(f"Failed to import Doosan API: {exc}")
        node.destroy_node()
        raise

    return {
        "DR_BASE": DR_BASE,
        "get_current_posx": get_current_posx,
        "movej": movej,
        "movel": movel,
        "set_tcp": set_tcp,
        "set_tool": set_tool,
        "wait": wait,
        "posj": posj,
        "posx": posx,
    }


def import_digital_output_apis():
    try:
        from DSR_ROBOT2 import set_digital_outputs as set_digital_outputs_fn
    except ImportError:
        set_digital_outputs_fn = None

    try:
        from DSR_ROBOT2 import set_digital_output as set_digital_output_fn
    except ImportError:
        set_digital_output_fn = None

    return set_digital_outputs_fn, set_digital_output_fn


def setup_tool_and_tcp(node, set_tool, set_tcp, tool_name: str, tcp_name: str) -> None:
    set_tool(tool_name)
    set_tcp(tcp_name)
    node.get_logger().info(f"Configured tool={tool_name}, tcp={tcp_name}")
