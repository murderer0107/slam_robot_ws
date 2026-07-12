# robot_tests

Doosan M0609 협동로봇 기반 스마트팜 식재 자동화 ROS 2 Python 패키지입니다.

이 저장소는 `robot_tests` 패키지를 루트에 둔 형태로 정리되어 있으며, PyQt Dashboard에서 토양 상태 측정, 상태별 보정 작업, 평탄화, 식물 심기, 수동 제어, 긴급정지/복구 흐름을 통합 실행합니다.

## 주요 기능

- PyQt 기반 통합 Dashboard 실행
- ROS 연결 상태 확인
- Tray A/B/C/D별 토양 상태 측정
- 토양 상태 판정: `미측정`, `정상`, `흙부족`, `흙많음`, `장애물감지`, `측정실패`
- 상태별 다음 작업 실행
  - 정상: 식물 심기
  - 흙부족: 흙추가
  - 흙많음: 흙제거
  - 장애물감지: 돌제거
  - 보정 완료: 평탄화 후 재측정
- 누름판/삽 pickup 및 putdown
- Base/Joint 수동 제어
- 작업 로그 표시
- 긴급정지 및 HOME 복귀 흐름

## 실행 환경

- ROS 2
- Doosan Robotics ROS 2 패키지
- Python ROS 2 package
- PyQt5
- Doosan M0609 로봇 및 DSR API 사용 환경

현재 Dashboard 내부 기본 workspace setup 경로:

```text
/home/rokey/ws_cobot_pjt/ws_cobot1/install/setup.bash
```

환경이 다르면 `robot_tests/integrated/config.py`의 `WORKSPACE_SETUP_PATH`를 실제 설치 경로에 맞게 수정해야 합니다.

## 빠른 실행

ROS 2 workspace 환경을 source 한 뒤 launch 파일을 실행합니다.

```bash
source /home/rokey/ws_cobot_pjt/ws_cobot1/install/setup.bash
ros2 launch robot_tests integrated_dashboard.launch.py
```

실행되는 메인 노드:

```text
integrated_dashboard
```

## 설치 / 빌드 예시

이 패키지를 ROS 2 workspace의 `src` 아래에 둔 뒤 빌드합니다.

```bash
cd /home/rokey/ws_cobot_pjt/ws_cobot1
colcon build --packages-select robot_tests
source install/setup.bash
```

## 프로젝트 구조

```text
robot_tests/
├─ launch/
│  └─ integrated_dashboard.launch.py
├─ resource/
│  └─ robot_tests
├─ robot_tests/
│  ├─ integrated/
│  │  ├─ main.py
│  │  ├─ dashboard_app.py
│  │  ├─ dashboard_logic.py
│  │  ├─ ros_runner.py
│  │  ├─ config.py
│  │  └─ smartfarm_dashboard.ui
│  ├─ integrated_tray_soil_state_check_node.py
│  ├─ integrated_tray_next_step_node.py
│  ├─ integrated_tray_soil_flatten_node.py
│  ├─ integrated_plant_pick_and_place_node.py
│  ├─ integrated_manual_control_node.py
│  ├─ integrated_emergency_stop_node.py
│  ├─ go_home_test_node.py
│  ├─ press_plate_pickup_node.py
│  ├─ press_plate_putdown_node.py
│  ├─ shovel_pickup_node.py
│  ├─ shovel_putdown_node.py
│  ├─ tray_soil_service_common.py
│  ├─ plant_pick_and_place_common.py
│  ├─ motion_primitives.py
│  ├─ robot_motion_data.py
│  ├─ node_common.py
│  └─ standalone_tests/
├─ package.xml
├─ setup.cfg
├─ setup.py
└─ README.md
```

## Dashboard 구조

Dashboard 관련 코드는 `robot_tests/integrated/`에 있습니다.

| 파일 | 역할 |
|---|---|
| `main.py` | PyQt application entry point |
| `dashboard_app.py` | UI 이벤트 처리, 버튼 연결, ROS 노드 실행 제어 |
| `dashboard_logic.py` | Tray 상태, 작업 단계, persistent state 관리 |
| `ros_runner.py` | `ros2 run robot_tests ...` 프로세스 실행 wrapper |
| `config.py` | Dashboard 상태명, 노드명, 경로 설정 |
| `smartfarm_dashboard.ui` | PyQt UI 파일 |

## 주요 ROS 실행 이름

### 통합 Dashboard 흐름

| 실행 이름 | 역할 |
|---|---|
| `integrated_dashboard` | PyQt Dashboard 실행 |
| `integrated_tray_soil_state_check_node` | 선택 Tray 접촉 측정 및 토양 상태 판정 |
| `integrated_tray_next_step_node` | Dashboard 상태 기반 다음 작업 실행 |
| `integrated_tray_soil_flatten_node` | 선택 Tray 평탄화 |
| `integrated_plant_pick_and_place_node` | 식물 pickup/place |
| `integrated_manual_control_node` | Base/Joint 수동 제어 및 현재 좌표 읽기 |
| `integrated_emergency_stop_node` | 긴급정지 명령 |

### 공구 / 복구

| 실행 이름 | 역할 |
|---|---|
| `go_home_test` | HOME 복귀 |
| `press_plate_pickup_node` | 누름판 집기 |
| `press_plate_putdown_node` | 누름판 놓기 |
| `shovel_pickup_node` | 삽 집기 |
| `shovel_putdown_node` | 삽 놓기 |

### 단독 테스트 / 디버깅

