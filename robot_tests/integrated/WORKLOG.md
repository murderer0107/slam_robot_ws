# Integrated Worklog

`robot_tests.integrated` 통합 작업 기록 파일이다.
최신 항목을 위에 추가한다.

## 2026-07-10 (Tool/TCP 시작 1회 및 compliance 원복)

- 작업: 대시보드 시작 시 공통 Tool/TCP 1회 설정, 일반 노드 중복 설정 제거
- 변경/확인 파일: `integrated_manual_control_node.py`, 일반 통합 작업 노드, compliance 노드
- 결정 사항: 토양 측정/평탄화만 전용 설정 적용 후 `finally`에서 공통 설정 원복
- 남은 이슈: compliance 중 SIGKILL 시 finally 미실행 가능, 안전복구가 공통 설정 재적용
- 다음 작업: 시작/측정 종료/평탄화 종료/안전복구 후 현재 Tool/TCP 조회 검증

## 2026-07-10 (흙 제거 폐기 Joint 경로 통일)

- 작업: A/B/D 흙 제거의 폐기 상자 이동을 C 트레이 티칭 Joint 경로로 변경
- 변경/확인 파일: `tray_soil_service_common.py`, `robot_motion_data.py`
- 결정 사항: 모든 트레이 폐기 `C_TRAY_REMOVE_BOX_TOP_JOINT → DUMP_JOINT → TOP_JOINT` 사용
- 남은 이슈: A/B/D 트레이 scoop 위치에서 공통 폐기 top Joint까지 충돌 없는 경로 확인 필요
- 다음 작업: A/B/D 각각 흙 제거 후 첫 폐기 이동 실기 검증

## 2026-07-10 (측정 전 다음 작업 비활성화)

- 작업: 초기/리셋/측정실패 상태에서 tray 다음 작업 버튼 비활성화
- 변경/확인 파일: `integrated/dashboard_app.py`
- 결정 사항: 유효한 토양 측정 결과가 있어야 다음 작업 버튼 활성화
- 남은 이슈: 없음
- 다음 작업: 초기, 리셋, 측정실패, 측정성공 상태별 버튼 확인

## 2026-07-10 (초기 다음 작업 버튼 문구)

- 작업: 초기/리셋 상태의 tray 버튼 텍스트를 `다음 작업`으로 표시
- 변경/확인 파일: `integrated/config.py`, `integrated/dashboard_app.py`
- 결정 사항: 초기 버튼 클릭 동작은 내부 next action에 따라 토양 측정 실행
- 남은 이슈: 없음
- 다음 작업: 초기/측정 후/리셋 후 버튼 텍스트 확인

## 2026-07-10 (평탄화 동시 토양 측정)

- 작업: 평탄화 4코너 접촉 Z로 토양 상태를 즉시 재판정하도록 변경
- 변경/확인 파일: `tray_soil_service_common.py`, `integrated_tray_soil_flatten_node.py`, `integrated/dashboard_logic.py`, `integrated/config.py`
- 결정 사항: 평탄화 완료 후 새 평균 Z/토양 상태를 유지하고 해당 상태로 다음 작업 결정
- 남은 이슈: 압착 전 최초 접촉 Z가 토양 높이 판정값으로 적합한지 실기 비교 필요
- 다음 작업: 평탄화 결과 avg_z와 별도 토양 측정 avg_z 비교 검증

## 2026-07-10 (다음 작업 라벨/버튼 동기화)

- 작업: 평탄화 후 토양 상태 유지, 다음 작업 라벨과 버튼 텍스트 동기화
- 변경/확인 파일: `integrated/config.py`, `integrated/dashboard_logic.py`, `integrated/dashboard_app.py`
- 결정 사항: 평탄화 완료 phase는 `REMEASURE`, 토양 상태는 유지하고 다음 작업은 토양 측정
- 남은 이슈: 긴 텍스트가 tray 버튼 폭에 맞는지 UI 확인 필요
- 다음 작업: 흙부족 → 흙추가 → 평탄화 → 토양 측정 → 새 판정 흐름 검증

## 2026-07-10 (일반 Tool/TCP 통일 및 compliance 분리)

- 작업: 일반 동작은 공통 Tool/TCP 상수로 통일하고 순응제어 설정은 독립 유지
- 변경/확인 파일: `robot_motion_data.py`
- 결정 사항: 일반 동작 `Tool Weight / Tool_v1`, compliance도 현재 같은 값이나 별도 상수
- 남은 이슈: 누름판/삽 Cartesian 경로와 payload 보상 실기 확인 필요
- 다음 작업: 이상 발생 시 PRESS 상수만 legacy 참고값과 컨트롤러 등록값에 맞춰 원복

## 2026-07-10 (보정 후 평탄화 Tool/상태 전이 수정)

