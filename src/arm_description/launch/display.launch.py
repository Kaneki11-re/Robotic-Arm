"""RViz2 only: robot_state_publisher + joint_state_publisher(_gui) + RViz2."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import (
    Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution)
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg = FindPackageShare('arm_description')

    gui = LaunchConfiguration('gui')
    rviz_config = LaunchConfiguration('rviz_config')

    robot_description = ParameterValue(
        Command([
            FindExecutable(name='xacro'), ' ',
            PathJoinSubstitution([pkg, 'urdf', 'arm.urdf.xacro']),
            ' use_gazebo:=false',
        ]),
        value_type=str)

    return LaunchDescription([
        DeclareLaunchArgument(
            'gui', default_value='true',
            description='Use joint_state_publisher_gui instead of the headless one'),
        DeclareLaunchArgument(
            'rviz_config',
            default_value=PathJoinSubstitution([pkg, 'rviz', 'arm.rviz']),
            description='RViz2 configuration file'),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description}],
            output='screen'),
        Node(
            condition=UnlessCondition(gui),
            package='joint_state_publisher',
            executable='joint_state_publisher'),
        Node(
            condition=IfCondition(gui),
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui'),
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', rviz_config],
            output='screen'),
    ])
