# 학습 노트

프로젝트별 상세 문서는 `docs/`, 개념 Q&A는 여기에 정리.

## turtle_chase.py — spawn과 future

### Q. spawn이 뭔가요?

turtlesim에 **새 거북이를 만들어내는 것**. `turtlesim_node`를 켜면 기본으로 `turtle1`만 존재해서,
`turtle2`가 필요하면 `/spawn` 서비스에 "이 위치에 이 이름으로 만들어줘"라고 요청해야 한다.

### Q. future가 뭔가요?

**비동기 호출의 결과를 나중에 받기 위한 티켓(운송장 번호)**. 택배 주문에 비유하면:

- `call_async(request)` — 주문 넣고 운송장 번호(future)를 받음. 이 시점엔 아직 결과 없음.
- `rclpy.spin_until_future_complete(self, future)` — 배송 완료될 때까지 대기.
- `future.result()` — 배송 완료된 상자를 열어서 실제 내용물(response) 꺼내기.

**왜 이렇게 나눠서 처리하나?**
서비스 호출을 "그냥 블로킹으로 기다리기"로 처리하면, ROS 노드의 실행기(executor)가 보통 스레드 하나로 돌기 때문에
콜백 안에서 그런 블로킹 대기를 하면 **응답을 받아줄 스레드 자체가 없어서 교착상태(deadlock)** 에 빠질 수 있다.
`call_async` + `spin_until_future_complete`를 명시적으로 쓰는 건 이 문제를 피하기 위한 안전한 패턴.

`__init__`은 `main()`에서 `rclpy.spin(node)`가 호출되기 **전**에 실행되므로, 이 시점엔 다른 spin이 돌고 있지 않아
`spin_until_future_complete`를 안전하게 쓸 수 있다. (반대로 이미 spin 중인 콜백 안에서 blocking 호출을 하면 위험.)

### 코드에서 어떻게 쓰였나 (`turtle_chase.py` `__init__`)

```python
spawn_client = self.create_client(Spawn, '/spawn')          # 주문 창구 연결
while not spawn_client.wait_for_service(timeout_sec=1.0):   # 창구 영업 중인지 확인
    self.get_logger().info('Waiting for /spawn service...')

request = Spawn.Request()                                   # 주문서 작성
request.x, request.y, request.theta = 0.0, 0.0, 0.0
request.name = 'turtle2'

future = spawn_client.call_async(request)                   # 주문 제출 + 운송장 번호
rclpy.spin_until_future_complete(self, future)               # 처리 완료까지 대기
response = future.result()                                  # 상자 열기
self.get_logger().info(f'Spawned: {response.name}')
```

이 블록이 끝나야 실제로 `turtle2`가 화면에 존재 → 그 이후에야 `/turtle2/pose` 구독,
`/turtle2/cmd_vel` 발행이 의미가 있다. (spawn 코드를 지우고 테스트할 땐 `turtlesim_node`를 완전히
재시작해야 함 — 이전 실행에서 이미 spawn된 turtle2가 남아있으면 지웠는데도 되는 것처럼 착각하기 쉬움.)

### Q. `self.turtle2_x = 0.0` 초기화가 spawn 요청의 `request.x = 0.0`이랑 같은 값인데, 중복 아닌가?

값만 같을 뿐 **완전히 다른 변수**.

- `request.x` — turtlesim한테 "여기 그려줘"라고 보내는 주문 내용. turtle2가 화면에 그려지는 실제 위치.
- `self.turtle2_x` — 우리 노드 **자신의 Python 변수**. `/turtle2/pose` 구독 콜백(`pose_callback_2`)이
  실시간으로 채워주는 값.

Python은 `self.turtle2_x`를 누군가 한 번 대입해야 존재하는 변수라서, `pose_callback_2`가 아직 한 번도
안 불렸을 때(타이밍 상 timer_callback이 먼저 도는 경우 등) 대비한 **기본값**으로 초기화해둔 것.
`draw_shape_pose.py`의 `pose_recived` 플래그와 같은 목적(진짜 데이터 도착 전 안전장치)인데,
`turtle_chase.py`는 그 가드 없이 그냥 0.0 기본값만 두고 있음 — 나중에 개선 여지로 남겨둠.

### Q. spawn의 `response`엔 turtle2의 위치도 들어있나?