- 작업: 보정 후 평탄화에서 누름판 pickup 강제, 평탄화 완료 후 토양 상태 미측정 초기화
- 변경/확인 파일: `integrated/dashboard_app.py`, `integrated/dashboard_logic.py`
- 결정 사항: AFTER_CORRECTION 평탄화는 빈 그리퍼 기준, 완료 후 다음 작업은 항상 토양 측정
- 남은 이슈: 사용자가 보정 후 수동으로 누름판을 집은 예외 흐름에서는 중복 pickup 주의
- 다음 작업: 흙부족 → 흙추가 → 평탄화 → 재측정 전체 흐름 검증

## 2026-07-10 (pickup handoff/측정 HOME 복귀 조정)

- 작업: 누름판 pickup 후 대기 0.5초 적용, 대시보드 토양 측정 종료 HOME 복귀 복원
- 변경/확인 파일: `integrated/config.py`, `integrated/dashboard_app.py`
- 결정 사항: pickup handoff만 500ms, 다른 handoff는 1000ms 유지
- 남은 이슈: pickup 직후 Tool/TCP 서비스 전환 안정성과 측정 종료 HOME 경로 확인 필요
- 다음 작업: pickup→측정 시작 로그와 측정 종료 `Step 1/2`, `Step 2/2` 확인

## 2026-07-10 (토양 측정 종료 HOME 생략)

- 작업: 대시보드 토양 측정 종료 후 상승/HOME 복귀 생략
- 변경/확인 파일: `integrated_tray_soil_state_check_node.py`, `integrated/dashboard_app.py`
- 결정 사항: 대시보드 실행은 트레이 중앙 상부에서 종료, 단독 실행은 기존 HOME 복귀 유지
- 남은 이슈: 다음 누름판 putdown의 트레이 상부 → HOME 직접 movej 경로 간섭 확인 필요
- 다음 작업: A~D 트레이별 측정 종료 자세와 후속 putdown 경로 검증

## 2026-07-10 (누름판 pickup 고속화/측정 시작 중복 제거)

- 작업: 누름판 pickup 빈 공간 이동 고속화, 토양 측정 시작의 중복 상승/HOME 제거
- 변경/확인 파일: `press_plate_pickup_node.py`, `integrated_tray_soil_state_check_node.py`
- 결정 사항: 빈 공간 85/80, 상부 접근 80/75, 파지 후 상승 50/45, 복귀 85/80
- 남은 이슈: 토양 측정 노드를 단독 실행하면 시작 위치가 HOME이라는 보장이 필요함
- 다음 작업: 대시보드 pickup→측정 연계와 단독 측정 실행 정책 확인

## 2026-07-10 (일반 이동 후 대기 0.5초 통일)

- 작업: 통합 토양 측정과 공통 흙 작업의 일반 이동 후 대기를 1.0초에서 0.5초로 단축
- 변경/확인 파일: `integrated_tray_soil_state_check_node.py`, `tray_soil_service_common.py`
- 결정 사항: 그리퍼/삽 안정화, compliance, 압착 유지, 폐기 유지, 노드 handoff 대기는 기존값 유지
- 남은 이슈: 코너 이동 직후 force 기준값 안정성 실기 확인 필요
- 다음 작업: 토양 측정 연속 코너와 평탄화 접촉값 변동 확인

## 2026-07-10 (누름판 pickup 추가 속도 조정)

- 작업: 누름판 하강/상승 및 HOME 복귀 속도 추가 상향
- 변경/확인 파일: `press_plate_pickup_node.py`
- 결정 사항: 하강 40/35, 파지 후 상승 45/40, 중간 경유 및 HOME 복귀 75/70
- 남은 이슈: 파지 위치 정렬 오차와 복귀 중 누름판 진동 실기 확인 필요
- 다음 작업: pickup 단독 실행으로 단계별 안정성 검증

## 2026-07-10 (누름판 집기 하강 속도 추가 조정)

- 작업: 누름판 상부에서 실제 집기 위치로 내려가는 속도 상향
- 변경/확인 파일: `press_plate_pickup_node.py`
- 결정 사항: 집기 하강 `20/20` → `30/30`
- 남은 이슈: 그리퍼와 누름판 정렬 오차 및 하강 정지 충격 확인 필요
- 다음 작업: 단독 pickup 경로 실기 확인

## 2026-07-10 (HOME/누름판 pickup 속도 조정)

- 작업: HOME 공통 이동과 누름판 pickup 구간별 속도 조정
- 변경/확인 파일: `motion_primitives.py`, `press_plate_pickup_node.py`
- 결정 사항: HOME 75/70, 빈 공간 75/70, 접근 70/65, 집기 하강 20/20, 파지 후 상승 35/35
- 남은 이슈: 누름판 payload 상태에서 가속/진동 실기 확인 필요
- 다음 작업: 저속 모드 준비 상태에서 HOME 및 pickup 전체 경로 검증

