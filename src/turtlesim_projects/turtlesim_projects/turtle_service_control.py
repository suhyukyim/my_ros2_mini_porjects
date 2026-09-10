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

from rcl_interfaces.msg import SetParametersResult
import rclpy
from rclpy.node import Node
from std_srvs.srv import Empty
from turtlesim.srv import Kill, SetPen, Spawn


class TurtleServiceControl(Node):

    def call_service(self, name, client, request):
        future = client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        self.get_logger().info(f'{name} completed: {future.result()}')
        return future.result()

    def __init__(self):
        super().__init__('turtle_service_control')

        # reset
        self.empty_client = self.create_client(Empty, '/reset')
        while not self.empty_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /reset service...')

        # spawn
        self.spawn_client = self.create_client(Spawn, '/spawn')
        while not self.spawn_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /spawn service...')

        # set_pen
        self.set_pen_client = self.create_client(SetPen, '/turtle1/set_pen')
        while not self.set_pen_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /set_pen service...')

        # kill
        self.kill_client = self.create_client(Kill, '/kill')
        while not self.kill_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /kill service...')

        self.declare_parameter('spawn_x', 0.0)
        self.declare_parameter('spawn_y', 0.0)
        self.declare_parameter('pen_r', 255)
        self.declare_parameter('pen_g', 0)
        self.declare_parameter('pen_b', 0)
        self.declare_parameter('pen_width', 3)
        self.spawn_x = self.get_parameter('spawn_x').value
        self.spawn_y = self.get_parameter('spawn_y').value
        self.pen_r = self.get_parameter('pen_r').value
        self.pen_g = self.get_parameter('pen_g').value
        self.pen_b = self.get_parameter('pen_b').value
        self.pen_width = self.get_parameter('pen_width').value

        self.add_on_set_parameters_callback(self.parameter_callback)

        self.do_reset()
        self.do_spawn(self.spawn_x, self.spawn_y, 0.0, 'turtle2')
        self.do_set_pen(r=self.pen_r, g=self.pen_g, b=self.pen_b, width=self.pen_width, off=0)
        self.do_kill('turtle2')

    def parameter_callback(self, params):
        for param in params:
            if param.name in ('pen_r', 'pen_g', 'pen_b', 'pen_width'):
                setattr(self, param.name, param.value)
        return SetParametersResult(successful=True)

    def do_spawn(self, x, y, theta, name):
        spawn_request = Spawn.Request()
        spawn_request.x = x
        spawn_request.y = y
        spawn_request.theta = theta
        spawn_request.name = name
        spawn_response = self.call_service('Spawn', self.spawn_client, spawn_request)
        return spawn_response

    def do_kill(self, name):
        kill_request = Kill.Request()
        kill_request.name = name
        kill_response = self.call_service('Kill', self.kill_client, kill_request)
        return kill_response

    def do_set_pen(self, r, g, b, width, off):
        set_pen_request = SetPen.Request()
        set_pen_request.r = r
        set_pen_request.g = g
        set_pen_request.b = b
        set_pen_request.width = width
        set_pen_request.off = off
        set_pen_response = self.call_service('SetPen', self.set_pen_client, set_pen_request)
        return set_pen_response

    def do_reset(self):
        empty_request = Empty.Request()
        empty_response = self.call_service('Reset', self.empty_client, empty_request)
        return empty_response


def main(args=None):
    rclpy.init(args=args)
    node = TurtleServiceControl()
    # s=spawn, k=kill, p=set_pen, r=reset, Ctrl+C=종료
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
                if key == 's':
                    node.do_spawn(1., 1., 0., 'turtle2')
                elif key == 'k':
                    node.do_kill('turtle2')
                elif key == 'p':
                    node.do_set_pen(node.pen_r, node.pen_g, node.pen_b, node.pen_width, 0)
                elif key == 'r':
                    node.do_reset()
                elif key == '\x03':
                    break
            else:
                continue
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, get_key)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
