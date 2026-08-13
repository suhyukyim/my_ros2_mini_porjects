# 6. obstacle_avoid — 장애물 회피 추격

## 목적

`turtle_chase`에 포텐셜 필드(potential field) 방식의 장애물 회피를 추가한다.
`turtle2`(추격자)가 `turtle1`(추격 대상)을 쫓아가되, 스폰된 `turtle3`(장애물, 고정 위치) 근처에서는 밀려나면서 우회한다.
Phase B 캡스톤(멀티 거북이 게임)의 AI 추격자가 장애물을 피하는 기반이 되는 단계.

## 사용 토픽/서비스

- Service client: `/spawn` (`turtlesim/srv/Spawn`) — turtle2(추격자), turtle3(장애물) 생성
- Subscribe: `/turtle1/pose`, `/turtle2/pose` (`turtlesim/msg/Pose`)
- Publish: `/turtle2/cmd_vel` (`geometry_msgs/msg/Twist`)

## 익힐 개념

- 포텐셜 필드 알고리즘: 인력(attractive, 목표로 끌어당김) + 척력(repulsive, 장애물에서 밀어냄) 벡터 합성
- 반경(threshold) 안에서만 척력이 작동하도록 하는 조건부 힘 계산
- 두 벡터를 (x, y) 성분으로 더한 뒤 atan2로 최종 목표 각도 추출
- 기존 turtle_chase.py의 스폰/구독/P 제어 패턴 재사용

## 헷갈렸던 개념 정리 (`/teach me` 세션에서 나온 질문들)

**1. create_client / create_publisher / create_subscription — 전부 "한 번만 만들면 끝"**
셋 다 `__init__`에서 딱 한 번 만들어두는 "창구"다. 매번 새로 만드는 게 아니라, 그 창구로
`.call_async()` / `.publish()` 를 필요한 만큼 반복 호출한다. 차이는 창구를 통해 무엇을 보내느냐:
- `create_publisher` → 고정된 토픽에 메시지만 계속 바뀌어서 나감 (토픽 이름은 생성 시점에 고정)
- `create_client` → 고정된 서비스에 `request` 내용물(이름, 좌표 등)을 바꿔서 보냄

**2. request / future / response 흐름**
```python
request = Spawn.Request()          # 1. 보낼 내용 채우기
request.name = 'turtle2'
future = spawn_client.call_async(request)      # 2. 비동기로 전송, future(진행 중인 작업표)를 받음
rclpy.spin_until_future_complete(self, future)  # 3. future가 끝날 때까지 대기
response = future.result()          # 4. 완료된 future에서 결과 꺼내기
```
`spin_until_future_complete`에는 `request`가 아니라 **`future`**(2번의 리턴값)를 넣어야 한다 —
`future`만 `.add_done_callback` 같은 진행 상태 추적 기능을 갖고 있음.

**3. 클래스 메서드 vs `__init__` 안의 지역 함수**
`class` 바로 아래(한 단계 들여쓰기)에 정의된 `def`만 `self.함수이름()`으로 호출 가능한 "메서드"가 된다.
`__init__` **안쪽**에 중첩해서 정의한 `def`는 `__init__`이 실행되는 동안만 존재하는 지역 함수라서
`self.`로 접근 불가능 (`AttributeError` 발생).

**4. 척력 세기 공식: `obstacle_radius - distance` vs `1/distance`**
반경 경계(`distance == obstacle_radius`)에서 `obstacle_radius - distance`는 정확히 0이 되어
부드럽게 척력이 시작된다. `1/distance`는 경계에서 `1/radius`라는 유한하지만 0이 아닌 값으로
갑자기 나타나서 부자연스럽다 (진짜 무한대 문제는 `distance`가 0에 가까워질 때 따로 있음).

**5. 벡터 연산은 성분(x, y)별로 — 각도끼리 더하면 안 됨**
인력 벡터 + 척력 벡터를 합칠 때 각도를 더하면 안 되고 `(dx, dy)` 성분끼리 더해야 한다.
각도는 크기(길이) 정보가 없어서, 각도만 더하면 벡터 합성이 정확하게 안 된다.
합친 뒤 `math.atan2(dy_final, dx_final)`로 최종 각도를 뽑는다 (atan2는 **y가 먼저, x가 나중**).

## 상태

구현 완료 — turtle2가 turtle1을 추격하는 것까지 동작 확인함.
장애물(turtle3) 근처에서의 회피 동작은 추가로 테스트해볼 것 (아직 실제로 가까이 접근하는 상황을 못 봄).

## 실행 방법

```bash
ros2 run turtlesim turtlesim_node   # 별도 터미널
ros2 run turtlesim_projects obstacle_avoid
```