## 2026-07-10 (수동 제어 상시 노드)

- 작업: Joint/TCP 읽기와 수동 이동 노드를 대시보드 수명 동안 유지되는 상시 프로세스로 변경
- 변경/확인 파일: `integrated_manual_control_node.py`, `integrated/ros_runner.py`, `integrated/dashboard_app.py`
- 결정 사항: stdin JSON 명령/결과 로그 방식, 자동 작업 QProcess와 분리
- 남은 이슈: 현장 최초 서버 준비 시간 및 이동 중 긴급정지 복귀 동작 확인 필요
- 다음 작업: 연속 Joint/Base 읽기 응답 시간 및 수동 이동 검증

## 2026-07-10 (Joint/Base 읽기 timeout 적용)

- 작업: 수동 제어의 현재 Joint/Base 조회를 SDK 무제한 대기에서 직접 ROS 서비스 호출로 변경
- 변경/확인 파일: `integrated_manual_control_node.py`
- 결정 사항: 서비스 탐색/응답 최대 3초, 실패 시 구체적 오류 출력
- 남은 이슈: 현장 `aux_control/get_current_posj`, `get_current_posx` 응답 확인 필요
- 다음 작업: 대시보드 Joint 값/Base 값 읽기 버튼 재검증

## 2026-07-10 (긴급정지 로그/안전복구 설정)

- 작업: 긴급정지 노드 출력을 대시보드에 연결하고 안전복구 시 Tool/TCP 재설정
- 변경/확인 파일: `integrated/ros_runner.py`, `integrated/dashboard_app.py`, `integrated_manual_control_node.py`, `integrated_emergency_stop_node.py`
- 결정 사항: 긴급정지는 현재 작업과 별도 QProcess로 실행, 복구 시 `Tool Weight / Tool_v1` 적용 및 기존 tool 상태 유지
- 남은 이슈: 현장 `MoveStop` 서비스 응답과 실제 감속/정지 동작 검증 필요
- 다음 작업: 이동 중 긴급정지 → stop 성공 로그 → 안전복구 설정 로그 확인

## 2026-07-10 (긴급정지 Tool 상태 유지)

- 작업: 긴급정지 시 `current_tool_state`를 `UNKNOWN`으로 변경하지 않도록 수정
- 변경/확인 파일: `integrated/dashboard_app.py`
- 결정 사항: 정지 직전 `NONE/PRESS_PLATE_HELD/SHOVEL_HELD` 값을 그대로 유지하고 로그 표시
- 남은 이슈: tool pickup/putdown 도중 정지하면 저장 상태와 실제 파지 상태가 다를 수 있음
- 다음 작업: 각 tool 상태에서 긴급정지/복구 UI 동작 확인

## 2026-07-10 (평탄화 compliance 적용)

- 작업: 통합 평탄화를 고정 중앙 Z 이동에서 4코너 힘 접촉 감지 방식으로 변경
- 변경/확인 파일: `tray_soil_service_common.py`
- 결정 사항: 코너별 접촉 감지 후 1mm 추가 압착, 실패 코너는 추가 압착 생략
- 남은 이슈: 누름판 장착 상태에서 force 임계값 3.0과 최대 하강거리 실기 검증 필요
- 다음 작업: 저속으로 코너별 contact z와 복귀 경로 확인

## 2026-07-10 (전용 평탄화 노드 직접 실행)

- 작업: 대시보드 평탄화 호출을 `integrated_tray_soil_flatten_node` 직접 실행으로 전환
- 변경/확인 파일: `integrated/dashboard_app.py`
- 결정 사항: 기존 next-step 평탄화 분기는 원복용으로 유지, 성공 후 누름판 보유 상태 유지
- 남은 이슈: 실기에서 전용 노드의 top/press/return 경로 확인 필요
- 다음 작업: 보정 완료 → 평탄화 버튼 → 재측정 흐름 검증

## 2026-07-10 (Tool/TCP 이름 통일)

- 작업: 누름판/삽 Tool/TCP를 컨트롤러에서 확인된 이름으로 변경
- 변경/확인 파일: `robot_motion_data.py`
- 결정 사항: 전체 통합 작업에서 `Tool Weight / Tool_v1` 사용
- 남은 이슈: 변경된 TCP 기준으로 누름판/삽 티칭 좌표 실기 확인 필요
- 다음 작업: HOME → 누름판 pickup → 토양 측정 → putdown → 식재 순서 재검증

## 2026-07-10 (Tool/TCP 거부 시 동작 복구)

