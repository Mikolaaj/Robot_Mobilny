"""Check measured odometry, timestamps, reset and TF without Gazebo."""

import math
import os
import subprocess
import sys
import tempfile
import time

from nav_msgs.msg import Odometry
import rclpy
from sensor_msgs.msg import JointState
from tf2_msgs.msg import TFMessage


def main():
    """Publish controlled joint measurements into an isolated odometry node."""
    os.environ['ROS_DOMAIN_ID'] = '90'
    os.environ.pop('ROS_LOCALHOST_ONLY', None)
    os.environ['ROS_AUTOMATIC_DISCOVERY_RANGE'] = 'LOCALHOST'
    rclpy.init()
    node = rclpy.create_node('odometry_test')
    process = None
    try:
        with tempfile.TemporaryDirectory(prefix='amr_odom_') as directory:
            env = os.environ.copy()
            env['ROS_LOG_DIR'] = directory
            process = subprocess.Popen([sys.argv[1]], env=env)
            results = []
            transforms = []
            subscriptions = [
                node.create_subscription(Odometry, '/odom', results.append, 10),
                node.create_subscription(TFMessage, '/tf', transforms.append, 10),
            ]
            publisher = node.create_publisher(JointState, '/joint_states', 10)

            def send(sec, left=2.0, right=2.0, sl=0.0, sr=0.0):
                """Use shuffled names to test lookup rather than fixed indices."""
                message = JointState()
                message.header.stamp.sec = sec
                message.name = [
                    'front_right_steering_joint',
                    'rear_right_wheel_joint',
                    'front_left_steering_joint',
                    'rear_left_wheel_joint',
                ]
                message.position = [sr, 0.0, sl, 0.0]
                message.velocity = [0.0, right, 0.0, left]
                publisher.publish(message)
                end = time.monotonic() + 0.2
                while time.monotonic() < end:
                    rclpy.spin_once(node, timeout_sec=0.01)

            deadline = time.monotonic() + 10
            while publisher.get_subscription_count() == 0:
                assert time.monotonic() < deadline, 'Odometry discovery timed out'
                rclpy.spin_once(node, timeout_sec=0.05)

            # Use 0.1 s stamps within the default max_dt.
            def sample(n, left=2.0, right=2.0, sl=0.0, sr=0.0):
                """Send one sample with a precise simulation timestamp."""
                message = JointState()
                message.header.stamp.sec = n // 10
                message.header.stamp.nanosec = (n % 10) * 100000000
                message.name = [
                    'front_right_steering_joint',
                    'rear_right_wheel_joint',
                    'front_left_steering_joint',
                    'rear_left_wheel_joint',
                ]
                message.position = [sr, 0.0, sl, 0.0]
                message.velocity = [0.0, right, 0.0, left]
                publisher.publish(message)
                end = time.monotonic() + 0.1
                while time.monotonic() < end:
                    rclpy.spin_once(node, timeout_sec=0.01)

            for n in range(10, 21):
                sample(n)
            assert len(results) > 1
            assert math.isclose(results[-1].pose.pose.position.x, 0.2, abs_tol=1e-6)
            assert math.isclose(results[-1].twist.twist.linear.x, 0.2, abs_tol=1e-6)
            for n in range(21, 31):
                sample(n, -2.0, -2.0)
            assert abs(results[-1].pose.pose.position.x) < 1e-6
            for n in range(31, 41):
                sample(n, 1.8, 2.2, math.atan2(0.06, 0.18), math.atan2(0.06, 0.22))
            assert math.isclose(results[-1].twist.twist.angular.z, 0.1, abs_tol=1e-6)
            assert math.isclose(
                results[-1].pose.pose.position.y, 2 * (1 - math.cos(0.1)), abs_tol=1e-6
            )
            old = results[-1].pose.pose.position.x
            count = len(results)
            sample(40)
            assert len(results) == count, 'Duplicate timestamp was integrated'
            send(10)  # Long gap: preserve position, do not extrapolate.
            assert math.isclose(results[-1].pose.pose.position.x, old, abs_tol=1e-6)
            send(1, 0.0, 0.0)  # Backwards time: start a new simulation epoch.
            assert abs(results[-1].pose.pose.position.x) < 1e-6
            assert results[-1].header.frame_id == 'odom'
            assert results[-1].child_frame_id == 'base_link'
            assert transforms
            tf = transforms[-1].transforms[0]
            assert tf.header.frame_id == 'odom' and tf.child_frame_id == 'base_link'
            assert tf.header.stamp == results[-1].header.stamp
            assert tf.transform.rotation == results[-1].pose.pose.orientation
            print('PASS: measured odometry, reverse, curve, timestamps, reset and TF')
            del subscriptions
    finally:
        if process is not None:
            process.terminate()
            process.wait(timeout=5)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
