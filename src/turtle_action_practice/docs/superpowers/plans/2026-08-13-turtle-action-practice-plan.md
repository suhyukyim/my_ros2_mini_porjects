# turtle_action_practice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Scaffold two new ROS2 packages (`turtle_action_interfaces`, `turtle_action_practice`) that give the user a TODO-stub action server and action client to implement themselves, learning the ROS2 action lifecycle (goal/feedback/result/cancel) on top of turtlesim.

**Architecture:** `turtle_action_interfaces` (ament_cmake) defines a single custom `MoveToGoal.action` type. `turtle_action_practice` (ament_python) contains two node stubs — `goal_server.py` (ActionServer wired up, control logic left as TODO) and `goal_client.py` (ActionClient wired up, goal-sending/result-handling left as TODO) — plus docs mirroring the `turtlesim_projects` numbered-doc + NOTES.md convention.

**Tech Stack:** ROS2 Jazzy, rclpy, rclpy.action (ActionServer/ActionClient), turtlesim, colcon.

**Spec:** `/home/suhyuk/ros2_workspaces/mini_project/src/turtle_action_practice/docs/superpowers/specs/2026-08-13-turtle-action-practice-design.md`

## Global Constraints

- ROS2 distro is **Jazzy**, not Humble — source `/opt/ros/jazzy/setup.bash` before any `colcon build` / `ros2` command in a fresh shell.
- No automated test framework for functional behavior (matches `turtlesim_projects` convention). Verification is `colcon build` + manual `ros2` CLI checks, not pytest.
- **Stub-style only**: node files get real ROS2 API wiring (publishers, subscriptions, `ActionServer`/`ActionClient` construction) but the actual control/decision logic (P-control math, goal accept/reject, feedback loop body, cancel handling, result handling) is left as `# TODO` comments for the user to write themselves. Do not fill in that logic. This overrides any default instinct to write complete implementations.
- Both packages live under `~/ros2_workspaces/mini_project/src/`, alongside the existing `turtlesim_projects` package.
- Docs follow the existing numbered-doc convention (`docs/NN_name.md` with 목적/익힐 개념/의미/상태/실행 방법 sections) and the running `NOTES.md` Q&A convention — do not pre-write NOTES.md Q&A content, only its header (Q&A accumulates as the user works and asks questions, same as `turtlesim_projects/NOTES.md`).
- All prose in docs/comments should be Korean, matching the existing project's voice.

---

### Task 1: `turtle_action_interfaces` package (custom action type)

**Files:**
- Create: `src/turtle_action_interfaces/action/MoveToGoal.action`
- Create: `src/turtle_action_interfaces/CMakeLists.txt`
- Create: `src/turtle_action_interfaces/package.xml`

**Interfaces:**
- Produces: `turtle_action_interfaces/action/MoveToGoal` — an action type with `Goal{x: float32, y: float32}`, `Result{success: bool, total_time: float32}`, `Feedback{distance_remaining: float32}`. Tasks 3 and 4 import it as `from turtle_action_interfaces.action import MoveToGoal`.

- [ ] **Step 1: Create the package directory and action definition**

```bash
mkdir -p /home/suhyuk/ros2_workspaces/mini_project/src/turtle_action_interfaces/action
```

Write `/home/suhyuk/ros2_workspaces/mini_project/src/turtle_action_interfaces/action/MoveToGoal.action`:

```
# Goal
float32 x
float32 y
---
# Result
bool success
float32 total_time
---
# Feedback
float32 distance_remaining
```

- [ ] **Step 2: Write CMakeLists.txt**

Write `/home/suhyuk/ros2_workspaces/mini_project/src/turtle_action_interfaces/CMakeLists.txt`:

```cmake
cmake_minimum_required(VERSION 3.8)
project(turtle_action_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "action/MoveToGoal.action"
)

ament_package()
```

- [ ] **Step 3: Write package.xml**

