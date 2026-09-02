# 학습 노트

프로젝트별 상세 문서는 `docs/`, 개념 Q&A는 여기에 정리.

---

## 1. 왜 액션인가 (토픽/서비스로는 뭐가 부족한가)

**토픽**은 발행자가 구독자로부터 아무것도 되돌려받지 못한다. `/turtle1/cmd_vel`에
Twist를 계속 쏘는 것만으로는 ① 상대가 목표를 접수했는지 ② 지금 얼마나 왔는지
③ 끝났는지·성공인지를 전부 알 수 없다. P제어 로직도 클라이언트가 직접 들고 있어야 한다.

**서비스**는 ①과 ③은 해결한다(요청→응답). 하지만 이동에 10초가 걸리면 그 10초 동안
클라이언트 화면은 깜깜하다. 진행 상황을 알 수 없고, 중간에 그만두게 할 수도 없다.

> **액션 = 서비스 + feedback + cancel.**
> 깜깜한 구간을 메우는 게 feedback, 그 구간에 끼어들 수 있게 하는 게 cancel.

## 2. Feedback vs Result — 무엇을 어디에 넣나

| | 발행 횟수 | 성격 |
|---|---|---|
| Feedback | 작업 중 계속 (매 루프) | 시간에 따라 변하는 **중간 상태** |
| Result | 끝날 때 딱 한 번 | 끝나야 확정되는 **최종 요약** |

- `distance_remaining`이 Feedback인 이유: 도착하면 값이 0이라 Result에 담아도 정보가 없다.
- `total_time`이 Result인 이유: 작업이 끝나기 전에는 계산 자체가 불가능하다.

## 3. executor가 하는 일

`rclpy.spin(node)`이 프로그램을 붙잡고 있는 이유 = **executor가 무한 루프를 돌기 때문**.

```
while 살아있는 동안:
    1. 도착한 게 있나 확인 (새 메시지? 타이머 만료? 서비스 요청? 액션 goal?)
    2. 있으면 등록된 콜백을 호출
    3. 콜백이 끝나면 1번으로
```

콜백은 우리가 **등록만** 해놓은 것이고, **실제로 불러주는 주체가 executor**다.
`publish()`는 우리가 직접 호출하므로 이 루프와 무관하다 — executor가 관여하는 건
**콜백 쪽**이다.

---

## 4. execute_callback에서 while을 돌리면 왜 무한루프가 되나 ★

`timer_callback`과 `execute_callback`의 결정적 차이:

| | 누가 호출 | 몇 번 호출 |
|---|---|---|
| `timer_callback` | 타이머 | 주기적으로 **계속** |
| `execute_callback` | ActionServer | goal 하나당 **딱 한 번** |

그래서 액션 서버는 "반복"을 타이머가 대신 해주지 않는다. **함수 안에서 직접 while로
만들어야 한다.** 그런데 기본 설정(`rclpy.spin(node)` = 싱글스레드)에서 while을 돌리면:

```
execute_callback 안에서 while 진입
  → 이 콜백이 return하지 않음
  → executor 루프가 2번 단계에 묶여서 3번(다음 확인)으로 못 감
  → 새로 온 /turtle1/pose 메시지는 큐에 쌓이기만 하고 pose_callback이 호출 안 됨
  → self.cur_x, self.cur_y가 __init__ 초기값(5.0, 5.0)에 그대로 고정
  → 매 루프 distance를 다시 계산해도 값이 안 변함
  → while distance > 0.1 이 영원히 안 끝남
```

**겉모습**: 거북이는 화면에서 실제로 움직이고 있는데, 서버는 그걸 전혀 모른 채
같은 거리만 계속 계산한다. 취소 요청도 같은 큐에 쌓여만 있어서 `cancel_callback`도
호출되지 않는다.

> 주의: 원인은 "spin이 나빠서"가 아니라 **콜백이 반환하지 않아서**다.
> spin의 루프는 "콜백 호출 → 끝나면 → 다음 확인"인데, 콜백을 안 끝내주고 있는 것.
> 메시지도 "못 가져오는" 게 아니라 **큐에 있는데 꺼내줄 사람이 없는** 상태다.
> (그래서 while이 끝나면 밀린 pose 콜백이 우르르 실행된다.)

