# 5. waypoint_nav — 경로 추종

## 목적
미리 정한 좌표(waypoint) 리스트를 순서대로 방문하도록 거북이를 제어한다.

## 사용 토픽
- Subscribe: `/turtle1/pose` (`turtlesim/msg/Pose`)
- Publish: `/turtle1/cmd_vel` (`geometry_msgs/msg/Twist`)

## 익힐 개념
- 상태(현재 목표 waypoint index) 관리
- 목표 지점 도착 판정(거리 임계값)
- 도착 시 다음 waypoint로 전환
- 추후 액션 서버/클라이언트로 확장 가능 (goal/feedback/result)

## 상태
구현 완료 — waypoint 리스트 순회, 거리 기반 도착 판정, P 제어(비례 제어) + 속도 상한(`min()`)으로 이동/회전 처리.
개념 설명은 `NOTES.md`의 "waypoint_nav.py" 섹션 참고.

## 실행 방법
```bash
ros2 run turtlesim turtlesim_node   # 별도 터미널
ros2 run turtlesim_projects waypoint_nav
```
