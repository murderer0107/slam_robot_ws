"""Common helpers for tray soil service action nodes."""

from __future__ import annotations

from robot_tests.compliance_common import extract_fz, safe_release_compliance
from robot_tests.motion_primitives import (
    GRIPPER_HOME_PREPARE,
    GRIPPER_PICK_CLOSE,
    HOME_JOINT,
    gripper_command,
    move_j,
    move_l,
    normalize_pose,
    prepare_home_joint,
)
from robot_tests.robot_motion_data import (
    SOIL_SHOVEL_PICKUP_POSE,
    SOIL_SHOVEL_PICKUP_TOP_POSE,
    SOIL_SUPPLY_BOX_SCOOP_POSE,
    SOIL_SUPPLY_BOX_TOP_POSE,
    SOIL_WASTE_BOX_DUMP_POSE,
    SOIL_WASTE_BOX_TOP_POSE,
    TRAY_CORNERS_XYZ,
    TRAY_ROCK_PICK_Z_OFFSET,
    TRAY_SOIL_ACC,
    TRAY_SOIL_ADD_DROP_Z_OFFSET,
    TRAY_SOIL_ADD_TARGET_NAMES,
    TRAY_SOIL_CONTACT_DELTA_FZ,
    TRAY_SOIL_MAX_DOWN_DISTANCE,
    TRAY_SOIL_PROBE_ACC,
    TRAY_SOIL_PROBE_VEL,
    TRAY_SOIL_REMOVE_SCOOP_Z_OFFSET,
    TRAY_SOIL_REMOVE_TARGET_NAMES,
    TRAY_SOIL_TOP_POSES,
    TRAY_SOIL_VEL,
)
from robot_tests.tray_soil_state_check_node import classify_tray_result, describe_soil_state, log_classification_result


def prompt_choice(prompt: str, valid_values: list[str]) -> str:
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
    return prompt_choice("\n작업할 트레이 선택 [A/B/C/D], 종료 [q]: ", ["A", "B", "C", "D"]).upper()


def import_soil_service_apis(node):
    try:
        from DSR_ROBOT2 import (
            DR_BASE,
            amovel,
            check_motion,
            get_current_posx,
            get_tool_force,
            movej,
            movel,
            release_compliance_ctrl,
            set_tcp,
            set_tool,
            task_compliance_ctrl,
            wait,
        )
        from DR_common2 import posj, posx
    except ImportError as exc:
        node.get_logger().error(f"Failed to import Doosan API: {exc}")
        node.destroy_node()
        raise

    return {
        "DR_BASE": DR_BASE,
        "amovel": amovel,
        "check_motion": check_motion,
        "get_current_posx": get_current_posx,
        "get_tool_force": get_tool_force,
        "movej": movej,
        "movel": movel,
        "posj": posj,
        "posx": posx,
        "release_compliance_ctrl": release_compliance_ctrl,
        "set_tcp": set_tcp,
        "set_tool": set_tool,
        "task_compliance_ctrl": task_compliance_ctrl,
        "wait": wait,
    }


def make_pose(posx_fn, x: float, y: float, z: float, rx: float, ry: float, rz: float):
    return posx_fn(float(x), float(y), float(z), float(rx), float(ry), float(rz))


def make_tray_pose(posx_fn, tray_name: str, x: float, y: float, z: float):
    tray_top_pose = normalize_pose(TRAY_SOIL_TOP_POSES[tray_name])
    return make_pose(posx_fn, x, y, z, tray_top_pose[3], tray_top_pose[4], tray_top_pose[5])


def corner_xyz_map(tray_name: str) -> dict[str, tuple[float, float, float]]:
    return {corner_name: xyz for corner_name, xyz in TRAY_CORNERS_XYZ[tray_name]}


def build_corner_pose(posx_fn, tray_name: str, corner_name: str, target_z: float | None = None):
    x, y, default_z = corner_xyz_map(tray_name)[corner_name]
    z = default_z if target_z is None else target_z
    return make_tray_pose(posx_fn, tray_name, x, y, z)


def go_home_with_gripper_held(node, apis) -> None:
    node.get_logger().info("Move up before home while keeping current gripper state")
    current_pose = normalize_pose(apis["get_current_posx"](ref=apis["DR_BASE"]))
    target_pose = current_pose.copy()
    target_pose[2] += 120.0
    apis["movel"](apis["posx"](target_pose), vel=60.0, acc=60.0)
    apis["wait"](0.5)

    node.get_logger().info(f"Move to home joint {HOME_JOINT}")
    apis["movej"](apis["posj"](HOME_JOINT), vel=60.0, acc=60.0)
    apis["wait"](0.5)


