from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [
            Node(package="amr_learning", executable="python_peer", output="screen"),
            Node(package="amr_learning", executable="cpp_peer", output="screen"),
            Node(package="amr_learning", executable="fibonacci_server", output="screen"),
        ]
    )
