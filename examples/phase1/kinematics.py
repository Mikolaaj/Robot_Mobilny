"""Differential drive: SI units, positive yaw turns left."""
from dataclasses import dataclass
from math import isfinite, pi


@dataclass(frozen=True)
class WheelSpeeds:
    left_rpm: float
    right_rpm: float


def wheel_speeds(v: float, yaw_rate: float, radius: float, track: float) -> WheelSpeeds:
    """Convert m/s and rad/s to wheel RPM for a no-slip planar robot."""
    if not all(isfinite(x) for x in (v, yaw_rate, radius, track)):
        raise ValueError("All inputs must be finite")
    if radius <= 0 or track <= 0:
        raise ValueError("Radius and track must be positive")
    to_rpm = 60.0 / (2.0 * pi * radius)
    return WheelSpeeds((v - yaw_rate * track / 2.0) * to_rpm,
                       (v + yaw_rate * track / 2.0) * to_rpm)


if __name__ == "__main__":
    speeds = wheel_speeds(v=0.5, yaw_rate=1.0, radius=0.1, track=0.4)
    print(f"left={speeds.left_rpm:.3f} RPM, right={speeds.right_rpm:.3f} RPM")