- 작업: Tool/TCP 설정 서비스가 이름을 거부해도 현재 controller 설정을 유지하고 작업 계속
- 변경/확인 파일: `node_common.py`
- 결정 사항: 서비스 무한 대기 방지는 유지하되 unavailable/timeout/rejected는 경고 처리
- 남은 이슈: `Tool Weight_1`, `Tool Weight`, `GripperDA_v1`, `Tool_v1` 등록 이름 현장 확인 필요
- 다음 작업: HOME/누름판/식재 동작 재확인 및 controller Tool/TCP 등록 목록 점검

## 2026-07-10 (식재 시작 Tool/TCP 대기 수정)

- 작업: Tool/TCP 설정을 무제한 SDK 대기에서 timeout 적용 ROS 서비스 호출로 변경
- 변경/확인 파일: `node_common.py`, 전체 `setup_tool_and_tcp()` 호출 노드
- 결정 사항: 각 서비스 탐색/응답을 최대 5초 기다리고 실패 시 명시적 오류로 종료
- 남은 이슈: 현장 controller에서 `tool/set_current_tool`, `tcp/set_current_tcp` 응답 확인 필요
- 다음 작업: A 트레이 식재 재실행 후 `Configured tool`, `Configured tcp` 로그 확인

## 2026-07-10 (MoveStop 정상 노드 정리)

- 작업: 전체 정상 작업 노드에서 사용하지 않는 `request_motion_stop()` 공통 함수 제거
- 변경/확인 파일: `node_common.py`, 전체 Python 노드
- 결정 사항: `MoveStop`은 `integrated_emergency_stop_node.py`에서만 사용
- 남은 이슈: 긴급정지 서비스 경로는 현장 bringup 기준으로 별도 검증 필요
- 다음 작업: 통합 작업별 실행 로그에서 MoveStop 경고 재발 여부 확인

## 2026-07-10 (누름판 노드 시작 경고 정리)

- 작업: 누름판 pickup/putdown 시작 시 선행 `MoveStop` 요청 제거
- 변경/확인 파일: `press_plate_pickup_node.py`, `press_plate_putdown_node.py`
- 결정 사항: 정상 작업 노드는 자체 시작 경로로 이동하고 `MoveStop`은 긴급정지에만 사용
- 남은 이슈: 실기에서 pickup/putdown 전체 경로 확인 필요
- 다음 작업: 재빌드 후 대시보드 누름판 집기/놓기 로그 확인

## 2026-07-10 (HOME 시작 경고 정리)

- 작업: HOME 노드 시작 시 선행 `MoveStop` 요청 제거
- 변경/확인 파일: `go_home_test_node.py`
- 결정 사항: 일반 HOME은 안전 상승 후 홈 이동을 바로 실행하고, `MoveStop`은 긴급정지 노드에 유지
- 남은 이슈: 실제 bringup에서 HOME 전체 경로 실기 확인 필요
- 다음 작업: 재빌드 후 대시보드 HOME 로그 확인

## 2026-07-10 (단독 돌멩이 제거 경로)

- 작업: 고정 좌표 기반 단독 돌멩이 pick/drop 시퀀스 추가
- 변경/확인 파일: `robot_motion_data.py`, `standalone_tests/tray_rock_remove_node.py`
- 결정 사항: 현재 tool을 `press/shovel/none`으로 입력받고 필요 시 기존 putdown 노드를 선행 실행
- 남은 이슈: 실기에서 각 waypoint, DR_BASE 자세 및 충돌 여부 검증 필요
- 다음 작업: 저속 실기 검증 후 통합 적용 여부 결정

## 2026-07-10 (단독 테스트 분리)

- 작업: 통합에서 직접 사용하지 않는 단독 테스트 노드 12개를 `robot_tests/standalone_tests/`로 이동
- 변경/확인 파일: `robot_tests/standalone_tests/`, `setup.py`
- 결정 사항: 파일 위치만 분리하고 기존 `ros2 run` 실행 이름은 유지
- 남은 이슈: 없음
- 다음 작업: 빌드 후 통합 launch 및 필요한 단독 테스트 실행 확인

## 2026-07-10

- 작업: 통합 대시보드를 ROS 2 launch로 실행할 수 있도록 진입점과 설치 설정 추가
- 변경/확인 파일:
  - `launch/integrated_dashboard.launch.py`
  - `setup.py`
  - `package.xml`
  - `robot_tests/integrated/README.md`
- 결정 사항: 작업 노드는 대시보드가 상태에 따라 순차 실행하므로 launch에서는 대시보드만 시작
- 남은 이슈: 실제 로봇 bringup 이후 GUI 표시 및 자식 작업 노드 실행 확인 필요
- 다음 작업: 워크스페이스 빌드 후 `ros2 launch robot_tests integrated_dashboard.launch.py` 실기 검증

## 2026-07-09 16:33

