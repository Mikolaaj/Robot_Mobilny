#pragma once
#include <cmath>
#include <stdexcept>

namespace amr {
struct WheelCommands {
  double front_left_rpm, front_right_rpm, rear_left_rpm, rear_right_rpm;
  double front_left_steering_rad, front_right_steering_rad;
};

inline WheelCommands wheel_commands(double v, double yaw_rate, double radius,
                                    double track, double wheelbase,
                                    double max_steering = 0.6) {
  constexpr double pi = 3.14159265358979323846;
  if (!std::isfinite(v) || !std::isfinite(yaw_rate) || !std::isfinite(radius) ||
      !std::isfinite(track) || !std::isfinite(wheelbase) ||
      !std::isfinite(max_steering) || radius <= 0 || track <= 0 ||
      wheelbase <= 0 || max_steering <= 0 || max_steering >= pi / 2) {
    throw std::invalid_argument("Invalid geometry or nonfinite input");
  }
  if (v == 0) {
    if (yaw_rate != 0) {
      throw std::invalid_argument("Ackermann robot cannot rotate in place");
    }
    return {0, 0, 0, 0, 0, 0};
  }
  const double curvature = yaw_rate / v;
  const double left = 1 - curvature * track / 2;
  const double right = 1 + curvature * track / 2;
  const double lateral = curvature * wheelbase;
  const double delta_left = std::atan2(lateral, left);
  const double delta_right = std::atan2(lateral, right);
  if (left <= 0 || right <= 0 || std::abs(delta_left) > max_steering ||
      std::abs(delta_right) > max_steering) {
    throw std::invalid_argument(
        "Requested turn exceeds steering geometry/limit");
  }
  const double rpm = 60 / (2 * pi * radius);
  return {v * std::hypot(left, lateral) * rpm,
          v * std::hypot(right, lateral) * rpm,
          v * left * rpm,
          v * right * rpm,
          delta_left,
          delta_right};
}
} // namespace amr
