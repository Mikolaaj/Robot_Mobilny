#include <array>
#include <memory>
#include <optional>
#include <string>
#include <unordered_map>

#include "amr_control/odometry.hpp"
#include "geometry_msgs/msg/transform_stamped.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/joint_state.hpp"
#include "tf2_ros/transform_broadcaster.h"

class AckermannOdometry : public rclcpp::Node {
public:
  AckermannOdometry() : Node("ackermann_odometry") {
    radius_ = declare_parameter("wheel_radius", 0.10);
    track_ = declare_parameter("wheel_track", 0.40);
    wheelbase_ = declare_parameter("wheelbase", 0.60);
    max_dt_ = declare_parameter("max_dt", 0.5);
    amr::measured_velocity(0, 0, 0, 0, radius_, track_, wheelbase_);
    if (!std::isfinite(max_dt_) || max_dt_ <= 0) {
      throw std::invalid_argument("max_dt must be positive and finite");
    }
    publisher_ = create_publisher<nav_msgs::msg::Odometry>("/odom", 10);
    broadcaster_ = std::make_unique<tf2_ros::TransformBroadcaster>(*this);
    subscription_ = create_subscription<sensor_msgs::msg::JointState>(
        "/joint_states", 10,
        [this](sensor_msgs::msg::JointState::ConstSharedPtr msg) { update(*msg); });
    RCLCPP_INFO(get_logger(), "Measured Ackermann odometry ready: odom -> base_link");
  }

private:
  void update(const sensor_msgs::msg::JointState &msg) {
    std::unordered_map<std::string, std::size_t> indices;
    for (std::size_t i = 0; i < msg.name.size(); ++i) {
      indices[msg.name[i]] = i;
    }
    const std::array<std::string, 4> names = {"rear_left_wheel_joint", "rear_right_wheel_joint",
                                              "front_left_steering_joint",
                                              "front_right_steering_joint"};
    for (const auto &name : names) {
      if (indices.count(name) == 0) {
        return;
      }
    }
    const auto l = indices[names[0]], r = indices[names[1]];
    const auto sl = indices[names[2]], sr = indices[names[3]];
    if (l >= msg.velocity.size() || r >= msg.velocity.size() || sl >= msg.position.size() ||
        sr >= msg.position.size()) {
      return;
    }
    amr::BodyVelocity velocity;
    try {
      velocity = amr::measured_velocity(msg.velocity[l], msg.velocity[r], msg.position[sl],
                                        msg.position[sr], radius_, track_, wheelbase_);
    } catch (const std::invalid_argument &) {
      return;
    }
    const int64_t stamp = rclcpp::Time(msg.header.stamp).nanoseconds();
    if (previous_stamp_) {
      const double dt = (stamp - *previous_stamp_) * 1e-9;
      if (dt == 0) {
        return;
      }
      if (dt < 0) {
        pose_ = {}; // New simulation epoch after reset.
      } else if (dt <= max_dt_) {
        pose_ = amr::integrate(pose_, velocity, dt);
      }
      // A long data gap is not extrapolated with an unknown historical speed.
    }
    previous_stamp_ = stamp;
    nav_msgs::msg::Odometry odom;
    odom.header = msg.header;
    odom.header.frame_id = "odom";
    odom.child_frame_id = "base_link";
    odom.pose.pose.position.x = pose_.x;
    odom.pose.pose.position.y = pose_.y;
    odom.pose.pose.orientation.z = std::sin(pose_.yaw / 2);
    odom.pose.pose.orientation.w = std::cos(pose_.yaw / 2);
    odom.twist.twist.linear.x = velocity.v;
    odom.twist.twist.angular.z = velocity.w;
    // Initial engineering estimates, not calibrated sensor uncertainty.
    odom.pose.covariance[0] = odom.pose.covariance[7] = 0.01;
    odom.pose.covariance[35] = 0.02;
    odom.twist.covariance[0] = odom.twist.covariance[35] = 0.01;
    for (const auto i : {14, 21, 28}) {
      odom.pose.covariance[i] = odom.twist.covariance[i] = 1e6;
    }
    publisher_->publish(odom);
    geometry_msgs::msg::TransformStamped tf;
    tf.header = odom.header;
    tf.child_frame_id = odom.child_frame_id;
    tf.transform.translation.x = pose_.x;
    tf.transform.translation.y = pose_.y;
    tf.transform.rotation = odom.pose.pose.orientation;
    broadcaster_->sendTransform(tf);
  }
  double radius_, track_, wheelbase_, max_dt_;
  amr::PlanarPose pose_;
  std::optional<int64_t> previous_stamp_;
  rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr publisher_;
  rclcpp::Subscription<sensor_msgs::msg::JointState>::SharedPtr subscription_;
  std::unique_ptr<tf2_ros::TransformBroadcaster> broadcaster_;
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<AckermannOdometry>());
  rclcpp::shutdown();
  return 0;
}