- 작업: `next_action` 저장형 상태머신을 `soil_status + work_phase` 계산형으로 전환하고, 최근 UI/안전/딜레이 변경사항까지 반영
- 변경/확인 파일:
  - `robot_tests/integrated/dashboard_app.py`
  - `robot_tests/integrated/dashboard_logic.py`
  - `robot_tests/integrated/config.py`
  - `robot_tests/integrated/smartfarm_dashboard.ui`
  - `robot_tests/integrated_tray_next_step_node.py`
- 현재 상태머신 핵심:
  - `TrayState` 에서 `next_action` 저장 제거
  - 대신 `soil_status` + `work_phase` 로 매번 `get_next_action()` 계산
  - `work_phase` 값:
    - `IDLE`
    - `AFTER_CORRECTION`
    - `DONE`
  - 계산 규칙:
    - `미측정`, `측정실패` -> `토양 측정`
    - `흙부족` -> `흙추가`
    - `흙많음` -> `흙제거`
    - `장애물감지` -> `돌제거`
    - `정상` -> `식물 심기`
    - `AFTER_CORRECTION` -> `평탄화`
    - `DONE` -> `완료`
- 현재 보정/평탄화 흐름:
  - `흙추가/흙제거/돌제거` 작업 성공 종료 시 `work_phase = AFTER_CORRECTION`
  - 그래서 UI `다음 작업` 글자는 `평탄화`
  - 사용자가 다시 `다음 작업` 눌러야 평탄화
  - 평탄화 완료 시 `work_phase = IDLE`, `last_measurement = {}`
  - 그 다음 UI `다음 작업` 은 `토양 측정`
- 현재 평탄화 tool 전이:
  - `SHOVEL_HELD` 면 `삽 놓기 -> 누름판 집기 -> 평탄화`
  - `NONE`/`UNKNOWN` 면 `누름판 집기 -> 평탄화`
  - `PRESS_PLATE_HELD` 면 바로 평탄화
  - flatten branch tool/tcp 는 `PRESS_TOOL_NAME`, `PRESS_TCP_NAME` 사용
- 현재 UI 시각 상태:
  - tray 카드 배경색:
    - `미측정` 회색
    - `정상` 녹색
    - `흙부족`, `흙많음` 노랑
    - `장애물감지`, `측정실패` 빨강
  - `lbl_trayN_state` 글자색도 위 상태색과 동일 계열로 변경
  - 각 tray 우측상단 `리셋` 버튼 위치 수정 완료
- 현재 ROS 연결 표시:
  - 2초마다 `/dsr01/system/get_robot_state` 서비스 존재 확인
  - 있으면 `Connected`, 없으면 `Disconnected`
  - 주의: 실제 응답 성공이 아니라 service 존재 기준이라 완전 신뢰는 어려움
- 현재 긴급정지:
  - `integrated_emergency_stop_node` (`MoveStop` + `DR_QSTOP`)
  - 현재 프로세스 kill
  - 팝업 표시: `긴급정지 하였습니다. 사용자가 상황을 확인하세요`
  - `안전복구` 는 robot-side recovery 호출 없이 UI 잠금만 해제
- 현재 안전 제한:
  - `ros_connected == False` 면 tray/manual/자동 작업 버튼 비활성
  - `current_tool_state == UNKNOWN` 이면 자동 작업 금지:
    - `토양 측정`
    - `흙추가/흙제거/돌제거`
    - `평탄화`
    - `식물 심기`
- 현재 노드 handoff delay:
  - `config.INTER_NODE_DELAY_MS = 1000`
  - `QTimer.singleShot()` 사용
  - 적용 구간:
    - `press pickup 완료 -> 토양 측정 시작`
    - `press pickup 완료 -> 평탄화 시작`
    - `press putdown 완료 -> 다음 작업 시작`
    - `shovel putdown 완료 -> press pickup 시작`
- 현재 남은 구조 이슈:
  - `SHOVEL_HELD` 상태에서 `토양 측정`, `식물 심기` 누를 때 shovel putdown 선행이 아직 없음
  - 사용자는 이 부분 추후 UI 운용으로 해결 예정이라 코드 수정 보류
  - `안전복구 완료` 문구는 실제 robot recovery보다 과한 표현일 수 있음
- 실행 전 주의:
  - 항상 재빌드 필요:
    - `colcon build --packages-select robot_tests`
    - `source install/setup.bash`
- 다음 세션 우선 포인트:
  - `흙추가 성공 종료` 와 `실제 로봇 동작 성공` 불일치 시 phase 전환 정책 재검토
  - `SHOVEL_HELD -> 측정/식재` 전이 보강 여부 결정
  - ROS 연결 판정을 service 존재가 아니라 실제 응답 성공 기준으로 강화할지 결정

## 2026-07-09 15:41

