# turtle_service_control.py Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement `#4 turtle_service_control.py` — a keyboard-triggered node that calls turtlesim's `/spawn`, `/kill`, `/turtle1/set_pen`, `/reset` services, completing the Phase A item from the design spec.

**Architecture:** Single node (`TurtleServiceControl`) creates four service clients in `__init__` (mirroring the `wait_for_service` + `call_async` + `spin_until_future_complete` pattern already used in `turtle_chase.py`). `main()` reuses the raw-terminal key-reading loop from `custom_teleop.py` (`termios`/`tty`/`select`) and maps keys to service calls: `s` spawn, `k` kill, `p` set_pen, `r` reset, Ctrl+C quit.

**Tech Stack:** rclpy, `turtlesim.srv` (`Spawn`, `Kill`, `SetPen`), `std_srvs.srv` (`Empty`).

## Global Constraints

- This package has **no automated test suite** (`setup.py` has no test entry points beyond the pytest boilerplate default, and no prior node in this repo has unit tests). Verification for every task is **manual**: build, run `turtlesim_node` + the new node in separate terminals, press the key, confirm the expected visual/log result. This replaces the pytest steps from the standard plan template.
- `~/ros2_workspaces/mini_project` is **not a git repository** (confirmed via `git status`). Every "Commit" step below is written for when/if git gets initialized here — until then, treat those steps as no-ops and just move to the next task.
- Follow existing repo conventions: entry point name `turtle_service_control` (already registered in `setup.py:22`, no change needed there).
- After implementation, update `docs/turtle_service_control.md`'s "상태" line from `TODO` to done, and document the keybindings.
- Spec reference: `docs/superpowers/specs/2026-08-06-turtlesim-progressive-buildup-design.md`, Phase A / `#4`.

---

### Task 1: Service clients in `__init__`

**Files:**
- Modify: `src/turtlesim_projects/turtlesim_projects/turtle_service_control.py`

**Interfaces:**
- Produces: `self.spawn_client`, `self.kill_client`, `self.set_pen_client`, `self.reset_client` — all `rclpy.client.Client` instances, ready for `call_async()` in later tasks.

- [ ] **Step 1: Write the four client declarations**

Replace the file's current stub body with:

```python
import rclpy
from rclpy.node import Node
from turtlesim.srv import Spawn, Kill, SetPen
from std_srvs.srv import Empty
import sys
import termios
import tty
import select


class TurtleServiceControl(Node):
    def __init__(self):
        super().__init__('turtle_service_control')

        self.spawn_client = self.create_client(Spawn, '/spawn')
        self.kill_client = self.create_client(Kill, '/kill')
        self.set_pen_client = self.create_client(SetPen, '/turtle1/set_pen')
        self.reset_client = self.create_client(Empty, '/reset')

        for client, name in (
            (self.spawn_client, '/spawn'),
            (self.kill_client, '/kill'),
            (self.set_pen_client, '/turtle1/set_pen'),
            (self.reset_client, '/reset'),
        ):
            while not client.wait_for_service(timeout_sec=1.0):
                self.get_logger().info(f'Waiting for {name} service...')

        self._pen_toggle = False
```

(The rest of the file — `main()` — stays as-is for this task; it will be rewritten in Task 3.)

- [ ] **Step 2: Build and check for import/syntax errors**

Run: `cd ~/ros2_workspaces/mini_project && colcon build --packages-select turtlesim_projects`
Expected: build succeeds with no errors.

- [ ] **Step 3: Manual smoke test — node starts and finds services**