`waypoint_nav.py`에서 배운 "타이머 콜백에 while 넣지 마라"와 **완전히 같은 얘기**,
콜백 종류만 다르다.

### 왜 타이머로 쪼개는 방식은 안 되나

`execute_callback`은 **반환값이 Result**다. 즉 `return`하는 순간 "이 goal은 끝났다"는
뜻이다. 타이머만 만들어놓고 바로 return하면 거북이가 출발도 안 했는데 goal이 종료된다.
그래서 액션 서버는 다른 길(멀티스레드)을 간다.

---

## 5. MultiThreadedExecutor + ReentrantCallbackGroup — 왜 둘 다 필요한가 ★

**식당 비유**가 제일 명확하다:

| 코드 | 비유 |
|---|---|
| `rclpy.spin(node)` | 직원 **1명** |
| `MultiThreadedExecutor()` | 직원 **여러 명** |
| `MutuallyExclusiveCallbackGroup` (기본값) | "한 번에 **한 테이블만** 받아라" |
| `ReentrantCallbackGroup` | "**여러 테이블 동시에** 받아도 된다" |

- 직원 5명 + "한 테이블만" 규칙 → 동시 처리 **1개**
- 직원 1명 + "여러 테이블 OK" 규칙 → 동시 처리 **1개**
- 직원 여러 명 **AND** "여러 테이블 OK" → 비로소 동시 처리 **2개 이상**

그래서 코드에도 **두 군데** 다 손이 간다:

```python
# __init__ — 규칙을 만들고
self.cb_group = ReentrantCallbackGroup()

# ...그 규칙을 실제 콜백에 붙여야 효과가 생긴다
self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10,
                         callback_group=self.cb_group)
ActionServer(self, MoveToGoal, 'move_to_goal', ...,
             callback_group=self.cb_group)

# main() — 직원 수
executor = MultiThreadedExecutor()
rclpy.spin(node, executor=executor)
```

**구독과 ActionServer가 같은 Reentrant 그룹**에 들어 있어야 하는 이유:
`execute_callback`이 while로 붙잡혀 있는 동안 **다른 스레드가 `pose_callback`을 실행**해서
`self.cur_x`를 갱신해줘야 4번의 무한루프가 풀린다. 취소 확인도 마찬가지.

Reentrant는 서로 다른 콜백끼리 동시 실행은 물론, **같은 콜백이 여러 번 겹쳐서** 돌 수도
있다(re-entrant = 재진입). goal을 2개 동시에 보내면 `execute_callback`이 2개 동시에 돈다.

### 멀티스레드의 대가: race condition

`pose_callback`은 `self.cur_x`에 **쓰고**, `execute_callback`은 같은 값을 **읽는다**.
서로 다른 스레드에서.

```python
self.cur_x = msg.x      # ← 여기까지 실행된 순간
self.cur_y = msg.y      # ← 아직 실행 전
```

바로 이 사이에 다른 스레드가 둘 다 읽으면, **x와 y가 서로 다른 pose 메시지에서 온
값**이 된다. 거북이가 실제로 있었던 적 없는 좌표다.

이 프로젝트에서 괜찮은 이유: turtlesim이 60Hz로 pose를 뿌리니 오차가 1/60초분 —
도달 임계값 0.1에 비해 무시할 만하다. 실제 로봇에서 1cm 단위 판정을 한다면
**튜플로 한 번에 대입**해서 막는다:

```python
self.pose = (msg.x, msg.y, msg.theta)   # 참조 하나를 통째로 교체
```

> `time.sleep(0.1)`이 노드 전체가 아니라 **그 스레드만** 멈추는 것도 멀티스레드 덕분이다.

---

## 6. 취소 흐름 ★

**시간 순서:**

```
(1) 클라이언트가 cancel_goal_async() 호출
(2) 취소 요청 메시지가 서버에 도착
(3) ActionServer가 cancel_callback을 호출
(4) ACCEPT를 반환하면 → is_cancel_requested가 False → True로 바뀜
(5) execute_callback이 루프 맨 앞에서 그 플래그를 읽고 True를 발견
```

