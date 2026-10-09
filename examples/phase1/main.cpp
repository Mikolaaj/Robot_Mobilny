#include "kinematics.hpp"
#include <iomanip>
#include <iostream>

int main() {
  const auto speeds = amr::wheel_speeds(0.5, 1.0, 0.1, 0.4);
  std::cout << std::fixed << std::setprecision(3)
            << "left=" << speeds.left_rpm << " RPM, right=" << speeds.right_rpm
            << " RPM\n";
}
