"""Centralized robot motion constants and taught positions."""

from __future__ import annotations

# =========================
# Robot / Tool / TCP
# =========================
# 현재 테스트 노드들이 공통으로 사용하는 Doosan 로봇 ID/모델명이다.
# node_common.py의 기본 설정값과 같은 의미이며, 필요 시 한곳에서 관리하려고 둔 값이다.
ROBOT_ID = "dsr01"
ROBOT_MODEL = "m0609"

# 프레스 판 픽업/적치 계열 노드에서 setup_tool_and_tcp() 호출에 넘기는 툴/TCP 이름이다.
# 사용처: go_home_test_node.py, press_plate_pickup_node.py, press_plate_putdown_node.py
PRESS_TOOL_NAME = "Tool Weight_1"
PRESS_TCP_NAME = "GripperDA_v1"

# 모종 집기/이식 시퀀스에서 사용하는 툴/TCP 이름이다.
# 사용처: plant_pick_and_place_common.py, plant_pick_and_place_tray_node.py,
# plant_pick_and_place_tray_select_node.py
PLANT_TOOL_NAME = "Tool Weight"
PLANT_TCP_NAME = "Tool_v1"

# 흙 높이 측정 프로브 동작 전에 세팅하는 툴/TCP 이름이다.
# 사용처: tray_soil_state_check_node.py
TRAY_SOIL_TOOL_NAME = "Tool Weight"
TRAY_SOIL_TCP_NAME = "Tool_v1"

# =========================
# Common Home / Gripper
# =========================
# 대부분의 테스트가 시작/복귀 기준점으로 삼는 공통 홈 조인트다.
# 사용처: motion_primitives.py, press_plate_pickup_node.py, press_plate_putdown_node.py,
# tray_soil_state_check_node.py, plant_pick_and_place_common.py
HOME_JOINT = [0.0, -15.0, 102.0, 0.0, 90.0, 0.0]
# 그리퍼를 완전히 닫지 않고 준비 상태로 벌릴 때 쓰는 디지털 출력 패턴이다.
# 사용처: motion_primitives.py의 prepare_home_joint(), press_plate_pickup_node.py
GRIPPER_HOME_PREPARE = [-1, 2, -3, -4]  # 0100
# 모종/프레스 판을 잡기 위해 강하게 닫을 때 쓰는 디지털 출력 패턴이다.
# 사용처: motion_primitives.py, press_plate_pickup_node.py, plant_pick_and_place_common.py
GRIPPER_PICK_CLOSE = [-1, -2, 3, -4]  # 0010

# =========================
# Press Plate
# =========================
# 홈에서 프레스 작업 영역으로 진입할 때 충돌 회피용 중간 경유 Cartesian pose다.
# 사용처: press_plate_pickup_node.py, press_plate_putdown_node.py
PRESS_MID_POSE = [278.939, -86.0, 200.486, 89.08, 179.97, 89.05]
# 프레스 판 바로 위 대기 위치다. 집기/내려놓기 직전 상부 안전 높이로 쓴다.
# 사용처: press_plate_pickup_node.py, press_plate_putdown_node.py
PRESS_PLATE_TOP_POSE = [376.7, -86.0, 200.486, 89.08, 179.97, 89.05]
# 프레스 판을 실제로 집기 위해 하강하는 목표 Cartesian pose다.
# 사용처: press_plate_pickup_node.py
PRESS_PLATE_PICK_POSE = [376.7, -86.0, 13.0, 89.08, 179.97, 89.05]
# 프레스 판을 내려놓는 목표 Cartesian pose다.
# 현재 값은 pick pose와 동일하지만, 이후 놓는 위치가 달라지면 이 상수만 분리 수정하면 된다.
# 사용처: press_plate_putdown_node.py
PRESS_PLATE_PLACE_POSE = [376.7, -86.0, 13.0, 89.08, 179.97, 89.05]

# =========================
# Plant Pick And Place
# =========================
# 고정형 plant pick 테스트 노드가 기본으로 집을 소스 트레이다.
# 사용처: plant_pick_and_place_tray_node.py, plant_pick_and_place_tray_select_node.py
PLANT_ACTIVE_TRAY = "tray_a"
# 고정형 plant pick 테스트 노드가 기본으로 집을 모종 번호다.
# 사용처: plant_pick_and_place_tray_node.py
PLANT_ACTIVE_PLANT = 1
# 고정형 plant pick 테스트 노드가 기본으로 심을 대상 트레이다.
# 사용처: plant_pick_and_place_tray_node.py
PLANT_ACTIVE_TARGET_TRAY = "tray_a"

