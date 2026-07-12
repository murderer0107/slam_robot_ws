# robot_tests

Doosan M0609 기반 테스트용 ROS 2 Python 패키지입니다.  
현재는 누름판 핸들링, 모종 pick/place, 트레이 흙 상태 점검, 수동 조그/홈 복귀 테스트 코드를 정리해 둔 상태입니다.

현재 `ws_cobot_pjt` 워크스페이스 전체 기준으로도 실작업 중심은 `ws_cobot1/src/robot_tests` 입니다.  
루트의 `smartfarm_main.py`, `smartfarm_lib.py` 는 아직 스켈레톤 성격이 강하고, 실제 장비 기준 테스트 코드는 이 패키지 쪽에 모여 있습니다.

통합 대시보드/시나리오 관련 구조 및 작업 기록은 `robot_tests/integrated/README.md`, `robot_tests/integrated/WORKLOG.md` 를 기준으로 관리합니다.

## 진행 상황

- `doosan_api` 계열 중복 파일 제거
- 좌표, 조인트, Tool/TCP, 그리퍼 출력 패턴, 판정 기준값을 `robot_motion_data.py`로 통합
- 공통 이동/그리퍼 동작을 `motion_primitives.py`로 분리
- 노드 공통 설정과 API import 보조를 `node_common.py`로 분리
- 모종 pick/place 메인 시퀀스를 `plant_pick_and_place_common.py`로 공통화
- 트레이 선택형 모종 이식 노드만 유지
- 각 트레이 기본 상단 조인트 이동 노드 추가
- 누름판 pickup/putdown 시 그리퍼 벌림 단계 조정
- 개별 `a/b/c/d_tray_soil_drop_test_node` 제거 후 통합 `abcd_tray_soil_drop_test_node` 추가

## 주요 파일

- `robot_tests/robot_motion_data.py`
  - 좌표, 조인트값, Tool/TCP 이름, 그리퍼 출력 패턴, soil 기준값 관리
- `robot_tests/motion_primitives.py`
  - `move_j`, `move_l`, `go_home`, 그리퍼 명령 등 공통 동작
- `robot_tests/node_common.py`
  - `ROBOT_ID`, `ROBOT_MODEL`, Doosan API import/setup 보조
- `robot_tests/plant_pick_and_place_common.py`
  - 모종 집기/이식 공통 시퀀스
- `robot_tests/compliance_common.py`
  - compliance 보조 함수
- `robot_tests/dsr_runtime.py`
  - overlay/source 상태와 무관하게 `DR_init`, `DSR_ROBOT2` import를 돕는 bootstrap

## 노드 목록

- `go_home_test`
  - 현재 위치에서 안전하게 상승 후 홈 복귀
- `keyboard_teleop_node`
  - 키보드 기반 수동 이동, 현재 좌표 확인, 그리퍼 제어
- `press_plate_pickup_node`
  - 홈 -> 경유점 -> 누름판 상부 -> 하강 -> 집기 -> 복귀
  - 하강 직전 `중간 벌리기(1000)` 적용
- `press_plate_putdown_node`
  - 홈 -> 경유점 -> 누름판 설치 위치 상부 -> 하강 -> 놓기 -> 복귀
  - 내려놓은 뒤 `중간 벌리기(1000)` 상태로 상승
- `plant_pick_and_place_tray_select_node`
  - 트레이와 식물 번호를 입력받아 모종 이식 실행
- `abcd_tray_soil_drop_test_node`
  - 트레이를 입력받아 shovel scoop 후 tray별 조인트 드롭 테스트 실행
  - 종료 시 그리퍼 상태 유지한 채 홈 복귀
- `tray_top_move_node`
  - 선택한 `A/B/C/D` 트레이의 기본 상단 조인트(`top`)로만 이동
- `tray_soil_state_check_node`
  - 트레이 흙 상태 측정 및 low/ok/high 판정
  - 평균값과 차이가 큰 코너는 돌맹이 의심으로 분류
- `tray_soil_add_node`
  - soil check 결과가 `SOIL_LOW` 일 때 shovel로 흙 보충 시도
- `tray_soil_keep_node`
  - soil check 결과가 `SOIL_OK` 일 때 no-op 확인
- `tray_soil_remove_node`
  - soil check 결과가 `SOIL_HIGH` 일 때 shovel로 흙 제거 시도
- `tray_rock_remove_node`
  - soil check 결과의 돌맹이 의심 위치로 이동해 집기 시도
- `simple_compliance_down_up_test`
  - 현재 TCP 기준 순응제어 하강/상승 단독 테스트

## 현재 데이터 정리 상태

### 그리퍼 출력 패턴

- `0100` = `GRIPPER_HOME_PREPARE`
  - 넓게 벌리기 / 홈 준비
- `1000` = `PLANT_GRIPPER_WAYPOINT1_PREPARE`
  - 중간 벌리기
