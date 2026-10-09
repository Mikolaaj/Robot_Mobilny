"""Run real peers; verify roundtrip, parameter, service and action lifecycle."""
import os
import signal
import subprocess
import sys
import tempfile
import time
import rclpy
from action_msgs.msg import GoalStatus
from action_tutorials_interfaces.action import Fibonacci
from rcl_interfaces.srv import SetParameters
from rcl_interfaces.msg import Parameter, ParameterValue, ParameterType
from rclpy.action import ActionClient
from std_msgs.msg import String
from std_srvs.srv import Trigger


def run() -> None:
    # Isolated local DDS domain. No robot hardware or existing graph is touched.
    env = dict(os.environ, ROS_DOMAIN_ID='87', ROS_AUTOMATIC_DISCOVERY_RANGE='LOCALHOST')
    os.environ.update(ROS_DOMAIN_ID='87', ROS_AUTOMATIC_DISCOVERY_RANGE='LOCALHOST')
    processes = []
    with tempfile.TemporaryFile(mode='w+') as logs:
        try:
            commands = [[sys.argv[1]], ['/usr/bin/python3', sys.argv[2]],
                        ['/usr/bin/python3', sys.argv[3]]]
            for command in commands:
                processes.append(subprocess.Popen(command, env=env, stdout=logs,
                                                  stderr=logs, start_new_session=True))
            rclpy.init()
            node = rclpy.create_node('phase2_integration_probe')
            received = []
            subscription = node.create_subscription(
                String, 'phase2/cpp_message', lambda msg: received.append(msg.data), 10)

            def wait_until(predicate, timeout=12.0):
                deadline = time.monotonic() + timeout
                while not predicate() and time.monotonic() < deadline:
                    if any(process.poll() is not None for process in processes):
                        raise RuntimeError('A peer exited unexpectedly')
                    rclpy.spin_once(node, timeout_sec=0.1)
                if not predicate():
                    raise TimeoutError('ROS communication timed out')

            def result(future):
                wait_until(future.done)
                return future.result()

            wait_until(lambda: any(msg.startswith('C++ reply: hello #') for msg in received))
            params = node.create_client(SetParameters, '/python_peer/set_parameters')
            if not params.wait_for_service(timeout_sec=10):
                raise TimeoutError('Parameter service missing')
            request = SetParameters.Request(parameters=[Parameter(
                name='message_prefix', value=ParameterValue(
                    type=ParameterType.PARAMETER_STRING, string_value='integration'))])
            if not result(params.call_async(request)).results[0].successful:
                raise AssertionError('Parameter change rejected')
            wait_until(lambda: any(msg.startswith('C++ reply: integration #') for msg in received))
            status = node.create_client(Trigger, 'phase2/status')
            if not status.wait_for_service(timeout_sec=10):
                raise TimeoutError('Status service missing')
            response = result(status.call_async(Trigger.Request()))
            if not response.success or int(response.message.split('=')[1]) < 1:
                raise AssertionError('Incorrect receive counter')
            action = ActionClient(node, Fibonacci, 'phase2/fibonacci')
            if not action.wait_for_server(timeout_sec=10):
                raise TimeoutError('Action server missing')
            feedback = []
            goal = result(action.send_goal_async(
                Fibonacci.Goal(order=6), feedback_callback=lambda msg: feedback.append(msg)))
            if not goal.accepted:
                raise AssertionError('Valid goal rejected')
            outcome = result(goal.get_result_async())
            if outcome.status != GoalStatus.STATUS_SUCCEEDED or list(outcome.result.sequence) != [0, 1, 1, 2, 3, 5]:
                raise AssertionError('Incorrect action result')
            if not feedback:
                raise AssertionError('Action feedback missing')
            invalid = result(action.send_goal_async(Fibonacci.Goal(order=0)))
            if invalid.accepted:
                raise AssertionError('Invalid action goal accepted')
            goal = result(action.send_goal_async(Fibonacci.Goal(order=20)))
            if not goal.accepted:
                raise AssertionError('Cancellation goal rejected')
            canceled = result(goal.cancel_goal_async())
            if not canceled.goals_canceling:
                raise AssertionError('Cancellation rejected')
            if result(goal.get_result_async()).status != GoalStatus.STATUS_CANCELED:
                raise AssertionError('Action did not finish canceled')
            node.destroy_subscription(subscription)
            node.destroy_node()
            print('PASS: Python/C++ roundtrip, parameter, service, action result/feedback/rejection/cancel')
        except Exception:
            logs.seek(0)
            print(logs.read(), file=sys.stderr)
            raise
        finally:
            if rclpy.ok():
                rclpy.shutdown()
            for process in processes:
                if process.poll() is None:
                    os.killpg(process.pid, signal.SIGINT)
            for process in processes:
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()


if __name__ == '__main__':
    run()
