#!/usr/bin/env python3

"""
Script to run air hockey with SO-101 robot using teleoperation (manual control)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lerobot.record import record
from lerobot.configs import parser

def run_teleop_air_hockey():
    print("Starting Air Hockey with manual teleoperation...")

    # Create record config
    from lerobot.record import RecordConfig
    from lerobot.robots.so101_follower.config_so101_follower import SO101FollowerConfig
    from lerobot.robots.so101_leader.config_so101_leader import SO101LeaderConfig
    from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig

    # Robot config (follower)
    robot_config = SO101FollowerConfig(
        port='/dev/tty.usbmodem5AAF2883661',  # Follower arm port
        id='follower_arm',
        cameras={
            'front': OpenCVCameraConfig(
                index_or_path=1,
                width=1920,
                height=1080,
                fps=30
            )
        }
    )

    # Teleoperator config (leader - you'll need to connect this)
    teleop_config = SO101LeaderConfig(
        port='/dev/tty.usbmodemXXXXX',  # Replace with your leader arm port
        id='leader_arm'
    )

    # Dataset config
    from lerobot.record import DatasetRecordConfig
    dataset_config = DatasetRecordConfig(
        repo_id='npaka/teleop_air_hockey',
        single_task='Air Hockey',
        fps=30,
        num_episodes=1,
        episode_time_s=60,
        video=True
    )

    # Record config (no policy, using teleop)
    config = RecordConfig(
        robot=robot_config,
        dataset=dataset_config,
        teleop=teleop_config,
        display_data=True,
        play_sounds=True
    )

    try:
        print("Starting teleoperation recording...")
        print("Use the leader arm to control the follower arm")
        print("Press 'q' or Ctrl+C to stop")
        dataset = record(config)
        print(f"✅ Recording complete! Dataset saved to: {dataset.repo_id}")
    except KeyboardInterrupt:
        print("🛑 Recording interrupted by user")
    except Exception as e:
        print(f"❌ Error during recording: {e}")
        return False

    return True

if __name__ == "__main__":
    run_teleop_air_hockey()