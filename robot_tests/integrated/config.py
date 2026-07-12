"""Integrated dashboard config and shared constants."""

from __future__ import annotations

from robot_tests.robot_motion_data import HOME_JOINT

TRAY_LABELS = ("A", "B", "C", "D")

INITIAL_SOIL_STATUS = "미측정"

NEXT_ACTION_MEASURE = "토양 측정"
NEXT_ACTION_ADD_SOIL = "흙추가"
NEXT_ACTION_REMOVE_SOIL = "흙제거"
NEXT_ACTION_REMOVE_ROCK = "돌제거"
NEXT_ACTION_FLATTEN = "평탄화"
NEXT_ACTION_PLANT = "식물 심기"
NEXT_ACTION_DONE = "완료"
NEXT_BUTTON_DEFAULT_TEXT = "다음 작업"

WORK_PHASE_IDLE = "IDLE"
WORK_PHASE_AFTER_CORRECTION = "AFTER_CORRECTION"
WORK_PHASE_DONE = "DONE"

SOIL_STATUS_UNKNOWN = "미측정"
SOIL_STATUS_LOW = "흙부족"
SOIL_STATUS_OK = "정상"
SOIL_STATUS_HIGH = "흙많음"
SOIL_STATUS_OBSTACLE = "장애물감지"
SOIL_STATUS_FAILED = "측정실패"

TOOL_STATE_NONE = "NONE"
TOOL_STATE_PRESS = "PRESS_PLATE_HELD"
TOOL_STATE_SHOVEL = "SHOVEL_HELD"
TOOL_STATE_UNKNOWN = "UNKNOWN"

HOME_POSE = list(HOME_JOINT)

WORKSPACE_SETUP_PATH = "/home/rokey/ws_cobot_pjt/ws_cobot1/install/setup.bash"

UI_PATH_CANDIDATES = (
    "/home/rokey/ws_cobot_pjt/ws_cobot1/src/robot_tests/robot_tests/integrated/smartfarm_dashboard.ui",
)

ROS_CONNECTION_CHECK_SERVICE = "/dsr01/system/get_robot_state"
INTER_NODE_DELAY_MS = 1000
PRESS_PICKUP_HANDOFF_DELAY_MS = 500
PRESS_PUTDOWN_HANDOFF_DELAY_MS = 500

MEASURE_NODE = "integrated_tray_soil_state_check_node"
FLATTEN_NODE = "integrated_tray_soil_flatten_node"
REMOVE_SOIL_NODE = "tray_soil_remove_node"
ADD_SOIL_NODE = "tray_soil_add_node"
ROCK_REMOVE_NODE = "tray_rock_remove_node"
PLANT_NODE = "plant_pick_and_place_tray_select_node"
HOME_NODE = "go_home_test"
PRESS_PICKUP_NODE = "press_plate_pickup_node"
PRESS_PUTDOWN_NODE = "press_plate_putdown_node"
SHOVEL_PICKUP_NODE = "shovel_pickup_node"
SHOVEL_PUTDOWN_NODE = "shovel_putdown_node"
INTEGRATED_PLANT_NODE = "integrated_plant_pick_and_place_node"
INTEGRATED_FLATTEN_NODE = "integrated_tray_soil_flatten_node"
INTEGRATED_NEXT_STEP_NODE = "integrated_tray_next_step_node"
INTEGRATED_MANUAL_NODE = "integrated_manual_control_node"
INTEGRATED_ESTOP_NODE = "integrated_emergency_stop_node"

TRAY_TO_PLANT_INDEX = {
    "A": 1,
    "B": 2,
    "C": 3,
    "D": 4,
}
