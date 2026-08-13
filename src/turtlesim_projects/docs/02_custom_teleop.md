# 2. custom_teleop — 키보드 원격 조종

## 목적
`teleop_twist_keyboard` 패키지 없이 직접 키 입력을 받아 `/turtle1/cmd_vel`을 퍼블리시한다.

## 사용 토픽
- Publish: `/turtle1/cmd_vel` (`geometry_msgs/msg/Twist`)

## 키 매핑
Twist는 위치가 아니라 **속도 명령**이며, turtle의 로컬 좌표계(바라보는 방향) 기준이다.

| 키 | linear.x | angular.z | 의미 |
|---|---|---|---|
| w | 2.0 | 0.0 | 전진 |
| s | -2.0 | 0.0 | 후진 |
| a | 0.0 | 2.0 | 좌회전 (제자리) |
| d | 0.0 | -2.0 | 우회전 (제자리) |
| Ctrl+C (`\x03`) | - | - | 루프 종료 |

- `linear.x`는 절대 x축이 아니라 turtle이 **지금 바라보는 방향**으로의 전진 속도 (body frame)
- `angular.z`는 각속도(rad/s)이지 회전 각도가 아님 — `theta`(현재 방향)와는 다른 값
- turtlesim은 2D라서 `linear.y/z`, `angular.x/y`는 존재하지만 무시됨 (`ros2 interface show geometry_msgs/msg/Twist`로 전체 필드 확인 가능)

## 구현 개념
- **퍼블리셔 재사용**: `create_publisher()`가 반환하는 Publisher 객체를 `self._publisher`에 저장해두고, 매 키 입력마다 `.publish()`로 재사용
- **터미널 raw 모드**: `termios.tcgetattr`로 원래 설정 저장 → `tty.setraw`로 라인 버퍼링 없이 키 1개 즉시 감지 → 종료 시 `termios.tcsetattr`로 복원 (안 하면 프로그램 종료 후 셸 입력이 깨짐)
- **non-blocking 읽기**: `select.select([sys.stdin], [], [], timeout)`으로 매 반복마다 "timeout 안에 입력이 있는지"만 확인, 없으면 다음 반복으로 (blocking `read()`와 달리 계속 대기하지 않음)
- **종료 시 정지**: cmd_vel은 새 명령이 올 때까지 마지막 속도를 유지하므로, 루프를 빠져나온 직후 `Twist()`(전부 0) 를 한 번 더 publish해서 turtle을 확실히 멈춤
- `try/finally`로 예외가 나도 raw 모드가 항상 복원되도록 보장

## 상태
구현 완료 (w/a/s/d 이동, Ctrl+C 종료, select 기반 non-blocking 읽기)

## 실행 방법
```bash
ros2 run turtlesim turtlesim_node   # 별도 터미널
ros2 run turtlesim_projects custom_teleop
```
