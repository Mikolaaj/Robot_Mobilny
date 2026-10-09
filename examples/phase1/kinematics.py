"""4WD Ackermann: velocity at rear axle centre, SI units."""

from dataclasses import dataclass
from math import atan2, hypot, isfinite, pi


@dataclass(frozen=True)
class WheelCommands:
    front_left_rpm: float
    front_right_rpm: float
    rear_left_rpm: float
    rear_right_rpm: float
    front_left_steering_rad: float
    front_right_steering_rad: float


def wheel_commands(
    v: float,
    yaw_rate: float,
    radius: float,
    track: float,
    wheelbase: float,
    max_steering: float = 0.6,
) -> WheelCommands:
    """Ideal rolling commands. Reject infeasible turns rather than clip them."""
    if not all(isfinite(x) for x in (v, yaw_rate, radius, track, wheelbase, max_steering)):
        raise ValueError("Inputs must be finite")
    if min(radius, track, wheelbase) <= 0 or not 0 < max_steering < pi / 2:
        raise ValueError("Positive geometry and steering limit in (0, pi/2) required")
    if v == 0:
        if yaw_rate != 0:
            raise ValueError("Ackermann robot cannot rotate in place")
        return WheelCommands(0, 0, 0, 0, 0, 0)
    curvature = yaw_rate / v
    left = 1 - curvature * track / 2
    right = 1 + curvature * track / 2
    lateral = curvature * wheelbase
    angles = (atan2(lateral, left), atan2(lateral, right))
    if min(left, right) <= 0 or max(abs(a) for a in angles) > max_steering:
        raise ValueError("Requested turn exceeds steering geometry/limit")
    rpm = 60 / (2 * pi * radius)
    return WheelCommands(
        v * hypot(left, lateral) * rpm,
        v * hypot(right, lateral) * rpm,
        v * left * rpm,
        v * right * rpm,
        *angles,
    )


if __name__ == "__main__":
    c = wheel_commands(v=0.5, yaw_rate=0.3, radius=0.1, track=0.4, wheelbase=0.6)
    print(f"front_left={c.front_left_rpm:.3f} RPM, front_right={c.front_right_rpm:.3f} RPM")
    print(f"rear_left={c.rear_left_rpm:.3f} RPM, rear_right={c.rear_right_rpm:.3f} RPM")
    print(
        f"steering_left={c.front_left_steering_rad:.3f} rad, steering_right={c.front_right_steering_rad:.3f} rad"
    )
