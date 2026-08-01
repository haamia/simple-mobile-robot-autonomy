#!/usr/bin/env python3

import math

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import TwistStamped


# ======================================================
# Topics
# ======================================================

CMD_TOPIC = "/diff_drive_controller/cmd_vel"
SCAN_TOPIC = "/scan"


# ======================================================
# Robot Parameters
# ======================================================

LINEAR_SPEED = 0.18
TURN_SPEED = 0.40

SAFE_DISTANCE = 0.70
MIN_VALID_RANGE = 0.10


class AutoMapper(Node):

    def __init__(self):

        super().__init__("auto_mapper")

        self.scan = None
        self.turn_direction = None

        self.publisher = self.create_publisher(
            TwistStamped,
            CMD_TOPIC,
            10
        )

        self.subscription = self.create_subscription(
            LaserScan,
            SCAN_TOPIC,
            self.scan_callback,
            10
        )

        self.timer = self.create_timer(
            0.05,
            self.control_loop
        )

        self.get_logger().info("Auto Mapper Started")

    # ==================================================

    def scan_callback(self, msg):
        self.scan = msg

    # ==================================================

    def publish(self, linear, angular):

        msg = TwistStamped()

        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "base_link"

        msg.twist.linear.x = linear
        msg.twist.angular.z = angular

        self.publisher.publish(msg)

    # ==================================================

    def sector_distance(self, start_deg, end_deg):

        values = []

        for i, r in enumerate(self.scan.ranges):

            if math.isnan(r) or math.isinf(r):
                continue

            if r < MIN_VALID_RANGE:
                continue

            if r > self.scan.range_max:
                continue

            angle = math.degrees(
                self.scan.angle_min +
                i * self.scan.angle_increment
            )

            if start_deg <= angle <= end_deg:
                values.append(r)

        if len(values) == 0:
            return self.scan.range_max

        return min(values)

    # ==================================================

    def front_distance(self):

        front1 = self.sector_distance(165, 180)
        front2 = self.sector_distance(-180, -165)

        return min(front1, front2)

    # ==================================================

    def closest_obstacle(self):

        closest_distance = self.scan.range_max
        closest_angle = 0.0

        for i, r in enumerate(self.scan.ranges):

            if math.isnan(r) or math.isinf(r):
                continue

            if r < MIN_VALID_RANGE:
                continue

            if r > self.scan.range_max:
                continue

            if r < closest_distance:

                closest_distance = r

                closest_angle = math.degrees(
                    self.scan.angle_min +
                    i * self.scan.angle_increment
                )

        return closest_distance, closest_angle

    # ==================================================

    def control_loop(self):

        if self.scan is None:
            return

        # -----------------------------
        # LiDAR sectors
        # -----------------------------

        front = self.front_distance()

        front_left = self.sector_distance(135, 165)

        front_right = self.sector_distance(-165, -135)

        left = self.sector_distance(90, 135)

        right = self.sector_distance(-135, -90)

        closest_distance, closest_angle = self.closest_obstacle()

        print("\n========================================")
        print(f"Front            : {front:.2f}")
        print(f"Front Left       : {front_left:.2f}")
        print(f"Front Right      : {front_right:.2f}")
        print(f"Left             : {left:.2f}")
        print(f"Right            : {right:.2f}")
        print("----------------------------------------")
        print(f"Closest Distance : {closest_distance:.2f}")
        print(f"Closest Angle    : {closest_angle:.1f}°")

        obstacle = (
            front < SAFE_DISTANCE or
            front_left < SAFE_DISTANCE or
            front_right < SAFE_DISTANCE
        )

        if obstacle:

            if self.turn_direction is None:

                if front_left < front_right:
                    self.turn_direction = "right"

                elif front_right < front_left:
                    self.turn_direction = "left"

                elif left > right:
                    self.turn_direction = "left"

                else:
                    self.turn_direction = "right"

                print(f"Obstacle Detected -> Turning {self.turn_direction.upper()}")

            if self.turn_direction == "left":

                self.publish(
                    0.0,
                    TURN_SPEED
                )

            else:

                self.publish(
                    0.0,
                    -TURN_SPEED
                )

            return

        self.turn_direction = None

        print("Moving Forward")

        self.publish(
            LINEAR_SPEED,
            0.0
        )


# ======================================================



def main():

    rclpy.init()

    node = AutoMapper()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:

        try:
            node.publish(0.0, 0.0)
        except Exception:
            pass

        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()