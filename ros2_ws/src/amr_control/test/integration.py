import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

# Osobna domena ROS: test nie komunikuje się z uruchomioną symulacją.
os.environ['ROS_DOMAIN_ID'] = '88'
os.environ.pop('ROS_LOCALHOST_ONLY', None)
os.environ['ROS_AUTOMATIC_DISCOVERY_RANGE'] = 'LOCALHOST'

import rclpy
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64


TOPICS = [
    '/amr/commands/front_left_velocity',
    '/amr/commands/front_right_velocity',
    '/amr/commands/rear_left_velocity',
    '/amr/commands/rear_right_velocity',
    '/amr/commands/front_left_steering',
    '/amr/commands/front_right_steering',
]


def main():
    process = None
    node = None
    rclpy.init()

    try:
        with tempfile.TemporaryDirectory(prefix='amr_control_test_') as directory:
            env = os.environ.copy()
            env['ROS_LOG_DIR'] = directory

            with (Path(directory) / 'controller.log').open('w+') as log:
                process = subprocess.Popen(
                    [sys.argv[1]],
                    env=env,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                )

                node = rclpy.create_node('control_integration_test')
                publisher = node.create_publisher(Twist, '/cmd_vel', 10)
                latest = {}
                subscriptions = []

                def callback(index, message):
                    latest[index] = message.data

                for index, topic in enumerate(TOPICS):
                    subscriptions.append(
                        node.create_subscription(
                            Float64,
                            topic,
                            lambda message, i=index: callback(i, message),
                            10,
                        )
                    )

                def wait_until(predicate, timeout, description):
                    deadline = time.monotonic() + timeout
                    while time.monotonic() < deadline:
                        if process.poll() is not None:
                            log.flush()
                            log.seek(0)
                            raise AssertionError(f'Controller exited:\n{log.read()}')
                        rclpy.spin_once(node, timeout_sec=0.02)
                        if predicate():
                            return
                    raise AssertionError(f'Timeout: {description}; received={latest}')

                def matches(expected):
                    return len(latest) == 6 and all(
                        math.isclose(latest[i], value, rel_tol=1e-5, abs_tol=1e-5)
                        for i, value in enumerate(expected)
                    )

                def command(v, yaw_rate):
                    message = Twist()
                    message.linear.x = v
                    message.angular.z = yaw_rate
                    return message

                def check_command(v, yaw_rate, expected, description):
                    message = command(v, yaw_rate)
                    latest.clear()
                    deadline = time.monotonic() + 3.0

                    while time.monotonic() < deadline:
                        publisher.publish(message)
                        # Obsłuż wszystkie sześć tematów między komendami.
                        end = time.monotonic() + 0.05
                        while time.monotonic() < end:
                            rclpy.spin_once(node, timeout_sec=0.005)
                        if matches(expected):
                            return

                    raise AssertionError(f'{description}: expected={expected}; received={latest}')

                zeros = [0.0] * 6

                wait_until(
                    lambda: publisher.get_subscription_count() > 0 and matches(zeros),
                    10.0,
                    'discovery and initial stop',
                )

                check_command(
                    0.2,
                    0.0,
                    [2.0, 2.0, 2.0, 2.0, 0.0, 0.0],
                    'straight',
                )

                # v=0.2 m/s, yaw_rate=0.1 rad/s:
                # rear speeds: 0.18 and 0.22 m/s;
                # lateral component at front axle: 0.06 m/s.
                left_angle = math.atan2(0.06, 0.18)
                right_angle = math.atan2(0.06, 0.22)
                left_speed = math.hypot(0.18, 0.06) / 0.1
                right_speed = math.hypot(0.22, 0.06) / 0.1

                check_command(
                    0.2,
                    0.1,
                    [
                        left_speed,
                        right_speed,
                        1.8,
                        2.2,
                        left_angle,
                        right_angle,
                    ],
                    'left turn',
                )

                check_command(
                    0.2,
                    -0.1,
                    [
                        right_speed,
                        left_speed,
                        2.2,
                        1.8,
                        -right_angle,
                        -left_angle,
                    ],
                    'right turn',
                )

                check_command(
                    -0.2,
                    0.0,
                    [-2.0, -2.0, -2.0, -2.0, 0.0, 0.0],
                    'reverse',
                )

                # Bez nowych komend sterownik musi zatrzymać robota.
                latest.clear()
                wait_until(
                    lambda: matches(zeros),
                    2.0,
                    'command timeout',
                )

                # Niedozwolona komenda musi zatrzymać jadącego robota.
                check_command(
                    0.2,
                    0.0,
                    [2.0, 2.0, 2.0, 2.0, 0.0, 0.0],
                    'moving before rejection',
                )
                check_command(
                    0.0,
                    0.2,
                    zeros,
                    'rotation in place rejected',
                )

                check_command(
                    0.2,
                    0.0,
                    [2.0, 2.0, 2.0, 2.0, 0.0, 0.0],
                    'recovery after rejection',
                )
                check_command(
                    0.0,
                    0.0,
                    zeros,
                    'explicit stop',
                )

                print(
                    'PASS: straight, left/right turn, reverse, timeout, '
                    'rejection, recovery and stop'
                )
    finally:
        if process is not None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()

        if node is not None:
            node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
