#pragma once
#include <cmath>
#include <stdexcept>

namespace amr {
struct WheelSpeeds {
  double left_rpm;
  double right_rpm;
};

inline WheelSpeeds wheel_speeds(double v, double yaw_rate, double radius,
                                double track) {
  if (!std::isfinite(v) || !std::isfinite(yaw_rate) ||
      !std::isfinite(radius) || !std::isfinite(track) || radius <= 0 || track <= 0) {
    throw std::invalid_argument("Finite inputs and positive geometry required");
  }
  constexpr double pi = 3.14159265358979323846;
  const double to_rpm = 60.0 / (2.0 * pi * radius);
  return {(v - yaw_rate * track / 2.0) * to_rpm,
          (v + yaw_rate * track / 2.0) * to_rpm};
}
} // namespace amr
