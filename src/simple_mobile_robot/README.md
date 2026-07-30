# Simple Mobile Robot

This project presents a simple beginner-level mobile robot modeled using URDF and visualized in RViz2. It was developed as a learning project to understand robot modeling concepts in ROS 2, including links, joints, coordinate frames, and basic sensor integration.

The robot consists of a mobile base, differential drive wheels, a caster wheel, and common robotic sensors such as a LiDAR, IMU, and depth camera. The project serves as a foundation for learning URDF, TF transformations, RViz visualization, and robot simulation workflows.


## Robot Structure

```text
base_link
├── left_wheel
├── right_wheel
├── castor_wheel
├── lidar_link
├── imu_link
└── depth_camera_link
```

## Features

- URDF-based robot description
- Differential drive wheel configuration
- LiDAR sensor integration
- IMU sensor integration
- Depth camera integration
- RViz2 visualization
- Beginner-friendly ROS 2 project


## Robot Model

<p align="center">
  <img src="images/model3.png" width="700">
</p>



<p align="center">
  <img src="images/model4.png" width="700">
</p>



## Tools Used

- ROS2
- URDF
- RViz2

## Future Work

- Convert the model to Xacro
- Add inertial and collision properties
- Simulate the robot in Gazebo
- Integrate sensor plugins
- Implement robot control and navigation