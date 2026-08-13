# turtlesim_projects 점진적 확장 — Phase A/B 설계

## 배경

`src/turtlesim_projects`는 ROS2(Humble) turtlesim으로 개념을 하나씩 익히는 학습형 미니 프로젝트 모음이다.
각 항목은 스텁 코드(노드 클래스 + `main()`) + `docs/<name>.md` 설명 문서로 시작하고, 개념 Q&A는
`NOTES.md`에 누적한다. 현재 상태:

| # | 파일 | 상태 |
|---|------|------|
| 1a/1b | draw_shape_time / draw_shape_pose | 완료 |
| 2 | custom_teleop | 완료 |
| 3 | turtle_chase | 완료 |
| 4 | turtle_service_control | 완료 |
| 5 | waypoint_nav | 스텁만 존재, 미구현 |

사용자가 "점진적으로 빌드업해서 나중엔 자연스럽게 하나의 프로젝트가 되는" 형태로 계속 진행하길 원함.
최종 목표 지향점: **멀티 거북이 게임** (추격/도망 + 장애물 회피 + 점수).

## 범위

이번 설계는 Phase A(기존 스텁 완성)와 Phase B(신규 주제, 캡스톤까지)의 로드맵을 확정한다.
실제 구현은 항목별로 순서대로 하나씩 진행하며, 각 항목 구현 직전에 (필요시) writing-plans로
세부 작업 계획을 만든다. 이 문서는 "무엇을, 어떤 순서로, 왜" 만드는지에 대한 합의이지,
각 파일의 코드 자체를 확정하는 것은 아니다.

## Phase A — 기존 스텁 완성

### #4 turtle_service_control.py
- 목적: `/spawn`, `/kill`, `/turtle1/set_pen`, `/reset` 서비스를 클라이언트로 호출.
- 익힐 개념: 서비스 클라이언트 생성 + `wait_for_service`, `call_async` + `spin_until_future_complete`
  (turtle_chase에서 배운 spawn 패턴을 Kill/SetPen/Empty 등 다른 요청 타입에 반복 적용).
- 산출물: `turtlesim_projects/turtle_service_control.py` 구현, `docs/turtle_service_control.md`의
  "상태"를 완료로 갱신.

### #5 waypoint_nav.py
- 목적: 미리 정한 좌표 리스트를 순서대로 방문.
- 익힐 개념: 목표 인덱스 상태 관리, 도착 판정(거리 임계값), 도착 시 다음 waypoint로 전환.
  turtle_chase의 거리/각도 P제어 로직을 재사용.
- 산출물: `turtlesim_projects/waypoint_nav.py` 구현, `docs/waypoint_nav.md` 상태 갱신.

## Phase B — 신규 주제 (멀티 거북이 게임을 향한 빌드업)

### #6 obstacle_avoid.py
- 목적: 추격 로직에 가상 장애물(좌표+반경 리스트)로부터 밀어내는 벡터를 더하는 potential-field
  방식 회피를 추가.
- 익힐 개념: 벡터 합성(끌어당기는 힘 + 밀어내는 힘), 파라미터 튜닝의 감각.
- 관계: `turtle_chase.py`를 확장하는 형태(새 노드 파일로 분리해 원본은 그대로 남김).

### #7 game_referee.py
- 목적: 여러 거북이의 pose를 동시에 구독해 "잡힘" 판정(거리 임계값 이하), 점수 집계,
  잡히면 `#4`에서 배운 kill/spawn 서비스 호출로 재배치.
- 익힐 개념: 다중 토픽 구독 관리, 게임 상태를 별도 토픽(예: `std_msgs/Int32` 점수)으로 publish,
  서비스 클라이언트를 "제어 로직"에서 실제로 호출하는 감각.

### #8 launch/game.launch.py
- 목적: `turtlesim_node` + 플레이어 teleop(#2) + AI 추격 거북이(#6) + referee(#7)를
  `ros2 launch turtlesim_projects game.launch.py` 한 줄로 동시 실행.
- 익힐 개념: ROS2 launch 파일 작성(Node 액션, 파라미터 전달), 여러 노드를 하나의 실행 단위로 묶기.
- 의미: 지금까지 "따로 실행하는 스크립트 모음"이었던 것이 여기서 "한 번에 실행되는 프로젝트"로 전환되는 지점.

## 진행 방식 (변경 없음, 기존 컨벤션 유지)

- 각 항목: 스텁 코드 + `docs/<name>.md` 설명 문서로 시작 → 함께 구현 → 개념 질문이 나오면
  `NOTES.md`에 Q&A로 누적.
- `README.md`의 프로젝트 목록 표에 Phase B 항목(#6~#8) 행 추가, 진행 상태 반영.

## 다음 단계

Phase A의 `#4 turtle_service_control.py`부터 시작. 구현 착수 전 writing-plans로 세부 계획을 만든다.