# 홈과 트레이 사이를 오갈 때 사용하는 공통 중간 waypoint Cartesian pose다.
# 사용처: plant_pick_and_place_common.py
PLANT_WAYPOINT1_POSE = [200.0, -148.0, 182.0, 134.0, 178.0, 134.0]
# 모종 픽업 시 진입 전에 그리퍼를 벌려 두는 출력 패턴이다.
# 사용처: plant_pick_and_place_common.py
PLANT_GRIPPER_WAYPOINT1_PREPARE = [1, -2, -3, -4]  # 1000

# 모종에 접근해 집는 구간에서 쓰는 상대적으로 느린 속도/가속도다.
# 사용처: plant_pick_and_place_common.py
PLANT_APPROACH_VEL = 20.0
PLANT_APPROACH_ACC = 20.0
# 집은 뒤 트레이 간 이송에서 쓰는 속도/가속도다.
# 사용처: plant_pick_and_place_common.py
PLANT_TRANSFER_VEL = 12.0
PLANT_TRANSFER_ACC = 12.0

# 각 소스 트레이 영역으로 처음 진입할 때 맞추는 entry joint다.
# 사용처: plant_pick_and_place_common.py에서 source_tray별 시작 진입점으로 사용한다.
TRAY_ENTRY_JOINTS = {
    "tray_a": [-37.0, 10.4, 83.3, -1.83, 86.57, -8.11],
}

# 소스 트레이 안 개별 모종 위치별 taught joint 묶음이다.
# pre_pick: 모종 바로 위 접근 위치
# pick: 실제로 집는 위치
# lift: 집은 뒤 위로 안전하게 빠지는 위치
# 사용처: plant_pick_and_place_common.py, plant_pick_and_place_tray_select_node.py
TRAY_PLANT_JOINTS = {
    "tray_a": {
        1: {
            "pre_pick": [-59.96, 26.93, 108.89, 55.70, 83.46, -47.82],
            "pick": [-50.16, 24.73, 112.94, 59.99, 76.35, -47.82],
            "lift": [-48.06, 3.47, 106.68, 56.34, 82.79, -19.29],
        },
        2: {
            "pre_pick": [-51.37, 24.18, 105.78, 53.66, 73.51, -38.56],
            "pick": [-41.81, 25.52, 105.71, 60.05, 68.61, -36.07],
            "lift": [-50.97, -1.83, 96.93, 57.82, 84.39, -6.41],
        },
        3: {
            "pre_pick": [-40.83, 35.05, 86.63, 53.79, 77.49, -33.43],
            "pick": [-35.98, 35.04, 86.51, 53.78, 75.11, -33.41],
            "lift": [-50.97, -1.83, 96.93, 57.82, 84.39, -6.41],
        },
        4: {
            "pre_pick": [-37.31, 42.49, 74.03, 54.13, 79.58, -30.83],
            "pick": [-33.31, 43.85, 72.60, 54.84, 79.37, -25.69],
            "lift": [-50.97, -1.83, 96.93, 57.82, 84.39, -6.41],
        },
    },
}

# 대상 트레이별 식재 위치 taught joint 묶음이다.
# top: 트레이 상부 대기 위치
# down: 실제로 내려가 심는 위치
# 2026-07-08 현장 재티칭 반영:
# 전달 순서는 트레이별 2개씩 A/B/C/D, 각 2개는 [down, top]이었다.
# 따라서 아래 저장값은 코드 의미(top -> 접근, down -> 설치)에 맞춰 재배치했다.
# 만약 현장 메모에서 "상단/하단"이 조인트 각도 크기 기준 표현이었다면 용어가 모호할 수 있으니
# 실제 로봇 동작은 tray별로 top 선행 후 down 하강 순서로 다시 확인하는 편이 안전하다.
# 사용처: plant_pick_and_place_common.py, plant_pick_and_place_tray_node.py,
# plant_pick_and_place_tray_select_node.py
TARGET_TRAY_PLACE_JOINTS = {
    "tray_a": {
        "top": [-11.35, -15.98, 120.22, 60.88, 64.38, 1.47],
        "down": [-14.66, 0.01, 133.86, 71.14, 60.49, -32.67],
    },
    "tray_b": {
        "top": [14.27, -6.83, 101.26, 13.80, 40.90, 61.23],
        "down": [14.18, -0.04, 119.96, 32.28, 17.12, 40.57],
    },
    "tray_c": {
        "top": [-40.24, -17.37, 114.22, 56.42, 83.88, -0.66],
        "down": [-41.65, -0.07, 130.02, 58.80, 70.84, -27.77],
    },
    "tray_d": {
        "top": [-15.43, -8.5, 109.49, 41.16, 48.33, 17.84],
        "down": [-15.49, -1.62, 123.53, 59.65, 34.77, -6.57],
    },
}

