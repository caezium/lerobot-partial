#!/usr/bin/env python3

"""
Test script to check SO-101 robot connection
"""

from lerobot.robots.so101_follower import SO101Follower
from lerobot.robots.so101_follower.config_so101_follower import SO101FollowerConfig

def test_robot_connection():
    print("Testing SO-101 robot connection...")

    # Configure robot
    config = SO101FollowerConfig(
        port='/dev/tty.usbmodem5AAF2883661',
        id='follower_arm'
    )

    robot = SO101Follower(config)

    try:
        print("Connecting to robot...")
        robot.connect()  # This will run calibration if needed
        print("✅ Robot connected successfully!")

        # Test getting observation
        print("Getting observation...")
        obs = robot.get_observation()
        print(f"✅ Got observation with keys: {list(obs.keys())}")

        # Test sending action (small movement)
        print("Testing action...")
        action = {
            "shoulder_pan.pos": 0.0,
            "shoulder_lift.pos": 0.0,
            "elbow_flex.pos": 0.0,
            "wrist_flex.pos": 0.0,
            "wrist_roll.pos": 0.0,
            "gripper.pos": 50.0
        }
        sent_action = robot.send_action(action)
        print(f"✅ Action sent: {sent_action}")

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    finally:
        try:
            robot.disconnect()
            print("✅ Robot disconnected")
        except:
            print("⚠️  Could not disconnect cleanly")

    return True

if __name__ == "__main__":
    test_robot_connection()