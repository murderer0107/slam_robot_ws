"""ROS node process launcher for the integrated dashboard."""

from __future__ import annotations

from pathlib import Path
import json
import shlex

from PyQt5.QtCore import QProcess

from robot_tests.integrated import config


class RosNodeRunner:
    """Wrap QProcess-based execution for `ros2 run robot_tests ...` commands."""

    def __init__(self, owner) -> None:
        self.owner = owner
        self.process: QProcess | None = None
        self.manual_process: QProcess | None = None

    def start_manual_server(self) -> QProcess:
        if self.manual_process is not None and self.manual_process.state() != QProcess.NotRunning:
            return self.manual_process

        process = QProcess(self.owner)
        process.setProgram("/bin/bash")
        setup_path = Path(config.WORKSPACE_SETUP_PATH)
        shell_cmd = (
            f"source '{setup_path}' && ros2 run robot_tests "
            f"{config.INTEGRATED_MANUAL_NODE} -- --mode server"
        )
        process.setArguments(["-lc", shell_cmd])
        process.setProcessChannelMode(QProcess.MergedChannels)
        process.readyReadStandardOutput.connect(
            lambda: self.owner.handle_process_output(process)
        )
        process.finished.connect(
            lambda exit_code, exit_status: self.owner.handle_manual_server_finished(
                process, exit_code, exit_status
            )
        )
        process.start()
        self.manual_process = process
        return process

    def send_manual_command(self, command: dict) -> None:
        process = self.start_manual_server()
        if not process.waitForStarted(3000):
            raise RuntimeError("Persistent manual control node failed to start")
        payload = json.dumps(command, ensure_ascii=False, separators=(",", ":")) + "\n"
        process.write(payload.encode("utf-8"))

    def start_node(
        self,
        node_name: str,
        *,
        node_args: list[str] | None = None,
        input_text: str = "",
    ) -> QProcess:
        if self.process is not None and self.process.state() != QProcess.NotRunning:
            raise RuntimeError("Another ROS node process is already running")

        process = QProcess(self.owner)
        process.setProgram("/bin/bash")
        setup_path = Path(config.WORKSPACE_SETUP_PATH)
        shell_cmd = f"source '{setup_path}' && ros2 run robot_tests {node_name}"
        if node_args:
            escaped_args = " ".join(shlex.quote(arg) for arg in node_args)
            shell_cmd = f"{shell_cmd} -- {escaped_args}"
        process.setArguments(["-lc", shell_cmd])
        process.setProcessChannelMode(QProcess.MergedChannels)
        process.readyReadStandardOutput.connect(
            lambda: self.owner.handle_process_output(process)
        )
        process.finished.connect(
            lambda exit_code, exit_status: self.owner.handle_process_finished(
                process, node_name, exit_code, exit_status
            )
        )
        process.start()

        self.process = process
        self.owner.logic.current_process = process

        if input_text:
            process.waitForStarted(3000)
            process.write(input_text.encode("utf-8"))

        return process

    def start_detached_node(self, node_name: str, *, node_args: list[str] | None = None) -> bool:
        setup_path = Path(config.WORKSPACE_SETUP_PATH)
        shell_cmd = f"source '{setup_path}' && ros2 run robot_tests {node_name}"
        if node_args:
            escaped_args = " ".join(shlex.quote(arg) for arg in node_args)
            shell_cmd = f"{shell_cmd} -- {escaped_args}"
        return QProcess.startDetached("/bin/bash", ["-lc", shell_cmd])

    def start_auxiliary_node(
        self,
        node_name: str,
        *,
        node_args: list[str] | None = None,
    ) -> QProcess:
        """Start a node without replacing the dashboard's current task process."""
        process = QProcess(self.owner)
        process.setProgram("/bin/bash")
        setup_path = Path(config.WORKSPACE_SETUP_PATH)
        shell_cmd = f"source '{setup_path}' && ros2 run robot_tests {node_name}"
        if node_args:
            escaped_args = " ".join(shlex.quote(arg) for arg in node_args)
            shell_cmd = f"{shell_cmd} -- {escaped_args}"
        process.setArguments(["-lc", shell_cmd])
        process.setProcessChannelMode(QProcess.MergedChannels)
        process.readyReadStandardOutput.connect(
            lambda: self.owner.handle_process_output(process)
        )
        process.finished.connect(
            lambda exit_code, exit_status: self.owner.handle_auxiliary_process_finished(
                process, node_name, exit_code, exit_status
            )
        )
        process.start()
        return process

    def stop_current_process(self, *, suppress_finished: bool = True) -> None:
        if self.process is None:
            return
        process = self.process
        if self.process.state() != QProcess.NotRunning:
            if suppress_finished:
                try:
                    process.finished.disconnect()
                except TypeError:
                    pass
            process.kill()
            process.waitForFinished(2000)
        self.process = None
        self.owner.logic.current_process = None