- 작업: 대시보드 UI/상태머신 최근 통합 변경사항 일괄 정리
- 변경/확인 파일:
  - `robot_tests/integrated/dashboard_app.py`
  - `robot_tests/integrated/dashboard_logic.py`
  - `robot_tests/integrated/config.py`
  - `robot_tests/integrated/smartfarm_dashboard.ui`
  - `robot_tests/integrated_tray_next_step_node.py`
  - `robot_tests/tray_soil_service_common.py`
  - `setup.py`
- 현재 UI 상태:
  - 시스템 제어 아래 추가 버튼 있음: `누름판 집기`, `누름판 놓기`, `삽 집기`, `삽 놓기`
  - `누름판 놓기`, `삽 놓기`는 tool state와 무관하게 `busy` 아닐 때 사용 가능
  - 각 tray 카드 우측상단에 `리셋` 버튼 있음
  - tray 카드 배경색 상태 연동:
    - `미측정` = 회색
    - `정상` = 녹색
    - `흙부족`, `흙많음` = 노랑
    - `장애물감지`, `측정실패` = 빨강
- 현재 ROS 연결 표시:
  - `lbl_ros_status`는 가짜 토글 아님
  - 2초마다 `/dsr01/system/get_robot_state` 서비스 존재 확인
  - 있으면 `Connected`, 없으면 `Disconnected`
- 현재 긴급정지 정책:
  - `긴급정지` 누르면 `integrated_emergency_stop_node` 실행 (`MoveStop` + `DR_QSTOP` 계열)
  - 현재 프로세스 kill
  - 경고 팝업 표시: `긴급정지 하였습니다. 사용자가 상황을 확인하세요`
  - `안전복구` 누르면 현재는 서보 제어 없이 UI 버튼만 다시 활성화
  - 참고: 한때 `servo_off/servo_on` 방식으로 바꿨다가 사용자 요청으로 되돌림. 현재는 `QSTOP` 유지
- 현재 tray 상태머신:
  - 초기값:
    - `토양 상태 = 미측정`
    - `다음 작업 = 토양 측정`
  - soil check 후 다음 작업 문구:
    - `흙부족` -> `흙추가`
    - `흙많음` -> `흙제거`
    - `장애물감지` -> `돌제거`
    - `정상` -> `식물 심기`
  - 보정 작업 흐름:
    - `흙추가/흙제거/돌제거` 끝나면 자동 평탄화 안 함
    - 완료 후 `다음 작업 = 평탄화`
    - 사용자가 `다음 작업` 다시 눌러야 평탄화 실행
    - 평탄화 끝나면 `다음 작업 = 토양 측정`
- 현재 흙추가 구현 기준:
  - UI `다음 작업` -> `integrated_tray_next_step_node`
  - `SOIL_LOW`면 `run_soil_add_action()`
  - `run_soil_add_action()` 흐름:
    - `pickup_shovel()`
    - `fill_shovel_from_supply()`
    - tray별 drop taught path 사용
      - `A -> drop_soil_to_a_tray_test`
      - `B -> drop_soil_to_b_tray_test`
      - `C -> drop_soil_to_c_tray_test`
      - `D -> drop_soil_to_d_tray_test`
    - `return_shovel()`
  - 즉 generic corner drop 아님. `abcd_tray_soil_drop_test_node` 계열 taught path 재사용
- shovel pickup/return 관련 결정:
  - placeholder Cartesian `SOIL_SHOVEL_PICKUP_*_POSE` 경로 사용 안 함
  - 기존 테스트 노드와 같은 `SHOVEL_READY_JOINT`, `SHOVEL_PICK_JOINT` 기반 경로 사용
  - 이유: 실기에서 placeholder pose가 대칭 이상/축 반전처럼 보였음
- remove 관련 결정:
  - `run_soil_remove_action()`도 add와 동일하게 앞에서 `pickup_shovel()`
  - 끝나면 `return_shovel()`
  - `C` tray custom remove도 now shovel pickup/return 정책 안으로 들어감
- reset 버튼 정책:
  - `busy` 아닐 때만 tray reset 가능
  - 완료 tray도 reset 가능
  - reset 시 해당 tray만 초기화:
    - `soil_status = 미측정`
    - `next_action = 토양 측정`
    - `last_error`, `last_measurement` 비움
    - 카드색 회색 복귀
- 완료 상태 정책:
  - `완료` 상태 tray는 `토양 측정`, `다음 작업` 버튼 비활성
  - reset 하면 다시 초기 상태로 돌아와 재사용 가능
- 수동 제어 상태:
  - `현재 Joint`, `현재 TCP` 읽기 동작 연결됨
  - 읽은 값은 spinbox에 반영됨
  - `Joint 이동`, `Base 이동` 연결됨
