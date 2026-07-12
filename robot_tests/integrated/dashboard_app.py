"""Integrated SmartFarm dashboard shell."""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QProcess, QTimer

from robot_tests.integrated import config
from robot_tests.integrated.dashboard_logic import IntegratedDashboardLogic
from robot_tests.integrated.ros_runner import RosNodeRunner


class IntegratedDashboard(QtWidgets.QMainWindow):
    """PyQt dashboard that orchestrates existing `robot_tests` nodes."""

    TRAY_FRAME_STYLES = {
        config.SOIL_STATUS_UNKNOWN: ("#f3f4f6", "#9ca3af"),
        config.SOIL_STATUS_OK: ("#f0fdf4", "#6bbf7a"),
        config.SOIL_STATUS_LOW: ("#fffbea", "#e0b84f"),
        config.SOIL_STATUS_HIGH: ("#fffbea", "#e0b84f"),
        config.SOIL_STATUS_OBSTACLE: ("#fff1f2", "#ef6b73"),
        config.SOIL_STATUS_FAILED: ("#fff1f2", "#ef6b73"),
    }

    TRAY_STATE_TEXT_COLORS = {
        config.SOIL_STATUS_UNKNOWN: "#6b7280",
        config.SOIL_STATUS_OK: "#0b6b20",
        config.SOIL_STATUS_LOW: "#b7791f",
        config.SOIL_STATUS_HIGH: "#b7791f",
        config.SOIL_STATUS_OBSTACLE: "#d60000",
        config.SOIL_STATUS_FAILED: "#d60000",
    }

    def __init__(self, ui_path: str | None = None) -> None:
        super().__init__()
        self.logic = IntegratedDashboardLogic()
        self.runner = RosNodeRunner(self)
        self.pending_task: tuple[str, str] | None = None
        self.ros_status_process: QProcess | None = None

        resolved_ui_path = self.resolve_ui_path(ui_path)
        if resolved_ui_path is None:
            raise FileNotFoundError("No SmartFarm dashboard .ui file found")

        uic.loadUi(str(resolved_ui_path), self)
        self.initialize_state()
        self.connect_signals()
        self.start_ros_connection_monitor()
        self.write_log("Integrated dashboard initialized")
        self.runner.start_manual_server()

    def resolve_ui_path(self, ui_path: str | None) -> Path | None:
        candidates = []
        if ui_path:
            candidates.append(Path(ui_path))

        current_dir = Path(__file__).resolve().parent
        candidates.append(current_dir / "smartfarm_dashboard.ui")

        for candidate in config.UI_PATH_CANDIDATES:
            candidates.append(Path(candidate))

        for candidate in candidates:
            if candidate.is_file():
                return candidate
        return None

    def closeEvent(self, event) -> None:
        """Prevent UI shutdown while a robot task or node handoff is active."""
        if self.logic.is_busy:
            event.ignore()
            self.write_log("로봇 동작 중 UI 종료 요청 차단")
            QtWidgets.QMessageBox.warning(
                self,
                "종료할 수 없음",
                "로봇 동작이 진행 중입니다. 작업이 완료된 후 UI를 종료하세요.",
            )
            return
        event.accept()

    def initialize_state(self) -> None:
        self.set_label("lbl_robot_status", "대기 중")
        self.set_label("lbl_ros_status", "Disconnected")

        # 물리 긴급정지 상태 연동 전까지 UI 버튼만 숨긴다. 긴급정지
        # 노드와 처리 코드는 추후 상태 감지 연동을 위해 유지한다.
        estop_button = getattr(self, "btn_estop", None)
        if estop_button is not None:
            estop_button.hide()

        for tray_label in config.TRAY_LABELS:
            self.update_tray_widgets(tray_label)

        if hasattr(self, "txt_log"):
            self.txt_log.clear()
            self.txt_log.setReadOnly(True)

        self.refresh_button_state()

    def connect_signals(self) -> None:
        self.connect_button("btn_start", self.start_system)
        self.connect_button("btn_shutdown", self.shutdown_system)
        self.connect_button("btn_home", self.run_home)
        self.connect_button("btn_estop", self.emergency_stop)
        self.connect_button("btn_recovery", self.recover_from_estop)
        self.connect_button("btn_press_pickup", self.run_press_pickup)
        self.connect_button("btn_press_putdown", self.run_press_putdown)
        self.connect_button("btn_shovel_pickup", self.run_shovel_pickup)
        self.connect_button("btn_shovel_putdown", self.run_shovel_putdown)
        self.connect_button("btn_move_joint", self.run_move_joint)
        self.connect_button("btn_read_joint", self.run_read_joint)
        self.connect_button("btn_move_base", self.run_move_base)
        self.connect_button("btn_read_base", self.run_read_base)

        for index, tray_label in enumerate(config.TRAY_LABELS, start=1):
            self.connect_button(
                f"btn_tray{index}_check",
                lambda _checked=False, tray=tray_label: self.run_measure(tray),
            )
            self.connect_button(
                f"btn_tray{index}_next",
                lambda _checked=False, tray=tray_label: self.run_next_action(tray),
            )
            self.connect_button(
                f"btn_tray{index}_reset",
                lambda _checked=False, tray=tray_label: self.reset_tray(tray),
            )

    def connect_button(self, object_name: str, callback) -> None:
        button = getattr(self, object_name, None)
        if button is not None:
            button.clicked.connect(callback)

    def set_label(self, object_name: str, text: str) -> None:
        label = getattr(self, object_name, None)
        if label is not None:
            label.setText(str(text))

    def write_log(self, text: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        message = f"[{timestamp}] {text}"
        if hasattr(self, "txt_log"):
            self.txt_log.append(message)

    def run_after_inter_node_delay(
        self,
        callback,
        *,
        reason: str = "",
        delay_ms: int | None = None,
    ) -> None:
        delay_ms = int(config.INTER_NODE_DELAY_MS if delay_ms is None else delay_ms)
        if reason:
            self.write_log(f"{reason} 후 {delay_ms}ms 대기")
        QTimer.singleShot(delay_ms, callback)

    def start_ros_connection_monitor(self) -> None:
        self.ros_status_timer = QTimer(self)
        self.ros_status_timer.setInterval(2000)
        self.ros_status_timer.timeout.connect(self.refresh_ros_connection_status)
        self.ros_status_timer.start()
        self.refresh_ros_connection_status()

    def refresh_ros_connection_status(self) -> None:
        if self.ros_status_process is not None and self.ros_status_process.state() != QProcess.NotRunning:
            return

        process = QProcess(self)
        process.setProgram("/bin/bash")
        setup_path = Path(config.WORKSPACE_SETUP_PATH)
        shell_cmd = (
            f"source '{setup_path}' && "
            f"ros2 service type '{config.ROS_CONNECTION_CHECK_SERVICE}' >/dev/null 2>&1"
        )
        process.setArguments(["-lc", shell_cmd])
        process.finished.connect(
            lambda exit_code, _exit_status, proc=process: self.handle_ros_status_finished(proc, exit_code)
        )
        process.start()
        self.ros_status_process = process

    def handle_ros_status_finished(self, process: QProcess, exit_code: int) -> None:
        if self.ros_status_process is process:
            self.ros_status_process = None

        connected = exit_code == 0
        self.logic.ros_connected = connected
        self.set_label("lbl_ros_status", "Connected" if connected else "Disconnected")
        self.refresh_button_state()

    def show_emergency_popup(self) -> None:
        message_box = QtWidgets.QMessageBox(self)
        message_box.setIcon(QtWidgets.QMessageBox.Critical)
        message_box.setWindowTitle("긴급정지")
        message_box.setText("긴급정지 하였습니다. 사용자가 상황을 확인하세요")
        message_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
        message_box.setDefaultButton(QtWidgets.QMessageBox.Ok)
        message_box.exec_()

    def update_tray_widgets(self, tray_label: str) -> None:
        tray = self.logic.tray_state[tray_label]
        idx = config.TRAY_LABELS.index(tray_label) + 1
        next_action = self.logic.get_next_action(tray_label)
        self.set_label(f"lbl_tray{idx}_state", tray.soil_status)
        self.set_label(f"lbl_tray{idx}_next_action", next_action)
        next_button = getattr(self, f"btn_tray{idx}_next", None)
        if next_button is not None:
            is_initial_state = (
                tray.soil_status == config.SOIL_STATUS_UNKNOWN
                and tray.work_phase == config.WORK_PHASE_IDLE
                and not tray.last_measurement
            )
            next_button.setText(
                config.NEXT_BUTTON_DEFAULT_TEXT if is_initial_state else next_action
            )
        self.update_tray_frame_color(idx, tray.soil_status)
        self.update_tray_state_text_color(idx, tray.soil_status)

    def update_tray_frame_color(self, idx: int, soil_status: str) -> None:
        frame = getattr(self, f"frame_tray{idx}", None)
        if frame is None:
            return

        background, border = self.TRAY_FRAME_STYLES.get(
            soil_status,
            self.TRAY_FRAME_STYLES[config.SOIL_STATUS_UNKNOWN],
        )
        frame.setStyleSheet(
            f"QFrame{{background:{background}; border:1px solid {border}; border-radius:12px;}}"
        )

    def update_tray_state_text_color(self, idx: int, soil_status: str) -> None:
        label = getattr(self, f"lbl_tray{idx}_state", None)
        if label is None:
            return

        color = self.TRAY_STATE_TEXT_COLORS.get(soil_status, "#1f2937")
        label.setStyleSheet(f"border:none; font-size:15px; font-weight:800; color:{color};")

    def refresh_button_state(self) -> None:
        if not self.logic.system_started:
            enabled = {"btn_start"}
            for button in self.findChildren(QtWidgets.QPushButton):
                button.setEnabled(button.objectName() in enabled)
            return

        busy = self.logic.is_busy
        estop = self.logic.is_emergency_stopped
        requires_home = self.logic.requires_home_after_estop
        tool_state = self.logic.current_tool_state
        ros_connected = self.logic.ros_connected

        # 자동/수동 로봇 작업이 실행 중일 때는 중복 명령이나 상태 변경이 들어오지
        # 않도록 화면의 모든 버튼을 잠근다. 작업 종료/실패 처리에서 is_busy가
        # 해제되면 현재 시스템 상태에 맞는 버튼들이 다시 활성화된다.
        if busy and not estop:
            enabled = set()
        elif estop or requires_home:
            enabled = {"btn_home", "btn_recovery"}
        else:
            enabled = {
                "btn_recovery",
                "btn_shutdown",
            }
            if ros_connected and not busy:
                enabled.update(
                    {
                        "btn_home",
                        "btn_move_joint",
                        "btn_read_joint",
                        "btn_move_base",
                        "btn_read_base",
                        "btn_press_putdown",
                        "btn_shovel_putdown",
                    }
                )
                if tool_state in (config.TOOL_STATE_NONE, config.TOOL_STATE_UNKNOWN):
                    enabled.update(
                        {
                            "btn_press_pickup",
                            "btn_shovel_pickup",
                        }
                    )
                for idx in range(1, 5):
                    tray_label = config.TRAY_LABELS[idx - 1]
                    enabled.add(f"btn_tray{idx}_reset")
                    if self.logic.get_next_action(tray_label) == config.NEXT_ACTION_DONE:
                        continue
                    enabled.add(f"btn_tray{idx}_check")
                    tray = self.logic.tray_state[tray_label]
                    if tray.soil_status not in (
                        config.SOIL_STATUS_UNKNOWN,
                        config.SOIL_STATUS_FAILED,
                    ):
                        enabled.add(f"btn_tray{idx}_next")

        for button in self.findChildren(QtWidgets.QPushButton):
            button.setEnabled(button.objectName() in enabled)

    def lock_for_task(self, task_name: str, tray_label: str) -> None:
        self.logic.is_busy = True
        self.logic.current_running_task = task_name
        self.logic.current_running_tray = tray_label
        self.set_label("lbl_robot_status", f"{tray_label} {task_name} 실행 중")
        self.refresh_button_state()

    def unlock_after_task(self) -> None:
        self.logic.is_busy = False
        self.logic.current_running_task = ""
        self.logic.current_running_tray = ""
        if self.logic.requires_home_after_estop:
            self.set_label("lbl_robot_status", "HOME 필요")
            self.refresh_button_state()
            return
        self.set_label("lbl_robot_status", "대기 중")
        self.refresh_button_state()

    def run_measure(self, tray_label: str) -> None:
        if self.logic.is_busy or not self.logic.ros_connected:
            return
        if self.logic.current_tool_state == config.TOOL_STATE_UNKNOWN:
            self.write_log("현재 툴 상태 UNKNOWN - 자동 토양 측정 금지")
            return
        if self.logic.current_tool_state != config.TOOL_STATE_PRESS:
            self.pending_task = ("measure", tray_label)
            self.lock_for_task("PRESS_PLATE_PICKUP", tray_label)
            self.write_log("누름판 미보유 상태 - pickup 먼저 실행")
            self.runner.start_node(config.PRESS_PICKUP_NODE)
            return
        self._start_measure_task(tray_label)

    def _start_measure_task(self, tray_label: str) -> None:
        self.lock_for_task(config.NEXT_ACTION_MEASURE, tray_label)
        self.write_log(f"{tray_label} 트레이 토양 측정 시작")
        self.runner.start_node(
            config.MEASURE_NODE,
            node_args=[
                "--tray",
                tray_label,
                "--skip-initial-home",
            ],
        )

    def run_corrective_action(self, tray_label: str) -> None:
        if self.logic.is_busy or not self.logic.ros_connected:
            return
        if self.logic.current_tool_state == config.TOOL_STATE_UNKNOWN:
            self.write_log("현재 툴 상태 UNKNOWN - 자동 보정 작업 금지")
            return
        if self.logic.current_tool_state == config.TOOL_STATE_PRESS:
            self.pending_task = ("next", tray_label)
            self.lock_for_task("PRESS_PLATE_PUTDOWN", tray_label)
            self.write_log("보정 작업 전 누름판 putdown 먼저 실행")
            self.runner.start_node(
                config.PRESS_PUTDOWN_NODE,
                node_args=["--skip-initial-home"],
            )
            return
        # 대시보드의 이전 자동 작업은 HOME 복귀 후 종료한다. 보정 노드에서 다시
        # TCP를 120 mm 상승시키면 불필요한 중복 동작과 위치 조회 대기가 발생한다.
        self._start_next_step_task(tray_label, skip_initial_home=True)

    def run_flatten_action(self, tray_label: str) -> None:
        if self.logic.is_busy or not self.logic.ros_connected:
            return
        if self.logic.current_tool_state == config.TOOL_STATE_UNKNOWN:
            self.write_log("현재 툴 상태 UNKNOWN - 자동 평탄화 금지")
            return
        if self.logic.current_tool_state == config.TOOL_STATE_SHOVEL:
            self.pending_task = ("flatten_press_pickup", tray_label)
            self.lock_for_task("SHOVEL_PUTDOWN", tray_label)
            self.write_log("평탄화 전 삽 putdown 먼저 실행")
            self.runner.start_node(config.SHOVEL_PUTDOWN_NODE)
            return
        tray = self.logic.tray_state[tray_label]
        if tray.work_phase == config.WORK_PHASE_AFTER_CORRECTION:
            # 보정 노드는 삽을 반환하고 빈 그리퍼로 끝나는 것이 정상 흐름이다.
            # 이전 상태가 잘못 남았더라도 평탄화 전에 누름판 pickup을 확실히 수행한다.
            self.logic.set_tool_state(config.TOOL_STATE_NONE)
            self.pending_task = ("flatten", tray_label)
            self.lock_for_task("PRESS_PLATE_PICKUP", tray_label)
            self.write_log("보정 완료 후 평탄화 - 누름판 pickup 강제 실행")
            self.runner.start_node(config.PRESS_PICKUP_NODE)
            return
        if self.logic.current_tool_state != config.TOOL_STATE_PRESS:
            self.pending_task = ("flatten", tray_label)
            self.lock_for_task("PRESS_PLATE_PICKUP", tray_label)
            self.write_log("평탄화 전 누름판 pickup 먼저 실행")
            self.runner.start_node(config.PRESS_PICKUP_NODE)
            return
        self._start_flatten_task(tray_label)

    def _start_flatten_task(self, tray_label: str) -> None:
        self.lock_for_task(config.NEXT_ACTION_FLATTEN, tray_label)
        self.write_log(f"{tray_label} 트레이 전용 평탄화 노드 시작")
        self.runner.start_node(
            config.INTEGRATED_FLATTEN_NODE,
            node_args=["--tray", tray_label],
        )

    def run_next_action(self, tray_label: str) -> None:
        next_action = self.logic.get_next_action(tray_label)
        if next_action == config.NEXT_ACTION_MEASURE:
            self.run_measure(tray_label)
        elif next_action in (
            config.NEXT_ACTION_ADD_SOIL,
            config.NEXT_ACTION_REMOVE_SOIL,
            config.NEXT_ACTION_REMOVE_ROCK,
        ):
            self.run_corrective_action(tray_label)
        elif next_action == config.NEXT_ACTION_FLATTEN:
            self.run_flatten_action(tray_label)
        elif next_action == config.NEXT_ACTION_PLANT:
            if self.logic.is_busy or not self.logic.ros_connected:
                return
            if self.logic.current_tool_state == config.TOOL_STATE_UNKNOWN:
                self.write_log("현재 툴 상태 UNKNOWN - 자동 식물 심기 금지")
                return
            if self.logic.current_tool_state == config.TOOL_STATE_PRESS:
                self.pending_task = ("next", tray_label)
                self.lock_for_task("PRESS_PLATE_PUTDOWN", tray_label)
                self.write_log("식물 심기 전 누름판 putdown 먼저 실행")
                self.runner.start_node(
                    config.PRESS_PUTDOWN_NODE,
                    node_args=["--skip-initial-home"],
                )
                return
            self._start_next_step_task(tray_label)
        else:
            self.write_log(f"{tray_label} 트레이는 완료 상태")

    def reset_tray(self, tray_label: str) -> None:
        if self.logic.is_busy:
            return
        self.logic.reset_tray(tray_label)
        self.update_tray_widgets(tray_label)
        self.write_log(f"{tray_label} 트레이 리셋 - 초기 상태로 복원")
        self.refresh_button_state()

    def _start_next_step_task(
        self,
        tray_label: str,
        *,
        skip_initial_home: bool = False,
    ) -> None:
        tray = self.logic.tray_state[tray_label]
        next_action = self.logic.get_next_action(tray_label)
        node_args = [
            "--tray",
            tray_label,
            "--soil-status",
            tray.soil_status,
            "--next-action",
            next_action,
        ]
        if skip_initial_home:
            node_args.append("--skip-initial-home")
        if next_action == config.NEXT_ACTION_PLANT:
            node_args.extend(["--plant", str(config.TRAY_TO_PLANT_INDEX[tray_label])])
        if tray.last_measurement:
            node_args.extend(
                [
                    "--measurement-json",
                    json.dumps(tray.last_measurement, ensure_ascii=False, separators=(",", ":")),
                ]
            )
        self.lock_for_task(next_action, tray_label)
        self.write_log(
            f"{tray_label} 트레이 다음 작업 시작 "
            f"(soil={tray.soil_status}, next={next_action})"
        )
        self.runner.start_node(config.INTEGRATED_NEXT_STEP_NODE, node_args=node_args)

    def run_read_joint(self) -> None:
        if self.logic.is_busy:
            return
        self.lock_for_task("READ_JOINT", "-")
        self.write_log("현재 joint 값 읽기")
        self.runner.send_manual_command({"mode": "read-joint"})

    def run_move_joint(self) -> None:
        if self.logic.is_busy:
            return
        joints = [getattr(self, f"spin_j{idx}").value() for idx in range(1, 7)]
        self.lock_for_task("MOVE_JOINT", "-")
        self.write_log(f"Joint 이동 시작 {joints}")
        self.runner.send_manual_command({"mode": "move-joint", "joints": joints})

    def run_read_base(self) -> None:
        if self.logic.is_busy:
            return
        self.lock_for_task("READ_BASE", "-")
        self.write_log("현재 base pose 값 읽기")
        self.runner.send_manual_command({"mode": "read-base"})

    def run_move_base(self) -> None:
        if self.logic.is_busy:
            return
        pose = [getattr(self, f"spin_{name}").value() for name in ("x", "y", "z", "rx", "ry", "rz")]
        self.lock_for_task("MOVE_BASE", "-")
        self.write_log(f"Base 이동 시작 {pose}")
        self.runner.send_manual_command({"mode": "move-base", "pose": pose})

    def run_home(self) -> None:
        if self.logic.is_busy:
            self.write_log("작업 중에는 HOME을 실행하지 않음")
            return
        if not self.logic.ros_connected:
            self.write_log("ROS 연결 전에는 HOME을 실행하지 않음")
            return
        self.lock_for_task("HOME", "-")
        self.write_log("HOME 실행")
        self.runner.start_node(config.HOME_NODE)

    def run_press_pickup(self) -> None:
        if self.logic.is_busy:
            return
        self.lock_for_task("PRESS_PLATE_PICKUP", "-")
        self.write_log("누름판 집기 실행")
        self.runner.start_node(config.PRESS_PICKUP_NODE)

    def run_press_putdown(self) -> None:
        if self.logic.is_busy:
            return
        self.lock_for_task("PRESS_PLATE_PUTDOWN", "-")
        self.write_log("누름판 놓기 실행")
        self.runner.start_node(config.PRESS_PUTDOWN_NODE)

    def run_shovel_pickup(self) -> None:
        if self.logic.is_busy:
            return
        self.lock_for_task("SHOVEL_PICKUP", "-")
        self.write_log("삽 집기 실행")
        self.runner.start_node(config.SHOVEL_PICKUP_NODE)

    def run_shovel_putdown(self) -> None:
        if self.logic.is_busy:
            return
        self.lock_for_task("SHOVEL_PUTDOWN", "-")
        self.write_log("삽 놓기 실행")
        self.runner.start_node(config.SHOVEL_PUTDOWN_NODE)

    def start_system(self) -> None:
        self.logic.system_started = True
        self.write_log("시스템 시작 - 기능 버튼 활성화")
        self.refresh_ros_connection_status()
        self.refresh_button_state()

    def shutdown_system(self) -> None:
        self.logic.system_started = False
        self.write_log("시스템 종료 - 시작 버튼 외 모든 버튼 비활성화")
        self.refresh_button_state()

    def emergency_stop(self) -> None:
        running_tray = self.logic.current_running_tray
        preserved_tool_state = self.logic.current_tool_state
        self.logic.is_emergency_stopped = True
        self.logic.requires_home_after_estop = True
        self.pending_task = None
        estop_process = self.runner.start_auxiliary_node(config.INTEGRATED_ESTOP_NODE)
        estop_started = estop_process.waitForStarted(1000)
        self.runner.stop_current_process()
        if running_tray in self.logic.tray_state:
            self.logic.clear_last_measurement(running_tray)
        self.logic.current_running_task = ""
        self.logic.current_running_tray = ""
        self.logic.current_process = None
        if estop_started:
            self.write_log("긴급정지 stop 노드 실행")
        else:
            self.write_log("긴급정지 stop 노드 실행 실패")
        self.write_log(f"긴급정지 - 툴 상태 유지: {preserved_tool_state}")
        self.set_label("lbl_robot_status", "긴급정지")
        self.logic.is_busy = False
        self.refresh_button_state()
        self.show_emergency_popup()

    def recover_from_estop(self) -> None:
        self.logic.is_emergency_stopped = False
        self.logic.requires_home_after_estop = False
        preserved_tool_state = self.logic.current_tool_state
        self.lock_for_task("RECOVER_TOOL_TCP", "-")
        self.write_log(
            "긴급정지 복구 - Tool/TCP 재설정, "
            f"툴 상태 유지: {preserved_tool_state}"
        )
        self.runner.send_manual_command({"mode": "recover-config"})

    def handle_manual_server_finished(
        self,
        process: QProcess,
        exit_code: int,
        _exit_status,
    ) -> None:
        if self.runner.manual_process is process:
            self.runner.manual_process = None
        self.write_log(f"상시 수동 제어 노드 종료 code={exit_code}")
        if self.logic.current_running_task in {
            "READ_JOINT",
            "READ_BASE",
            "MOVE_JOINT",
            "MOVE_BASE",
            "RECOVER_TOOL_TCP",
        }:
            self.unlock_after_task()
        process.deleteLater()

    def handle_auxiliary_process_finished(
        self,
        process: QProcess,
        node_name: str,
        exit_code: int,
        _exit_status,
    ) -> None:
        if exit_code == 0:
            self.write_log(f"{node_name} 보조 실행 완료")
        else:
            self.write_log(f"{node_name} 보조 실행 실패 code={exit_code}")
        process.deleteLater()

    def handle_process_output(self, process: QProcess) -> None:
        raw = bytes(process.readAllStandardOutput()).decode("utf-8", errors="replace")
        for line in raw.splitlines():
            if not line.strip():
                continue
            self.write_log(line)
            self._consume_process_line(line)

    def _consume_process_line(self, line: str) -> None:
        tray_label = self.logic.current_running_tray
        if "soil_state=SOIL_LOW" in line:
            self.logic.set_soil_status(tray_label, config.SOIL_STATUS_LOW)
            self.update_tray_widgets(tray_label)
        elif "soil_state=SOIL_OK" in line:
            self.logic.set_soil_status(tray_label, config.SOIL_STATUS_OK)
            self.update_tray_widgets(tray_label)
        elif "soil_state=SOIL_HIGH" in line:
            self.logic.set_soil_status(tray_label, config.SOIL_STATUS_HIGH)
            self.update_tray_widgets(tray_label)
        elif "soil_state=SKIPPED_DUE_TO_ROCK" in line:
            self.logic.set_soil_status(tray_label, config.SOIL_STATUS_OBSTACLE)
            self.update_tray_widgets(tray_label)
        elif "measurement_result_json=" in line:
            payload = line.split("measurement_result_json=", 1)[1]
            self.logic.set_last_measurement(tray_label, json.loads(payload))
        elif "joint_position_json=" in line:
            payload = json.loads(line.split("joint_position_json=", 1)[1])
            self._set_joint_spin_values(payload)
        elif "base_pose_json=" in line:
            payload = json.loads(line.split("base_pose_json=", 1)[1])
            self._set_base_spin_values(payload)
        elif "manual_command_result_json=" in line:
            payload = json.loads(line.split("manual_command_result_json=", 1)[1])
            mode = payload.get("mode", "unknown")
            if payload.get("success"):
                self.write_log(f"수동 명령 완료: {mode}")
                if mode == "recover-config":
                    self.set_label("lbl_robot_status", "안전복구 완료")
            else:
                error = payload.get("error", "unknown error")
                self.write_log(f"수동 명령 실패: {mode}, {error}")
                self.logic.last_error_message = str(error)
            self.unlock_after_task()
        elif "Pickup shovel start" in line:
            self.logic.set_tool_state(config.TOOL_STATE_SHOVEL)
        elif "Return shovel start" in line:
            self.logic.set_tool_state(config.TOOL_STATE_NONE)

    def _set_joint_spin_values(self, joint_values: list[float]) -> None:
        for idx, value in enumerate(joint_values[:6], start=1):
            spin = getattr(self, f"spin_j{idx}", None)
            if spin is not None:
                spin.setValue(float(value))

    def _set_base_spin_values(self, pose_values: list[float]) -> None:
        for name, value in zip(("x", "y", "z", "rx", "ry", "rz"), pose_values[:6]):
            spin = getattr(self, f"spin_{name}", None)
            if spin is not None:
                spin.setValue(float(value))

    def handle_process_finished(
        self,
        process: QProcess,
        node_name: str,
        exit_code: int,
        exit_status,
    ) -> None:
        if self.runner.process is process:
            self.runner.process = None
        self.logic.current_process = None

        if self.logic.is_emergency_stopped:
            self.refresh_button_state()
            return

        tray_label = self.logic.current_running_tray
        if exit_code == 0:
            self.write_log(f"{node_name} 종료")
            if node_name == config.PRESS_PICKUP_NODE:
                self.logic.set_tool_state(config.TOOL_STATE_PRESS)
                pending_task = self.pending_task
                self.pending_task = None
                if pending_task == ("measure", tray_label):
                    self.run_after_inter_node_delay(
                        lambda tray=tray_label: self._start_measure_task(tray),
                        reason="press pickup 완료",
                        delay_ms=config.PRESS_PICKUP_HANDOFF_DELAY_MS,
                    )
                    return
                if pending_task == ("flatten", tray_label):
                    self.run_after_inter_node_delay(
                        lambda tray=tray_label: self._start_flatten_task(tray),
                        reason="press pickup 완료",
                        delay_ms=config.PRESS_PICKUP_HANDOFF_DELAY_MS,
                    )
                    return
            if node_name == config.PRESS_PUTDOWN_NODE:
                self.logic.set_tool_state(config.TOOL_STATE_NONE)
                pending_task = self.pending_task
                self.pending_task = None
                if pending_task == ("next", tray_label):
                    self.run_after_inter_node_delay(
                        lambda tray=tray_label: self._start_next_step_task(
                            tray,
                            skip_initial_home=True,
                        ),
                        reason="press putdown 완료",
                        delay_ms=config.PRESS_PUTDOWN_HANDOFF_DELAY_MS,
                    )
                    return
            if node_name == config.SHOVEL_PICKUP_NODE:
                self.logic.set_tool_state(config.TOOL_STATE_SHOVEL)
            if node_name == config.SHOVEL_PUTDOWN_NODE:
                self.logic.set_tool_state(config.TOOL_STATE_NONE)
                pending_task = self.pending_task
                self.pending_task = None
                if pending_task == ("flatten_press_pickup", tray_label):
                    self.pending_task = ("flatten", tray_label)
                    def _start_press_pickup_after_shovel_putdown(tray=tray_label):
                        self.lock_for_task("PRESS_PLATE_PICKUP", tray)
                        self.write_log("평탄화 전 누름판 pickup 먼저 실행")
                        self.runner.start_node(config.PRESS_PICKUP_NODE)

                    self.run_after_inter_node_delay(
                        _start_press_pickup_after_shovel_putdown,
                        reason="shovel putdown 완료",
                    )
                    return
            if node_name == config.INTEGRATED_NEXT_STEP_NODE and tray_label in self.logic.tray_state:
                if self.logic.current_running_task in (
                    config.NEXT_ACTION_ADD_SOIL,
                    config.NEXT_ACTION_REMOVE_SOIL,
                    config.NEXT_ACTION_REMOVE_ROCK,
                ):
                    self.logic.set_tool_state(config.TOOL_STATE_NONE)
                    self.logic.mark_corrective_action_completed(tray_label)
                    self.update_tray_widgets(tray_label)
                elif self.logic.current_running_task == config.NEXT_ACTION_FLATTEN:
                    self.logic.set_tool_state(config.TOOL_STATE_NONE)
                    self.logic.mark_flatten_completed(tray_label)
                    self.update_tray_widgets(tray_label)
                elif self.logic.current_running_task == config.NEXT_ACTION_PLANT:
                    self.logic.set_tool_state(config.TOOL_STATE_NONE)
                    self.logic.mark_plant_completed(tray_label)
                    self.update_tray_widgets(tray_label)
            if node_name == config.INTEGRATED_FLATTEN_NODE and tray_label in self.logic.tray_state:
                self.logic.set_tool_state(config.TOOL_STATE_PRESS)
                self.logic.mark_flatten_completed(tray_label)
                self.update_tray_widgets(tray_label)
            if node_name == config.HOME_NODE:
                self.logic.requires_home_after_estop = False
        else:
            self.pending_task = None
            self.logic.set_error(tray_label, f"{node_name} failed with code {exit_code}")
            self.write_log(f"{node_name} 실패 code={exit_code}")

        self.unlock_after_task()
