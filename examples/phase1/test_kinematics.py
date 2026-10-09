import math
import unittest
from kinematics import wheel_commands


class KinematicsTests(unittest.TestCase):
    def test_stop(self):
        self.assertEqual(tuple(vars(wheel_commands(0, 0, 1, 1, 1)).values()), (0,) * 6)

    def test_straight(self):
        c = wheel_commands(2 * math.pi, 0, 1, 1, 1)
        for rpm in (c.front_left_rpm, c.front_right_rpm, c.rear_left_rpm, c.rear_right_rpm):
            self.assertAlmostEqual(rpm, 60)
        self.assertEqual((c.front_left_steering_rad, c.front_right_steering_rad), (0, 0))

    def test_known_turn(self):
        # Rear axle centre travels radius 1: wheel radii 0.5, 1.5,
        # front radii sqrt(1.25), sqrt(3.25), wheelbase 1.
        c = wheel_commands(1, 1, 1, 1, 1, 1.3)
        factor = 60 / (2 * math.pi)
        self.assertAlmostEqual(c.rear_left_rpm, 0.5 * factor)
        self.assertAlmostEqual(c.rear_right_rpm, 1.5 * factor)
        self.assertAlmostEqual(c.front_left_rpm, math.sqrt(1.25) * factor)
        self.assertAlmostEqual(c.front_right_rpm, math.sqrt(3.25) * factor)
        self.assertAlmostEqual(c.front_left_steering_rad, math.atan(2))
        self.assertAlmostEqual(c.front_right_steering_rad, math.atan(2 / 3))

    def test_right_turn_mirrors_left(self):
        left = wheel_commands(1, 0.3, 0.1, 0.4, 0.6)
        right = wheel_commands(1, -0.3, 0.1, 0.4, 0.6)
        self.assertAlmostEqual(left.front_left_rpm, right.front_right_rpm)
        self.assertAlmostEqual(left.rear_left_rpm, right.rear_right_rpm)
        self.assertAlmostEqual(left.front_left_steering_rad, -right.front_right_steering_rad)

    def test_reverse_same_steering(self):
        forward = wheel_commands(1, 0.3, 0.1, 0.4, 0.6)
        reverse = wheel_commands(-1, -0.3, 0.1, 0.4, 0.6)
        for name, value in vars(forward).items():
            expected = value if 'steering' in name else -value
            self.assertAlmostEqual(getattr(reverse, name), expected)

    def test_invalid_or_infeasible(self):
        for args in ((0, 1, 1, 1, 1), (1, 0, 0, 1, 1), (1, 0, 1, -1, 1),
                     (1, 0, 1, 1, 0), (math.nan, 0, 1, 1, 1),
                     (1, 0, 1, 1, 1, math.inf), (1, 1, 1, 1, 1),
                     (1, 4, 1, 1, 1), (1, 0, 1, 1, 1, 0)):
            with self.assertRaises(ValueError):
                wheel_commands(*args)