- install/runtime 주의:
  - `smartfarm_dashboard.ui`는 `setup.py`의 `package_data`에 포함되도록 수정됨
  - 실행 전 항상 재빌드 필요:
    - `colcon build --packages-select robot_tests`
    - `source install/setup.bash`
- 다음 세션에서 먼저 볼 포인트:
  - `흙추가 -> 평탄화 -> 재측정` 실기 흐름 확인
  - `긴급정지`/`안전복구` 현장 동작 검증
  - ROS 연결 표시 기준 서비스 `/dsr01/system/get_robot_state` 가 현장 bringup과 항상 일치하는지 확인
  - 필요하면 `안전복구` 후 `HOME` 강제 여부 다시 결정
  - 필요하면 `WORKLOG.md` 계속 최신 항목 위에 누적

## 2026-07-09 00:00

- 작업: `integrated_emergency_stop_node` 추가, 긴급정지 시 현재 프로세스 kill 전에 MoveStop 서비스 기반 detached stop 요청을 보내도록 보강
- 변경/확인 파일: `integrated_emergency_stop_node.py`, `ros_runner.py`, `dashboard_app.py`, `config.py`, `setup.py`
- 결정 사항: 즉시정지는 `dsr_msgs2.srv.MoveStop` + `DR_QSTOP` 우선 사용, 현재 실행 노드와 독립적으로 실행되도록 detached QProcess로 호출
- 남은 이슈: 현장 환경에서 `MoveStop` 서비스 이름과 `DR_QSTOP` 동작 강도 실기 확인 필요
- 다음 작업: estop 실기 검증, 필요시 `ServoOff` 또는 추가 safe stop/reset 절차 검토

## 2026-07-09 00:00

- 작업: 긴급정지 시 tool state를 `UNKNOWN`으로 전환하고, 복구 후 `HOME` 전까지 일반 작업을 막는 안전 정책 반영
- 변경/확인 파일: `config.py`, `dashboard_logic.py`, `dashboard_app.py`
- 결정 사항: 작업 중간 긴급정지는 hand/tool 상태를 신뢰하지 않으므로 `TOOL_STATE_UNKNOWN` 도입, 해당 tray의 `last_measurement`는 즉시 폐기, `recover` 후에도 `HOME` 완료 전까지 일반 버튼 비활성 유지
- 남은 이슈: 실제 로봇 controller stop API를 호출하는 전용 `integrated_emergency_stop_node`는 아직 없음
- 다음 작업: `integrated_emergency_stop_node` 구현, `HOME` 완료 후만 정상 상태 복귀되도록 실기 검증

## 2026-07-09 00:00

- 작업: 수동제어 탭용 `integrated_manual_control_node` 추가, joint/base 읽기와 이동 버튼을 대시보드에 연결
- 변경/확인 파일: `integrated_manual_control_node.py`, `dashboard_app.py`, `config.py`, `setup.py`
- 결정 사항: 수동제어는 기존 `QProcess` 구조를 유지하고, `read-joint/read-base/move-joint/move-base`를 하나의 통합 노드 인자로 분기한다
- 남은 이슈: Doosan API의 `get_current_posj()` 가 현장 환경에서 제공되는지 실기 확인 필요
- 다음 작업: 수동제어 읽기/이동 실기 검증, 필요시 속도/가속도 UI 노출 여부 결정

## 2026-07-09 00:00

- 작업: `완료` 상태 트레이의 `토양 측정`/`다음 작업` 버튼 비활성화 처리 추가
- 변경/확인 파일: `dashboard_app.py`
- 결정 사항: `next_action == 완료`인 tray는 추후 reset 기능 전까지 `btn_trayN_check`, `btn_trayN_next` 모두 활성화하지 않음
- 남은 이슈: reset 기능은 아직 없음
- 다음 작업: reset 정책/버튼 설계 시 완료 tray 재활성화 경로 추가

## 2026-07-09 00:00

- 작업: soil 보정 중 shovel pickup/return 로그를 파싱해 `current_tool_state`를 `SHOVEL_HELD`/`NONE`으로 갱신하도록 보강
- 변경/확인 파일: `dashboard_app.py`
- 결정 사항: shovel은 별도 프로세스가 아니라 `integrated_tray_next_step_node` 내부 시퀀스이므로 stdout 로그 `"Pickup shovel start"`, `"Return shovel start"`를 기준으로 UI tool state를 추적
- 남은 이슈: rock remove는 shovel이 아니라 gripper 직접 사용이라 별도 tool state 정의는 아직 두지 않음
- 다음 작업: 실패/긴급정지 시 `current_tool_state`와 `last_measurement` 정리 정책 보강

## 2026-07-09 00:00

