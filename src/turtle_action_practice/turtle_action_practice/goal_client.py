import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from turtle_action_interfaces.action import MoveToGoal


class GoalClient(Node):
    def __init__(self):
        super().__init__('goal_client')
        self._action_client = ActionClient(self, MoveToGoal, 'move_to_goal')
        self._goal_handle = None

    def send_goal(self, x, y):
        # TODO:
        # 1. self._action_client.wait_for_server()로 서버가 뜰 때까지 대기.
        # 2. goal_msg = MoveToGoal.Goal(); goal_msg.x = x; goal_msg.y = y
        # 3. send_goal_future = self._action_client.send_goal_async(
        #        goal_msg, feedback_callback=self.feedback_callback)
        # 4. send_goal_future.add_done_callback(self.goal_response_callback)
        #    (game_referee.py의 do_kill -> on_kill_done 체이닝과 같은 구조:
        #    call_async 대신 send_goal_async, add_done_callback으로 다음 단계 잇기)
        
        self.timer = self.create_timer(3.0,self.cancel_goal)
        self._action_client.wait_for_server()
        
        goal_msg = MoveToGoal.Goal()
        goal_msg.x = x 
        goal_msg.y = y
        
        self.send_goal_future = self._action_client.send_goal_async(goal_msg,feedback_callback = self.feedback_callback)
        self.send_goal_future.add_done_callback(self.goal_response_callback)
        

    def feedback_callback(self, feedback_msg):
        # TODO: feedback_msg.feedback.distance_remaining을 self.get_logger().info(...)로 출력.
        self.get_logger().info(f'{feedback_msg.feedback.distance_remaining}')

    def goal_response_callback(self, future):
        # TODO: goal_handle = future.result()
        # goal_handle.accepted가 False면 거절된 것 — 로그 남기고 return.
        # True면 self._goal_handle = goal_handle로 저장해두고(취소용),
        # goal_handle.get_result_async().add_done_callback(self.get_result_callback)
        goal_handle = future.result()
        if goal_handle.accepted :
            self._goal_handle = goal_handle
            goal_handle.get_result_async().add_done_callback(self.get_result_callback)
        else:    
            self.get_logger().info("False")
            return
        
    def get_result_callback(self, future):
        # TODO: result = future.result().result
        # result.success / result.total_time을 self.get_logger().info(...)로 출력.
        result = future.result().result
        self.get_logger().info(f'{result.success} , {result.total_time}')

    def cancel_goal(self):
        # TODO: self._goal_handle이 있으면 self._goal_handle.cancel_goal_async() 호출.
        # 중간 취소 경로를 직접 확인해보기 위한 테스트용 메서드 —
        # 예: send_goal 이후 몇 초 뒤 create_timer로 이 메서드를 한 번 호출하도록 만들어보기.
        if self._goal_handle:
            self._goal_handle.cancel_goal_async()
        self.timer.cancel()



def main(args=None):
    rclpy.init(args=args)
    node = GoalClient()
    # TODO: node.send_goal(x, y)를 원하는 목표 좌표로 호출한 뒤 rclpy.spin(node).
    node.send_goal(1.0,1.0)
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
