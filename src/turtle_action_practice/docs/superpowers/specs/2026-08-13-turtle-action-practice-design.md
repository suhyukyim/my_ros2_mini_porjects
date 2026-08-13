# turtle_action_practice — Design Spec

## Overview

A standalone ROS2 learning project (separate from `turtlesim_projects`) focused
on the one communication pattern not yet covered there: **actions**. The user
writes a turtle to a goal point using a custom action type, learning the
goal/feedback/result/cancel lifecycle by implementing both the action server
and the action client themselves.

This is roadmap phase 1 of a two-phase plan; phase 2 (TurtleBot3 + Gazebo +
Nav2) is out of scope for this spec and will be brainstormed separately once
this phase is done.

## Motivation

The user has built `turtlesim_projects` up through topics and services
(sync blocking calls and async fire-and-forget with `add_done_callback`), but
has never authored an action server. Nav2 (the eventual phase 2 target) is
built entirely on actions, so understanding the mechanism — not just calling
someone else's action server — is the prerequisite.

## Packages

Two new ROS2 packages under `mini_project/src/`, alongside the existing
`turtlesim_projects` package. A custom `.action` definition requires message
generation, which `ament_python` packages cannot do — hence the split.

### 1. `turtle_action_interfaces` (ament_cmake)

Defines the custom action type only. No node code.

```
turtle_action_interfaces/
├── action/
│   └── MoveToGoal.action
├── CMakeLists.txt
└── package.xml
```

`CMakeLists.txt` uses `rosidl_generate_interfaces` to build the action type,
following the standard ROS2 custom-interface package pattern.

### 2. `turtle_action_practice` (ament_python)

Server and client nodes, plus docs. Depends on `turtle_action_interfaces`,
`rclpy`, `rclpy.action`, and `turtlesim`.

```
turtle_action_practice/
├── turtle_action_practice/
│   ├── goal_server.py
│   └── goal_client.py
├── docs/
│   ├── 01_action_interface.md
│   ├── 02_goal_server.md
│   └── 03_goal_client.md
├── NOTES.md
├── README.md
├── package.xml
└── setup.py
```

## Action Definition

`turtle_action_interfaces/action/MoveToGoal.action`:

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

Goal: target `(x, y)` in turtlesim's coordinate frame. Feedback: distance
remaining to the goal, published periodically while moving. Result: whether
the goal was reached (vs. cancelled) and how long it took.

## Node Design

### `goal_server.py`

Subscribes to `/turtle1/pose`, publishes to `/turtle1/cmd_vel`. Stub includes:

- `ActionServer` construction wired to `MoveToGoal`, with `execute_callback`
  and `cancel_callback` registered (boilerplate filled in).
- `execute_callback` left as `# TODO`: drive the turtle toward `(goal.x,
  goal.y)` using proportional control (reuse the P-controller math from
  `waypoint_nav.py`), publish `MoveToGoal.Feedback` each loop iteration with
  the remaining distance, and return a `Result` when the goal is reached.
- `cancel_callback` left as `# TODO`: accept a cancel request and stop the
  turtle (zero `cmd_vel`).
- TODO comments point at `waypoint_nav.py` and `turtle_chase.py` for the
  reusable distance/heading math.

### `goal_client.py`

Stub includes:

- `ActionClient` construction wired to `MoveToGoal`, `send_goal_async`
  boilerplate, and a `feedback_callback` registered.
- Goal coordinates and the send/wait-for-result flow left as `# TODO`.
- A `# TODO` for triggering a mid-flight cancel (e.g. cancel after N seconds)
  so the user exercises the cancel path, not just the happy path.

Both files follow the existing stub convention: class + `__init__`
boilerplate, ROS2 API wiring filled in, actual control/decision logic left as
`# TODO` with pointers to prior files. See project memory
`feedback_stub_style` for the full convention this follows.

## Docs Plan

Mirrors `turtlesim_projects`' per-node doc + running `NOTES.md` pattern:

- `docs/01_action_interface.md` — what an action is, why it's a different
  type from topic/service, walkthrough of the `.action` file fields.
- `docs/02_goal_server.md` — server-side concepts (goal handle, feedback
  publishing, cancel handling, executor considerations).
- `docs/03_goal_client.md` — client-side concepts (send_goal_async, feedback
  callback, get_result_async, requesting a cancel).
- `NOTES.md` accumulates Q&A as the user runs into questions, same as
  `turtlesim_projects/NOTES.md`.
- `README.md` gives the package a short overview and run instructions.

## Testing / Verification

Manual, interactive verification only (matches `turtlesim_projects`
conventions — no automated test suite):

1. Launch `turtlesim_node`.
2. Run `goal_server`.
3. Run `goal_client` with a goal; confirm the turtle moves toward it, the
   client prints feedback distance updates, and a result is returned on
   arrival.
4. Re-run with a cancel triggered mid-flight; confirm the turtle stops and
   the client observes a cancelled result rather than a success result.

## Out of Scope

- Phase 2 (TurtleBot3 + Gazebo + Nav2) — separate future spec.
- Launch file for this package — not needed at this scale; revisit if it
  grows multiple nodes.
- Multi-goal queuing, action server concurrency (multiple simultaneous
  goals) — single in-flight goal is enough to learn the core lifecycle.
