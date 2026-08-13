import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import sys
import termios
import tty
import select

class CustomTeleop(Node):
    def __init__(self):
        super().__init__('custom_teleop')   
        self._publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)


def main(args=None):
    rclpy.init(args=args)
    node = CustomTeleop()

    get_key = termios.tcgetattr(sys.stdin)
    while True:
        try:
            tty.setraw(sys.stdin.fileno())
            ready, _, _ = select.select([sys.stdin], [], [], 1)
            if ready:
                key = sys.stdin.read(1)
                twist = Twist()
                if key == 'w':
                    twist.linear.x= 2.0
                elif key == 's':
                    twist.linear.x= -2.0
                elif key == 'a':
                    twist.angular.z = 2.0
                elif key == 'd':
                    twist.angular.z = -2.0
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

