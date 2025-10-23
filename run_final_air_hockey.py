#!/usr/bin/env python3

"""
Final script to run air hockey with SO-101 robot using migrated policy
"""

import sys
import os
import subprocess
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def run_air_hockey_command():
    """Run the air hockey recording command"""

    # First, clean up any existing dataset
    dataset_path = os.path.expanduser("~/.cache/huggingface/lerobot/npaka/eval_air_hockey_test")
    if os.path.exists(dataset_path):
        print(f"Removing existing dataset: {dataset_path}")
        import shutil
        shutil.rmtree(dataset_path)

    # Command to run
    cmd = [
        sys.executable, "-m", "lerobot.record",
        "--robot.type=so101_follower",
        "--robot.port=/dev/tty.usbmodem5AAF2883661",
        "--robot.id=follower_arm",
        "--robot.cameras={ front: {type: opencv, index_or_path: 1, width: 1920, height: 1080, fps: 30}}",
        "--display_data=true",
        "--dataset.repo_id=npaka/eval_air_hockey_test",
        "--dataset.single_task=Air Hockey",
        "--dataset.num_episodes=1",
        "--dataset.episode_time_s=30",
        "--policy.device=cpu",
        "--policy.path=outputs/migrated_air_hockey_5000"
    ]

    print("Running command:")
    print(" ".join(cmd))
    print("\nStarting air hockey recording...")

    try:
        # Run the command
        result = subprocess.run(cmd, cwd=os.getcwd())
        return result.returncode == 0
    except KeyboardInterrupt:
        print("🛑 Recording interrupted by user")
        return True
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False

if __name__ == "__main__":
    success = run_air_hockey_command()
    if success:
        print("\n🎉 Air hockey recording completed successfully!")
        print("Check the dataset at: https://huggingface.co/npaka/eval_air_hockey_test")
    else:
        print("\n💥 Recording failed. Check the error messages above.")