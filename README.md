# ws_cobot_pjt

Doosan M0609 협동로봇 기반의 트레이 핸들링, 모종 이식, 토양 검사 및 후속 작업 실험을 위한 ROS 2 워크스페이스입니다.

현재 정리된 주요 작업 내용은 `Cobot1` 워크스페이스인 `ws_cobot1/src/robot_tests` 에 있습니다.

현재 실제 작업 중심은 `ws_cobot1/src/robot_tests` 패키지입니다.

## 프로젝트 개요

현재 프로젝트에는 다음 기능이 포함되어 있습니다.

- 안전 홈 복귀 및 수동 조그 기능
- 프레스 판 pickup / putdown 테스트 시퀀스
- 모종 pick-and-place 테스트 시퀀스
- 순응제어 기반 트레이 흙 상태 검사
- 흙 보충 / 유지 / 제거 / 돌맹이 제거 시도용 후속 작업 노드

주요 구현 위치:

- `ws_cobot1/src/robot_tests`

참고용 로봇 스택 및 벤더 소스:

- `ws_dsr/`

## 워크스페이스 구조

```text
ws_cobot_pjt/
├── docs/                       # 프로젝트 문서 및 Doosan API 정리
├── pyqt/                       # 로컬 UI 실험 코드
├── ws_cobot1/
│   └── src/
│       └── robot_tests/        # 메인 ROS 2 Python 패키지
└── ws_dsr/                     # Doosan / gripper 관련 스택 소스
```

## 주요 노드

### 메인 작업 노드

- `go_home_test`
  - 현재 TCP 위치에서 안전하게 상승한 뒤 홈 자세로 복귀
- `plant_pick_and_place_tray_select_node`
  - 트레이와 식물 번호를 입력받아 모종을 집고 선택한 대상 트레이에 식재
- `plant_pick_and_place_tray_node`
  - 고정된 tray / plant / target 값으로 모종 이식 경로를 검증
- `tray_soil_state_check_node`
  - 트레이 각 코너를 측정해 흙 상태를 판정하고 돌맹이 의심 위치를 분류

### soil 대응 노드

- `tray_soil_add_node`
  - 흙 상태가 `SOIL_LOW` 일 때 흙을 보충
- `tray_soil_keep_node`
  - 흙 상태가 `SOIL_OK` 일 때 그대로 유지
- `tray_soil_remove_node`
  - 흙 상태가 `SOIL_HIGH` 일 때 흙을 제거
- `tray_rock_remove_node`
  - 돌맹이 의심 위치에 접근해 제거를 시도

### 개별 작업 노드

- `press_plate_pickup_node`
  - 프레스 판을 집는 단일 작업 시퀀스
- `press_plate_putdown_node`
  - 프레스 판을 지정 위치에 내려놓는 단일 작업 시퀀스
- `tray_top_move_node`
  - 선택한 트레이의 상단 접근 조인트로만 이동하는 확인용 노드

### 테스트 / 디버깅 노드

- `keyboard_teleop_node`
  - TCP 수동 이동, 좌표 확인, 그리퍼 제어
- `simple_compliance_down_up_test`
  - 순응제어 하강 및 접촉 감지 최소 재현 테스트

## 공통 모듈

- `robot_motion_data.py`
  - 좌표, 조인트값, Tool / TCP 이름, soil 기준값 등 핵심 데이터 관리
- `motion_primitives.py`
  - `move_j`, `move_l`, `go_home`, 그리퍼 제어, pose 보조 함수
- `node_common.py`
  - Doosan 노드 공통 설정 및 import 보조
- `compliance_common.py`
  - 순응제어 관련 공통 보조 함수
- `plant_pick_and_place_common.py`
  - 모종 이식 공통 시퀀스
- `tray_soil_service_common.py`
  - soil add / remove / rock 대응 공통 시퀀스
- `dsr_runtime.py`
  - Doosan Python 모듈 import bootstrap

## 현재 soil 판정 기준

- `55.0 ~ 65.0` -> `SOIL_LOW`
- `66.0 ~ 74.0` -> `SOIL_OK`
- `75.0 ~ 87.0` -> `SOIL_HIGH`
- 측정 코너 z가 전체 평균과 `10.0` 이상 차이 나면 -> `OBSTACLE_CANDIDATE`

## 실행 예시

ROS 2 환경 source 이후:

```bash
ros2 run robot_tests go_home_test
ros2 run robot_tests keyboard_teleop_node
ros2 run robot_tests press_plate_pickup_node
ros2 run robot_tests press_plate_putdown_node
ros2 run robot_tests plant_pick_and_place_tray_node
ros2 run robot_tests plant_pick_and_place_tray_select_node
ros2 run robot_tests tray_soil_state_check_node
ros2 run robot_tests tray_soil_add_node
ros2 run robot_tests tray_soil_keep_node
ros2 run robot_tests tray_soil_remove_node
ros2 run robot_tests tray_rock_remove_node
ros2 run robot_tests tray_top_move_node
ros2 run robot_tests simple_compliance_down_up_test
```

키보드 텔레옵 예시:

```bash
ros2 run robot_tests keyboard_teleop_node --ros-args -p step_mm:=10.0 -p velocity:=30.0 -p acceleration:=30.0
```

## 현재 진행 상태

- 중복된 legacy `doosan_api` 파일 제거 완료
- 공통 로봇 설정과 이동 로직 정리 완료
- 티칭값과 기준값을 `robot_motion_data.py` 로 통합
- 트레이 선택형 모종 이식 노드 정리 완료
- soil 대응 테스트 노드 추가 완료

## 현재 한계 / 주의 사항

- 현재 노드들은 실제 장비에서 경로 검증이 필요합니다.
- `plant_pick_and_place_tray_select_node` 는 모든 종료 경로에서 자동 `go_home()` 이 보장되도록 추가 보완이 필요합니다.
- soil 대응 노드의 shovel pickup / 흙상자 / 폐기상자 좌표는 아직 placeholder 값이므로 재티칭이 필요합니다.
- 돌맹이 제거는 비전 없이 검사 결과 기반으로 접근하는 제한적 방식입니다.
- press plate pickup / putdown 시퀀스는 아직 완전히 공통화되지 않았습니다.

## 관련 문서

- 패키지 진행 현황: [`ws_cobot1/src/robot_tests/README.md`](ws_cobot1/src/robot_tests/README.md)
- 내부 인수인계 메모: [`ws_cobot1/src/robot_tests/CODEX_HANDOFF.md`](ws_cobot1/src/robot_tests/CODEX_HANDOFF.md)
- Doosan API 정리: [`docs/doosan_api_index.md`](docs/doosan_api_index.md)
