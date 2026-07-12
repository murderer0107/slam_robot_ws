# integrated

`robot_tests.integrated` 는 통합 실행 코드와 통합 작업 기록을 함께 관리하는 폴더다.
다른 Codex가 실제 구현을 진행하더라도, 이 폴더 문서를 기준으로 구조와 진행 상황을 추적한다.

## 목적

- 통합 대시보드 관련 실행 코드 유지
- 통합 작업의 현재 구조 설명
- 세션별 작업 내용과 결정 사항 기록
- 다음 작업자가 빠르게 이어받을 수 있게 인수인계 기준 제공

## 현재 코드 구조

- `main.py`
  - PyQt 대시보드 엔트리포인트
- `dashboard_app.py`
  - 대시보드 UI 동작과 화면 제어
- `dashboard_logic.py`
  - 대시보드 상태 전이와 업무 로직
- `ros_runner.py`
  - ROS 2 노드 실행 보조
- `config.py`
  - tray, 상태값, 노드 이름, 공통 상수

## 기록 파일

- `WORKLOG.md`
  - 통합 작업 이력, 현재 이슈, 다음 작업 기록

## 기록 규칙

- 실제 코드 수정은 구현 담당 Codex가 진행해도 된다.
- 구조 변경, 기능 추가, 작업 중단, 확인 필요 항목은 `WORKLOG.md` 에 남긴다.
- 로그는 최신 항목이 위로 오게 추가한다.
- 한 항목에는 최소한 날짜, 작업 요약, 영향 파일, 남은 이슈를 적는다.
- 구현이 끝나지 않은 상태라도 중간 판단과 막힌 지점을 남긴다.

## 권장 작업 흐름

1. `README.md` 로 현재 구조 확인
2. `WORKLOG.md` 최신 항목 확인
3. 코드 수정 또는 검토 진행
4. 변경 후 `WORKLOG.md` 에 작업 내용 기록

## launch 실행

통합 launch는 대시보드만 시작한다. 로봇 작업 노드는 대시보드가 버튼 입력과
상태 전이에 맞춰 순차적으로 실행하므로 launch에서 동시에 시작하지 않는다.

```bash
cd /home/rokey/ws_cobot_pjt/ws_cobot1
colcon build --packages-select robot_tests
source install/setup.bash
ros2 launch robot_tests integrated_dashboard.launch.py
```

통합 실행에 직접 필요한 파일은 다음과 같다.

- `launch/integrated_dashboard.launch.py`: launch 진입점
- `robot_tests/integrated/`: 대시보드 UI, 상태 로직, ROS 실행 보조
- `robot_tests/integrated_*_node.py`: 통합 전용 작업 노드
- `robot_tests/{dsr_runtime,node_common,motion_primitives,robot_motion_data}.py`: 로봇 공통 코드
- `robot_tests/{compliance_common,plant_pick_and_place_common,tray_soil_service_common}.py`: 작업별 공통 코드
- `setup.py`, `package.xml`, `resource/robot_tests`: ROS 2 패키지 설치 정보

그 밖의 단독 테스트 노드는 통합 대시보드에서 호출되는 노드인지 확인한 뒤 제거해야
한다. 현재 대시보드는 홈 복귀와 tool pickup/putdown 노드도 직접 호출하므로 유지한다.

## 기록 템플릿

아래 형식으로 `WORKLOG.md` 에 추가한다.

```md
## YYYY-MM-DD HH:MM

- 작업:
- 변경/확인 파일:
- 결정 사항:
- 남은 이슈:
- 다음 작업:
```
