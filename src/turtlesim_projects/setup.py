import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'turtlesim_projects'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='suhyuk',
    maintainer_email='yimp2001@gmail.com',
    description='Small turtlesim practice projects',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'draw_shape_time = turtlesim_projects.draw_shape_time:main',
            'draw_shape_pose = turtlesim_projects.draw_shape_pose:main',
            'custom_teleop = turtlesim_projects.custom_teleop:main',
            'turtle_chase = turtlesim_projects.turtle_chase:main',
            'turtle_service_control = turtlesim_projects.turtle_service_control:main',
            'waypoint_nav = turtlesim_projects.waypoint_nav:main',
            'obstacle_avoid = turtlesim_projects.obstacle_avoid:main',
            'game_referee = turtlesim_projects.game_referee:main',
        ],
    },
)
