"""Centralized robot motion constants and taught positions."""

from __future__ import annotations

# =========================
# Robot / Tool / TCP
# =========================
# 현재 테스트 노드들이 공통으로 사용하는 Doosan 로봇 ID/모델명이다.
# node_common.py의 기본 설정값과 같은 의미이며, 필요 시 한곳에서 관리하려고 둔 값이다.
ROBOT_ID = "dsr01"
ROBOT_MODEL = "m0609"

# 컨트롤러에서 조회/설정 성공을 확인한 일반 동작용 공통 Tool/TCP다.
# HOME, 누름판, 삽, 모종, 흙 보정, 돌 제거가 이 설정을 공유한다.
COMMON_TOOL_NAME = "Tool Weight"
COMMON_TCP_NAME = "Tool_v1"

# 원복 참고값. Tool Weight_1은 현 컨트롤러에서 거부되어 현재 사용하지 않는다.
LEGACY_PRESS_TOOL_NAME = "Tool Weight_1"
LEGACY_PRESS_TCP_NAME = "GripperDA_v1"

PRESS_TOOL_NAME = COMMON_TOOL_NAME
PRESS_TCP_NAME = COMMON_TCP_NAME

# 모종 집기/이식 시퀀스에서 사용하는 툴/TCP 이름이다.
# 사용처: plant_pick_and_place_common.py, plant_pick_and_place_tray_node.py,
# plant_pick_and_place_tray_select_node.py
PLANT_TOOL_NAME = COMMON_TOOL_NAME
PLANT_TCP_NAME = COMMON_TCP_NAME

# 순응제어 전용 설정이다. 현재 값은 공통값과 같지만 독립적으로 유지한다.
# 사용처: 토양 높이 측정, compliance 평탄화
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
# Shovel
# =========================
# 삽 pickup/putdown 테스트에서 쓰는 툴/TCP다. 현재 그리퍼 계열과 동일 설정을 사용한다.
SHOVEL_TOOL_NAME = PRESS_TOOL_NAME
SHOVEL_TCP_NAME = PRESS_TCP_NAME
# 삽 위치로 접근하기 전 준비 조인트다.
SHOVEL_READY_JOINT = [-10.59, -8.07, 85.69, -0.20, 100.53, 81.59]
# 삽을 실제로 잡거나 놓는 조인트다.
SHOVEL_PICK_JOINT = [-10.60, -6.66, 114.48, -0.20, 70.34, 81.19]

# 단독 돌멩이 제거 테스트에서 사용하는 고정 경로다.
# 모든 Cartesian pose는 DR_BASE 기준 [x, y, z, rx, ry, rz]이다.
ROCK_REMOVE_READY_JOINT = [9.09, 30.16, 51.56, 0.0, 90.0, 0.0]
ROCK_REMOVE_PICK_POSE = [566.640, 88.440, 127.280, 2.79, 178.32, 2.13]
ROCK_REMOVE_LIFT_POSE = [565.640, 87.45, 269.54, 4.44, 178.09, 3.96]
ROCK_REMOVE_WASTE_TOP_POSE = [251.80, -137.10, 257.79, 172.71, -178.36, 172.98]
ROCK_REMOVE_WASTE_DROP_POSE = [250.79, -137.29, 70.95, 173.40, -178.52, 173.99]

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
TRAY_SOIL_OK_MIN = 65.1
TRAY_SOIL_OK_MAX = 74.0
TRAY_SOIL_HIGH_MIN = 74.1
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
# 흙 보충/제거/돌맹이 제거는 일반 동작용 공통 설정을 사용한다.
SOIL_SERVICE_TOOL_NAME = COMMON_TOOL_NAME
SOIL_SERVICE_TCP_NAME = COMMON_TCP_NAME

# 흙 추가/제거 시 서로 다른 2개 위치를 순회하기 위한 기본 코너 이름 순서다.
TRAY_SOIL_ADD_TARGET_NAMES = ("corner_1", "corner_4")
TRAY_SOIL_REMOVE_TARGET_NAMES = ("corner_2", "corner_3")

# 측정된 흙 높이를 기준으로 작업 pose를 만들 때 더하는 오프셋이다.
# 실제 장비에서는 shovel 길이와 tray 간섭을 보며 재조정 필요.
TRAY_SOIL_ADD_DROP_Z_OFFSET = 25.0
TRAY_SOIL_REMOVE_SCOOP_Z_OFFSET = 8.0
TRAY_SOIL_REMOVE_LIFT_Z_OFFSET = 18.0
TRAY_ROCK_PICK_Z_OFFSET = 8.0