**핵심**: `is_cancel_requested`를 True로 바꾸는 건 **`cancel_callback`이 ACCEPT를
반환했기 때문**이다. `execute_callback`은 그 플래그를 **읽기만** 하지 쓰지 않는다.

**REJECT를 반환하면**: (4)가 일어나지 않는다 → 플래그는 계속 False → 루프의
`if goal_handle.is_cancel_requested:`가 절대 안 걸린다 → **작업이 그대로 계속된다.**

> 즉 취소는 클라이언트의 **부탁**이지 명령이 아니다. 서버가 거부권을 갖는다.
> 거부권이 필요한 이유: 로봇 팔이 무거운 상자를 공중에 든 상태에서 "즉시 정지"하면
> 위험하다. "지금 멈추면 오히려 더 나쁜 순간"이 실제로 존재한다.

### 취소 확인은 루프 맨 앞에

맨 뒤에 두면 취소 요청이 도착한 뒤에도 한 바퀴(0.1초)를 더 움직이고 나서야 멈춘다.

### 종료 메서드 3종 — 반환값과 별개다

| 상황 | 메서드 | status |
|---|---|---|
| 목표 도착 | `goal_handle.succeed()` | SUCCEEDED |
| 취소 수락 후 중단 | `goal_handle.canceled()` | CANCELED |
| 에러로 실패 | `goal_handle.abort()` | ABORTED |

`return`은 **내용물(Result)** 만 실어나르고, "이게 어떤 결말이었나(status)"는 이
메서드가 정한다. 안 부르면 클라이언트는 결과는 받는데 상태가 미정으로 남는다.

**나가기 전에 반드시 속도 0을 발행할 것** — 취소든 성공이든. 직전 바퀴에서 이미
"전진해" Twist를 쏴뒀기 때문이다. `Twist()`는 만들면 모든 필드가 0.0이라 그대로 쓰면 된다.

### 루프 한 바퀴의 확정된 순서

```
1. 취소 요청 확인   → True면: 속도 0 발행, canceled(), Result 반환
2. 거리/각도 오차 계산
3. 도착 판정        → True면 break
4. Twist 발행 (P제어)
5. feedback 발행
6. time.sleep(0.1)
--- 루프 밖 = 도착 ---
속도 0 발행, succeed(), Result 반환
```

---

## 7. 클라이언트는 왜 콜백으로 쪼개지나 (future) ★

서버는 `while`로 쭉 이어지는데 클라이언트는 메서드 5개로 잘게 쪼개져 있다. 이유는
**클라이언트 코드도 `rclpy.spin(node)` 안에서 돌기 때문**이다. 결과가 나오려면 서버가
10초 일해야 하는데, 그동안 결과를 기다리며 블로킹하면 클라이언트의 executor가 멈춘다 —
feedback도 못 받는다. (4번과 정확히 같은 문제)

그래서 `send_goal_async()`를 쓴다. 호출 즉시 반환하고, 결과는 나중에 콜백으로 받는다.

### future = 아직 안 채워진 빈 상자

- `future` — 결과가 들어올 자리. 아직 비어 있다.
- `future.add_done_callback(f)` — "이 상자가 **채워지면** f를 불러줘"라는 **예약**
- `future.result()` — 그 상자를 여는 동작

### 액션은 상자가 두 개

서비스는 상자가 하나인데, 액션은 **시간 순으로 두 개**다:

| | 담기는 것 | 언제 채워지나 | 뜻 |
|---|---|---|---|
| 상자 1 `send_goal_async()` | goal_handle | 서버가 goal을 받자마자 | "**수락**됐는가?" |
| 상자 2 `get_result_async()` | Result | 서버가 일을 다 끝냈을 때 | "**어떻게 끝났는가**?" |

서버가 goal을 거절할 수도 있으므로 두 단계로 나뉜다 → `goal_handle.accepted` 확인.

