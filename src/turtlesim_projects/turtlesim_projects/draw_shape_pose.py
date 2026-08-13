import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from math import pi

class DrawShapePose(Node):
    def __init__(self):
        super().__init__('draw_shape_pose')
        self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

        self.subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10
        )

        self.mode = 'move'  # 'move' or 'turn'
        self.target_distance = 2.0
        self.side_count = 0
        self.timer_period = 0.1
        self.pose_recived = False  # Flag to indicate if the pose has been received

        # TODO: what else needs to be initialized here?
        # (e.g. where to remember the start of the current move/turn segment)
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_theta = 0.0
        self.start_x = 0.0
        self.start_y = 0.0
        self.start_theta = 0.0
        self.target_angle = 1.57  # 90 degrees in radians
        self.turn_gain = 1.5  # proportional gain: settle time ~= ln(target_angle/tolerance) / turn_gain
        self.timer = self.create_timer(self.timer_period, self.timer_callback)

    def pose_callback(self, msg):
        # TODO: store msg.x, msg.y, msg.theta so timer_callback can read them
        self.current_x = msg.x
        self.current_y = msg.y
        self.current_theta = msg.theta
        if not self.pose_recived:
            self.start_x = msg.x
            self.start_y = msg.y
            self.start_theta = msg.theta
            self.pose_recived = True

    def timer_callback(self):
        if not self.pose_recived:
            return  # Do nothing until the first pose message is received
        twist = Twist()
        if self.mode == 'move':
            twist.linear.x = 1.0  
            if ((self.current_x - self.start_x)**2 + (self.current_y-self.start_y)**2)**0.5  >= self.target_distance:
                self.mode = 'turn'
                self.start_theta = self.current_theta
        elif self.mode == 'turn':
            delta = self.current_theta - self.start_theta
            if delta < -pi:
                delta += 2 * pi
            elif delta > pi:
                delta -= 2 * pi
            remain = self.target_angle - abs(delta)
            if remain < 0.005:
                remain = 0.0
            else:
                twist.angular.z = self.turn_gain * remain
            if remain == 0.0:
                self.mode = 'move'
                self.start_x = self.current_x
                self.start_y = self.current_y
                self.start_theta = self.current_theta
                #self.side_count += 1
                #if self.side_count >= 4:
                    # Stop the turtle after completing the square
                #    twist.linear.x = 0.0
                #    twist.angular.z = 0.0
                #    self.timer.cancel()  # Stop the timer to stop moving
        self.publisher.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node = DrawShapePose()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
