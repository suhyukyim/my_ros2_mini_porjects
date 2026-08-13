# 8. launch/game.launch.py — 게임 한 번에 실행

## 목적
`turtlesim_node` + `custom_teleop`(플레이어 조종, #2) + `obstacle_avoid`(AI 추격 거북이, #6)
+ `game_referee`(심판, #7)를 `ros2 launch turtlesim_projects game.launch.py` 한 줄로 동시 실행.

## 익힐 개념
- ROS2 launch 파일 작성 (`launch_ros.actions.Node` 액션)
- 여러 노드를 하나의 실행 단위(`LaunchDescription`)로 묶기
- `setup.py`의 `data_files`에 launch 디렉터리를 등록해 `ros2 launch`가 찾을 수 있게 하는 방법
  (이미 `setup.py`에 `glob('launch/*.launch.py')` 항목 추가됨)

## 의미
지금까지 "따로 실행하는 스크립트 모음"이었던 것이 여기서 "한 번에 실행되는 프로젝트"로
전환되는 지점. 이게 완성되면 Phase B 캡스톤(멀티 거북이 게임)이 완결됨.

## 상태
TODO — LaunchDescription 안에 노드 4개(turtlesim_node, custom_teleop, obstacle_avoid, game_referee)
구성 미완료. custom_teleop이 키보드 입력을 받아야 하므로 launch로 띄웠을 때
표준입력이 제대로 전달되는지 직접 확인 필요 (`output='screen'`, `emulate_tty=True` 등).

## 실행 방법 (구현 완료 후)
```bash
colcon build --packages-select turtlesim_projects
source install/setup.bash
ros2 launch turtlesim_projects game.launch.py
```
