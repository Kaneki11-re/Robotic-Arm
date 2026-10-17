from launch import LaunchDescription
from launch_ros.actions import SetParameter
from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import generate_demo_launch


def generate_launch_description():
    moveit_config = ( 
        MoveItConfigsBuilder("arm", package_name="arm_moveit").to_moveit_configs()
    )
    demo_launch = generate_demo_launch(moveit_config)

    return LaunchDescription([
        SetParameter(name="use_sim_time", value=False),
        *demo_launch.entities,
    ])