- 작업: 토양 측정 상세결과를 `measurement_result_json`으로 저장하고, `다음 작업`에서 `tray_state.last_measurement`를 우선 재사용하도록 개선
- 변경/확인 파일: `dashboard_logic.py`, `dashboard_app.py`, `integrated_tray_soil_state_check_node.py`, `integrated_tray_next_step_node.py`
- 결정 사항: `다음 작업`의 soil 보정은 저장된 상세 측정 결과가 있으면 재측정 없이 사용하고, 없을 때만 `inspect_tray_soil()`로 fallback
- 남은 이슈: 긴급정지/실패 후 저장 측정결과를 언제 무효화할지 정책 추가 필요
- 다음 작업: 실패/복구 시 `last_measurement` 정리 정책, flatten 후 자동 재측정 여부 결정

## 2026-07-09 00:00

- 작업: `integrated_tray_next_step_node` 추가, `다음 작업` 버튼을 통합 노드 경유로 묶고 flatten/plant 분기 처리 연결
- 변경/확인 파일: `integrated_tray_next_step_node.py`, `dashboard_app.py`, `config.py`, `setup.py`
- 결정 사항: `다음 작업`의 soil 보정 분기는 마지막 측정의 상세 corner 데이터가 UI에 없으므로, 통합 노드 시작 시 `inspect_tray_soil()`를 다시 호출해 상세 결과를 복원한 뒤 add/remove/rock를 결정
- 남은 이슈: `다음 작업`의 `토양 측정`은 여전히 `run_measure()` 경로를 사용하며, flatten 분기에서 UI 표시 상태와 재측정 결과가 다를 수 있음
- 다음 작업: flatten 후 자동 재측정까지 통합할지 결정, `tray_state.last_measurement`에 상세 결과 저장하는 구조 검토

## 2026-07-09 00:00

- 작업: 통합본 전용 `integrated_tray_soil_flatten_node` 추가, 대시보드 평탄화 호출을 tray 인자형 1회 press 노드로 전환
- 변경/확인 파일: `integrated_tray_soil_flatten_node.py`, `dashboard_app.py`, `config.py`, `setup.py`
- 결정 사항: 통합본 `평탄화`는 기존 코너 순회 테스트가 아니라 후처리용 중앙 press 1회 동작으로 정의하고, 실제 동작은 `run_tray_flatten_action()`을 재사용
- 남은 이슈: 후속 재측정 자동화와 상세 측정 결과의 UI 상태 저장은 아직 없음
- 다음 작업: `integrated_tray_next_step_node` 설계/구현

## 2026-07-09 00:00

- 작업: 식물 심기 통합본 전용 `integrated_plant_pick_and_place_node` 추가, 대시보드에서 press plate putdown 선행 후 tray별 plant index 매핑으로 호출 연결
- 변경/확인 파일: `integrated_plant_pick_and_place_node.py`, `dashboard_app.py`, `config.py`, `setup.py`
- 결정 사항: 대시보드에는 plant 번호 입력 UI가 없으므로 임시로 `A/B/C/D -> plant 1/2/3/4` 매핑을 `config.TRAY_TO_PLANT_INDEX`로 관리
- 남은 이슈: 이 plant index 매핑이 실제 운영 정책과 다를 수 있어 추후 UI 입력 또는 별도 배정표로 교체 필요
- 다음 작업: `tray_soil_flatten_node` 통합본 분리 여부 검토, `integrated_tray_next_step_node` 설계

## 2026-07-09 00:00

- 작업: 토양 측정 통합본 경로를 기존 테스트 노드와 분리해 `integrated_tray_soil_state_check_node` 신설, pickup 선행 후 통합본 전용 노드 호출로 통합
- 변경/확인 파일: `dashboard_app.py`, `ros_runner.py`, `tray_soil_state_check_node.py`, `integrated_tray_soil_state_check_node.py`, `setup.py`, `config.py`
- 결정 사항: 기존 `tray_soil_state_check_node.py`는 interactive 테스트용 유지, 대시보드는 새 `integrated_tray_soil_state_check_node`만 호출
- 남은 이슈: `run_flatten()`과 `plant_pick_and_place_tray_select_node.py`는 아직 대화식/직접입력 의존이 남아 있음
- 다음 작업: `plant_pick_and_place_tray_select_node.py` 인자화, `tray_next_step_node` 설계, `평탄화`/`식물 심기`도 tool 전이 규칙 반영

## 2026-07-09 00:00

- 작업: `integrated` 폴더를 통합 작업 기록 허브로 사용하기 위한 문서 구조 추가
- 변경/확인 파일: `README.md`, `WORKLOG.md`
- 결정 사항: 구현 코드는 기존 Python 파일에 유지하고, 구조/진행 기록은 이 로그에 누적
- 남은 이슈: 실제 통합 대시보드 기능 변경 이력은 아직 별도 기록 없음
- 다음 작업: 다른 Codex가 진행 중인 통합 기능 작업 내용을 이 로그 형식으로 계속 누적