Terminal 1: `ros2 run turtlesim turtlesim_node`
Terminal 2: `source install/setup.bash && ros2 run turtlesim_projects turtle_service_control`, then Ctrl+C immediately.
Expected: node starts, logs nothing about "Waiting for..." (services already up), exits cleanly on Ctrl+C without traceback (a `KeyboardInterrupt` traceback is fine/expected at this stage since the key-loop isn't wired yet).

- [ ] **Step 4: Commit**

```bash
cd ~/ros2_workspaces/mini_project
git add src/turtlesim_projects/turtlesim_projects/turtle_service_control.py
git commit -m "turtle_service_control: create service clients for spawn/kill/set_pen/reset"
```

---

### Task 2: Request-building helper methods

**Files:**
- Modify: `src/turtlesim_projects/turtlesim_projects/turtle_service_control.py`

**Interfaces:**
- Consumes: `self.spawn_client`, `self.kill_client`, `self.set_pen_client`, `self.reset_client`, `self._pen_toggle` (from Task 1).
- Produces: `self.do_spawn()`, `self.do_kill()`, `self.do_set_pen()`, `self.do_reset()` — each builds a request, calls `call_async`, blocks with `spin_until_future_complete`, and logs the result. Task 3's key-loop calls these by name.

- [ ] **Step 1: Add the four methods to the class**

Add after `__init__` (still inside `TurtleServiceControl`):

```python
    def do_spawn(self):
        request = Spawn.Request()
        request.x = 5.0
        request.y = 5.0
        request.theta = 0.0
        request.name = 'turtle2'
        future = self.spawn_client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        response = future.result()
        self.get_logger().info(f'Spawned: {response.name}')

    def do_kill(self):
        request = Kill.Request()
        request.name = 'turtle2'
        future = self.kill_client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        future.result()
        self.get_logger().info('Killed: turtle2')

    def do_set_pen(self):
        self._pen_toggle = not self._pen_toggle
        request = SetPen.Request()
        if self._pen_toggle:
            request.r, request.g, request.b = 255, 0, 0
            request.width = 5
        else:
            request.r, request.g, request.b = 255, 255, 255
            request.width = 3
        request.off = 0
        future = self.set_pen_client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        future.result()
        self.get_logger().info(f'Pen set: rgb=({request.r},{request.g},{request.b}) width={request.width}')

    def do_reset(self):
        request = Empty.Request()
        future = self.reset_client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        future.result()
        self.get_logger().info('Reset simulation')
```

- [ ] **Step 2: Build**

Run: `colcon build --packages-select turtlesim_projects`
Expected: succeeds (methods aren't called yet, so no runtime check possible here).

- [ ] **Step 3: Commit**

```bash
git add src/turtlesim_projects/turtlesim_projects/turtle_service_control.py
git commit -m "turtle_service_control: add do_spawn/do_kill/do_set_pen/do_reset methods"
```

---

### Task 3: Keyboard-triggered main loop

**Files:**
- Modify: `src/turtlesim_projects/turtlesim_projects/turtle_service_control.py`

**Interfaces:**
- Consumes: `node.do_spawn()`, `node.do_kill()`, `node.do_set_pen()`, `node.do_reset()` (from Task 2).

- [ ] **Step 1: Replace `main()`**

```python
def main(args=None):
    rclpy.init(args=args)
    node = TurtleServiceControl()

    print('Keys: s=spawn turtle2, k=kill turtle2, p=toggle pen, r=reset, Ctrl+C=quit')

    settings = termios.tcgetattr(sys.stdin)
    try:
        while True:
            tty.setraw(sys.stdin.fileno())
            ready, _, _ = select.select([sys.stdin], [], [], 1)
            if not ready:
                continue
            key = sys.stdin.read(1)
            if key == 's':
                node.do_spawn()
            elif key == 'k':
                node.do_kill()
            elif key == 'p':
                node.do_set_pen()
            elif key == 'r':
                node.do_reset()
            elif key == '\x03':  # Ctrl+C
                break
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

- [ ] **Step 2: Build**

Run: `colcon build --packages-select turtlesim_projects`
Expected: succeeds.

- [ ] **Step 3: Manual test — spawn**

Terminal 1: `ros2 run turtlesim turtlesim_node`
Terminal 2: `source install/setup.bash && ros2 run turtlesim_projects turtle_service_control`, press `s`.
Expected: a second turtle appears at (5, 5) in the turtlesim window; terminal logs `Spawned: turtle2`.

- [ ] **Step 4: Manual test — kill**

Same session, press `k`.
Expected: turtle2 disappears from the window; terminal logs `Killed: turtle2`.

- [ ] **Step 5: Manual test — set_pen**

Press `p` twice (toggle on then off), and between the two presses drive turtle1 with another `custom_teleop` instance (or `ros2 run turtlesim turtle_teleop_key`) in a third terminal.
Expected: turtle1's drawn trail changes from default to thick red, then back to default (white/thin), matching the log line's rgb/width values.

- [ ] **Step 6: Manual test — reset**

Press `r`.
Expected: turtlesim window resets to a single turtle1 at the center, any drawn trail is cleared; terminal logs `Reset simulation`.

- [ ] **Step 7: Commit**

```bash
git add src/turtlesim_projects/turtlesim_projects/turtle_service_control.py
git commit -m "turtle_service_control: wire keyboard input to service calls"
```

---

### Task 4: Docs update

**Files:**
- Modify: `src/turtlesim_projects/docs/turtle_service_control.md`

- [ ] **Step 1: Update status and add keybindings**

Change line 17-18 from:
```
## 상태
TODO — 서비스 클라이언트 로직 미구현
```
to:
```
## 상태
완료

## 조작 키
- `s` : turtle2 spawn (5, 5)
- `k` : turtle2 kill
- `p` : turtle1 펜 토글 (빨강 두껍게 ↔ 기본)
- `r` : 시뮬레이션 reset
- `Ctrl+C` : 종료
```

- [ ] **Step 2: Commit**

```bash
git add src/turtlesim_projects/docs/turtle_service_control.md
git commit -m "docs: mark turtle_service_control as complete, document keybindings"
```