| 실행 이름 | 역할 |
|---|---|
| `keyboard_teleop_node` | 키보드 기반 수동 이동 |
| `plant_pick_and_place_tray_select_node` | 대화식 Tray/식물 선택형 식재 테스트 |
| `tray_soil_state_check_node` | 대화식 토양 상태 측정 |
| `tray_soil_add_node` | 단독 흙추가 테스트 |
| `tray_soil_remove_node` | 단독 흙제거 테스트 |
| `tray_rock_remove_node` | 단독 돌제거 테스트 |
| `tray_soil_flatten_node` | 단독 평탄화 테스트 |
| `simple_compliance_down_up_test` | 순응제어 하강/상승 단독 테스트 |

## 핵심 작업 흐름

```text
Dashboard 실행
 ↓
ROS 연결 확인
 ↓
Tray 선택
 ↓
토양 상태 측정
 ↓
토양 상태 판정
 ↓
상태별 작업 실행
 ↓
평탄화 / 재측정
 ↓
정상 판정
 ↓
식물 심기
 ↓
작업 완료
```

상태별 분기:

```text
토양 상태 판정
 ├─ 정상 → 식물 심기 → DONE
 ├─ 흙부족 → 흙추가 → 평탄화 → 재측정
 ├─ 흙많음 → 흙제거 → 평탄화 → 재측정
 ├─ 장애물감지 → 돌제거 → 평탄화 → 재측정
 └─ 측정실패 → UI 에러 표시 → 재측정 / HOME / 초기화
```

## Tray 상태 관리

Dashboard는 Tray별 상태를 관리합니다.

| 값 | 의미 |
|---|---|
| `soil_status` | 토양 상태 |
| `work_phase` | 작업 단계 |
| `last_error` | 마지막 오류 |
| `last_measurement` | 마지막 측정 결과 |

작업 단계:

| 상태 | 의미 |
|---|---|
| `IDLE` | 일반 대기 |
| `AFTER_CORRECTION` | 보정 후 평탄화 필요 |
| `DONE` | 식물 심기 완료 |

## 토양 상태 판정

측정 결과는 다음 상태 중 하나로 분류됩니다.

| 상태 | 다음 작업 |
|---|---|
| `미측정` | 토양 측정 |
| `정상` | 식물 심기 |
| `흙부족` | 흙추가 |
| `흙많음` | 흙제거 |
| `장애물감지` | 돌제거 |
| `측정실패` | 재측정 / 복구 |

현재 구현은 `TRAY_CORNERS_XYZ`에 정의된 corner 기반 측정 구조를 사용합니다. 접촉 시점의 z값, 평균, 평균 대비 편차를 기반으로 판정합니다.

## 공구 상태

Dashboard는 현재 로봇이 어떤 공구를 들고 있는지 추적합니다.

| 상태 | 의미 |
|---|---|
| `NONE` | 공구 없음 |
| `PRESS_PLATE_HELD` | 누름판 보유 |
| `SHOVEL_HELD` | 삽 보유 |
| `UNKNOWN` | 상태 불명 |

`UNKNOWN` 상태에서는 자동 작업을 제한하고 복구가 필요합니다.

## 주요 공통 파일

| 파일 | 역할 |
|---|---|
| `robot_motion_data.py` | 좌표, 조인트, Tool/TCP, 판정 기준값 관리 |
| `motion_primitives.py` | 공통 이동 및 그리퍼 동작 |
| `node_common.py` | Doosan API 설정 및 공통 노드 설정 |
| `tray_soil_service_common.py` | 흙추가/흙제거/돌제거/평탄화 공통 로직 |
| `plant_pick_and_place_common.py` | 식물 pickup/place 공통 시퀀스 |
| `compliance_common.py` | 순응제어 보조 함수 |
| `dsr_runtime.py` | `DR_init`, `DSR_ROBOT2` import bootstrap |

## 실행 예시

환경 source 이후:

```bash
ros2 run robot_tests go_home_test
ros2 run robot_tests press_plate_pickup_node
ros2 run robot_tests press_plate_putdown_node
ros2 run robot_tests shovel_pickup_node
ros2 run robot_tests shovel_putdown_node
ros2 run robot_tests integrated_tray_soil_state_check_node -- --tray A
ros2 run robot_tests integrated_tray_soil_flatten_node -- --tray A
ros2 run robot_tests integrated_plant_pick_and_place_node -- --tray A --plant 1
```

수동 제어 서버는 Dashboard에서 자동 실행됩니다.

```bash
ros2 run robot_tests integrated_manual_control_node -- --mode server
```

## 테스트 / 검증 항목

- Dashboard launch 실행 확인
- ROS 연결 상태 표시 확인
- HOME 이동 확인
- 누름판 집기/놓기 확인
- 삽 집기/놓기 확인
- Tray별 토양 측정 확인
- 흙부족 → 흙추가 → 평탄화 → 재측정 확인
- 흙많음 → 흙제거 → 평탄화 → 재측정 확인
- 장애물감지 → 돌제거 → 평탄화 → 재측정 확인
- 정상 → 식물 심기 확인
- 긴급정지 / HOME 복귀 확인
- 작업 로그 출력 확인

## 주의 사항

- 실제 로봇에서 실행하기 전 좌표, Tool/TCP, 조인트값을 현장 환경에 맞게 확인해야 합니다.
- `robot_motion_data.py`의 좌표와 판정 기준값은 실기 재티칭 및 threshold 튜닝 대상입니다.
- Dashboard 내부 `WORKSPACE_SETUP_PATH`가 실제 workspace 설치 경로와 맞아야 합니다.
- 물리적 E-Stop 상태를 Dashboard에 직접 반영하는 기능은 추가 개선 대상입니다.
- 영상, 발표자료, PDF 등 대용량 산출물은 Git 저장소가 아니라 별도 문서/Notion에 첨부하는 것을 권장합니다.
