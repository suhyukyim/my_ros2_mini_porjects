import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtlesim.srv import Spawn
import math

class TurtleChase(Node):
    def __init__(self):
        super().__init__('turtle_chase')
        # TODO: spawn turtle2, subscribe to /turtle1/pose and /turtle2/pose,
        # publish to /turtle2/cmd_vel to chase turtle1
        self.publisher_2 = self.create_publisher(Twist, '/turtle2/cmd_vel', 10)

        spawn_client = self.create_client(Spawn, '/spawn')
        while not spawn_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /spawn service...')
        request = Spawn.Request()
        request.x = 0.0
        request.y = 0.0
        request.theta = 0.0
        request.name = 'turtle2'
        future = spawn_client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        response = future.result()
        self.get_logger().info(f'Spawned: {response.name}')

        # s
        # subcribe
        self.subscription_1 = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback_1,
            10
        )
        self.subscription_2 = self.create_subscription(
            Pose,
            '/turtle2/pose',
            self.pose_callback_2,
            10
        )

        #vlaue init
        self.turtle1_x = 0.0
        self.turtle1_y = 0.0
        self.turtle1_theta = 0.0
        self.turtle2_x = 0.0
        self.turtle2_y = 0.0
        self.turtle2_theta = 0.0
        self.timer_period = 0.1  # seconds

        #timer
        self.timer = self.create_timer(self.timer_period, self.timer_callback)



    #callback
    def pose_callback_1(self, msg):
        self.turtle1_x = msg.x
        self.turtle1_y = msg.y
        self.turtle1_theta = msg.theta

    def pose_callback_2(self, msg):
        self.turtle2_x = msg.x
        self.turtle2_y = msg.y
        self.turtle2_theta = msg.theta

    def timer_callback(self):
        #거리오차
        distance = ((self.turtle1_x - self.turtle2_x)**2 + (self.turtle1_y - self.turtle2_y)**2)**0.5
        #목표 각도
        target_angle = math.atan2(self.turtle1_y - self.turtle2_y, self.turtle1_x - self.turtle2_x)    
        #각도오차
        angle_error = target_angle - self.turtle2_theta
        if angle_error > math.pi:
            angle_error -= 2 * math.pi
        elif angle_error < -math.pi:
            angle_error += 2 * math.pi
        #속도 제어
        twist = Twist()
        twist.linear.x = 1.0 * distance
        twist.angular.z = 1.0 * angle_error
        self.publisher_2.publish(twist) 

def main(args=None):
    rclpy.init(args=args)
    node = TurtleChase()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
