#!/usr/bin/env python3

"""
Script to run air hockey with SO-101 robot using migrated policy with retry logic
"""

import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lerobot.record import record
from lerobot.configs.policies import PreTrainedConfig
from lerobot.configs import parser

def run_air_hockey_with_retry(max_retries=3):
    print("Starting Air Hockey with SO-101 robot (with retry logic)...")

    for attempt in range(max_retries):
        try:
            print(f"\n🔄 Attempt {attempt + 1}/{max_retries}")

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
                repo_id=f'npaka/eval_so101_final_v1{attempt + 1}',
                single_task='Air Hockey',
                fps=30,
                num_episodes=1,
                episode_time_s=30,  # Shorter episodes for testing
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

            print("Starting recording with policy control...")
            dataset = record(config)
            print(f"✅ Recording complete! Dataset saved to: {dataset.repo_id}")
            return True

        except KeyboardInterrupt:
            print("🛑 Recording interrupted by user")
            return True
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Attempt {attempt + 1} failed: {error_msg}")

            if "Present_Position" in error_msg or "status packet" in error_msg:
                print("🔌 Hardware communication error. Waiting before retry...")
                time.sleep(2)  # Wait 2 seconds before retry
            else:
                print("💻 Software error. No retry needed.")
                break

            if attempt < max_retries - 1:
                print("🔄 Retrying...")
            else:
                print("❌ All attempts failed.")

    return False

if __name__ == "__main__":
    success = run_air_hockey_with_retry()
    if success:
        print("\n🎉 Air hockey session completed successfully!")
    else:
        print("\n💥 All attempts failed. Check hardware connections.")