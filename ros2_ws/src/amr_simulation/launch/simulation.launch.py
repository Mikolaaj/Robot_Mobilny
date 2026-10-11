from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    EmitEvent,
    IncludeLaunchDescription,
    RegisterEventHandler,
)
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.events import Shutdown
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import xacro


def generate_launch_description():
    simulation_dir = Path(get_package_share_directory('amr_simulation'))
    description_dir = Path(get_package_share_directory('amr_description'))
    gazebo_dir = Path(get_package_share_directory('ros_gz_sim'))

    world_path = simulation_dir / 'worlds' / 'warehouse.sdf'
    bridge_config = simulation_dir / 'config' / 'bridge.yaml'
    model_path = description_dir / 'urdf' / 'robot.urdf.xacro'
    robot_description = xacro.process_file(str(model_path)).toxml()

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(str(gazebo_dir / 'launch' / 'gz_sim.launch.py')),
        launch_arguments={
            'gz_args': [LaunchConfiguration('gz_args'), ' ', str(world_path)],
        }.items(),
    )

    state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[
            {
                'robot_description': robot_description,
                'use_sim_time': True,
            }
        ],
        output='screen',
    )

    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-world',
            'warehouse',
            '-name',
            'amr_robot',
            '-topic',
            '/robot_description',
            '-x',
            '0',
            '-y',
            '0',
            '-z',
            '0.15',
        ],
        output='screen',
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{'config_file': str(bridge_config)}],
        output='screen',
    )

    controller = Node(
        package='amr_control',
        executable='ackermann_controller',
        parameters=[{'use_sim_time': True}],
        output='screen',
    )

    odometry = Node(
        package='amr_control',
        executable='ackermann_odometry',
        parameters=[{'use_sim_time': True}],
        output='screen',
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', str(simulation_dir / 'config' / 'odometry.rviz')],
        parameters=[{'use_sim_time': True}],
        condition=IfCondition(LaunchConfiguration('rviz')),
        output='screen',
    )

    stop_on_controller_exit = RegisterEventHandler(
        OnProcessExit(
            target_action=controller,
            on_exit=[EmitEvent(event=Shutdown(reason='Controller exited; closing simulation'))],
        )
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument('gz_args', default_value='-r'),
            DeclareLaunchArgument('rviz', default_value='false'),
            stop_on_controller_exit,
            gazebo,
            state_publisher,
            spawn_robot,
            bridge,
            controller,
            odometry,
            rviz,
        ]
    )
