import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from turtlesim.srv import Spawn, Kill
from std_msgs.msg import Int32
import random

class GameReferee(Node):
    def __init__(self):
        super().__init__('game_referee')
        # TODO: turtle1(도망자/플레이어), turtle2(추격자, obstacle_avoid에서 만든 놈)
        # TODO: /kill, /spawn 서비스 클라이언트 생성 
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

        self.kill_client = self.create_client(Kill, '/kill')
        while not self.kill_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /kill service...')

        # spawn
        self.spawn_client = self.create_client(Spawn, '/spawn')
        while not self.spawn_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /spawn service...')
            
        # TODO: 점수를 알리는 퍼블리셔. 토픽 이름/타입은 자유 (예: '/game/score', Int32)
        self.score_publisher = self.create_publisher(Int32, '/game/score', 10)

        self.turtle1_x = 0.0
        self.turtle1_y = 0.0
        self.turtle2_x = 0.0
        self.turtle2_y = 0.0
        self.catch_radius = 0.5  # 이 거리 이하면 "잡힘"
        self.score = 0
        self.turtle2_ready = False

        self.timer_period = 0.1
        self.timer = self.create_timer(self.timer_period, self.timer_callback)

        
    def pose_callback_1(self, msg):
        self.turtle1_x = msg.x
        self.turtle1_y = msg.y

    def pose_callback_2(self, msg):
        self.turtle2_ready =True
        self.turtle2_x = msg.x
        self.turtle2_y = msg.y

    def timer_callback(self):
        # 거리 계산
        distance = ((self.turtle1_x - self.turtle2_x)**2 + (self.turtle1_y - self.turtle2_y)**2)**0.5

        # atch_radius 이하로 가까워지면 "잡힘" 처리 -> kill -> spawn
        if distance <= self.catch_radius:
            if self.turtle2_ready == False:
                return 
            score = Int32()
            self.score +=1 
            score.data = self.score
            self.score_publisher.publish(score)
            self.do_kill('turtle1')

    def do_spawn(self, x, y, theta, name):
        spawn_request = Spawn.Request()
        spawn_request.x = x
        spawn_request.y = y
        spawn_request.theta = theta
        spawn_request.name = name
        future = self.spawn_client.call_async(spawn_request)
        

    def do_kill(self, name):
        kill_request = Kill.Request()
        kill_request.name = name 
        future = self.kill_client.call_async(kill_request)
        future.add_done_callback(self.on_kill_done)

    def on_kill_done(self, future):
        self.get_logger().info(f'kill done: {future.result()}')
        # 여기서 kill이 끝났으니, 다음 할 일(spawn)을 이어서 호출
        self.do_spawn(float(random.randint(1,10)),float(random.randint(1,10)),0.0,'turtle1')

def main(args=None):
    rclpy.init(args=args)
    node = GameReferee()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
