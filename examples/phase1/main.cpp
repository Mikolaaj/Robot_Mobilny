#include "kinematics.hpp"
#include <iomanip>
#include <iostream>

int main() {
  const auto c = amr::wheel_commands(0.5, 0.3, 0.1, 0.4, 0.6);
  std::cout << std::fixed << std::setprecision(3) << "front_left=" << c.front_left_rpm
            << " RPM, front_right=" << c.front_right_rpm << " RPM\n"
            << "rear_left=" << c.rear_left_rpm << " RPM, rear_right=" << c.rear_right_rpm
            << " RPM\n"
            << "steering_left=" << c.front_left_steering_rad
            << " rad, steering_right=" << c.front_right_steering_rad << " rad\n";
}