# =========================
# Tray Soil Check
# =========================
# 트레이 흙 상태 점검 노드의 일반 이동 속도/가속도다.
# 사용처: tray_soil_state_check_node.pyC
TRAY_SOIL_VEL = 200.0
TRAY_SOIL_ACC = 200.0
# 흙을 찌르며 내려갈 때 쓰는 저속 probe 속도/가속도다.
# 사용처: tray_soil_state_check_node.py
TRAY_SOIL_PROBE_VEL = 25.0
TRAY_SOIL_PROBE_ACC = 20.0
# 트레이 상부 기준 접근 Z 높이다.
# 사용처: tray_soil_state_check_node.py에서 상부 접근 pose 계산에 사용한다.
TRAY_SOIL_TOP_Z = 194.74
# 접촉 탐지 전까지 허용하는 최대 하강 거리다.
# 사용처: tray_soil_state_check_node.py
TRAY_SOIL_MAX_DOWN_DISTANCE = 260.0
# 힘 변화량으로 접촉을 판단할 때 쓰는 Fz 임계값이다.
# 사용처: tray_soil_state_check_node.py
TRAY_SOIL_CONTACT_DELTA_FZ = 4.0

# 측정된 침투 깊이를 low/ok/high 상태로 분류하는 임계 범위다.
# 사용처: tray_soil_state_check_node.py
TRAY_SOIL_LOW_MIN = 55.0
TRAY_SOIL_LOW_MAX = 65.0
TRAY_SOIL_OK_MIN = 66.0
TRAY_SOIL_OK_MAX = 74.0
TRAY_SOIL_HIGH_MIN = 75.0
TRAY_SOIL_HIGH_MAX = 87.0
# 코너 측정값이 평균과 크게 차이날 때 돌맹이 의심으로 보는 기준이다.
# 사용처: tray_soil_state_check_node.py
TRAY_SOIL_OUTLIER_DIFF = 10.0

# 흙 측정 시 툴 방향을 고정하는 자세 각도다.
# 사용처: tray_soil_state_check_node.py
TRAY_SOIL_RX = 89.08
TRAY_SOIL_RY = 179.97
TRAY_SOIL_RZ = 89.05

# 트레이별 흙 높이 측정 시작용 "기본 상단" 6축 pose다.
# 각 트레이 중심 상부로 먼저 이동할 때 쓰며, corner probing 자세 기준값 역할도 한다.
# 사용처: tray_soil_state_check_node.py
TRAY_SOIL_TOP_POSES = {
    "A": [385.31, 197.67, 284.0, 34.36, 175.78, 32.48],
    "B": [530.12, 202.37, 284.00, 34.36, 175.78, 32.48],
    "C": [383.38, 45.35, 284.00, 179.26, 179.66, -179.69],
    "D": [515.11, 52.51, 284.00, 29.66, 174.07, 24.49],
}

# 각 트레이 중앙 상부의 XY 기준점이다.
# 사용처: tray_soil_state_check_node.py에서 코너 위치 계산/로그 기준 XY로 사용한다.
# 참고: 실제 상단 접근 시작 자세는 TRAY_SOIL_TOP_POSES를 우선 사용한다.
TRAY_TOPS_XY = {
    "A": (392.0, 203.0),
    "B": (526.0, 201.0),
    "C": (387.0, 47.0),
    "D": (522.0, 42.0),
}