# soil remove 시 tray 내부에서 scoop를 흔들어 흙을 모으기 위한 주기 이동 파라미터다.
# move_periodic 사용 시 [x, y, z, rx, ry, rz] 진폭과 주기를 그대로 넘긴다.
TRAY_SOIL_REMOVE_SHAKE_AMP = [6.0, 6.0, 0.0, 0.0, 0.0, 0.0]
TRAY_SOIL_REMOVE_SHAKE_PERIOD = [1.0, 1.0, 0.0, 0.0, 0.0, 0.0]
TRAY_SOIL_REMOVE_SHAKE_ATIME = 0.2
TRAY_SOIL_REMOVE_SHAKE_REPEAT = 2

# tray soil 작업 후 중앙을 한 번 눌러 평탄화할 때 쓰는 기본 파라미터다.
# tray_soil_state_check_node와 비슷한 구조로 코너를 순회하며 접촉 후 한 번 더 누르는 용도다.
TRAY_SOIL_FLATTEN_CONTACT_DELTA_FZ = 3.0
TRAY_SOIL_FLATTEN_EXTRA_PRESS_MM = 1.0
TRAY_SOIL_FLATTEN_TOP_Z_OFFSET = -40.0
TRAY_SOIL_FLATTEN_PRESS_Z_OFFSET = -95.0
TRAY_SOIL_FLATTEN_VEL = 20.0
TRAY_SOIL_FLATTEN_ACC = 20.0
TRAY_SOIL_FLATTEN_HOLD_SEC = 1.0

# C 트레이에서 티칭한 흙 퍼내기 경로다. 폐기 상자 top/dump Joint는
# A/B/D 일반 흙 제거에서도 공통 폐기 경로로 재사용한다.
# 첫 접근과 흙상자 투입은 조인트, 실제 흙을 가르는 구간은 베이스 pose를 사용한다.
# 참고: 사용자가 전달한 `27,55`는 문맥상 `27.55`로 해석했다.
C_TRAY_REMOVE_APPROACH_JOINT = [20.51, -8.94, 87.76, -1.24, 97.10, 27.55]
C_TRAY_REMOVE_SCOOP_START_JOINT = [13.92, -27.5, 132.39, -8.73, 34.43, 25.48]
C_TRAY_REMOVE_SCOOP_START_POSE = [387.22, 71.58, 143.52, 6.52, 138.32, 12.69]
C_TRAY_REMOVE_SCOOP_END_POSE = [345.55, 69.91, 137.67, 7.17, 148.18, 16.59]
C_TRAY_REMOVE_POSTURE_ADJUST_JOINT = [11.31, 21.44, 76.95, -0.68, 101.2, 25.48]
C_TRAY_REMOVE_BOX_TOP_JOINT = [11.27, 9.43, 86.15, 1.98, 107.31, 26.50]
C_TRAY_REMOVE_BOX_DUMP_JOINT = [13.60, 12.00, 88.48, 4.72, 113.2, 194.57]
C_TRAY_REMOVE_SHAKE_Z_AMPLITUDE = 2.0
C_TRAY_REMOVE_SHAKE_STEPS = 8

# shovel pickup/return, 흙 상자, 폐기 상자 자세들이다.
# 폐기 Cartesian pose는 Joint 방식 원복 참고용이며 현재 흙 제거에서는 사용하지 않는다.
SOIL_SHOVEL_PICKUP_TOP_POSE = [237.0, 294.0, 210.0, 89.08, 179.97, 89.05]
SOIL_SHOVEL_PICKUP_POSE = [237.0, 294.0, 122.0, 89.08, 179.97, 89.05]
SOIL_SUPPLY_BOX_TOP_POSE = [122.0, 327.0, 220.0, 89.08, 179.97, 89.05]
SOIL_SUPPLY_BOX_SCOOP_POSE = [122.0, 327.0, 118.0, 89.08, 179.97, 89.05]
SOIL_WASTE_BOX_TOP_POSE = [156.0, -255.0, 220.0, 89.08, 179.97, 89.05]
SOIL_WASTE_BOX_DUMP_POSE = [156.0, -255.0, 132.0, 89.08, 179.97, 89.05]

# 흙창고에서 비비탄을 퍼 올릴 때 사용하는 조인트 시퀀스다.
# 현재는 삽을 잡은 상태에서 흙창고 쪽으로 진입해 퍼 올리고 다시 빠지는 순서까지 반영한다.
SOIL_SUPPLY_JOINT_SEQUENCE = [
    [11.99, -16.28, 103.30, 0.19, 92.91, 111.42],
    [11.99, -16.27, 117.94, 0.00, 76.72, 111.42],
    [11.99, -16.26, 120.34, 8.89, 71.85, 111.42],
    [-11.34, -17.14, 122.34, 24.85, 78.34, 79.15],
    [-25.83, -17.60, 104.10, 26.37, 101.81, 74.93],
]