Write `/home/suhyuk/ros2_workspaces/mini_project/src/turtle_action_interfaces/package.xml`:

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>turtle_action_interfaces</name>
  <version>0.0.1</version>
  <description>Custom MoveToGoal action type for turtle_action_practice</description>
  <maintainer email="yimp2001@gmail.com">suhyuk</maintainer>
  <license>Apache-2.0</license>

  <buildtool_depend>ament_cmake</buildtool_depend>

  <build_depend>rosidl_default_generators</build_depend>
  <exec_depend>rosidl_default_runtime</exec_depend>
  <member_of_group>rosidl_interface_packages</member_of_group>

  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```

- [ ] **Step 4: Build and verify the interface generates correctly**

Run:
```bash
source /opt/ros/jazzy/setup.bash
cd /home/suhyuk/ros2_workspaces/mini_project
colcon build --packages-select turtle_action_interfaces
source install/setup.bash
ros2 interface show turtle_action_interfaces/action/MoveToGoal
```

Expected output:
```
float32 x
float32 y
---
bool success
float32 total_time
---
float32 distance_remaining
```

If `colcon build` fails, check CMakeLists.txt syntax and that `action/MoveToGoal.action` path matches exactly.

- [ ] **Step 5: Commit**

```bash
cd /home/suhyuk/ros2_workspaces/mini_project
git add src/turtle_action_interfaces
git commit -m "feat: add turtle_action_interfaces package with MoveToGoal action"
```

(Skip this step if `git status` shows this workspace is not a git repository — it currently is not, per prior session notes. Confirm with `git status` first; if it errors with "not a git repository", skip committing for all tasks in this plan.)

---

### Task 2: `turtle_action_practice` package skeleton + interface doc

**Files:**
- Create: `src/turtle_action_practice/package.xml`
- Create: `src/turtle_action_practice/setup.py`
- Create: `src/turtle_action_practice/setup.cfg`
- Create: `src/turtle_action_practice/resource/turtle_action_practice` (empty marker file)
- Create: `src/turtle_action_practice/turtle_action_practice/__init__.py` (empty)
- Create: `src/turtle_action_practice/docs/01_action_interface.md`
- Create: `src/turtle_action_practice/README.md`
- Create: `src/turtle_action_practice/NOTES.md`

**Interfaces:**
- Consumes: `turtle_action_interfaces/action/MoveToGoal` from Task 1 (declared as a `<depend>` in package.xml).
- Produces: an installable, currently-empty `turtle_action_practice` ament_python package that Tasks 3–4 add entry points and node files to.

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p /home/suhyuk/ros2_workspaces/mini_project/src/turtle_action_practice/turtle_action_practice
mkdir -p /home/suhyuk/ros2_workspaces/mini_project/src/turtle_action_practice/resource
touch /home/suhyuk/ros2_workspaces/mini_project/src/turtle_action_practice/resource/turtle_action_practice
touch /home/suhyuk/ros2_workspaces/mini_project/src/turtle_action_practice/turtle_action_practice/__init__.py
```

- [ ] **Step 2: Write package.xml**

Write `/home/suhyuk/ros2_workspaces/mini_project/src/turtle_action_practice/package.xml`:

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>turtle_action_practice</name>
  <version>0.0.1</version>
  <description>Custom action server/client practice using turtlesim</description>
  <maintainer email="yimp2001@gmail.com">suhyuk</maintainer>
  <license>Apache-2.0</license>

  <depend>rclpy</depend>
  <depend>turtlesim</depend>
  <depend>geometry_msgs</depend>
  <depend>turtle_action_interfaces</depend>

  <test_depend>ament_copyright</test_depend>
  <test_depend>ament_flake8</test_depend>
  <test_depend>ament_pep257</test_depend>
  <test_depend>python3-pytest</test_depend>

  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
```

- [ ] **Step 3: Write setup.py (empty entry_points for now)**

Write `/home/suhyuk/ros2_workspaces/mini_project/src/turtle_action_practice/setup.py`:

```python
from setuptools import find_packages, setup

