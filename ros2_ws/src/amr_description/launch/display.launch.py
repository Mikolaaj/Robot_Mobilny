from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
import xacro


def generate_launch_description():
    package_dir = Path(get_package_share_directory('amr_description'))
    model_path = package_dir / 'urdf' / 'robot.urdf.xacro'
    rviz_config = package_dir / 'rviz' / 'robot.rviz'
    robot_description = xacro.process_file(str(model_path)).toxml()

    return LaunchDescription(
        [
            Node(
                package='robot_state_publisher',
                executable='robot_state_publisher',
                parameters=[{'robot_description': robot_description}],
                output='screen',
            ),
            Node(
                package='joint_state_publisher_gui',
                executable='joint_state_publisher_gui',
                output='screen',
            ),
            Node(
                package='rviz2',
                executable='rviz2',
                arguments=['-d', str(rviz_config)],
                output='screen',
            ),
        ]
    )
