#include "kinematics.hpp"
#include <cmath>
#include <iostream>

int main() {
  // Independently chosen cases: stationary, one full wheel turn/s, rotation.
  constexpr double pi = 3.14159265358979323846;
  const auto stopped = amr::wheel_speeds(0, 0, 0.1, 0.4);
  const auto straight = amr::wheel_speeds(2 * pi * 0.1, 0, 0.1, 0.4);
  const auto turn = amr::wheel_speeds(0, pi, 0.1, 0.4);
  const auto near = [](double a, double b) { return std::abs(a - b) < 1e-9; };
  if (!near(stopped.left_rpm, 0) || !near(stopped.right_rpm, 0) ||
      !near(straight.left_rpm, 60) || !near(straight.right_rpm, 60) ||
      !near(turn.left_rpm, -60) || !near(turn.right_rpm, 60)) {
    std::cerr << "Kinematics test failed\n";
    return 1;
  }
  try {
    amr::wheel_speeds(0, 0, 0, 0.4);
    return 1;
  } catch (const std::invalid_argument &) {
  }
  std::cout << "Kinematics tests passed\n";
}
