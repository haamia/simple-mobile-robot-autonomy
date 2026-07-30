
 
from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription,
    RegisterEventHandler,
    OpaqueFunction,
)
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

from ament_index_python.packages import get_package_share_directory

import os
import xacro


def generate_launch_description():

    def robot_state_publisher(context):

        pkg_path = get_package_share_directory(
            "simple_mobile_robot"
        )

        xacro_file = os.path.join(
            pkg_path,
            "urdf",
            "simple_robot.urdf.xacro"
        )

        robot_description = xacro.process_file(
            xacro_file
        ).toxml()

        return [
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                output="screen",
                parameters=[
                    {
                        "robot_description": robot_description
                    }
                ],
            )
        ]

    world_file = os.path.join(
    get_package_share_directory("simple_mobile_robot"),
    "worlds",
    "empty_with_sensors.sdf",
     )

    gazebo = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(
        PathJoinSubstitution(
            [
                FindPackageShare("ros_gz_sim"),
                "launch",
                "gz_sim.launch.py",
            ]
        )
    ),
    launch_arguments={
        "gz_args": "-r " + world_file
    }.items(),
    ) 

    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
          "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
          "/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan",
          "/imu@sensor_msgs/msg/Imu[gz.msgs.IMU",
          "/camera@sensor_msgs/msg/Image[gz.msgs.Image",
          "/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo",
          "/camera/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked",
        ],
        output="screen",
    )

    spawn_robot = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-topic",
            "robot_description",
            "-name",
            "simple_mobile_robot",
            "-allow_renaming",
            "true",
        ],
        output="screen",
    )

    joint_state_broadcaster = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster"
        ],
    )

    diff_drive_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "diff_drive_controller",
            "--param-file",
            PathJoinSubstitution(
                [
                    FindPackageShare("simple_mobile_robot"),
                    "config",
                    "controllers.yaml",
                ]
            ),
        ],
    )

    return LaunchDescription(

        [

            gazebo,

            bridge,

            OpaqueFunction(
                function=robot_state_publisher
            ),

            spawn_robot,

            RegisterEventHandler(
                OnProcessExit(
                    target_action=spawn_robot,
                    on_exit=[
                        joint_state_broadcaster
                    ],
                )
            ),

            RegisterEventHandler(
                OnProcessExit(
                    target_action=joint_state_broadcaster,
                    on_exit=[
                        diff_drive_controller
                    ],
                )
            ),

        ]

    )
    


    