아니다. `response`엔 **생성 확인 정보**(이 예제에선 `response.name` — 실제로 부여된 이름)만 있음.
위치(x, y, theta)는 spawn과 무관하게 계속 흘러나오는 `/turtle2/pose` 토픽 구독을 통해서만 받는다.
spawn = "생성 확인", pose 구독 = "실시간 위치 추적". 서로 다른 통신 채널.

## turtle_service_control.py — 서비스 이름 vs 타입, 블로킹 안전성

### Q. `create_client(SetPen, '/set_pen')`처럼 두 번째 인자를 아무 문자열이나 넣어도 되나?

안 된다. `create_client(TYPE, 'service_name')`의 두 인자는 역할이 다르다:
- **첫 번째(타입)** — 요청/응답 필드 구조를 정의하는 파이썬 클래스 (`import`한 것).
- **두 번째(문자열)** — 실제로 접속할 서비스의 **주소**. 서버(`turtlesim_node`)가 이미 등록해놓은
  이름과 정확히 똑같이 써야 접속된다. 자유롭게 짓는 이름이 아니다.

이 둘은 독립적이라 우연히 비슷하게 생겼을 뿐(`Spawn`/`/spawn`, `Kill`/`/kill`), 항상 일치하는 게 아니다.
`SetPen` 타입을 쓴다고 서비스 주소가 `/set_pen`이나 `/SetPen`이 되는 게 아니라 `/turtle1/set_pen`이고,
`Empty` 타입을 쓴다고 서비스 주소가 `/empty`가 되는 게 아니라 `/reset`이다. 실제 주소는
`docs/04_turtle_service_control.md`나 `ros2 service list`로 확인해야 한다.

### Q. 왜 `/turtle1/set_pen`만 이름 앞에 `turtle1/`이 붙고, `/spawn`/`/kill`/`/reset`은 안 붙나?

서비스가 **무엇을 대상으로 하는 동작이냐**로 갈린다:
- `spawn`(아직 없는 turtle을 새로 만듦), `kill`(turtle을 없앰), `reset`(화면 전체 초기화) —
  전부 "시뮬레이션에 어떤 turtle들이 존재하는지"를 관리하는, **시뮬레이션 전체 관리자**의 일.
  특정 turtle 하나에 종속되지 않으므로 이름 앞에 아무것도 안 붙는다.
- `set_pen`은 "**이미 존재하는** turtle1 자기 자신의 펜(자기 소유 속성)"을 바꾸는 일이라,
  turtlesim이 turtle마다 각자의 `set_pen` 서비스를 따로 만들어준다 (`/turtle1/pose`,
  `/turtle1/cmd_vel`과 같은 이유). `turtle2`를 spawn해도 `/turtle2/set_pen`이 별도로 생길 뿐,
  `/turtle1/set_pen`으로 turtle2를 조작할 수는 없다.

패키지 출처(`turtlesim` vs `std_srvs`)는 이 구분과 무관하다 — `Spawn`, `Kill`, `SetPen` 전부
`turtlesim` 패키지 소속이지만 전역/개별 여부는 서로 다르다.

### Q. `SetPen`으로 펜 색을 바꿨는데 화면에 아무 변화가 없다.

버그가 아니다. `SetPen`은 **앞으로 그 turtle이 움직이며 그릴 선의 색**을 정해두는 것뿐이고,
이미 그려진 선을 다시 칠하거나 turtle 아이콘 자체의 색을 바꾸지 않는다. turtle이 실제로
움직이지 않으면(= 이 프로젝트처럼 `cmd_vel`을 한 번도 publish 안 하면) 그릴 선 자체가
없으므로 눈에 보이는 변화도 없다. 확인하려면 `set_pen` 호출 후 `custom_teleop.py` 등으로
그 turtle을 조금이라도 움직여봐야 한다.

### Q. `rclpy.spin_until_future_complete`(블로킹)를 어디서 써도 되고 어디서 위험한가?

`turtle_chase.py`에서 정리했던 "택배 비유"의 연장: 블로킹 호출은 **완료 처리를 해줄 스레드가
따로 있어야** 안전하다.
- `__init__` 안 — 안전. `main()`의 `rclpy.spin(node)`가 아직 시작 전이라 경쟁하는 다른 spin이 없다.
- 이미 `rclpy.spin(node)`이 돌고 있는 **콜백(타이머 콜백 등) 안** — 위험. 그 콜백을 실행 중인
  스레드 자신이 future 완료 처리도 해줘야 하는데, 스스로 블로킹 대기 중이라 아무도 처리를
  못 해줘서 교착상태(deadlock)에 빠진다.
