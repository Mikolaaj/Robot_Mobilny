#include <array>
#include <chrono>
#include <memory>
#include <stdexcept>

#include "geometry_msgs/msg/twist.hpp"
#include "kinematics.hpp"
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/float64.hpp"

using namespace std::chrono_literals;

class AckermannController : public rclcpp::Node {
public:
  AckermannController() : Node("ackermann_controller") {
    const std::array<const char *, 6> topics = {
        "/amr/commands/front_left_velocity", "/amr/commands/front_right_velocity",
        "/amr/commands/rear_left_velocity",  "/amr/commands/rear_right_velocity",
        "/amr/commands/front_left_steering", "/amr/commands/front_right_steering"};

    for (std::size_t i = 0; i < topics.size(); ++i) {
      publishers_[i] = create_publisher<std_msgs::msg::Float64>(topics[i], 10);
    }

    subscription_ = create_subscription<geometry_msgs::msg::Twist>(
        "/cmd_vel", 1, [this](const geometry_msgs::msg::Twist::SharedPtr msg) {
          try {
            commands_ = amr::wheel_commands(msg->linear.x, msg->angular.z, 0.10, 0.40, 0.60, 0.60);

            last_command_ = std::chrono::steady_clock::now();
            active_ = true;
          } catch (const std::invalid_argument &error) {
            commands_ = {};
            active_ = false;
            RCLCPP_WARN(get_logger(), "Rejected command: %s", error.what());
          }
        });

    timer_ = create_wall_timer(20ms, [this]() {
      if (active_ && std::chrono::steady_clock::now() - last_command_ > 500ms) {
        commands_ = {};
        active_ = false;
        RCLCPP_WARN(get_logger(), "Command timeout: stopping robot");
      }

      publish_commands();
    });

    RCLCPP_INFO(get_logger(), "4WD Ackermann controller ready");
  }

private:
  void publish_commands() {
    // Kinematyka zwraca RPM, a Gazebo oczekuje rad/s.
    constexpr double rpm_to_rad_s = 2.0 * 3.14159265358979323846 / 60.0;

    const std::array<double, 6> values = {
        commands_.front_left_rpm * rpm_to_rad_s, commands_.front_right_rpm * rpm_to_rad_s,
        commands_.rear_left_rpm * rpm_to_rad_s,  commands_.rear_right_rpm * rpm_to_rad_s,
        commands_.front_left_steering_rad,       commands_.front_right_steering_rad};

    for (std::size_t i = 0; i < values.size(); ++i) {
      std_msgs::msg::Float64 msg;
      msg.data = values[i];
      publishers_[i]->publish(msg);
    }
  }

  amr::WheelCommands commands_{};
  bool active_{false};
  std::chrono::steady_clock::time_point last_command_{};

  std::array<rclcpp::Publisher<std_msgs::msg::Float64>::SharedPtr, 6> publishers_;

  rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr subscription_;
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<AckermannController>());
  rclcpp::shutdown();
  return 0;
}