"""Exercise the real Gazebo bridge, joint physics and controller failure shutdown."""

import os
import signal
import subprocess
import tempfile
import time

from geometry_msgs.msg import Twist
import rclpy
from rclpy.qos import qos_profile_sensor_data
from rosgraph_msgs.msg import Clock
from sensor_msgs.msg import JointState


def main():
    """Run an isolated headless simulation and clean up its process group."""
    os.environ.pop('ROS_LOCALHOST_ONLY', None)
    os.environ['ROS_DOMAIN_ID'] = '89'
    os.environ['ROS_AUTOMATIC_DISCOVERY_RANGE'] = 'LOCALHOST'
    node = None
    process = None
    rclpy.init()
    try:
        with tempfile.TemporaryDirectory(prefix='amr_gazebo_test_') as directory:
            env = os.environ.copy()
            env['GZ_PARTITION'] = directory
            env['ROS_LOG_DIR'] = directory
            with tempfile.TemporaryFile(mode='w+') as log:
                process = subprocess.Popen(
                    ['ros2', 'launch', 'amr_simulation', 'simulation.launch.py', 'gz_args:=-r -s'],
                    env=env,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                )
                node = rclpy.create_node('gazebo_integration_test')
                state = {}
                clocks = []

                def receive(message):
                    """Keep actual joint positions and velocities by joint name."""
                    for i, name in enumerate(message.name):
                        state[name] = (message.position[i], message.velocity[i])

                joint_sub = node.create_subscription(JointState, '/joint_states', receive, 10)
                clock_sub = node.create_subscription(
                    Clock, '/clock', clocks.append, qos_profile_sensor_data
                )
                publisher = node.create_publisher(Twist, '/cmd_vel', 10)

                def wait_for(predicate, timeout, label, command=None):
                    """Spin and optionally refresh a command until an assertion is met."""
                    deadline = time.monotonic() + timeout
                    while time.monotonic() < deadline:
                        if process.poll() is not None:
                            raise AssertionError('Simulation exited before ' + label)
                        if command is not None:
                            publisher.publish(command)
                        rclpy.spin_once(node, timeout_sec=0.02)
                        if predicate():
                            return
                    raise AssertionError(f'Timeout: {label}; state={state}')

                wheels = [
                    'front_left_wheel_joint',
                    'front_right_wheel_joint',
                    'rear_left_wheel_joint',
                    'rear_right_wheel_joint',
                ]
                steering = ['front_left_steering_joint', 'front_right_steering_joint']
                wait_for(
                    lambda: len(state) == 6
                    and len(clocks) > 1
                    and publisher.get_subscription_count() > 0,
                    30,
                    'clock, six joints and controller discovery',
                )
                baseline = {name: state[name][0] for name in wheels}
                drive = Twist()
                drive.linear.x = 0.2
                wait_for(
                    lambda: all(state[name][0] - baseline[name] > 0.5 for name in wheels),
                    10,
                    'four wheels rotating',
                    drive,
                )
                turn = Twist()
                turn.linear.x = 0.2
                turn.angular.z = 0.1
                wait_for(
                    lambda: 0.30 < state[steering[0]][0] < 0.35
                    and 0.24 < state[steering[1]][0] < 0.29,
                    10,
                    'physical Ackermann steering',
                    turn,
                )
                wait_for(
                    lambda: all(abs(state[name][1]) < 0.01 for name in wheels)
                    and all(abs(state[name][0]) < 0.01 for name in steering),
                    5,
                    'timeout stops wheels and straightens steering',
                )

                # Only kill a controller belonging to this test's launch process tree.
                rows = subprocess.check_output(
                    ['ps', '-eo', 'pid=,ppid=,args='],
                    text=True,
                ).splitlines()
                entries = [row.strip().split(maxsplit=2) for row in rows]
                descendants = {process.pid}
                for _ in range(len(entries)):
                    before = len(descendants)
                    for row in entries:
                        if len(row) == 3 and int(row[1]) in descendants:
                            descendants.add(int(row[0]))
                    if len(descendants) == before:
                        break
                controllers = [
                    int(row[0])
                    for row in entries
                    if len(row) == 3
                    and int(row[0]) in descendants
                    and '/lib/amr_control/ackermann_controller' in row[2]
                ]
                assert len(controllers) == 1, f'Expected one test controller: {controllers}'
                os.kill(controllers[0], signal.SIGKILL)
                process.wait(timeout=20)
                print(
                    'PASS: Gazebo clock, bridge, four drives, steering, timeout and crash shutdown'
                )
                # Keep subscriptions alive throughout the test.
                del joint_sub, clock_sub
    except Exception:
        if 'log' in locals() and not log.closed:
            log.seek(0)
            print(log.read())
        raise
    finally:
        if process is not None:
            try:
                os.killpg(process.pid, signal.SIGINT)
            except ProcessLookupError:
                pass
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
        if node is not None:
            node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