- 회피 방법 두 가지: ① `MultiThreadedExecutor`로 스레드를 늘린다, ② `future.add_done_callback(fn)`로
  블로킹 없이 "완료되면 자동 호출"만 예약해둔다(폴링이 아니라 이벤트 콜백 등록).

`turtle_service_control.py`의 키 입력 인터랙티브 버전은 ①②가 필요 없었다 — `custom_teleop.py`
패턴을 그대로 재사용해서 `main()`에 **`rclpy.spin(node)`을 아예 안 쓰고** `while True` 수동
루프로 키를 읽기 때문. 이 경우 키 핸들러가 "이미 도는 spin 안의 콜백"이 아니라 그냥 메인
스레드의 평범한 코드라서, `__init__`과 동일하게 블로킹 호출이 안전하다.

## waypoint_nav.py — 타이머 콜백 안에 while을 넣으면 안 되는 이유, 도착 판정과 P 제어

### Q. `create_timer`로 등록한 콜백 안에 `while` 루프를 넣어서 "도착할 때까지 반복"시키면 안 되나?

안 된다. `create_timer(period, callback)`을 등록하는 순간, **executor가 이미 그 반복 역할**을
대신 해준다 — `period`마다 자동으로 콜백을 다시 불러주기 때문에, 콜백 자체는 "한 번 호출되면
딱 한 스텝만 판단하고 끝나는" 함수여야 한다.

콜백 안에 `while`을 넣으면, rclpy의 기본 실행기는 싱글 스레드라 그 콜백이 `return`하기 전까지
다른 콜백(예: `/turtle1/pose` 구독 콜백)이 끼어들 기회가 없다. 즉 `while` 루프가 도는 동안
`self.cur_x`/`self.cur_y`가 최신 위치로 갱신될 수 없어서, 매번 같은 낡은 값으로 거리를 계산하게
되고, 노드 전체가 그 콜백 안에 갇혀 응답 불능 상태가 된다.

### Q. turtle이 목표 지점을 못 찍고 계속 그 주변을 빙빙 돌았다. 왜?

도착 판정 임계값(`distance < threshold`)과 "한 tick당 실제로 이동하는 거리"의 관계를 안 따졌기
때문. 예를 들어 `linear.x`를 고정 속도 1.0(= 초당 1 유닛)으로 두고 타이머 주기가 0.1초면, 한
tick마다 최대 약 0.1만큼 이동하는데, 임계값을 그보다 작은 0.05로 잡으면 target 반경 0.05 안으로
"들어오는 순간"을 한 tick 단위로는 못 잡고 훌쩍 지나쳐버릴(overshoot) 수 있다. 그러면
`target_angle`이 갑자기 반대 방향으로 확 튀면서 다시 그쪽으로 도는 게 반복돼 궤도를 그리는
것처럼 보인다.

### Q. 그래서 어떻게 고쳤나?

임계값을 무작정 키우는 대신(정확도가 떨어짐), **목표에 가까워질수록 속도 자체가 자연스럽게
줄어들도록** 거리에 비례한 속도(P 제어, 비례 제어)를 쓰고, 동시에 `min()`으로 상한을 씌워서
멀리 있는 waypoint로 갈 때 속도가 무한정 커지지 않게 막았다.

```python
twist.linear.x = 0.5 * min(0.5 * distance, self.max_speed)
twist.angular.z = 0.5 * angle_error
```

이렇게 하면 목표에 다가갈수록 한 tick당 이동 거리도 같이 줄어들어서, 작은 임계값으로도
문턱을 놓치지 않고 정확하게 도착 판정을 낼 수 있다. (참고로 "회전 먼저 → 직진 → 회전"처럼
단계를 나누는 방식도 가능한데, 그건 상태(지금 회전 중/이동 중)를 추가로 관리해야 해서 더
복잡하고 예측 가능한 대신 경로가 끊기는 식으로 움직인다. 지금 방식은 거리·각도 오차를 동시에
반영하는 연속 제어라서 경로가 곡선으로 부드럽게 이어진다.)
