# 2. goal_server.py — 액션 서버

## 목적
`MoveToGoal` 액션의 서버 역할. 클라이언트가 보낸 목표 좌표로 turtle1을 이동시키고,
이동 중 남은 거리를 feedback으로 보고하며, 취소 요청도 처리한다.

## 익힐 개념
- `ActionServer(node, action_type, action_name, execute_callback, cancel_callback)` 로
  액션 서버를 등록하는 방법.
- `execute_callback`은 `create_timer` 콜백과 다르게 액션 실행 전용 스레드에서 동작하므로,
  콜백 안에서 블로킹 루프(`while`)를 직접 돌려도 executor 전체가 멈추지 않는다 —
  waypoint_nav.py에서 배운 "타이머 콜백에 while 넣으면 안 된다"는 제약이 왜 여기선
  다르게 적용되는지 이해하기.
- `goal_handle.publish_feedback(...)`으로 진행 중 상태를 클라이언트에 계속 보고.
- `goal_handle.is_cancel_requested` 확인 → `goal_handle.canceled()` → `Result(success=False, ...)`
  반환하는 취소 처리 흐름.
- `goal_handle.succeed()` → `Result(success=True, ...)` 반환하는 정상 종료 흐름.

## 의미
서비스(`turtle_service_control.py`)까지는 "요청 한 번, 응답 한 번"이었는데, 액션은
그 사이에 진행상황(feedback)과 취소 가능성이 추가된 구조. Nav2 같은 실제 자율주행
스택이 전부 이 패턴 위에 세워져 있다.

## 상태
TODO — `execute_callback`/`cancel_callback` 내부 로직 미구현. 서버 자체는 뜨고
`ros2 action list`에 `/move_to_goal`이 보여야 하지만, 실제로 goal을 보내면
아직 아무 동작도 하지 않는다.

## 실행 방법
```bash
colcon build --packages-select turtle_action_practice
source install/setup.bash
ros2 run turtlesim turtlesim_node   # 별도 터미널
ros2 run turtle_action_practice goal_server
```
확인: 다른 터미널에서 `ros2 action list`에 `/move_to_goal`이 뜨는지,
`ros2 action info /move_to_goal -t`로 타입이 `turtle_action_interfaces/action/MoveToGoal`인지 확인.
```