def inspect_tray_soil(node, apis, tray_name: str) -> dict:
    def move_line(name: str, target, vel: float = TRAY_SOIL_VEL, acc: float = TRAY_SOIL_ACC, sleep: float = 1.0):
        node.get_logger().info(f"Move start: {name} -> {target}")
        ret = apis["movel"](target, vel=vel, acc=acc)
        node.get_logger().info(f"Move ret: {name} = {ret}")
        apis["wait"](sleep)

    def return_to_pose(name: str, pose_values: list[float]) -> None:
        node.get_logger().info(f"Return to {name}")
        apis["movel"](apis["posx"](pose_values), vel=TRAY_SOIL_PROBE_VEL, acc=TRAY_SOIL_PROBE_ACC)
        apis["wait"](1.0)

    def compliance_probe_down(corner_name: str, top_pose_values: list[float]):
        start_pose = normalize_pose(apis["get_current_posx"](ref=apis["DR_BASE"]))
        start_z = start_pose[2]
        limit_z = start_z - TRAY_SOIL_MAX_DOWN_DISTANCE
        limit_pose = start_pose.copy()
        limit_pose[2] = limit_z

        node.get_logger().info(
            f"{tray_name}_{corner_name} compliance down start_z={start_z:.3f}, "
            f"limit_z={limit_z:.3f}, delta_fz={TRAY_SOIL_CONTACT_DELTA_FZ}"
        )

        apis["task_compliance_ctrl"]()
        apis["wait"](0.5)
        base_fz = extract_fz(apis["get_tool_force"](ref=apis["DR_BASE"]))
        node.get_logger().info(f"{tray_name}_{corner_name} base_fz={base_fz:.3f}")

        contact_detected = False
        current_z = start_z

        apis["amovel"](apis["posx"](limit_pose), vel=TRAY_SOIL_PROBE_VEL, acc=TRAY_SOIL_PROBE_ACC)

        while apis["check_motion"]() == 2:
            apis["wait"](0.05)
            current_pose = normalize_pose(apis["get_current_posx"](ref=apis["DR_BASE"]))
            current_z = current_pose[2]
            current_fz = extract_fz(apis["get_tool_force"](ref=apis["DR_BASE"]))
            delta_fz = abs(current_fz - base_fz)

            if delta_fz >= TRAY_SOIL_CONTACT_DELTA_FZ:
                node.get_logger().info(
                    f"{tray_name}_{corner_name} contact detected z={current_z:.3f}"
                )
                contact_detected = True
                break

        if not contact_detected:
            current_pose = normalize_pose(apis["get_current_posx"](ref=apis["DR_BASE"]))
            current_z = current_pose[2]
            node.get_logger().warn(
                f"{tray_name}_{corner_name} contact failed, limit reached z={current_z:.3f}"
            )

        safe_release_compliance(node, apis["release_compliance_ctrl"])
        return_to_pose(f"{tray_name}_{corner_name}_TOP", top_pose_values)

        if not contact_detected:
            return None
        return current_z

    tray_top_pose = normalize_pose(TRAY_SOIL_TOP_POSES[tray_name])
    move_line(f"{tray_name}_CENTER_TOP", apis["posx"](tray_top_pose))

    corner_results = []
    for corner_name, (x, y, z) in TRAY_CORNERS_XYZ[tray_name]:
        top_pose = make_tray_pose(apis["posx"], tray_name, x, y, z)
        move_line(
            f"{tray_name}_{corner_name}_TOP",
            top_pose,
            vel=TRAY_SOIL_VEL,
            acc=TRAY_SOIL_ACC,
            sleep=0.5,
        )
        contact_z = compliance_probe_down(corner_name, normalize_pose(top_pose))
        corner_results.append(
            {
                "name": corner_name,
                "x": float(x),
                "y": float(y),
                "z": contact_z,
            }
        )

    result = classify_tray_result(corner_results)
    log_classification_result(node, result)
    move_line(f"{tray_name}_CENTER_TOP_RETURN", apis["posx"](tray_top_pose))
    return result


def require_soil_state(node, result: dict, expected_state: str) -> bool:
    actual = result["soil_state"]
    if actual != expected_state:
        node.get_logger().warn(
            f"Expected {expected_state}, but tray result is {actual} ({describe_soil_state(actual)})"
        )
        return False
    return True


def require_rock_candidate(node, result: dict) -> bool:
    candidates = result["obstacle_candidates"]
    if not candidates:
        node.get_logger().warn("No rock candidate found. Nothing to remove.")
        return False
    return True