package_name = 'turtle_action_practice'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='suhyuk',
    maintainer_email='yimp2001@gmail.com',
    description='Custom action server/client practice using turtlesim',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        ],
    },
)
```

- [ ] **Step 4: Write setup.cfg**

Write `/home/suhyuk/ros2_workspaces/mini_project/src/turtle_action_practice/setup.cfg`:

```ini
[develop]
script_dir=$base/lib/turtle_action_practice
[install]
install_scripts=$base/lib/turtle_action_practice
```

- [ ] **Step 5: Write docs/01_action_interface.md**

```bash
mkdir -p /home/suhyuk/ros2_workspaces/mini_project/src/turtle_action_practice/docs
```

Write `/home/suhyuk/ros2_workspaces/mini_project/src/turtle_action_practice/docs/01_action_interface.md`:

```markdown
# 1. MoveToGoal — 커스텀 액션 인터페이스

## 목적
turtle_action_interfaces 패키지에 정의된 `MoveToGoal.action`을 이해한다.
이 액션이 이후 goal_server(#2)/goal_client(#3)가 주고받는 메시지 타입이 된다.

## 왜 토픽/서비스가 아니라 액션인가
- **토픽**: 한쪽이 계속 보내기만 함. "완료됐다"는 개념이 없음.
- **서비스**: 요청 → 응답 한 번으로 끝남. 오래 걸리는 작업의 중간 진행상황을 알 수 없고,
  진행 중 취소도 못 함.
- **액션**: 목표(goal)를 보내고, 진행 중 계속 feedback을 받고, 끝나면 result를 받고,
  중간에 cancel도 할 수 있음. "시간이 걸리는 작업"에 맞는 유일한 표준 통신 패턴.

## MoveToGoal.action 필드
```
# Goal
float32 x
float32 y
---
# Result
bool success
float32 total_time
---
# Feedback
float32 distance_remaining
```

- **Goal** (`x`, `y`): 거북이가 도착해야 할 목표 좌표. 클라이언트가 채워서 보냄.
- **Feedback** (`distance_remaining`): 서버가 이동 도중 주기적으로 보고하는 남은 거리.
- **Result** (`success`, `total_time`): 도착 성공 여부와 걸린 시간. 서버가 종료 시 한 번 보냄.

`---`로 구분된 세 블록이 `.action` 파일 문법. `ros2 interface show
turtle_action_interfaces/action/MoveToGoal`로 언제든 확인 가능.

## 익힐 개념
- `.action` 파일은 `ament_python` 패키지에서 직접 정의할 수 없고, 별도의 `ament_cmake`
  인터페이스 패키지(`turtle_action_interfaces`)가 필요한 이유 (`rosidl_generate_interfaces`가
  코드 생성을 하는데, 이게 CMake 빌드 단계에서 일어남).
- Goal / Result / Feedback 세 블록의 역할 구분.

## 상태
완료 — `turtle_action_interfaces` 패키지 자체는 인터페이스 정의만 담당하며 로직이 없어서
TODO 스텁이 필요 없음.
```

- [ ] **Step 6: Write initial README.md**

Write `/home/suhyuk/ros2_workspaces/mini_project/src/turtle_action_practice/README.md`:

```markdown
# turtle_action_practice

ROS2(Jazzy) 액션(action) 통신 패턴을 turtlesim으로 익히는 미니 프로젝트.
`turtlesim_projects`와 별개의 프로젝트 — 토픽/서비스는 거기서 익혔고, 여기선 액션만 다룬다.

두 개 패키지로 구성:
- `turtle_action_interfaces` (`ament_cmake`) — 커스텀 액션 타입 `MoveToGoal` 정의만 담당.
- `turtle_action_practice` (`ament_python`) — 실제 액션 서버/클라이언트 노드.

## 프로젝트 목록

| # | 파일 | 주제 | 문서 |
|---|------|------|------|
| 1 | `turtle_action_interfaces/action/MoveToGoal.action` | 커스텀 액션 인터페이스 | [docs/01_action_interface.md](docs/01_action_interface.md) |
| 2 | `turtle_action_practice/goal_server.py` | 액션 서버 (목표 이동 + feedback + cancel) | [docs/02_goal_server.md](docs/02_goal_server.md) |
| 3 | `turtle_action_practice/goal_client.py` | 액션 클라이언트 (goal 전송 + result 대기) | [docs/03_goal_client.md](docs/03_goal_client.md) |

1은 구현 완료(인터페이스 정의만이라 로직 없음). 2~3은 노드 클래스/ActionServer/ActionClient
연결 보일러플레이트만 있고 핵심 로직은 TODO 상태.

## 빌드 & 실행

```bash
# 워크스페이스 루트에서
cd ~/ros2_workspaces/mini_project
colcon build --packages-select turtle_action_interfaces turtle_action_practice
source install/setup.bash

# turtlesim 실행 (터미널 1)
ros2 run turtlesim turtlesim_node

# 액션 서버 실행 (터미널 2)
ros2 run turtle_action_practice goal_server

# 액션 클라이언트 실행 (터미널 3)
ros2 run turtle_action_practice goal_client
```

## Q&A / 진행 노트

자세한 개념 정리는 [NOTES.md](NOTES.md) 참고.
```

- [ ] **Step 7: Write initial NOTES.md**

Write `/home/suhyuk/ros2_workspaces/mini_project/src/turtle_action_practice/NOTES.md`:

```markdown
# 학습 노트

프로젝트별 상세 문서는 `docs/`, 개념 Q&A는 여기에 정리.
```

- [ ] **Step 8: Build and verify the skeleton compiles**

Run:
```bash
source /opt/ros/jazzy/setup.bash
cd /home/suhyuk/ros2_workspaces/mini_project
colcon build --packages-select turtle_action_interfaces turtle_action_practice
```

Expected: both packages report `Finished <<< turtle_action_interfaces` and `Finished <<< turtle_action_practice` with no errors. (`turtle_action_practice` currently has zero nodes and an empty `entry_points` list — this is expected to build cleanly with nothing to `ros2 run` yet.)

- [ ] **Step 9: Commit**

```bash
cd /home/suhyuk/ros2_workspaces/mini_project
git add src/turtle_action_practice
git commit -m "feat: scaffold turtle_action_practice package skeleton and interface doc"
```

(Skip if not a git repo — see Task 1 Step 5 note.)

---

### Task 3: `goal_server.py` stub

**Files:**
- Create: `src/turtle_action_practice/turtle_action_practice/goal_server.py`
- Modify: `src/turtle_action_practice/setup.py` (add entry point)
- Create: `src/turtle_action_practice/docs/02_goal_server.md`

**Interfaces:**
- Consumes: `turtle_action_interfaces.action.MoveToGoal` (Task 1).
- Produces: `ros2 run turtle_action_practice goal_server` — an action server named `move_to_goal` of type `MoveToGoal`, subscribing to `/turtle1/pose` and publishing to `/turtle1/cmd_vel`. Task 4's client targets this exact action name (`move_to_goal`).

- [ ] **Step 1: Write goal_server.py**

Write `/home/suhyuk/ros2_workspaces/mini_project/src/turtle_action_practice/turtle_action_practice/goal_server.py`:

```python
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
```

- [ ] **Step 2: Register the entry point**

Edit `/home/suhyuk/ros2_workspaces/mini_project/src/turtle_action_practice/setup.py`, change:

```python
    entry_points={
        'console_scripts': [
        ],
    },
```

to:

```python
    entry_points={
        'console_scripts': [
            'goal_server = turtle_action_practice.goal_server:main',
        ],
    },
```

- [ ] **Step 3: Write docs/02_goal_server.md**

Write `/home/suhyuk/ros2_workspaces/mini_project/src/turtle_action_practice/docs/02_goal_server.md`:

```markdown
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

- [ ] **Step 4: Build and verify the server starts and registers the action**

Run (in separate terminals):
```bash
# terminal A
source /opt/ros/jazzy/setup.bash
cd /home/suhyuk/ros2_workspaces/mini_project
colcon build --packages-select turtle_action_practice
source install/setup.bash
ros2 run turtlesim turtlesim_node

# terminal B
source /opt/ros/jazzy/setup.bash
source /home/suhyuk/ros2_workspaces/mini_project/install/setup.bash
ros2 run turtle_action_practice goal_server

# terminal C
source /opt/ros/jazzy/setup.bash
source /home/suhyuk/ros2_workspaces/mini_project/install/setup.bash
ros2 action list
```

Expected: `colcon build` succeeds; `goal_server` starts without a traceback and stays running; `ros2 action list` prints `/move_to_goal`. Stop `goal_server` with Ctrl+C when done.

- [ ] **Step 5: Commit**

```bash
cd /home/suhyuk/ros2_workspaces/mini_project
git add src/turtle_action_practice/turtle_action_practice/goal_server.py \
        src/turtle_action_practice/setup.py \
        src/turtle_action_practice/docs/02_goal_server.md
git commit -m "feat: add goal_server action server stub"
```

(Skip if not a git repo.)

---

### Task 4: `goal_client.py` stub

**Files:**
- Create: `src/turtle_action_practice/turtle_action_practice/goal_client.py`
- Modify: `src/turtle_action_practice/setup.py` (add entry point)
- Create: `src/turtle_action_practice/docs/03_goal_client.md`

**Interfaces:**
- Consumes: `turtle_action_interfaces.action.MoveToGoal` (Task 1), the `move_to_goal` action name (Task 3).
- Produces: `ros2 run turtle_action_practice goal_client` — a node with a `send_goal(x, y)` method the user will call from `main()` once implemented.

- [ ] **Step 1: Write goal_client.py**

Write `/home/suhyuk/ros2_workspaces/mini_project/src/turtle_action_practice/turtle_action_practice/goal_client.py`:

```python
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
        pass

    def feedback_callback(self, feedback_msg):
        # TODO: feedback_msg.feedback.distance_remaining을 self.get_logger().info(...)로 출력.
        pass

    def goal_response_callback(self, future):
        # TODO: goal_handle = future.result()
        # goal_handle.accepted가 False면 거절된 것 — 로그 남기고 return.
        # True면 self._goal_handle = goal_handle로 저장해두고(취소용),
        # goal_handle.get_result_async().add_done_callback(self.get_result_callback)
        pass

    def get_result_callback(self, future):
        # TODO: result = future.result().result
        # result.success / result.total_time을 self.get_logger().info(...)로 출력.
        pass

    def cancel_goal(self):
        # TODO: self._goal_handle이 있으면 self._goal_handle.cancel_goal_async() 호출.
        # 중간 취소 경로를 직접 확인해보기 위한 테스트용 메서드 —
        # 예: send_goal 이후 몇 초 뒤 create_timer로 이 메서드를 한 번 호출하도록 만들어보기.
        pass


def main(args=None):
    rclpy.init(args=args)
    node = GoalClient()
    # TODO: node.send_goal(x, y)를 원하는 목표 좌표로 호출한 뒤 rclpy.spin(node).
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

- [ ] **Step 2: Register the entry point**

Edit `/home/suhyuk/ros2_workspaces/mini_project/src/turtle_action_practice/setup.py`, change:

```python
    entry_points={
        'console_scripts': [
            'goal_server = turtle_action_practice.goal_server:main',
        ],
    },
```

to:

```python
    entry_points={
        'console_scripts': [
            'goal_server = turtle_action_practice.goal_server:main',
            'goal_client = turtle_action_practice.goal_client:main',
        ],
    },
```

- [ ] **Step 3: Write docs/03_goal_client.md**

Write `/home/suhyuk/ros2_workspaces/mini_project/src/turtle_action_practice/docs/03_goal_client.md`:

```markdown
# 3. goal_client.py — 액션 클라이언트

## 목적
`MoveToGoal` 액션의 클라이언트 역할. 목표 좌표를 서버로 보내고, feedback을 구독하고,
결과를 기다리고, 필요하면 중간에 취소한다.

## 익힐 개념
- `ActionClient(node, action_type, action_name)`로 클라이언트를 만드는 방법.
- `send_goal_async(goal_msg, feedback_callback=...)` — 서비스의 `call_async`와 같은
  자리지만, feedback 콜백을 함께 등록한다는 점이 다르다.
- goal 전송 → 수락/거절 응답(`goal_response_callback`) → 결과 대기(`get_result_callback`)로
  이어지는 3단계 콜백 체이닝. game_referee.py의 `do_kill` → `on_kill_done` 패턴과
  구조적으로 동일 (블로킹 대신 `add_done_callback`으로 다음 단계 잇기).
- `goal_handle.cancel_goal_async()`로 진행 중인 goal을 취소하는 방법.

## 의미
서버 쪽에서 배운 걸 클라이언트 쪽에서 대칭적으로 확인하는 노드. 서버의 feedback
publish -> 클라이언트의 feedback_callback, 서버의 succeed()/canceled() -> 클라이언트의
result.success 로 이어지는 왕복을 직접 눈으로 확인하는 게 목표.

## 상태
TODO — `send_goal`부터 `cancel_goal`까지 전부 미구현. `main()`도 아직 `send_goal`을
호출하지 않아서, 지금 실행하면 그냥 액션 없이 spin만 한다.

## 실행 방법 (구현 완료 후)
```bash
colcon build --packages-select turtle_action_practice
source install/setup.bash
# turtlesim_node + goal_server가 이미 떠 있는 상태에서
ros2 run turtle_action_practice goal_client
```
확인: goal_server 터미널과 goal_client 터미널 양쪽에 feedback/result 로그가 찍히고,
거북이가 실제로 목표 좌표로 이동하는지 확인. cancel_goal도 별도로 테스트해볼 것.
```

- [ ] **Step 4: Build and verify the client starts cleanly**

Run:
```bash
source /opt/ros/jazzy/setup.bash
cd /home/suhyuk/ros2_workspaces/mini_project
colcon build --packages-select turtle_action_practice
source install/setup.bash
ros2 run turtle_action_practice goal_client
```

Expected: node starts with no traceback and just spins (since `main()`'s `send_goal` call is still a TODO). Stop with Ctrl+C — expect clean shutdown, no errors.

- [ ] **Step 5: Commit**

```bash
cd /home/suhyuk/ros2_workspaces/mini_project
git add src/turtle_action_practice/turtle_action_practice/goal_client.py \
        src/turtle_action_practice/setup.py \
        src/turtle_action_practice/docs/03_goal_client.md
git commit -m "feat: add goal_client action client stub"
```

(Skip if not a git repo.)

---

### Task 5: Final README pass

**Files:**
- Modify: `src/turtle_action_practice/README.md`

**Interfaces:**
- Consumes: nothing new — this task only verifies the README written in Task 2 Step 6 still accurately describes the finished (stub) state of all three deliverables after Tasks 3–4 landed.

- [ ] **Step 1: Re-read the README and confirm accuracy**

Open `/home/suhyuk/ros2_workspaces/mini_project/src/turtle_action_practice/README.md` and confirm:
- The project table lists all three rows (`MoveToGoal.action`, `goal_server.py`, `goal_client.py`) with working relative links to `docs/01_action_interface.md`, `docs/02_goal_server.md`, `docs/03_goal_client.md`.
- The build/run instructions list both packages in the `colcon build --packages-select` command and both `ros2 run` commands.

No changes are expected if Tasks 2–4 were followed exactly (the README was written to be accurate for the final state up front). If any doc filename or command drifted during implementation, fix the README to match.

- [ ] **Step 2: Full workspace build sanity check**

Run:
```bash
source /opt/ros/jazzy/setup.bash
cd /home/suhyuk/ros2_workspaces/mini_project
colcon build
```

Expected: all packages (`turtlesim_projects`, `turtle_action_interfaces`, `turtle_action_practice`) build with no errors.

- [ ] **Step 3: Commit (if any README changes were made)**

```bash
cd /home/suhyuk/ros2_workspaces/mini_project
git add src/turtle_action_practice/README.md
git commit -m "docs: verify turtle_action_practice README matches final scaffold"
```

(Skip if not a git repo, or if Step 1 made no changes.)