```
send_goal ──send_goal_async()──▶ [상자1] ──add_done_callback──▶ goal_response_callback
                                                                       │ accepted?
                                                          get_result_async()
                                                                       ▼
                                        [상자2] ──add_done_callback──▶ get_result_callback

feedback_callback ◀── 별도로 계속 (future 체인 밖)
```

### feedback만 왜 체인 밖인가

future는 **딱 한 번** 채워지면 끝나는 일회용 상자다. feedback은 작업 중 **계속** 오므로
future에 담을 수 없다. 그래서 `send_goal_async(goal_msg, feedback_callback=...)`처럼
인자로 따로 등록한다.

### goal_handle을 저장해두는 이유

`self._goal_handle = goal_handle` — 나중에 `cancel_goal_async()`를 부르려면 핸들이
있어야 한다. 저장 안 하고 버리면 취소를 보낼 방법이 없다.

> `game_referee.py`의 `do_kill` → `on_kill_done` 체이닝과 같은 구조.
> `call_async` 자리에 `send_goal_async`가 들어갔을 뿐.

---

## 삽질 기록 / 도구

### 이 객체에 뭐가 있는지 어떻게 아나

```bash
# ① 객체의 속성·메서드 전부 나열
python3 -c "
from rclpy.action.server import ServerGoalHandle
print([m for m in dir(ServerGoalHandle) if not m.startswith('_')])
"
# → ['abort','canceled','destroy','execute','executing','goal_id','is_active',
#     'is_cancel_requested','publish_feedback','request','status','succeed']

# ② 소스 파일 위치 찾아서 직접 읽기 (rclpy는 전부 파이썬이라 읽을 수 있다)
python3 -c "import rclpy.action.server as m; print(m.__file__)"

# ③ 인터페이스 구조 보기
ros2 interface show geometry_msgs/msg/Twist
ros2 interface show turtle_action_interfaces/action/MoveToGoal
```

`help(클래스.메서드)`도 있다. IDE 자동완성이 90%를 해결하지만, 안 될 때 위 방법으로 판다.

### 타입 vs 이름

`ActionServer(self, MoveToGoal, 'move_to_goal', ...)`

- `MoveToGoal` = **타입** (`.action` 파일에서 나옴, 대문자)
- `'move_to_goal'` = **이름** (그냥 문자열로 직접 적은 것, 네트워크상의 주소)

`create_publisher(Twist, '/turtle1/cmd_vel', 10)`와 같은 구조.
`.action` 파일이 아니라 이름을 바꾸면 `ros2 action list`에 뜨는 게 바뀌고,
`send_goal` 명령의 해당 부분도 바꿔야 한다.

### `MoveToGoal.Result(...)`는 내장이 아니다

`.action` 파일을 `colcon build`할 때 ROS가 파이썬 클래스 3개(`Goal`/`Result`/`Feedback`)를
자동 생성한다. 그래서 필드 이름이 `.action`에 쓴 것과 정확히 같아야 한다.

```
install/turtle_action_interfaces/lib/python3.12/site-packages/turtle_action_interfaces/action/
```

**오타를 내면 `AssertionError`가 난다.** 실제로 겪은 증상:

```
Result:  success: false        ← 코드엔 success=True로 썼는데?
Goal finished with status: SUCCEEDED
```

원인: `MoveToGoal.Result(succees=True, ...)` 오타 →
`succeed()`는 이미 호출됨(status는 SUCCEEDED 확정) → 그 다음 줄에서 예외 발생 →
`return`이 실행 안 됨 → ActionServer가 예외를 잡고 **빈 Result**를 대신 돌려줌.

> **교훈**: "성공했다는데 값이 이상하다"면 클라이언트 터미널만 보면 안 된다.
> **서버 터미널의 traceback을 봐야** 원인이 나온다.
> 그리고 파이썬은 키워드 인자 오타를 **실행할 때**만 잡는다 (동적 언어의 대가).

### 그 외 실수들

