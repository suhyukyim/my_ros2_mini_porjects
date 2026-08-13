import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class DrawShapeTime(Node):
    def __init__(self):
        super().__init__('draw_shape_time')
        self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

        self.current_distance = 0.0
        self.current_angle = 0.0
        self.target_distance = 2.0  # Move forward 2 units
        self.target_angle = 1.57  # Turn 90 degrees in radians
        self.mode = 'move'  # Start with moving forward
        self.timer_period = 0.1  # Timer period in seconds

        self.timer = self.create_timer(self.timer_period, self.timer_callback)

    def timer_callback(self):
        twist = Twist()
        if self.mode == 'move':
            twist.linear.x = 2.0
            twist.angular.z = 0.0
            self.publisher.publish(twist)
            self.current_distance += 2.0 * self.timer_period  # Increment distance based on timer frequency 
            if self.current_distance >= self.target_distance:
                self.mode = 'turn'
                self.current_distance = 0.0
        elif self.mode == 'turn':
            twist.linear.x = 0.0
            twist.angular.z = 1.57 # 90 degrees in radians
            self.publisher.publish(twist)
            self.current_angle += 1.57 * self.timer_period  # Increment angle based on timer frequency
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
