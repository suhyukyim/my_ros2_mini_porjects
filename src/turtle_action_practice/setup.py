from setuptools import find_packages, setup

package_name = 'turtle_action_practice'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='suhyuk',
    maintainer_email='yimp2001@gmail.com',
    description='Custom action server/client practice using turtlesim',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'goal_server = turtle_action_practice.goal_server:main',
            'goal_client = turtle_action_practice.goal_client:main',
        ],
    },
)
