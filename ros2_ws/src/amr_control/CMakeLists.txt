cmake_minimum_required(VERSION 3.8)
project(amr_control)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(tf2_ros REQUIRED)

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

add_executable(ackermann_odometry src/ackermann_odometry.cpp)
target_compile_features(ackermann_odometry PRIVATE cxx_std_17)
target_compile_options(ackermann_odometry PRIVATE -Wall -Wextra -Wpedantic)
target_include_directories(ackermann_odometry PRIVATE include)
ament_target_dependencies(ackermann_odometry rclcpp sensor_msgs nav_msgs geometry_msgs tf2_ros)

install(
  TARGETS ackermann_controller ackermann_odometry
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  add_executable(test_odometry test/test_odometry.cpp)
  target_compile_features(test_odometry PRIVATE cxx_std_17)
  target_include_directories(test_odometry PRIVATE include)
  add_test(NAME odometry_math COMMAND test_odometry)
  find_package(Python3 REQUIRED COMPONENTS Interpreter)

  add_test(
    NAME control_integration
    COMMAND "${Python3_EXECUTABLE}"
      "${CMAKE_CURRENT_SOURCE_DIR}/test/integration.py"
      "$<TARGET_FILE:ackermann_controller>"
  )

  add_test(
    NAME odometry_integration
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/test/odometry_integration.py"
      "$<TARGET_FILE:ackermann_odometry>"
  )
  set_tests_properties(odometry_integration PROPERTIES TIMEOUT 30)
  set_tests_properties(control_integration PROPERTIES TIMEOUT 45)
endif()

ament_package()
