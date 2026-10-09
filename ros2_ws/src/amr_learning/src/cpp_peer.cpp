#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"
#include "std_srvs/srv/trigger.hpp"
#include <memory>
#include <string>

class CppPeer : public rclcpp::Node {
public:
  CppPeer() : Node("cpp_peer") {
    const auto qos = rclcpp::QoS(rclcpp::KeepLast(10)).reliable().durability_volatile();
    publisher_ = create_publisher<std_msgs::msg::String>("phase2/cpp_message", qos);
    subscription_ = create_subscription<std_msgs::msg::String>(
        "phase2/python_message", qos, [this](std_msgs::msg::String::ConstSharedPtr message) {
          ++received_;
          RCLCPP_INFO(get_logger(), "Received: %s", message->data.c_str());
          std_msgs::msg::String reply;
          reply.data = "C++ reply: " + message->data;
          publisher_->publish(reply);
        });
    status_ = create_service<std_srvs::srv::Trigger>(
        "phase2/status", [this](const std::shared_ptr<std_srvs::srv::Trigger::Request>,
                                std::shared_ptr<std_srvs::srv::Trigger::Response> response) {
          response->success = true;
          response->message = "received=" + std::to_string(received_);
        });
  }

private:
  unsigned long received_{0};
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;
  rclcpp::Subscription<std_msgs::msg::String>::SharedPtr subscription_;
  rclcpp::Service<std_srvs::srv::Trigger>::SharedPtr status_;
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<CppPeer>());
  rclcpp::shutdown();
  return 0;
}
