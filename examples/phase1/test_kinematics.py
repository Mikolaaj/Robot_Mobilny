import math
import unittest
from kinematics import wheel_speeds


class KinematicsTests(unittest.TestCase):
    def test_stationary(self):
        speeds = wheel_speeds(0, 0, 0.1, 0.4)
        self.assertEqual((speeds.left_rpm, speeds.right_rpm), (0, 0))

    def test_one_turn_per_second(self):
        speeds = wheel_speeds(2 * math.pi * 0.1, 0, 0.1, 0.4)
        self.assertAlmostEqual(speeds.left_rpm, 60)
        self.assertAlmostEqual(speeds.right_rpm, 60)

    def test_rotation_left(self):
        speeds = wheel_speeds(0, math.pi, 0.1, 0.4)
        self.assertAlmostEqual(speeds.left_rpm, -60)
        self.assertAlmostEqual(speeds.right_rpm, 60)

    def test_invalid_inputs(self):
        for args in ((0, 0, 0, 0.4), (0, 0, 0.1, -1), (math.nan, 0, 0.1, 0.4)):
            with self.assertRaises(ValueError):
                wheel_speeds(*args)
