# Copyright 2026 suhyuk
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import select
import sys
import termios
import tty

from geometry_msgs.msg import Twist
from rcl_interfaces.msg import SetParametersResult
import rclpy
from rclpy.node import Node


class CustomTeleop(Node):

    def __init__(self):
        super().__init__('custom_teleop')
        self._publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.declare_parameter('linear_speed', 2.0)
        self.declare_parameter('angular_speed', 2.0)
        self.linear_speed = self.get_parameter('linear_speed').value
        self.angular_speed = self.get_parameter('angular_speed').value
        self.add_on_set_parameters_callback(self.parameter_callback)

    def parameter_callback(self, params):
        for param in params:
            if param.name in ('linear_speed', 'angular_speed'):
                setattr(self, param.name, param.value)
        return SetParametersResult(successful=True)


def main(args=None):
    rclpy.init(args=args)
    node = CustomTeleop()

    get_key = termios.tcgetattr(sys.stdin)
    while True:
        try:
            tty.setraw(sys.stdin.fileno())
            # spin_once services pending calls (e.g. rqt parameter changes) between
            # keystrokes, since this loop never calls rclpy.spin().
            rclpy.spin_once(node, timeout_sec=0)
            ready, _, _ = select.select([sys.stdin], [], [], 0.1)
            if ready:
                key = sys.stdin.read(1)
                twist = Twist()
                if key == 'w':
                    twist.linear.x = node.linear_speed
                elif key == 's':
                    twist.linear.x = -node.linear_speed
                elif key == 'a':
                    twist.angular.z = node.angular_speed
                elif key == 'd':
                    twist.angular.z = -node.angular_speed
                elif key == '\x03':  # Ctrl+C
                    break
                node._publisher.publish(twist)
            else:
                continue

        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, get_key)

    twist = Twist()  # Stop the turtle when exiting
    node._publisher.publish(twist)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
