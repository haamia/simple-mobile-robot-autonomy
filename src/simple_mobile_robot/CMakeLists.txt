cmake_minimum_required(VERSION 3.8)
project(simple_mobile_robot)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY
    launch
    urdf
    rviz
    worlds
    config
  DESTINATION share/${PROJECT_NAME}
)

ament_package()