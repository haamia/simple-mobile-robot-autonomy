#!/usr/bin/env python3

import math

import rclpy
from rclpy.node import Node

from nav_msgs.msg import Odometry
from geometry_msgs.msg import TwistStamped


CMD_TOPIC = "/diff_drive_controller/cmd_vel"
ODOM_TOPIC = "/diff_drive_controller/odom"

LINEAR_SPEED = 0.18
TURN_SPEED = 0.20

FORWARD_DISTANCE = 2.0      # meters
TURN_ANGLE = math.radians(90)


class MoveThenTurn(Node):

    def __init__(self):

        super().__init__("move_then_turn")

        self.pub = self.create_publisher(
            TwistStamped,
            CMD_TOPIC,
            10
        )

        self.sub = self.create_subscription(
            Odometry,
            ODOM_TOPIC,
            self.odom_callback,
            10
        )

        self.started = False

        self.start_x = 0.0
        self.start_y = 0.0
        self.start_yaw = 0.0

        self.prev_yaw = 0.0
        self.total_rotation = 0.0

        self.state = "FORWARD"

        self.get_logger().info("Waiting for odometry...")

    # -------------------------------------------------

    def quaternion_to_yaw(self, q):

        siny = 2 * (q.w*q.z + q.x*q.y)
        cosy = 1 - 2 * (q.y*q.y + q.z*q.z)

        return math.atan2(siny, cosy)

    # -------------------------------------------------

    def normalize(self, a):

        while a > math.pi:
            a -= 2*math.pi

        while a < -math.pi:
            a += 2*math.pi

        return a

    # -------------------------------------------------

    def publish(self, linear, angular):

        msg = TwistStamped()

        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "base_link"

        msg.twist.linear.x = linear
        msg.twist.angular.z = angular

        self.pub.publish(msg)

    # -------------------------------------------------

    def odom_callback(self, msg):

        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y

        yaw = self.quaternion_to_yaw(
            msg.pose.pose.orientation
        )

        if not self.started:

            self.started = True

            self.start_x = x
            self.start_y = y
            self.start_yaw = yaw

            self.prev_yaw = yaw

            self.get_logger().info("Started")

            return

        # -----------------------------
        # Move Forward
        # -----------------------------

        if self.state == "FORWARD":

            dist = math.sqrt(
                (x-self.start_x)**2 +
                (y-self.start_y)**2
            )

            print(f"Distance = {dist:.2f}")

            if dist >= FORWARD_DISTANCE:

                self.publish(0.0,0.0)

                self.state = "TURN"

                self.prev_yaw = yaw
                self.total_rotation = 0.0

                self.get_logger().info("Starting 90 degree turn")

                return

            self.publish(
                LINEAR_SPEED,
                0.0
            )

            return

        # -----------------------------
        # Turn
        # -----------------------------

        if self.state == "TURN":

            delta = self.normalize(
                yaw-self.prev_yaw
            )

            self.total_rotation += abs(delta)

            self.prev_yaw = yaw

            print(
                f"Rotation = {math.degrees(self.total_rotation):.1f}"
            )

            if self.total_rotation >= TURN_ANGLE:

                self.publish(
                    0.0,
                    0.0
                )

                self.state = "DONE"

                self.get_logger().info("Finished")

                return

            self.publish(
                0.0,
                TURN_SPEED
            )

            return

        self.publish(0.0,0.0)


def main():

    rclpy.init()

    node = MoveThenTurn()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:

        node.publish(0.0,0.0)

        node.destroy_node()

        rclpy.shutdown()


if __name__ == "__main__":
    main()