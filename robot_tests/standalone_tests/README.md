# Standalone test nodes

통합 대시보드가 직접 사용하지 않는 단독 장비 테스트 노드를 보관한다.

- 파일 위치만 분리했으며 기존 `ros2 run robot_tests <실행 이름>`은 그대로 유지한다.
- 통합 대시보드에서 호출하는 노드와 공통 모듈은 상위 `robot_tests/`에 둔다.
- 단독 테스트 코드를 통합 흐름에서 사용하게 되면 상위 통합 노드나 공통 모듈로 옮긴다.

## 고정 좌표 돌멩이 제거

현재 잡고 있는 tool을 선택하면 필요한 putdown 노드를 먼저 실행한 뒤 고정 좌표
pick/drop 경로를 실행한다.

```bash
ros2 run robot_tests tray_rock_remove_node -- --held-tool none
ros2 run robot_tests tray_rock_remove_node -- --held-tool press
ros2 run robot_tests tray_rock_remove_node -- --held-tool shovel
```

`--held-tool`을 생략하면 실행 시 현재 상태를 입력받는다.
