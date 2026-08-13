from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    # custom_teleop은 키보드 입력(stdin)이 필요한데 ros2 launch는 자식 프로세스의
    # stdin을 터미널에 연결해주지 않아서(emulate_tty로도 해결 안 됨) launch에 넣지 않음.
    # 이 launch 실행 후 별도 터미널에서 `ros2 run turtlesim_projects custom_teleop`로 조종.
    return LaunchDescription([
        Node(package='turtlesim', executable='turtlesim_node'),
        Node(package='turtlesim_projects', executable='obstacle_avoid'),
        Node(package='turtlesim_projects', executable='game_referee'),
    ])
