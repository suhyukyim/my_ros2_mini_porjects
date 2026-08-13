from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    # TODO: 아래 4개 노드를 하나의 LaunchDescription으로 묶는다.
    #
    # 1) turtlesim 패키지의 turtlesim_node (package='turtlesim', executable='turtlesim_node')
    # 2) custom_teleop (플레이어 조종, package='turtlesim_projects', executable='custom_teleop')
    #    - 주의: custom_teleop은 터미널 키 입력을 받으므로 launch로 띄우면 표준입력을 못 받을 수 있음
    #      (output='screen' + emulate_tty=True 옵션이 필요할 수 있음, 직접 테스트하며 확인)
    # 3) obstacle_avoid (AI 추격 거북이, package='turtlesim_projects', executable='obstacle_avoid')
    # 4) game_referee (심판, package='turtlesim_projects', executable='game_referee')
    #
    # 각 노드는 Node(package=..., executable=..., name=..., output='screen') 형태로 생성하고,
    # 리스트로 묶어서 LaunchDescription(...)에 전달하면 됨.

    return LaunchDescription([
        # TODO: Node(...) 4개 채우기
    ])
