# 1b. draw_shape_pose — 도형 그리기 (pose 실측 기반)

## 목적
[draw_shape_time](draw_shape_time.md)의 dead-reckoning(속도×시간 추정) 방식은 부동소수점 누적 오차로 정사각형이 정확히 닫히지 않는 문제가 있었음. `/turtle1/pose`를 구독해서 실제 위치/각도(x, y, theta)를 기준으로 판단하는 closed-loop 방식으로 구현.

## 사용 토픽
- Publish: `/turtle1/cmd_vel` (`geometry_msgs/msg/Twist`)
- Subscribe: `/turtle1/pose` (`turtlesim/msg/Pose`) — `x`, `y`, `theta`, `linear_velocity`, `angular_velocity` flat float 필드

## 익힐 개념

### 1. 두 콜백 사이의 read/write 역할 분리
- `pose_callback`은 turtlesim이 새 Pose를 publish할 때마다(우리 timer보다 훨씬 빠른 주기로) 호출됨 → `self.current_x/current_y/current_theta`에 **씀(write)**
- `timer_callback`은 0.1초마다 별도 스케줄로 호출됨 → 그 값을 **읽기만(read)** 하고, 대신 `twist`, `self.mode`, `self.start_x/y/theta`, `self.side_count`는 자기가 씀
- 두 콜백은 파라미터를 주고받는 게 아니라 `self.xxx`라는 공유 인스턴스 변수를 통해 "우편함"처럼 소통 — 트리거 주기가 다른 두 콜백을 연결하는 유일한 방법
- `timer_callback`이 `self.current_x`/`self.current_theta`를 직접 덮어써버리는 실수를 했었는데, 이러면 pose_callback이 다음에 또 진짜 값으로 덮어써버리므로 의미 없는 코드가 됨 → 역할 분리를 어기지 않는 게 중요

### 2. 시작 위치를 실측으로 캡처 (스폰 위치 가정 금지)
- `self.start_x`, `self.start_y`를 `__init__`에서 `0.0`으로 고정하면, turtlesim의 실제 스폰 위치(대략 5.5, 5.5)와 달라서 첫 `move` 구간의 거리 계산이 처음부터 틀어짐
- 해결: `self.pose_recived` 플래그를 두고, `pose_callback`이 **최초 1회** 메시지를 받을 때만 `start_x/y/theta`를 그 실측값으로 채움
- `timer_callback`도 첫 pose가 도착하기 전에 먼저 호출될 수 있으므로, 맨 앞에서 같은 플래그로 조기 리턴 처리 필요

### 3. 거리 판정 — 피타고라스
- `move` 모드: `sqrt((current_x - start_x)^2 + (current_y - start_y)^2) >= target_distance`로 실제 이동 거리를 직접 측정 (dead-reckoning처럼 속도×시간을 누적 추정하지 않음)

### 4. 각도 wraparound 정규화
- theta 범위는 `-π ~ π`. 개별 값(`current_theta`, `start_theta`)은 둘 다 이 범위 안에 있어도, **둘의 차이(delta)**는 범위를 벗어날 수 있음
  - 예: `start_theta=3.0`에서 90도(`π/2`) 더 돌면 이상적으론 `4.57`이지만 실제로는 `-1.71`로 감겨서(wrap) 나타남 → `raw delta = current - start = -4.71`, 기대값(`1.57`)과 전혀 다름
- 해결: `delta = current_theta - start_theta`를 구한 뒤, `π`보다 크면 `2π`를 빼고 `-π`보다 작으면 `2π`를 더해서 `-π~π`로 재정규화
- **정규화는 반드시 `delta`를 사용하기 전에** 해야 함 — 처음엔 `remain` 계산에 정규화 전 raw delta를 써버려서, 경계 근처에서 회전을 시작하자마자 "다 돌았다"고 오판하는 버그가 있었음

### 5. 이산 tick 체크로 인한 오버슈트 — pose를 써도 완전히는 안 사라짐
- pose 기반이라도 `timer_callback`은 0.1초에 한 번만 "목표 도달?"을 확인하므로, 확인하는 시점엔 이미 그 tick만큼(`angular.z × timer_period`) 더 돌아버린 뒤
- 이 오버슈트는 항상 같은 방향(항상 "더" 도는 쪽)으로 생기는 **일관된 바이어스**라서, `side_count` 정지 로직 없이 사각형을 무한 반복시키면 코너를 돌 때마다 오차가 쌓여 도형 전체가 점점 더 틀어짐(누적 drift)
- time 버전의 부동소수점 오버슈트와 근본적으로 같은 종류의 문제 — closed-loop(pose)는 "잘못된 가정으로 인한 오차 전파"는 막아주지만, "이산 시간 간격 자체의 오버슈트"는 별개 문제라서 안 없어짐

### 6. 비례 제어(P 제어)로 오버슈트 완화
- 고정 속도로 돌다가 갑자기 멈추는 대신, 남은 각도(`remain = target_angle - abs(delta)`)에 **비례**하는 속도로 회전: `angular.z = turn_gain * remain`
- 목표에 가까워질수록 속도가 같이 줄어드니, 마지막 tick의 오버슈트 폭도 자연히 작아짐
- 속도가 `remain`에 비례해서 계속 작아지기만 하면 이론상 완전히 도달하지 못하고 무한히 다가서기만 할 수 있음 → 최소 속도(floor)를 두는 대신 **허용오차(tolerance)** 방식 채택: `remain`이 특정 값 밑으로 내려가면 "도달한 것으로 간주"하고 회전 종료
- 수학적으로 `angular.z = k·remain`는 지수 감쇠(`remain(t) = remain(0)·e^(-k·t)`)이므로, 정착 시간은 `ln(remain(0)/tolerance) / k`로 계산 가능 — 이 공식으로 `turn_gain`, `tolerance` 값을 역산해서 튜닝

## 파라미터 선택 근거
- `turn_gain = 1.5`: `k=0.2`일 때 정착 시간이 `ln(1.57/0.01)/0.2 ≈ 25초`로 실습하기엔 너무 느려서, `1.5`로 올려 `ln(1.57/0.005)/1.5 ≈ 3.8초`로 단축. 초기 각속도(`1.5×1.57≈2.36 rad/s`)도 turtlesim이 무리 없이 소화하는 범위.
- `tolerance = 0.005`: `0.01→0.005`로 줄여도 추가 시간은 `τ·ln2 ≈ 0.46초`뿐이라, 체감 속도 큰 손해 없이 도달 정밀도만 높임.

## 알려진 남은 이슈
- `side_count` 증가 + 4변 완료 시 `timer.cancel()` 로직은 반복 동작을 눈으로 확인하려고 현재 주석 처리된 상태 — 재활성화하면 정사각형 하나 그리고 정지하도록 완성됨

## 상태
구현 완료 — pose 기반 이동/회전 판정, wraparound 정규화, 스폰 위치 실측 캡처, 비례 제어로 회전. `side_count` 정지 로직만 주석 해제하면 최종 완성.

## 실행 방법
```bash
ros2 run turtlesim turtlesim_node   # 별도 터미널
ros2 run turtlesim_projects draw_shape_pose
```