| 쓴 것 | 문제 | 고침 |
|---|---|---|
| `Twist(0, 0)` | 이 생성자는 위치 인자를 안 받음 | `Twist()` (기본값 전부 0) |
| `goal_handle.is_cancel_requested()` | **속성**인데 괄호를 붙임 | 괄호 제거 |
| `if goal_handle.succeed():` | succeed는 "성공했니?"가 아니라 "성공으로 **끝내라**" | `if distance < 0.1:` |
| `if distance == 0:` | 실수가 정확히 0.0이 될 일은 거의 없음 → 영원히 안 멈춤 | `distance < 0.1` |
| `twist.linear.x = 1.5` | 상수라 P제어가 아님 (오차와 무관하게 등속) | `1.5 * distance` |
| `twist.linear.x = 0` | ROS 메시지는 타입이 엄격 (`float64`) | `0.0` |
| `self.get_logger.info(...)` | `get_logger`는 로거를 **돌려주는 함수** | `self.get_logger().info(...)` |
| `return succeed(), status()` | 반환형은 `Result` 하나 | `MoveToGoal.Result(...)` |

### 시간 재기

```python
start = self.get_clock().now()
...
elapsed = (self.get_clock().now() - start).nanoseconds / 1e9
```

`time.time()`이 아니라 **ROS 시계**를 쓴다. Gazebo에서 `use_sim_time`을 켜고 시뮬레이션을
2배속으로 돌리면 벽시계는 틀린 값을 준다. Nav2 갈 거니까 지금부터 습관을 잡는다.

### 각도 오차 정규화

```python
angle_error = target_angle - self.cur_theta
if angle_error > math.pi:
    angle_error -= 2 * math.pi
elif angle_error < -math.pi:
    angle_error += 2 * math.pi
```

안 하면: `theta=3.0`, 목표 방향 `-3.0`일 때 오차가 `-6.0`으로 계산돼서 먼 쪽으로 크게 돈다.
실제로는 반대쪽으로 `0.28`만 돌면 되는데.

### 테스트 방법

**클라이언트 없이 서버만 테스트** — CLI가 클라이언트 역할을 대신해준다:

```bash
ros2 action list
ros2 action info /move_to_goal -t
ros2 action send_goal --feedback /move_to_goal \
    turtle_action_interfaces/action/MoveToGoal "{x: 8.0, y: 8.0}"
```

`--feedback`을 붙여야 중간 feedback이 화면에 찍힌다.

**단, CLI로는 취소 테스트를 못 한다.** Ctrl+C를 누르면:

```
^CCanceling goal...
Executor is already spinning
```

CLI 쪽이 결과를 출력하기 전에 죽어버린다. 그래서 클라이언트에 타이머를 걸어서 테스트했다:

```python
self.timer = self.create_timer(3.0, self.cancel_goal)   # send_goal 안에서

def cancel_goal(self):
    if self._goal_handle:
        self._goal_handle.cancel_goal_async()
        self.timer.cancel()      # 타이머는 반복 호출되므로 한 번 쓰고 끈다
```

목표를 멀리(`1.0, 1.0`) 잡아야 3초 안에 도착 안 해서 취소가 걸린다.

> **"거북이가 멈췄다"만으로는 취소가 됐다는 증거가 안 된다.**
> turtlesim은 cmd_vel이 일정 시간 안 오면 스스로 거북이를 세운다.
> 성공/취소 양쪽 경로에 로그를 찍어서 구분할 것. (취소는 `warn`으로 찍으면 노란색이라 눈에 띈다)

### 검증 결과 (2026-09-02)

```
# 성공 경로
[goal_client]: 3.4726 → 3.0774 → ... → 0.1589
[goal_client]: True , 2.1266558170318604

# 취소 경로 (3초 뒤 자동 취소)
[goal_server]: goal = (1.0 , 1.0)
[WARN] [goal_server]: goal canceled
[goal_client]: False , 2.7910616397857666
```

---

## 다음: Nav2

4번과 5번(블로킹 execute_callback + MultiThreadedExecutor + ReentrantCallbackGroup)은
Nav2를 포함한 **실제 액션 서버들이 쓰는 바로 그 패턴**이다. Nav2로 넘어가면 그대로 다시 만난다.
