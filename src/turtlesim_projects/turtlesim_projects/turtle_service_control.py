import rclpy
from rclpy.node import Node
from turtlesim.srv import Spawn, Kill, SetPen
from std_srvs.srv import Empty   
import sys
import termios
import tty
import select

class TurtleServiceControl(Node):
    def call_service(self, name ,client, request):
        future = client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        self.get_logger().info(f'{name} completed: {future.result()}')
        return future.result()
    
    def __init__(self):
        super().__init__('turtle_service_control')

        #reset
        self.empty_client = self.create_client(Empty, '/reset')
        while not self.empty_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /reset service...')

        #spawn
        self.spawn_client = self.create_client(Spawn, '/spawn')
        while not self.spawn_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /spawn service...')

        #set_pen
        self.set_pen_client = self.create_client(SetPen, '/turtle1/set_pen')
        while not self.set_pen_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /set_pen service...')

        #kill
        self.kill_client = self.create_client(Kill, '/kill')
        while not self.kill_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /kill service...')

        self.do_reset()
        self.do_spawn(0.0,0.0,0.0,'turtle2')
        self.do_set_pen(r=255,g=0,b=0,width=3,off=0)
        self.do_kill('turtle2')
    

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
            ready, _, _ = select.select([sys.stdin], [], [],1)
            if ready:
                key = sys.stdin.read(1)
                if key == "s":
                    node.do_spawn(1. , 1. , 0. , 'turtle2')
                elif key == "k":
                    node.do_kill('turtle2')
                elif key == "p":
                    node.do_set_pen(255,255,0,3,0)
                elif key == "r":
                    node.do_reset()
                elif key == '\x03' :
                    break
            else:
                continue
        finally:
            termios.tcsetattr(sys.stdin,termios.TCSADRAIN,get_key)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
