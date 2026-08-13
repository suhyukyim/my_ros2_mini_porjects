# 4. turtle_service_control — 서비스 활용

## 목적
turtlesim이 제공하는 서비스들(`spawn`, `kill`, `set_pen`, `reset`)을 클라이언트로 호출해본다.

## 사용 서비스
- `/spawn` (`turtlesim/srv/Spawn`)
- `/kill` (`turtlesim/srv/Kill`)
- `/turtle1/set_pen` (`turtlesim/srv/SetPen`)
- `/reset` (`std_srvs/srv/Empty`)

## 익힐 개념
- 서비스 클라이언트 생성, `wait_for_service`
- 비동기 요청(`call_async`) + 콜백/퓨처 처리
- 요청 메시지 필드 채우기 (예: SetPen의 r/g/b/width)

## 상태
완료 — 4개 서비스 클라이언트 구현, 키 입력(`s`/`k`/`p`/`r`)으로 인터랙티브 호출 가능

## 실행 방법
```bash
ros2 run turtlesim turtlesim_node   # 별도 터미널
ros2 run turtlesim_projects turtle_service_control
```

실행하면 시작 시 `reset → spawn(turtle2) → set_pen(turtle1 빨간펜) → kill(turtle2)` 체크포인트가
자동으로 한 번 실행된다. 그 이후 터미널에 포커스를 둔 채:
- `s` — turtle2 spawn
- `k` — turtle2 kill
- `p` — turtle1 펜 색 변경(노란색 고정값)
- `r` — 화면 전체 reset
- `Ctrl+C` — 종료

자세한 개념 설명은 `NOTES.md`의 "turtle_service_control.py" 섹션 참고.
