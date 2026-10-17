"""Optional combined launch: Gazebo Sim + controllers + RViz2 on sim time."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg = FindPackageShare('arm_description')
    pkg_share = get_package_share_directory('arm_description')

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_share, 'launch', 'gazebo.launch.py')),
        launch_arguments={
            'world': LaunchConfiguration('world'),
            'gz_gui': LaunchConfiguration('gz_gui'),
        }.items())

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', LaunchConfiguration('rviz_config')],
        parameters=[{'use_sim_time': True}],
        output='screen')

    return LaunchDescription([
        DeclareLaunchArgument('world', default_value='empty.sdf'),
        DeclareLaunchArgument('gz_gui', default_value='true'),
        DeclareLaunchArgument(
            'rviz_config',
            default_value=PathJoinSubstitution([pkg, 'rviz', 'arm.rviz'])),
        gazebo,
        rviz,
    ])
