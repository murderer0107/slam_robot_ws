# 홈에서 출발해 선택한 트레이의 선택한 모종을 집고 목표 트레이에 옮겨 심는 테스트 코드다.
"""Interactive Doosan M0609 plant pick route test node."""

from __future__ import annotations

import rclpy

from robot_tests.dsr_runtime import bootstrap_dsr_python
from robot_tests.motion_primitives import (
    set_outputs_compat,
)
from robot_tests.node_common import (
    ROBOT_ID,
    ROBOT_MODEL,
    configure_dsr_init,
    import_basic_motion_apis,
    import_digital_output_apis,
    setup_tool_and_tcp,
)
from robot_tests.plant_pick_and_place_common import (
    TARGET_TRAY_PLACE_JOINTS,
    TOOL_NAME,
    TCP_NAME,
    run_plant_pick_and_place_sequence,
)
from robot_tests.robot_motion_data import (
    PLANT_ACTIVE_TRAY,
    TRAY_PLANT_JOINTS,
)

bootstrap_dsr_python()

import DR_init

configure_dsr_init(DR_init)


def prompt_choice(prompt: str, valid_values: list[str]) -> str:
    # 대소문자 구분 없이 허용 목록만 받아 반복 선택 입력에 재사용한다.
    valid_map = {value.upper(): value for value in valid_values}
    while True:
        raw = input(prompt).strip()
        if not raw:
            print("입력이 비었습니다. 다시 입력하세요.")
            continue
        if raw.lower() == "q":
            raise KeyboardInterrupt
        key = raw.upper()
        if key not in valid_map:
            print(f"잘못된 입력입니다. 가능한 값: {', '.join(valid_values)}")
            continue
        return valid_map[key]


def prompt_target_tray() -> str:
    # 사용자 입력은 A/B/C/D로 받고, 실제 트레이 키 변환은 메인 루프에서 수행한다.
    tray_map = {
        "A": "tray_a",
        "B": "tray_b",
        "C": "tray_c",
        "D": "tray_d",
    }
    return prompt_choice("\n심을 트레이 선택 [A/B/C/D], 종료 [q]: ", list(tray_map)).upper()


def prompt_plant_index() -> int:
    # 현재 활성 소스 트레이에 정의된 식물 번호만 유효값으로 허용한다.
    valid_plants = sorted(TRAY_PLANT_JOINTS[PLANT_ACTIVE_TRAY].keys())
    while True:
        raw = input(
            f"식물 번호 선택 [{'/'.join(str(value) for value in valid_plants)}], 종료 [q]: "
        ).strip()
        if raw.lower() == "q":
            raise KeyboardInterrupt
        if not raw.isdigit():
            print("숫자를 입력하세요.")
            continue
        plant_index = int(raw)
        if plant_index not in valid_plants:
            print(f"잘못된 입력입니다. 가능한 식물 번호: {valid_plants}")
            continue
        return plant_index


def main(args=None):
    rclpy.init(args=args)

    # Doosan API가 참조할 ROS 노드를 생성하고 DR_init 전역에 연결한다.
    node = rclpy.create_node("plant_pick_and_place_tray_select", namespace=ROBOT_ID)
    DR_init.__dsr__node = node

    try:
        motion_apis = import_basic_motion_apis(node)
    except ImportError:
        node.destroy_node()
        rclpy.shutdown()
        return

    set_digital_outputs_fn, set_digital_output_fn = import_digital_output_apis()

    try:
        # gripper on/off 제어 함수 시그니처 차이를 감싸는 호환 래퍼를 준비한다.
        set_digital_outputs = set_outputs_compat(
            node,
            set_digital_outputs_fn=set_digital_outputs_fn,
            set_digital_output_fn=set_digital_output_fn,
        )

        # 이 테스트에서 사용하는 툴과 TCP를 먼저 맞춰 둔다.
        setup_tool_and_tcp(node, motion_apis["set_tool"], motion_apis["set_tcp"], TOOL_NAME, TCP_NAME)

        tray_map = {
            "A": "tray_a",
            "B": "tray_b",
            "C": "tray_c",
            "D": "tray_d",
        }

        while rclpy.ok():
            # 매 반복마다 목표 트레이와 집어 올릴 모종 번호를 대화식으로 선택한다.
            target_tray_label = prompt_target_tray()
            plant_index = prompt_plant_index()
            target_tray = tray_map[target_tray_label]

            node.get_logger().info(
                f"Selected source={PLANT_ACTIVE_TRAY}, plant={plant_index}, target={target_tray_label}"
            )
            # 공통 시퀀스 함수에 현재 선택값과 Doosan motion API를 넘겨 실제 이송을 수행한다.
            run_plant_pick_and_place_sequence(
                node=node,
                movej=motion_apis["movej"],
                movel=motion_apis["movel"],
                posj=motion_apis["posj"],
                posx=motion_apis["posx"],
                set_digital_outputs=set_digital_outputs,
                wait=motion_apis["wait"],
                get_current_posx=motion_apis["get_current_posx"],
                dr_base=motion_apis["DR_BASE"],
                source_tray=PLANT_ACTIVE_TRAY,
                plant_index=plant_index,
                target_tray=target_tray,
            )
            # 마지막 하강 목표 joint를 함께 남겨 실제 배치 위치 확인에 도움을 준다.
            node.get_logger().info(
                "plant_pick_and_place_tray_select complete; "
                f"final place joint={TARGET_TRAY_PLACE_JOINTS[target_tray]['down']}"
            )

    except KeyboardInterrupt:
        node.get_logger().info("Stopped by user")
    except Exception as exc:
        node.get_logger().error(f"plant_pick_and_place_tray_select failed: {exc}")
        raise
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
