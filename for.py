#!/usr/bin/env python3

import sys
import tty
import termios

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import TwistStamped


CMD_TOPIC = "/diff_drive_controller/cmd_vel"

LINEAR_SPEED = 0.18
TURN_SPEED = 0.20


class SimpleTeleop(Node):

    def __init__(self):

        super().__init__("simple_teleop")

        self.publisher = self.create_publisher(
            TwistStamped,
            CMD_TOPIC,
            10
        )

        self.linear = 0.0
        self.angular = 0.0

        self.timer = self.create_timer(
            0.05,
            self.publish_cmd
        )

    # --------------------------------------------------

    def publish_cmd(self):

        msg = TwistStamped()

        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "base_link"

        msg.twist.linear.x = self.linear
        msg.twist.angular.z = self.angular

        self.publisher.publish(msg)


# ------------------------------------------------------

def get_key(settings):

    tty.setraw(sys.stdin.fileno())

    key = sys.stdin.read(1)

    termios.tcsetattr(
        sys.stdin,
        termios.TCSADRAIN,
        settings
    )

    return key


# ------------------------------------------------------

def main():

    rclpy.init()

    node = SimpleTeleop()

    settings = termios.tcgetattr(sys.stdin)

    print()
    print("========== SIMPLE TELEOP ==========")
    print(" w : Forward")
    print(" s : Backward")
    print(" a : Turn Left")
    print(" d : Turn Right")
    print(" SPACE : Stop")
    print(" Ctrl+C : Exit")
    print("===================================")

    try:

        while rclpy.ok():

            rclpy.spin_once(node, timeout_sec=0.0)

            key = get_key(settings)

            if key == 'w':

                node.linear = LINEAR_SPEED
                node.angular = 0.0
                print("Forward")

            elif key == 's':

                node.linear = -LINEAR_SPEED
                node.angular = 0.0
                print("Backward")

            elif key == 'a':

                node.linear = 0.0
                node.angular = TURN_SPEED
                print("Left")

            elif key == 'd':

                node.linear = 0.0
                node.angular = -TURN_SPEED
                print("Right")

            elif key == ' ':

                node.linear = 0.0
                node.angular = 0.0
                print("Stop")

    except KeyboardInterrupt:

        pass

    finally:

        node.linear = 0.0
        node.angular = 0.0

        node.publish_cmd()

        node.destroy_node()

        rclpy.shutdown()


if __name__ == "__main__":
    main()