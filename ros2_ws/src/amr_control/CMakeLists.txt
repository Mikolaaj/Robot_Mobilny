cmake_minimum_required(VERSION 3.8)
project(amr_control)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(std_msgs REQUIRED)

add_executable(ackermann_controller
  src/ackermann_controller.cpp
)

target_compile_features(ackermann_controller PRIVATE cxx_std_17)

target_compile_options(ackermann_controller PRIVATE
  -Wall -Wextra -Wpedantic
)

# Wspólny nagłówek kinematyki z fazy 1.
target_include_directories(ackermann_controller PRIVATE
  "${CMAKE_CURRENT_SOURCE_DIR}/../../../examples/phase1"
)

ament_target_dependencies(ackermann_controller
  rclcpp
  geometry_msgs
  std_msgs
)

install(
  TARGETS ackermann_controller
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(Python3 REQUIRED COMPONENTS Interpreter)

  add_test(
    NAME control_integration
    COMMAND "${Python3_EXECUTABLE}"
      "${CMAKE_CURRENT_SOURCE_DIR}/test/integration.py"
      "$<TARGET_FILE:ackermann_controller>"
  )

  set_tests_properties(control_integration PROPERTIES TIMEOUT 45)
endif()

ament_package()