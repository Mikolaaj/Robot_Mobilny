#include "amr_control/odometry.hpp"
#include <cmath>
#include <iostream>
#include <stdexcept>

void near(double actual, double expected) {
  if (std::abs(actual - expected) > 1e-8) {
    throw std::runtime_error("Odometry mismatch");
  }
}
int main() {
  auto straight = amr::measured_velocity(2, 2, 0, 0, .1, .4, .6);
  near(straight.v, .2);
  near(straight.w, 0);
  auto pose = amr::integrate({}, straight, 2);
  near(pose.x, .4);
  near(pose.y, 0);
  auto turn =
      amr::measured_velocity(1.8, 2.2, std::atan2(.06, .18), std::atan2(.06, .22), .1, .4, .6);
  near(turn.v, .2);
  near(turn.w, .1);
  pose = amr::integrate({}, turn, 10);
  near(pose.x, 2 * std::sin(1));
  near(pose.y, 2 * (1 - std::cos(1)));
  near(pose.yaw, 1);
  auto reverse = amr::integrate(pose, {-.2, -.1}, 10);
  near(reverse.x, 0);
  near(reverse.y, 0);
  near(reverse.yaw, 0);
  auto right = amr::integrate({}, {.2, -.1}, 10);
  near(right.x, pose.x);
  near(right.y, -pose.y);
  bool rejected = false;
  try {
    amr::measured_velocity(0, 0, 0, 0, 0, .4, .6);
  } catch (const std::invalid_argument &) {
    rejected = true;
  }
  if (!rejected) {
    return 1;
  }
  std::cout << "PASS: straight, turn, reverse, mirror, invalid geometry\n";
}
