"""Launch the integrated SmartFarm dashboard."""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            Node(
                package="robot_tests",
                executable="integrated_dashboard",
                name="integrated_dashboard",
                output="screen",
            )
        ]
    )
