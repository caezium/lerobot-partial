#!/usr/bin/env python3

"""
Script to run air hockey with SO-101 robot using migrated policy
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lerobot.record import record
from lerobot.configs.policies import PreTrainedConfig
from lerobot.configs import parser

def run_air_hockey():
    print("Starting Air Hockey with SO-101 robot...")

    # Create record config
    from lerobot.record import RecordConfig
    from lerobot.robots.so101_follower.config_so101_follower import SO101FollowerConfig
    from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig

    # Robot config
    robot_config = SO101FollowerConfig(
        port='/dev/tty.usbmodem5AAF2883661',
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

    # Dataset config
    from lerobot.record import DatasetRecordConfig
    dataset_config = DatasetRecordConfig(
        repo_id='npaka/eval_so101_final1231',
        single_task='Air Hockey',
        fps=30,
        num_episodes=1,  # Start with 1 episode
        episode_time_s=60,
        video=True
    )

    # Policy config
    policy_config = PreTrainedConfig.from_pretrained('outputs/migrated_air_hockey_5000')

    # Record config
    config = RecordConfig(
        robot=robot_config,
        dataset=dataset_config,
        policy=policy_config,
        display_data=True,
        play_sounds=True
    )

    try:
        print("Starting recording with policy control...")
        dataset = record(config)
        print(f"✅ Recording complete! Dataset saved to: {dataset.repo_id}")
    except KeyboardInterrupt:
        print("🛑 Recording interrupted by user")
    except Exception as e:
        print(f"❌ Error during recording: {e}")
        return False

    return True

if __name__ == "__main__":
    run_air_hockey()