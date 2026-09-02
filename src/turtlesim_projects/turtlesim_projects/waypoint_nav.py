import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
import math

class WaypointNav(Node):
    def __init__(self):
        super().__init__('waypoint_nav')
        # TODO: hold a list of waypoints, subscribe to /turtle1/pose,
        # publish to /turtle1/cmd_vel, advance to next waypoint on arrival
        self.publisher = self.create_publisher (Twist, '/turtle1/cmd_vel',10)

        self.subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10
        )

        self.waypoint = [(2.0,2.0),(3.0,2.0),(2.0,3.0),(3.0,3.0),(5.0,5.0)] # (x,y)
        self.index = 0 
        self.finished = False
        self.length = len(self.waypoint)
        self.cur_x = 5.0
        self.cur_y = 5.0
        self.cur_theata = 0.0
        self.time_period = 0.1
        self.max_speed = 2

        self.timer = self.create_timer(self.time_period,self.timer_callback)

    def pose_callback(self,msg):
        self.cur_x = msg.x
        self.cur_y = msg.y
        self.cur_theata = msg.theta

    def timer_callback(self):
        if not self.finished : 
            # 거리 차이
            target_x , target_y = self.waypoint[self.index]
            distance = ((target_x-self.cur_x)**2 + (target_y-self.cur_y)**2)**0.5
            # 각도 차이
            target_angle = math.atan2(target_y - self.cur_y , target_x - self.cur_x)
            angle_error = target_angle - self.cur_theata
            # 각도 보정
            if angle_error > math.pi:
                angle_error -= 2 * math.pi
            elif angle_error < -math.pi:
                angle_error += 2 * math.pi
            # 이동 및 회전
            if distance >= 0.05 :
                twist = Twist()
                twist.linear.x = 0.5 * min( 1 * distance,self.max_speed)
                twist.angular.z = 0.5 * angle_error
                self.publisher.publish(twist) 
            else: 
                self.index +=1 
                if not self.index - self.length: #범위 넘었을 때
                    self.finished = True
                    twist = Twist()
                else:
                    return
                                
            

def main(args=None):
    rclpy.init(args=args)
    node = WaypointNav()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
