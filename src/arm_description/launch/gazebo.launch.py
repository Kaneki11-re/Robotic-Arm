"""Gazebo Sim only: world, robot spawn, /clock bridge, ros2_control controllers."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    AppendEnvironmentVariable, DeclareLaunchArgument, IncludeLaunchDescription,
    RegisterEventHandler, TimerAction)
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution,
    PythonExpression)
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg = FindPackageShare('arm_description')
    pkg_share = get_package_share_directory('arm_description')
    ros_gz_sim_share = get_package_share_directory('ros_gz_sim')

    world = LaunchConfiguration('world')
    gz_gui = LaunchConfiguration('gz_gui')
    spawn_delay = LaunchConfiguration('spawn_delay')

    robot_description = ParameterValue(
        Command([
            FindExecutable(name='xacro'), ' ',
            PathJoinSubstitution([pkg, 'urdf', 'arm.urdf.xacro']),
            ' use_gazebo:=true',
        ]),
        value_type=str)

    # package:// mesh URIs are resolved by Gazebo through this path.
    resource_path = AppendEnvironmentVariable(
        'GZ_SIM_RESOURCE_PATH', os.path.dirname(pkg_share))

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim_share, 'launch', 'gz_sim.launch.py')),
        launch_arguments={
            'gz_args': PythonExpression([
                "'-r -v 4 ' + ('' if '", gz_gui, "' == 'true' else '-s ') + '",
                world, "'"]),
        }.items())

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description,
                     'use_sim_time': True}],
        output='screen')

    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'arm',
            '-allow_renaming', 'false',
            '-x', LaunchConfiguration('x'),
            '-y', LaunchConfiguration('y'),
            '-z', LaunchConfiguration('z'),
        ],
        output='screen')

    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{
            'config_file': PathJoinSubstitution(
                [pkg, 'config', 'ros_gz_bridge_gazebo.yaml'])}],
        output='screen')

    def spawner(controller):
        return Node(
            package='controller_manager',
            executable='spawner',
            arguments=[controller, '--controller-manager', '/controller_manager',
                       '--controller-manager-timeout', '60'],
            parameters=[{'use_sim_time': True}],
            output='screen')

    joint_state_broadcaster = spawner('joint_state_broadcaster')
    arm_controller = spawner('arm_controller')

    return LaunchDescription([
        DeclareLaunchArgument('world', default_value='empty.sdf',
                              description='Gazebo world file'),
        DeclareLaunchArgument('gz_gui', default_value='true',
                              description='Start the Gazebo GUI (false: server only)'),
        DeclareLaunchArgument('spawn_delay', default_value='5.0',
                              description='Seconds to wait for Gazebo before spawning'),
        DeclareLaunchArgument('x', default_value='0.0'),
        DeclareLaunchArgument('y', default_value='0.0'),
        DeclareLaunchArgument('z', default_value='0.0'),
        resource_path,
        gz_sim,
        robot_state_publisher,
        clock_bridge,
        TimerAction(period=spawn_delay, actions=[spawn_robot]),
        RegisterEventHandler(OnProcessExit(
            target_action=spawn_robot, on_exit=[joint_state_broadcaster])),
        RegisterEventHandler(OnProcessExit(
            target_action=joint_state_broadcaster, on_exit=[arm_controller])),
    ])
