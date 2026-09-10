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

from geometry_msgs.msg import Twist
from rcl_interfaces.msg import SetParametersResult
import rclpy
from rclpy.node import Node


class DrawShapeTime(Node):

    def __init__(self):
        super().__init__('draw_shape_time')
        self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

        self.declare_parameter('target_distance', 2.0)
        self.declare_parameter('target_angle', 1.57)
        self.declare_parameter('linear_speed', 2.0)
        self.declare_parameter('angular_speed', 1.57)
        self.declare_parameter('timer_period', 0.1)

        self.current_distance = 0.0
        self.current_angle = 0.0
        self.target_distance = self.get_parameter('target_distance').value  # Move forward N units
        self.target_angle = self.get_parameter('target_angle').value  # Turn N radians
        self.linear_speed = self.get_parameter('linear_speed').value
        self.angular_speed = self.get_parameter('angular_speed').value
        self.mode = 'move'  # Start with moving forward
        self.timer_period = self.get_parameter('timer_period').value  # Timer period in seconds

        self.timer = self.create_timer(self.timer_period, self.timer_callback)
        self.add_on_set_parameters_callback(self.parameter_callback)

    def parameter_callback(self, params):
        for param in params:
            if param.name in ('target_distance', 'target_angle', 'linear_speed', 'angular_speed'):
                setattr(self, param.name, param.value)
        return SetParametersResult(successful=True)

    def timer_callback(self):
        twist = Twist()
        if self.mode == 'move':
            twist.linear.x = self.linear_speed
            twist.angular.z = 0.0
            self.publisher.publish(twist)
            # Increment distance based on timer frequency
            self.current_distance += self.linear_speed * self.timer_period
            if self.current_distance >= self.target_distance:
                self.mode = 'turn'
                self.current_distance = 0.0
        elif self.mode == 'turn':
            twist.linear.x = 0.0
            twist.angular.z = self.angular_speed
            self.publisher.publish(twist)
            # Increment angle based on timer frequency
            self.current_angle += self.angular_speed * self.timer_period
            if self.current_angle >= self.target_angle:
                self.mode = 'move'
                self.current_angle = 0.0


def main(args=None):
    rclpy.init(args=args)
    node = DrawShapeTime()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
