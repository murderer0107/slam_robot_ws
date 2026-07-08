# 로봇 테스트 노드들이 공통으로 사용하는 이동/그리퍼 보조 함수 모음이다.
"""Shared motion/gripper primitives for robot test nodes."""

from __future__ import annotations

from robot_tests.robot_motion_data import GRIPPER_HOME_PREPARE, GRIPPER_PICK_CLOSE, HOME_JOINT

DEFAULT_VELOCITY = 60.0
DEFAULT_ACCELERATION = 60.0
DEFAULT_WAIT = 0.5
DEFAULT_HOME_Z_OFFSET = 120.0


def normalize_pose(raw_pose: object) -> list[float]:
    """Doosan pose 반환형을 6개 float 리스트로 정규화."""
    pose = raw_pose

    if isinstance(raw_pose, tuple):
        if not raw_pose:
            raise ValueError("Current pose tuple is empty")
        pose = raw_pose[0]

    if hasattr(pose, "tolist"):
        pose = pose.tolist()

    if not isinstance(pose, (list, tuple)):
        raise TypeError(f"Unsupported pose type: {type(pose).__name__}")

    pose_list = list(pose)
    if len(pose_list) < 6:
        raise ValueError(f"Current pose has insufficient length: {len(pose_list)}")

    return [float(value) for value in pose_list[:6]]


def pose(values: list[float]) -> list[float]:
    if len(values) != 6:
        raise ValueError(f"Pose must have 6 elements, got {len(values)}")
    return [float(value) for value in values]


def set_outputs_compat(node, set_digital_outputs_fn=None, set_digital_output_fn=None):
    if set_digital_outputs_fn is not None:
        return set_digital_outputs_fn

    if set_digital_output_fn is None:
        raise RuntimeError("No gripper digital output API available")

    # 구형 API만 있을 때도 동일한 채널 리스트 형식으로 호출 가능하게 맞춘다.
    def _set_outputs(channels: list[int]) -> None:
        for channel in channels:
            index = abs(int(channel))
            value = 1 if int(channel) > 0 else 0
            set_digital_output_fn(index, value)

    node.get_logger().info("Using set_digital_output compatibility wrapper")
    return _set_outputs


def gripper_command(node, set_digital_outputs, wait, name: str, channels: list[int]) -> None:
    node.get_logger().info(f"Gripper command: {name} -> {channels}")
    set_digital_outputs(channels)
    wait(DEFAULT_WAIT)


def prepare_home_joint(node, set_digital_outputs, wait) -> None:
    # 홈 복귀 전 그리퍼 간섭을 줄이기 위해 넓게 열린 상태로 맞춘다.
    gripper_command(
        node,
        set_digital_outputs,
        wait,
        "HOME_PREPARE_OPEN_0100",
        GRIPPER_HOME_PREPARE,
    )


def move_j(
    node,
    movej,
    posj,
    wait,
    name: str,
    joint_values: list[float],
    vel: float = DEFAULT_VELOCITY,
    acc: float = DEFAULT_ACCELERATION,
) -> None:
    # 조인트 기반 이동. 큰 자세 전환이나 IK 해를 고정하고 싶을 때 사용.
    target = posj(pose(joint_values))
    node.get_logger().info(f"MoveJ start: {name} -> {joint_values} @ vel={vel}, acc={acc}")
    movej(target, vel=vel, acc=acc)
    wait(DEFAULT_WAIT)


def move_l(
    node,
    movel,
    posx,
    wait,
    name: str,
    pose_values: list[float],
    vel: float = DEFAULT_VELOCITY,
    acc: float = DEFAULT_ACCELERATION,
) -> None:
    # TCP 직선 이동. 집기/삽입처럼 경로 자체가 중요한 구간에 사용.
    target_pose = pose(pose_values)
    node.get_logger().info(f"MoveL start: {name} -> {target_pose} @ vel={vel}, acc={acc}")
    movel(posx(target_pose), vel=vel, acc=acc)
    wait(DEFAULT_WAIT)


def move_up_from_current(
    node,
    get_current_posx,
    movel,
    posx,
    wait,
    dr_base,
    z_offset: float = DEFAULT_HOME_Z_OFFSET,
) -> None:
    # 현재 TCP 자세에서 base Z 방향으로 먼저 들어 올린 뒤 홈으로 가기 위한 준비 동작.
    node.get_logger().info(f"Move up {z_offset:.1f} mm from current TCP pose")
    current_pose = normalize_pose(get_current_posx(ref=dr_base))
    target_pose = current_pose.copy()
    target_pose[2] += float(z_offset)

    node.get_logger().info(
        f"Current pose z={current_pose[2]:.3f} -> target z={target_pose[2]:.3f}"
    )
    movel(posx(target_pose), vel=DEFAULT_VELOCITY, acc=DEFAULT_ACCELERATION)
    wait(DEFAULT_WAIT)


def go_home(
    node,
    set_digital_outputs,
    wait,
    get_current_posx,
    movel,
    movej,
    posx,
    posj,
    dr_base,
) -> None:
    # 기본 홈 복귀 절차: 그리퍼 열기 -> 현재 위치에서 위로 상승 -> 홈 조인트 이동.
    node.get_logger().info("Step 1/3: open gripper")
    gripper_command(
        node,
        set_digital_outputs,
        wait,
        "HOME_RETURN_OPEN_0100",
        GRIPPER_HOME_PREPARE,
    )

    node.get_logger().info("Step 2/3: move up before home")
    move_up_from_current(
        node=node,
        get_current_posx=get_current_posx,
        movel=movel,
        posx=posx,
        wait=wait,
        dr_base=dr_base,
    )

    node.get_logger().info(f"Step 3/3: move to home joint {HOME_JOINT}")
    prepare_home_joint(node, set_digital_outputs, wait)
    movej(posj(HOME_JOINT), vel=DEFAULT_VELOCITY, acc=DEFAULT_ACCELERATION)
    wait(DEFAULT_WAIT)
