import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtle_action_interfaces.action import MoveToGoal
import math


class GoalServer(Node):
    def __init__(self):
        super().__init__('goal_server')

        self.cb_group = ReentrantCallbackGroup()

        self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10,
            callback_group=self.cb_group
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
            callback_group=self.cb_group,
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
        # 1. waypoint_nav.py의 timer_callback이나 turtle_chase.py의 P제어 로직
        #    (거리/각도 오차 계산, twist.linear.x / angular.z 계산)을 참고해서,
        #    목표에 도착할 때까지 반복 이동시킨다.
        #    주의: execute_callback이라고 해서 저절로 블로킹해도 되는 건 아니다.
        #    기본 설정(rclpy.spin(node) = 싱글스레드 executor + 기본 콜백그룹은
        #    MutuallyExclusive)에서는 여기서 while을 돌리면 노드 전체가 멈춘다 —
        #    pose 구독 콜백도 안 돌아서 feedback이 옛날 좌표를 쓰게 되고,
        #    cancel_callback도 호출되지 않는다. waypoint_nav.py에서 배운
        #    "타이머 콜백에 while 넣지 마라"와 완전히 같은 얘기, 콜백 종류만 다를 뿐.
        #    이 파일은 그래서 main()을 MultiThreadedExecutor로 돌리고, 구독과
        #    ActionServer에 같은 ReentrantCallbackGroup을 물려놨다. 그 덕분에
        #    여기서 while로 블로킹해도 pose 구독과 취소 확인이 동시에 계속 돌아간다.
        #    대신 루프 안에서 직접 주기 제어가 필요하다 (예: time.sleep(0.1)).
        #    실제 액션 서버들(Nav2 포함)이 쓰는 패턴이 딱 이거다 — 나중에 Nav2로
        #    넘어갈 때 그대로 다시 만난다. 왜 이렇게 되는지 NOTES.md에 정리해볼 것.
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
    executor = MultiThreadedExecutor()
    rclpy.spin(node, executor=executor)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
