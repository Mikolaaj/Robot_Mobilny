#include "kinematics.hpp"
#include <cmath>
#include <iostream>
#include <limits>

int main() {
  constexpr double pi = 3.14159265358979323846;
  const auto near = [](double a, double b) { return std::abs(a - b) < 1e-9; };
  const auto check = [](bool condition) {
    if (!condition)
      throw std::runtime_error("Kinematics test failed");
  };
  const auto stop = amr::wheel_commands(0, 0, 1, 1, 1);
  check(near(stop.front_left_rpm, 0) && near(stop.front_right_rpm, 0) &&
        near(stop.rear_left_rpm, 0) && near(stop.rear_right_rpm, 0) &&
        near(stop.front_left_steering_rad, 0) &&
        near(stop.front_right_steering_rad, 0));
  const auto straight = amr::wheel_commands(2 * pi, 0, 1, 1, 1);
  check(near(straight.front_left_rpm, 60) &&
        near(straight.front_right_rpm, 60) &&
        near(straight.rear_left_rpm, 60) && near(straight.rear_right_rpm, 60));
  const auto turn = amr::wheel_commands(1, 1, 1, 1, 1, 1.3);
  const double factor = 60 / (2 * pi);
  check(near(turn.rear_left_rpm, .5 * factor) &&
        near(turn.rear_right_rpm, 1.5 * factor) &&
        near(turn.front_left_rpm, std::sqrt(1.25) * factor) &&
        near(turn.front_right_rpm, std::sqrt(3.25) * factor) &&
        near(turn.front_left_steering_rad, std::atan(2)) &&
        near(turn.front_right_steering_rad, std::atan(2.0 / 3)));
  const auto reverse = amr::wheel_commands(-1, -1, 1, 1, 1, 1.3);
  check(near(reverse.front_left_rpm, -turn.front_left_rpm) &&
        near(reverse.front_right_rpm, -turn.front_right_rpm) &&
        near(reverse.rear_left_rpm, -turn.rear_left_rpm) &&
        near(reverse.rear_right_rpm, -turn.rear_right_rpm) &&
        near(reverse.front_left_steering_rad, turn.front_left_steering_rad));
  const auto right = amr::wheel_commands(1, -1, 1, 1, 1, 1.3);
  check(near(right.front_left_rpm, turn.front_right_rpm) &&
        near(right.rear_left_rpm, turn.rear_right_rpm) &&
        near(right.front_left_steering_rad, -turn.front_right_steering_rad));
  const auto rejects = [&](double v, double w, double r, double t, double l,
                           double limit = .6) {
    bool rejected = false;
    try {
      amr::wheel_commands(v, w, r, t, l, limit);
    } catch (const std::invalid_argument &) {
      rejected = true;
    }
    check(rejected);
  };
  rejects(0, 1, 1, 1, 1);
  rejects(1, 0, 0, 1, 1);
  rejects(1, 0, 1, -1, 1);
  rejects(1, 0, 1, 1, 0);
  rejects(std::numeric_limits<double>::quiet_NaN(), 0, 1, 1, 1);
  rejects(1, 0, 1, 1, 1, std::numeric_limits<double>::infinity());
  rejects(1, 1, 1, 1, 1);
  rejects(1, 4, 1, 1, 1);
  rejects(1, 0, 1, 1, 1, 0);
  std::cout << "Ackermann tests passed\n";
}
