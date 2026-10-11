#pragma once
#include <cmath>
#include <initializer_list>
#include <stdexcept>

namespace amr {
struct PlanarPose {
  double x = 0, y = 0, yaw = 0;
};
struct BodyVelocity {
  double v, w;
};
inline BodyVelocity measured_velocity(double rear_left, double rear_right, double steer_left,
                                      double steer_right, double radius, double track,
                                      double wheelbase) {
  for (double value : {rear_left, rear_right, steer_left, steer_right, radius, track, wheelbase}) {
    if (!std::isfinite(value)) {
      throw std::invalid_argument("Nonfinite odometry input");
    }
  }
  if (radius <= 0 || track <= 0 || wheelbase <= 0 || std::abs(steer_left) >= 1.5 ||
      std::abs(steer_right) >= 1.5) {
    throw std::invalid_argument("Invalid odometry geometry or steering");
  }
  const double tl = std::tan(steer_left), tr = std::tan(steer_right);
  const double dl = wheelbase + track * tl / 2;
  const double dr = wheelbase - track * tr / 2;
  if (dl <= 0 || dr <= 0) {
    throw std::invalid_argument("Infeasible steering geometry");
  }
  const double v = radius * (rear_left + rear_right) / 2;
  return {v, v * (tl / dl + tr / dr) / 2};
}
inline PlanarPose integrate(PlanarPose pose, BodyVelocity velocity, double dt) {
  if (!std::isfinite(dt) || dt < 0 || !std::isfinite(velocity.v) || !std::isfinite(velocity.w)) {
    throw std::invalid_argument("Invalid integration input");
  }
  const double angle = velocity.w * dt;
  const double half = angle / 2;
  const double sinc = std::abs(half) < 1e-8 ? 1.0 : std::sin(half) / half;
  pose.x += velocity.v * dt * sinc * std::cos(pose.yaw + half);
  pose.y += velocity.v * dt * sinc * std::sin(pose.yaw + half);
  pose.yaw = std::atan2(std::sin(pose.yaw + angle), std::cos(pose.yaw + angle));
  return pose;
}
} // namespace amr