def pickup_shovel(node, apis, set_digital_outputs) -> None:
    node.get_logger().info("Pickup shovel start")
    prepare_home_joint(node, set_digital_outputs, apis["wait"])
    move_j(node, apis["movej"], apis["posj"], apis["wait"], "HOME", HOME_JOINT)
    move_l(node, apis["movel"], apis["posx"], apis["wait"], "SHOVEL_TOP", SOIL_SHOVEL_PICKUP_TOP_POSE)
    gripper_command(
        node,
        set_digital_outputs,
        apis["wait"],
        "SHOVEL_OPEN_0100",
        GRIPPER_HOME_PREPARE,
    )
    move_l(node, apis["movel"], apis["posx"], apis["wait"], "SHOVEL_PICK", SOIL_SHOVEL_PICKUP_POSE)
    gripper_command(
        node,
        set_digital_outputs,
        apis["wait"],
        "SHOVEL_GRIP_0010",
        GRIPPER_PICK_CLOSE,
    )
    move_l(
        node,
        apis["movel"],
        apis["posx"],
        apis["wait"],
        "SHOVEL_TOP_RETURN",
        SOIL_SHOVEL_PICKUP_TOP_POSE,
    )


def return_shovel(node, apis, set_digital_outputs) -> None:
    node.get_logger().info("Return shovel start")
    move_l(node, apis["movel"], apis["posx"], apis["wait"], "SHOVEL_RETURN_TOP", SOIL_SHOVEL_PICKUP_TOP_POSE)
    move_l(node, apis["movel"], apis["posx"], apis["wait"], "SHOVEL_RETURN_DOWN", SOIL_SHOVEL_PICKUP_POSE)
    gripper_command(
        node,
        set_digital_outputs,
        apis["wait"],
        "SHOVEL_RELEASE_0100",
        GRIPPER_HOME_PREPARE,
    )
    move_l(
        node,
        apis["movel"],
        apis["posx"],
        apis["wait"],
        "SHOVEL_RETURN_TOP_EXIT",
        SOIL_SHOVEL_PICKUP_TOP_POSE,
    )
    prepare_home_joint(node, set_digital_outputs, apis["wait"])
    move_j(node, apis["movej"], apis["posj"], apis["wait"], "HOME_RETURN", HOME_JOINT)


def select_target_corners(tray_name: str, result: dict, target_names: tuple[str, ...]) -> list[dict]:
    corner_lookup = {corner["name"]: dict(corner) for corner in result["valid_corners"]}
    xyz_lookup = corner_xyz_map(tray_name)
    avg_z = result["avg_z"]
    selected = []

    for name in target_names:
        if name in corner_lookup:
            selected.append(corner_lookup[name])
            continue

        x, y, _ = xyz_lookup[name]
        selected.append(
            {
                "name": name,
                "x": float(x),
                "y": float(y),
                "z": avg_z,
            }
        )
    return selected


def fill_shovel_from_supply(node, apis) -> None:
    move_l(node, apis["movel"], apis["posx"], apis["wait"], "SUPPLY_BOX_TOP", SOIL_SUPPLY_BOX_TOP_POSE)
    move_l(node, apis["movel"], apis["posx"], apis["wait"], "SUPPLY_BOX_SCOOP", SOIL_SUPPLY_BOX_SCOOP_POSE)
    apis["wait"](0.5)
    move_l(
        node,
        apis["movel"],
        apis["posx"],
        apis["wait"],
        "SUPPLY_BOX_TOP_RETURN",
        SOIL_SUPPLY_BOX_TOP_POSE,
    )


def dump_to_waste_box(node, apis) -> None:
    move_l(node, apis["movel"], apis["posx"], apis["wait"], "WASTE_BOX_TOP", SOIL_WASTE_BOX_TOP_POSE)
    move_l(node, apis["movel"], apis["posx"], apis["wait"], "WASTE_BOX_DUMP", SOIL_WASTE_BOX_DUMP_POSE)
    apis["wait"](0.5)
    move_l(
        node,
        apis["movel"],
        apis["posx"],
        apis["wait"],
        "WASTE_BOX_TOP_RETURN",
        SOIL_WASTE_BOX_TOP_POSE,
    )


