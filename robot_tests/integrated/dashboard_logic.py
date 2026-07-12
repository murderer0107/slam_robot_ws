"""Integrated dashboard state model."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
from typing import Any

from robot_tests.integrated import config


@dataclass
class TrayState:
    soil_status: str = config.INITIAL_SOIL_STATUS
    work_phase: str = config.WORK_PHASE_IDLE
    last_error: str = ""
    last_measurement: dict[str, Any] = field(default_factory=dict)


class IntegratedDashboardLogic:
    """State container for the integrated SmartFarm dashboard."""

    STATE_PATH = Path.home() / ".config" / "robot_tests" / "integrated_dashboard_state.json"

    def __init__(self) -> None:
        self.system_started = False
        self.current_tool_state = config.TOOL_STATE_NONE
        self.is_busy = False
        self.is_emergency_stopped = False
        self.requires_home_after_estop = False
        self.current_running_task = ""
        self.current_running_tray = ""
        self.current_process = None
        self.ros_connected = False
        self.last_error_message = ""

        self.tray_state = {
            tray_label: TrayState()
            for tray_label in config.TRAY_LABELS
        }
        self._load_persistent_state()

    def _load_persistent_state(self) -> None:
        try:
            payload = json.loads(self.STATE_PATH.read_text(encoding="utf-8"))
        except (FileNotFoundError, OSError, ValueError, TypeError):
            return

        saved_tool = payload.get("current_tool_state")
        if saved_tool in {
            config.TOOL_STATE_NONE,
            config.TOOL_STATE_PRESS,
            config.TOOL_STATE_SHOVEL,
            config.TOOL_STATE_UNKNOWN,
        }:
            self.current_tool_state = saved_tool

        saved_trays = payload.get("tray_state", {})
        if not isinstance(saved_trays, dict):
            return
        for tray_label in config.TRAY_LABELS:
            saved = saved_trays.get(tray_label)
            if not isinstance(saved, dict):
                continue
            self.tray_state[tray_label] = TrayState(
                soil_status=str(saved.get("soil_status", config.INITIAL_SOIL_STATUS)),
                work_phase=str(saved.get("work_phase", config.WORK_PHASE_IDLE)),
                last_error=str(saved.get("last_error", "")),
                last_measurement=dict(saved.get("last_measurement", {})),
            )

    def save_persistent_state(self) -> None:
        payload = {
            "current_tool_state": self.current_tool_state,
            "tray_state": {
                tray_label: asdict(tray)
                for tray_label, tray in self.tray_state.items()
            },
        }
        self.STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.STATE_PATH.with_suffix(".tmp")
        temporary_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporary_path.replace(self.STATE_PATH)

    def set_tool_state(self, tool_state: str) -> None:
        self.current_tool_state = tool_state
        self.save_persistent_state()

    def reset_tray(self, tray_label: str) -> None:
        self.tray_state[tray_label] = TrayState()
        self.save_persistent_state()

    def set_soil_status(self, tray_label: str, soil_status: str) -> None:
        tray = self.tray_state[tray_label]
        tray.soil_status = soil_status
        # 새 측정 결과가 들어오면 이전 보정/평탄화 phase를 종료한다.
        tray.work_phase = config.WORK_PHASE_IDLE
        self.save_persistent_state()

    def set_last_measurement(self, tray_label: str, result: dict[str, Any]) -> None:
        if tray_label in self.tray_state:
            self.tray_state[tray_label].last_measurement = dict(result)
            self.save_persistent_state()

    def mark_flatten_completed(self, tray_label: str) -> None:
        tray = self.tray_state[tray_label]
        # 평탄화 과정에서 새로 측정된 토양 상태를 유지한다.
        tray.work_phase = config.WORK_PHASE_IDLE
        self.save_persistent_state()

    def mark_corrective_action_completed(self, tray_label: str) -> None:
        tray = self.tray_state[tray_label]
        tray.work_phase = config.WORK_PHASE_AFTER_CORRECTION
        self.save_persistent_state()

    def mark_plant_completed(self, tray_label: str) -> None:
        tray = self.tray_state[tray_label]
        tray.soil_status = config.SOIL_STATUS_OK
        tray.work_phase = config.WORK_PHASE_DONE
        self.save_persistent_state()

    def get_next_action(self, tray_label: str) -> str:
        tray = self.tray_state[tray_label]
        if tray.work_phase == config.WORK_PHASE_DONE:
            return config.NEXT_ACTION_DONE
        if tray.work_phase == config.WORK_PHASE_AFTER_CORRECTION:
            return config.NEXT_ACTION_FLATTEN
        if tray.soil_status == config.SOIL_STATUS_LOW:
            return config.NEXT_ACTION_ADD_SOIL
        if tray.soil_status == config.SOIL_STATUS_HIGH:
            return config.NEXT_ACTION_REMOVE_SOIL
        if tray.soil_status == config.SOIL_STATUS_OBSTACLE:
            return config.NEXT_ACTION_REMOVE_ROCK
        if tray.soil_status == config.SOIL_STATUS_OK:
            return config.NEXT_ACTION_PLANT
        return config.NEXT_ACTION_MEASURE

    def set_error(self, tray_label: str, message: str) -> None:
        self.last_error_message = message
        if tray_label in self.tray_state:
            self.tray_state[tray_label].last_error = message
        self.save_persistent_state()

    def clear_last_measurement(self, tray_label: str) -> None:
        if tray_label in self.tray_state:
            self.tray_state[tray_label].last_measurement = {}
            self.save_persistent_state()