# 각 트레이 네 모서리 측정 포인트의 이름과 XYZ 좌표다.
# z는 코너 간 이동/프로빙 시작 높이를 통일하기 위한 상단 접근 높이다.
# 사용처: tray_soil_state_check_node.py에서 코너별 probing 순회에 사용한다.
TRAY_CORNERS_XYZ = {
    "A": [
        ("corner_1", (412.80, 235.45, 150.0)),
        ("corner_2", (415.25, 151.32, 150.0)),
        ("corner_3", (352.54, 235.52, 150.0)),
        ("corner_4", (351.92, 153.15, 150.0)),
    ],
    "B": [
        ("corner_1", (557.61, 238.15, 150.0)),
        ("corner_2", (560.06, 154.02, 150.0)),
        ("corner_3", (497.35, 238.22, 150.0)),
        ("corner_4", (496.73, 155.85, 150.0)),
    ],
    "C": [
        # 모든 트레이는 좌상단 -> 우상단 -> 좌하단 -> 우하단 순서로 probing한다.
        ("corner_1", (410.87, 83.13, 150.0)),
        ("corner_2", (413.32, -1.00, 150.0)),
        ("corner_3", (350.61, 83.20, 150.0)),
        ("corner_4", (349.99, 0.83, 150.0)),
    ],
    "D": [
        ("corner_1", (542.60, 83.8, 150.0)),
        ("corner_2", (545.05, -0.35, 150.0)),
        ("corner_3", (492.34, 83.84, 150.0)),
        ("corner_4", (491.72, 0.49, 150.0)),
    ],
}

# =========================
# Tray Soil Service
# =========================
# 흙 보충/제거/돌맹이 제거 테스트 노드에서 공통으로 쓰는 툴/TCP 설정이다.
# 현재는 soil check와 같은 툴 기준으로 맞춰 둔다.
SOIL_SERVICE_TOOL_NAME = TRAY_SOIL_TOOL_NAME
SOIL_SERVICE_TCP_NAME = TRAY_SOIL_TCP_NAME

# 흙 추가/제거 시 서로 다른 2개 위치를 순회하기 위한 기본 코너 이름 순서다.
TRAY_SOIL_ADD_TARGET_NAMES = ("corner_1", "corner_4")
TRAY_SOIL_REMOVE_TARGET_NAMES = ("corner_2", "corner_3")

# 측정된 흙 높이를 기준으로 작업 pose를 만들 때 더하는 오프셋이다.
# 실제 장비에서는 shovel 길이와 tray 간섭을 보며 재조정 필요.
TRAY_SOIL_ADD_DROP_Z_OFFSET = 25.0
TRAY_SOIL_REMOVE_SCOOP_Z_OFFSET = 8.0
TRAY_ROCK_PICK_Z_OFFSET = 8.0

# shovel pickup/return, 흙 상자, 폐기 상자 자세들이다.
# 현재 값은 테스트용 placeholder 이므로 실기 투입 전 재티칭 필요.
SOIL_SHOVEL_PICKUP_TOP_POSE = [237.0, 294.0, 210.0, 89.08, 179.97, 89.05]
SOIL_SHOVEL_PICKUP_POSE = [237.0, 294.0, 122.0, 89.08, 179.97, 89.05]
SOIL_SUPPLY_BOX_TOP_POSE = [122.0, 327.0, 220.0, 89.08, 179.97, 89.05]
SOIL_SUPPLY_BOX_SCOOP_POSE = [122.0, 327.0, 118.0, 89.08, 179.97, 89.05]
SOIL_WASTE_BOX_TOP_POSE = [156.0, -255.0, 220.0, 89.08, 179.97, 89.05]
SOIL_WASTE_BOX_DUMP_POSE = [156.0, -255.0, 132.0, 89.08, 179.97, 89.05]

# =========================
# Keyboard Teleop
# =========================
# 키보드 수동 조작 노드의 1회 이동량과 기본 속도/가속도다.
# 사용처: keyboard_teleop_node.py
KEYBOARD_DEFAULT_STEP = 20.0
KEYBOARD_DEFAULT_VEL = 50.0
KEYBOARD_DEFAULT_ACC = 50.0

# =========================
# Simple Compliance
# =========================
# 단순 compliance 테스트에서 하강 탐지에 쓰는 거리/힘/속도 기준값이다.
# 사용처: simple_compliance_down_up_test.py
SIMPLE_COMPLIANCE_MAX_DOWN_DISTANCE = 185.0
SIMPLE_COMPLIANCE_CONTACT_DELTA_FZ = 5.0
SIMPLE_COMPLIANCE_VEL = 20.0
SIMPLE_COMPLIANCE_ACC = 20.0
