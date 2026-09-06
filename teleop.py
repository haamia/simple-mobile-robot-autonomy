import sys
import tty
import termios

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped


KEYS = {
    'w': ( 0.20,  0.00),   # forward
    's': (-0.20,  0.00),   # backward
    'a': ( 0.00,  0.50),   # turn left
    'd': ( 0.00, -0.50),   # turn right
    'q': ( 0.20,  0.50),   # forward + left
    'e': ( 0.20, -0.50),   # forward + right
    ' ': ( 0.00,  0.00),   # stop
}

BANNER = """
Teleop Keyboard — TwistStamped
-------------------------------
   q    w    e
   a    s    d

w/s : forward / backward
a/d : turn left / right
q/e : forward + turn
SPACE : stop
CTRL+C : quit
-------------------------------
"""


def get_key(settings):
    tty.setraw(sys.stdin.fileno())
    key = sys.stdin.read(1)
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key


class TeleopKeyboard(Node):

    def __init__(self):
        super().__init__("teleop_keyboard")

        self.cmd_pub = self.create_publisher(
            TwistStamped,
            "/diff_drive_controller/cmd_vel",
            10
        )

        self.LINEAR_SPEED  = 0.20
        self.TURN_SPEED    = 0.50

        self.get_logger().info("Teleop Keyboard Node Started")

    def publish(self, linear, angular):
        cmd = TwistStamped()
        cmd.header.stamp    = self.get_clock().now().to_msg()
        cmd.header.frame_id = "base_link"
        cmd.twist.linear.x  = linear
        cmd.twist.angular.z = angular
        self.cmd_pub.publish(cmd)
        print(f"Linear: {linear:.2f}   Angular: {angular:.2f}")

    def stop(self):
        self.publish(0.0, 0.0)


def main(args=None):
    rclpy.init(args=args)
    node = TeleopKeyboard()

    settings = termios.tcgetattr(sys.stdin)

    print(BANNER)

    try:
        while rclpy.ok():
            key = get_key(settings)

            if key == '\x03':   # CTRL+C
                break

            if key in KEYS:
                linear, angular = KEYS[key]
                node.publish(linear, angular)
            else:
                # unknown key — stop
                node.publish(0.0, 0.0)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        node.stop()
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()