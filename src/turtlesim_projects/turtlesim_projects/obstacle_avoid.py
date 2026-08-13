import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtlesim.srv import Spawn
import math

class ObstacleAvoid(Node):
    def __init__(self):
        super().__init__('obstacle_avoid')
        # TODO: turtle_chase.py처럼 turtle2를 스폰해서 turtle1을 쫓게 한다.
        # 여기에 turtle3를 "장애물"로 하나 더 스폰해서(고정 위치) 화면에 보이게 한다.
        # spawn 두 번 호출하는 패턴은 turtle_chase.py의 spawn_client 부분 참고.
        self.publisher_2 = self.create_publisher(Twist, '/turtle2/cmd_vel', 10)

        spawn_client = self.create_client(Spawn,'/spawn')
        while not spawn_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /spawn service...')

        self.request2 = self.spawn_turtle("turtle2",0.0,0.0)
        self.request3 = self.spawn_turtle("turtle3",2.0,2.0)
        move_to_target = spawn_client.call_async(self.request2)
        avoid_to_obstacle = spawn_client.call_async(self.request3)
        rclpy.spin_until_future_complete(self,move_to_target)
        rclpy.spin_until_future_complete(self,avoid_to_obstacle)
        response_2 = move_to_target.result()
        response_3 = avoid_to_obstacle.result()
        


        # TODO: subscription_1 (turtle1/pose, 추격 대상), subscription_2 (turtle2/pose, 내 위치)
        # 는 turtle_chase.py의 create_subscription 패턴과 동일.
        # 장애물(turtle3)은 스폰 후 위치가 고정이므로 굳이 구독하지 않고
        # 스폰할 때 받은 x, y를 그냥 멤버 변수로 저장해도 됨.
        self.subscription_1 = self.create_subscription(
            Pose,
            'turtle1/pose',
            self.pose_callback_1,
            10
        )

        self.subscription_2 = self.create_subscription(
            Pose,
            'turtle2/pose',
            self.pose_callback_2,
            10
        )
        
        # value init (turtle_chase.py 참고, 필요한 대로 수정)
        self.turtle1_x = 0.0
        self.turtle1_y = 0.0
        self.turtle2_x = 0.0
        self.turtle2_y = 0.0
        self.turtle2_theta = 0.0
        self.obstacle_x = self.request3.x
        self.obstacle_y = self.request3.y
        self.obstacle_radius = 2.0  # 이 반경 안에 들어오면 반발력 작동

        self.timer_period = 0.1
        self.timer = self.create_timer(self.timer_period, self.timer_callback)
        
    def spawn_turtle(self,name,x,y,theta=0.0):
        request = Spawn.Request()
        request.x = x
        request.y = y
        request.name = name
        request.theta = float(theta)
        return request
            
    def pose_callback_1(self, msg):
        self.turtle1_x = msg.x
        self.turtle1_y = msg.y
        self.turtle1_theta = msg.theta


    def pose_callback_2(self, msg):
        self.turtle2_x = msg.x
        self.turtle2_y = msg.y
        self.turtle2_theta = msg.theta

    def timer_callback(self):        
        # 목표까지의 벡터
        (dx_t , dy_t) = (self.turtle1_x-self.turtle2_x,self.turtle1_y-self.turtle2_y)
        # 목표까지의 거리 
        distance = ((self.turtle1_x - self.turtle2_x)**2 + (self.turtle1_y - self.turtle2_y)**2)**0.5       
        # 장애물까지 거리
        distance_obstacle =  ((self.turtle2_x - self.obstacle_x)**2 + (self.turtle2_y - self.obstacle_y)**2)**0.5 

        # raidus 영역 밖일 때만 유닛 역벡터 만들어서 다가올 수록 더 밀어내기 위함 , 아니면 그냥 (0,0) 설정 
        if distance_obstacle < self.obstacle_radius: 
            dx_o = self.turtle2_x - self.obstacle_x
            dy_o = self.turtle2_y - self.obstacle_y
            weigth = distance_obstacle * (self.obstacle_radius - distance_obstacle)
            dx_o *= weigth
            dy_o *= weigth
        else: 
            (dx_o , dy_o) = (0.0 , 0.0)

        # 합성 벡터
        (dx_final , dy_final) = (dx_t+dx_o , dy_t+dy_o)

        # 목표 각도
        target_angle = math.atan2(dy_final,dx_final)

        # 목표 각도 오차 
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
    node = ObstacleAvoid()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