# A 트레이에 흙을 떨굴 때 사용하는 준비 조인트 2개와 조인트 2단계 x 2회 테스트 시퀀스다.
# 마지막 준비 조인트를 상단 진입 조인트로 재사용한다.
A_TRAY_SOIL_DROP_PREP_JOINTS = [
    # [14.45, -25.24, 107.92, -7.80, 71.24, 197.58],
    [41.48, -16.14, 104.90, -17.85, 68.34, 234.74],
     [48.23, -23.42, 123.95, -26.17, 59.24, 242.82],
]
A_TRAY_SOIL_DROP_TOP_JOINT =  [48.23, -23.42, 123.95, -26.17, 59.24, 242.82]
# [41.48, -16.14, 104.90, -17.85, 68.34, 234.74]
A_TRAY_SOIL_DROP_CYCLES = [
    {
        "approach": [11.74, 45.34, 48.60, 14.81, 131.48, 204.75],
        # [48.23, -23.42, 123.95, -26.17, 59.24, 242.82],
        "drop": [59.84, -12.99, 116.92, -29.98, 60.84, 257.23],
        # [11.74, 45.34, 48.60, 14.81, 131.48, 204.75],
    },
    {
        "approach": [18.99, 49.76, 40.45, 20.77, 138.01, 213.39],
        # [59.84, -12.99, 116.92, -29.98, 60.84, 257.23],
        "drop": [17.92, 42.66, 52.12, 22.34, 125.99, 212.74]
        # [18.99, 49.76, 40.45, 20.77, 138.01, 213.39],
    },
]

# B 트레이에 흙을 떨굴 때 사용하는 준비 조인트 2개와 조인트 2단계 x 2회 테스트 시퀀스다.
B_TRAY_SOIL_DROP_PREP_JOINTS = [
    [9.02, 12.94, 84.14, 12.25, 109.04, 18.69],
    [13.00, 32.46, 38.51, 8.01, 133.06, 17.33],
]
B_TRAY_SOIL_DROP_TOP_JOINT = [13.00, 32.46, 38.51, 8.01, 133.06, 17.33]
B_TRAY_SOIL_DROP_CYCLES = [
    {
        "approach": [11.52, 55.27, 15.33, 6.40, 129.95, 19.65],
        "drop": [24.52, 2.19, 103.28, -23.24, 42.65, 38.96],
    },
    {
        "approach": [20.92, 52.09, 20.81, 5.04, 122.46, 31.18],
        "drop": [34.09, 4.73, 102.55, -29.44, 41.60, 54.02],
    },
]

# C 트레이에 흙을 떨굴 때 사용하는 상단 진입 조인트와 조인트 2단계 x 2회 테스트 시퀀스다.
C_TRAY_SOIL_DROP_TOP_JOINT = [14.45, -25.24, 107.92, -7.8, 71.24, 197.58]
SOIL_DROP_C_TRAY_CYCLES = [
    {
        "approach": [6.59, -19.70, 117.50, -8.37, 65.65, 193.11],
        "drop": [-2.32, 43.55, 48.71, 1.08, 130.18, 191.54],
    },
    {
        "approach": [19.62, -28.30, 122.06, -6.88, 63.50, 198.18],
        "drop": [6.88, 44.88, 46.06, 4.67, 130.85, 196.25],
    },
]

# D 트레이에 흙을 떨굴 때 사용하는 준비 조인트 3개와 조인트 2단계 x 2회 테스트 시퀀스다.
D_TRAY_SOIL_DROP_PREP_JOINTS = [
    [-19.29, -14.54, 111.56, 27.93, 93.62, 78.51],
    [8.21, 7.04, 98.35, 13.00, 110.96, 14.67],
    [7.94, 46.17, 22.01, 1.92, 133.25, 9.23],
]
D_TRAY_SOIL_DROP_TOP_JOINT = [7.94, 46.17, 22.01, 1.92, 133.25, 9.23]
D_TRAY_SOIL_DROP_CYCLES = [
    {
        "approach": [7.77, 45.02, 35.96, 0.39, 118.07, 14.87],
        "drop": [14.13, -2.52, 109.14, -18.20, 38.09, 31.82],
    },
    {
        "approach": [0.09, 45.92, 34.11, -3.64, 120.42, 4.66],
        "drop": [0.13, -3.82, 108.58, -4.76, 38.68, 5.21],
    },
]

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
