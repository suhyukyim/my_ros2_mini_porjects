# Copyright 2026 suhyuk
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
