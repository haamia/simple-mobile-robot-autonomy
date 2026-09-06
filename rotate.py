#!/usr/bin/env python3

import sys
import select
import termios
import tty

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import TwistStamped


CMD_TOPIC = "/diff_drive_controller/cmd_vel"
TURN_SPEED = 0.20


class RotateUntilX(Node):

    def __init__(self):

        super().__init__("rotate_until_x")

        self.publisher = self.create_publisher(
            TwistStamped,
            CMD_TOPIC,
            10
        )

        self.settings = termios.tcgetattr(sys.stdin)

        self.get_logger().info("")
        self.get_logger().info("==============================")
        self.get_logger().info(" Rotating...")
        self.get_logger().info(" Press X to Stop")
        self.get_logger().info("==============================")

    # ---------------------------------------------

    def get_key(self):

        tty.setraw(sys.stdin.fileno())

        rlist, _, _ = select.select(
            [sys.stdin],
            [],
            [],
            0.02
        )

        key = ""

        if rlist:
            key = sys.stdin.read(1)

        termios.tcsetattr(
            sys.stdin,
            termios.TCSADRAIN,
            self.settings
        )

        return key

    # ---------------------------------------------

    def publish(self, linear, angular):

        msg = TwistStamped()

        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "base_link"

        msg.twist.linear.x = linear
        msg.twist.angular.z = angular

        self.publisher.publish(msg)


def main():

    rclpy.init()

    node = RotateUntilX()

    try:

        while rclpy.ok():

            key = node.get_key()

            if key.lower() == "x":

                node.publish(
                    0.0,
                    0.0
                )

                print("\nStopped.")

                break

            node.publish(
                0.0,
                TURN_SPEED
            )

            rclpy.spin_once(
                node,
                timeout_sec=0.0
            )

    except KeyboardInterrupt:
        pass

    finally:

        node.publish(
            0.0,
            0.0
        )

        termios.tcsetattr(
            sys.stdin,
            termios.TCSADRAIN,
            node.settings
        )

        node.destroy_node()

        rclpy.shutdown()


if __name__ == "__main__":
    main()