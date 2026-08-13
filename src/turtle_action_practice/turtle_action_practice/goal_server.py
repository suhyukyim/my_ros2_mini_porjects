import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtle_action_interfaces.action import MoveToGoal
import math


class GoalServer(Node):
    def __init__(self):
        super().__init__('goal_server')

        self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10
        )

        self.cur_x = 5.0
        self.cur_y = 5.0
        self.cur_theta = 0.0

        self._action_server = ActionServer(
            self,
            MoveToGoal,
            'move_to_goal',
            execute_callback=self.execute_callback,
            cancel_callback=self.cancel_callback,
        )

    def pose_callback(self, msg):
        self.cur_x = msg.x
        self.cur_y = msg.y
        self.cur_theta = msg.theta

    def cancel_callback(self, goal_handle):
        # TODO: 취소 요청을 받아들일지 결정해서 반환.
        # 대부분의 경우 그냥 항상 허용: return CancelResponse.ACCEPT
        # (거절하려면 CancelResponse.REJECT)
        pass

    def execute_callback(self, goal_handle):
        # goal_handle.request.x, goal_handle.request.y가 목표 좌표.
        #
        # TODO 해야 할 일:
        # 1. waypoint_nav.py의 timer_callback에 있는 P제어 로직(거리/각도 오차 계산,
        #    twist.linear.x / angular.z 계산)을 참고해서, 목표에 도착할 때까지
        #    반복 이동시킨다.
        #    주의: 여기 execute_callback은 create_timer 콜백이 아니라 액션 실행 전용
        #    스레드에서 도는 함수라서, waypoint_nav.py와 달리 이 함수 안에서
        #    while 루프를 써도 된다 — 대신 루프 안에서 직접 주기 제어가 필요하다
        #    (예: time.sleep(0.1)). 왜 다른지 NOTES.md에 정리해볼 것.
        # 2. 매 스텝마다 아래처럼 feedback을 보고한다:
        #        feedback = MoveToGoal.Feedback()
        #        feedback.distance_remaining = distance
        #        goal_handle.publish_feedback(feedback)
        # 3. 매 스텝마다 goal_handle.is_cancel_requested를 확인한다. True면:
        #        goal_handle.canceled()
        #        return MoveToGoal.Result(success=False, total_time=...)
        # 4. 목표에 도착하면:
        #        goal_handle.succeed()
        #        return MoveToGoal.Result(success=True, total_time=...)
        pass


def main(args=None):
    rclpy.init(args=args)
    node = GoalServer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