def run_soil_add_action(node, apis, set_digital_outputs, tray_name: str, result: dict) -> None:
    targets = select_target_corners(tray_name, result, TRAY_SOIL_ADD_TARGET_NAMES)
    pickup_shovel(node, apis, set_digital_outputs)

    for index, target in enumerate(targets, start=1):
        node.get_logger().info(f"Soil add cycle {index}/2 target={target['name']}")
        fill_shovel_from_supply(node, apis)

        approach_pose = build_corner_pose(apis["posx"], tray_name, target["name"])
        drop_z = (target["z"] if target["z"] is not None else result["avg_z"]) + TRAY_SOIL_ADD_DROP_Z_OFFSET
        drop_pose = build_corner_pose(apis["posx"], tray_name, target["name"], target_z=drop_z)

        move_l(node, apis["movel"], apis["posx"], apis["wait"], f"{target['name']}_APPROACH", normalize_pose(approach_pose))
        move_l(node, apis["movel"], apis["posx"], apis["wait"], f"{target['name']}_DROP", normalize_pose(drop_pose))
        apis["wait"](0.5)
        move_l(
            node,
            apis["movel"],
            apis["posx"],
            apis["wait"],
            f"{target['name']}_APPROACH_RETURN",
            normalize_pose(approach_pose),
        )

    return_shovel(node, apis, set_digital_outputs)


def run_soil_keep_action(node, tray_name: str, result: dict) -> None:
    node.get_logger().info(
        f"Tray {tray_name} soil state is OK. No action needed. avg_z={result['avg_z']}"
    )


def run_soil_remove_action(node, apis, set_digital_outputs, tray_name: str, result: dict) -> None:
    targets = select_target_corners(tray_name, result, TRAY_SOIL_REMOVE_TARGET_NAMES)
    pickup_shovel(node, apis, set_digital_outputs)

    for index, target in enumerate(targets, start=1):
        node.get_logger().info(f"Soil remove cycle {index}/2 target={target['name']}")

        approach_pose = build_corner_pose(apis["posx"], tray_name, target["name"])
        scoop_z = (target["z"] if target["z"] is not None else result["avg_z"]) + TRAY_SOIL_REMOVE_SCOOP_Z_OFFSET
        scoop_pose = build_corner_pose(apis["posx"], tray_name, target["name"], target_z=scoop_z)

        move_l(node, apis["movel"], apis["posx"], apis["wait"], f"{target['name']}_APPROACH", normalize_pose(approach_pose))
        move_l(node, apis["movel"], apis["posx"], apis["wait"], f"{target['name']}_SCOOP", normalize_pose(scoop_pose))
        apis["wait"](0.5)
        move_l(
            node,
            apis["movel"],
            apis["posx"],
            apis["wait"],
            f"{target['name']}_APPROACH_RETURN",
            normalize_pose(approach_pose),
        )
        dump_to_waste_box(node, apis)

    return_shovel(node, apis, set_digital_outputs)


def run_rock_remove_action(node, apis, set_digital_outputs, tray_name: str, result: dict) -> None:
    gripper_command(
        node,
        set_digital_outputs,
        apis["wait"],
        "ROCK_PICK_PREPARE_OPEN_0100",
        GRIPPER_HOME_PREPARE,
    )

    for candidate in result["obstacle_candidates"]:
        corner_name = candidate["name"]
        node.get_logger().info(f"Rock remove attempt at {corner_name}")

        approach_pose = build_corner_pose(apis["posx"], tray_name, corner_name)
        pick_z = candidate["z"] + TRAY_ROCK_PICK_Z_OFFSET
        pick_pose = build_corner_pose(apis["posx"], tray_name, corner_name, target_z=pick_z)

        move_l(node, apis["movel"], apis["posx"], apis["wait"], f"{corner_name}_APPROACH", normalize_pose(approach_pose))
        move_l(node, apis["movel"], apis["posx"], apis["wait"], f"{corner_name}_ROCK_PICK", normalize_pose(pick_pose))
        gripper_command(
            node,
            set_digital_outputs,
            apis["wait"],
            f"{corner_name}_ROCK_GRIP_0010",
            GRIPPER_PICK_CLOSE,
        )
        move_l(
            node,
            apis["movel"],
            apis["posx"],
            apis["wait"],
            f"{corner_name}_APPROACH_RETURN",
            normalize_pose(approach_pose),
        )
        dump_to_waste_box(node, apis)
        gripper_command(
            node,
            set_digital_outputs,
            apis["wait"],
            f"{corner_name}_ROCK_RELEASE_0100",
            GRIPPER_HOME_PREPARE,
        )

    prepare_home_joint(node, set_digital_outputs, apis["wait"])
    move_j(node, apis["movej"], apis["posj"], apis["wait"], "HOME_RETURN", HOME_JOINT)
