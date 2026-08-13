# 8. launch/game.launch.py — 게임 한 번에 실행

## 목적
`turtlesim_node` + `obstacle_avoid`(AI 추격 거북이, #6) + `game_referee`(심판, #7)를
`ros2 launch turtlesim_projects game.launch.py` 한 줄로 동시 실행.
`custom_teleop`(플레이어 조종, #2)은 아래 "헷갈렸던 개념 정리" 참고해 별도 터미널에서 실행.

## 익힐 개념
- ROS2 launch 파일 작성 (`launch_ros.actions.Node` 액션)
- 여러 노드를 하나의 실행 단위(`LaunchDescription`)로 묶기
- `setup.py`의 `data_files`에 launch 디렉터리를 등록해 `ros2 launch`가 찾을 수 있게 하는 방법
  (이미 `setup.py`에 `glob('launch/*.launch.py')` 항목 추가됨)

## 의미
지금까지 "따로 실행하는 스크립트 모음"이었던 것이 여기서 "한 번에 실행되는 프로젝트"로
전환되는 지점. 이게 완성되면 Phase B 캡스톤(멀티 거북이 게임)이 완결됨.

## 상태
완료 (2026-08-13) — LaunchDescription 안에 `turtlesim_node`, `obstacle_avoid`, `game_referee`
3개 구성. `custom_teleop`은 launch에 포함하지 않고 별도 터미널에서 수동 실행하는 방식으로 결정.

## 헷갈렸던 개념 정리
- **`Node(...)`의 `name` 인자**: 각 노드 파이썬 파일 안에 이미 `rclpy.create_node(...)` /
  `super().__init__(...)`로 기본 이름이 정의되어 있어서, launch에서 `name=`을 안 주면
  그 기본 이름을 그대로 씀. 처음엔 한글 이름(`'화면 띄우기'` 등)을 넣었다가
  `Invalid node name: node name must not contain characters other than alphanumerics or '_'`
  에러가 났음 — ROS2 노드 이름은 영문자/숫자/`_`만 허용. 애초에 새 이름을 지을 필요가 없어서 삭제.
- **launch와 키보드 입력(stdin)**: `ros2 launch`는 각 노드를 자식 프로세스로 띄우는데,
  기본적으로 그 자식 프로세스의 표준입력은 부모 터미널과 연결되지 않음.
  `emulate_tty=True`는 노드가 TTY에 연결된 것처럼 착각하게 해서 색깔 있는 로그 출력 등을
  가능하게 하는 옵션일 뿐, **키보드 입력을 실제로 전달해주진 않음**. 그래서 `output='screen'`
  + `emulate_tty=True`를 다 넣어도 `custom_teleop` 조종은 안 됐음.
  해결하려면 `prefix='xterm -e'`로 새 터미널 창을 띄우는 방법도 있지만, 여기선 단순하게
  `custom_teleop`을 launch 밖으로 빼고 별도 터미널에서 직접 실행하는 쪽을 선택.

## 실행 방법
```bash
colcon build --packages-select turtlesim_projects
source install/setup.bash
ros2 launch turtlesim_projects game.launch.py
# 다른 터미널에서:
ros2 run turtlesim_projects custom_teleop
```
