from setuptools import find_packages, setup


package_name = "robot_tests"


setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        (
            "share/ament_index/resource_index/packages",
            ["resource/" + package_name],
        ),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="spacewhale0107",
    maintainer_email="murderer0107@gmail.com",
    description="Test nodes for Doosan M0609 and peripherals.",
    license="Apache-2.0",
    extras_require={
        "test": [
            "pytest",
        ],
    },
    entry_points={
        "console_scripts": [
            "go_home_test = robot_tests.go_home_test_node:main",
            "keyboard_teleop_node = robot_tests.keyboard_teleop_node:main",
            "plant_pick_and_place_tray_node = robot_tests.plant_pick_and_place_tray_node:main",
            "plant_pick_and_place_tray_select_node = robot_tests.plant_pick_and_place_tray_select_node:main",
            "press_plate_pickup_node = robot_tests.press_plate_pickup_node:main",
            "press_plate_putdown_node = robot_tests.press_plate_putdown_node:main",
            "simple_compliance_down_up_test = robot_tests.simple_compliance_down_up_test:main",
            "tray_rock_remove_node = robot_tests.tray_rock_remove_node:main",
            "tray_soil_add_node = robot_tests.tray_soil_add_node:main",
            "tray_soil_keep_node = robot_tests.tray_soil_keep_node:main",
            "tray_soil_remove_node = robot_tests.tray_soil_remove_node:main",
            "tray_top_move_node = robot_tests.tray_top_move_node:main",
            "tray_soil_state_check_node = robot_tests.tray_soil_state_check_node:main",
        ],
    },
)