- `0010` = `GRIPPER_PICK_CLOSE`
  - 강하게 잡기

### 모종 이식 조인트

- `TRAY_ENTRY_JOINTS`
  - 소스 트레이 진입 조인트
- `TRAY_PLANT_JOINTS`
  - 식물별 `pre_pick`, `pick`, `lift`
- `TARGET_TRAY_PLACE_JOINTS`
  - 대상 트레이별 `top`, `down`

### 트레이 상부 기준

- `TARGET_TRAY_PLACE_JOINTS[tray]["top"]`
  - 각 트레이 기본 상단 조인트
- `TRAY_TOPS_XY`
  - soil check용 트레이 상부 XY 기준점
- `TRAY_CORNERS_XYZ`
  - tray soil check용 코너별 측정 좌표

### 흙 상태 판정 기준

- `55.0 ~ 65.0`
  - `SOIL_LOW`
- `66.0 ~ 74.0`
  - `SOIL_OK`
- `75.0 ~ 87.0`
  - `SOIL_HIGH`
- 측정 코너 z가 전체 평균과 `10.0` 이상 차이
  - `OBSTACLE_CANDIDATE` 로 처리

## 실행 예시

환경 source 이후:

```bash
ros2 run robot_tests go_home_test
ros2 run robot_tests keyboard_teleop_node
ros2 run robot_tests press_plate_pickup_node
ros2 run robot_tests press_plate_putdown_node
ros2 run robot_tests plant_pick_and_place_tray_select_node
ros2 run robot_tests abcd_tray_soil_drop_test_node
ros2 run robot_tests tray_soil_add_node
ros2 run robot_tests tray_soil_keep_node
ros2 run robot_tests tray_soil_remove_node
ros2 run robot_tests tray_rock_remove_node
ros2 run robot_tests tray_top_move_node
ros2 run robot_tests tray_soil_state_check_node
ros2 run robot_tests simple_compliance_down_up_test
```

키보드 텔레옵 파라미터 예시:

```bash
ros2 run robot_tests keyboard_teleop_node --ros-args -p step_mm:=10.0 -p velocity:=30.0 -p acceleration:=30.0
```

## 최근 반영 사항

- `tray_a` 식물 1~4의 `pre_pick/pick` 조인트 재티칭값 반영
- `press_plate_pickup_node` 하강 직전 `1000` 중간 벌리기 적용
- `press_plate_putdown_node` release 후 `1000` 중간 벌리기 적용
- `tray_top_move_node` 신규 추가
- `plant_pick_and_place_tray_node` 제거, 선택형 `plant_pick_and_place_tray_select_node`만 유지
- `a/b/c/d_tray_soil_drop_test_node` 제거, `abcd_tray_soil_drop_test_node`로 통합
- `abcd_tray_soil_drop_test_node` 종료 시 그리퍼 유지 홈 복귀 추가
- `doosan_api` 계열 중복 파일 제거
- 좌표/조인트/Tool/TCP/판정 기준값을 `robot_motion_data.py` 로 통합
- 공통 동작을 `motion_primitives.py`, `node_common.py`, `compliance_common.py` 로 분리
- `plant_pick_and_place_tray_select_node` 에서 목표 트레이/식물 번호를 대화식 입력으로 선택 가능
- soil 대응 테스트 노드 `tray_soil_add_node`, `tray_soil_keep_node`, `tray_soil_remove_node`, `tray_rock_remove_node` 추가

## 주의 사항

- 현재 노드들은 실제 장비에서 경로 검증이 필요합니다.
- `TARGET_TRAY_PLACE_JOINTS`의 `top/down`은 현장 재티칭 기준으로 저장되어 있으므로 실기 동작 확인이 필요합니다.
- `plant_pick_and_place_tray_select_node` 는 현재 종료 시 자동 `go_home()` 보장이 아직 없습니다.
- soil 대응 노드의 shovel pickup/흙상자/폐기상자 좌표는 현재 placeholder 이므로 실기 투입 전 재티칭이 필요합니다.
- soil 대응 노드의 shovel dump/scoop 시퀀스는 비비탄용 기본 skeleton 이며, 실제 삽 형상에 맞는 세부 경로 조정이 필요합니다.
- `tray_soil_add_node` 는 soil 상태 검사 후 corner 기반 보정 동작이고, `abcd_tray_soil_drop_test_node` 는 tray별 조인트 드롭 테스트 노드라 역할이 다릅니다.
- press plate pickup/putdown 은 좌표는 공통화됐지만 시퀀스 자체는 아직 각 노드에 따로 있습니다.
- tray soil 판정 로직은 아직 `tray_soil_state_check_node.py` 내부에 함께 들어 있습니다.
- 이 README는 업로드용 진행 현황 요약이며, 세부 인수인계 메모는 `CODEX_HANDOFF.md`에 있습니다.
