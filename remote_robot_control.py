#!/usr/bin/env python3
"""
Remote GPU-Powered Robot Control for Air Hockey
Runs AI inference on Google Colab GPU while controlling physical SO-101 robot locally
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import requests
import cv2
import numpy as np
import base64
import json
import time
from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig
from lerobot.cameras.opencv import OpenCVCameraConfig

def run_remote_inference():
    """
    Main function to run remote inference with physical robot control
    """
    # Create robot config
    robot_config = SO101FollowerConfig(
        port='/dev/tty.usbmodem5AAF2885151',  # Update with your actual port
        id='follower_arm',
        cameras={
            'front': OpenCVCameraConfig(
                index_or_path=1,  # Your camera index
                width=320,  # Reduced for faster transmission
                height=240,
                fps=15  # Reduced FPS for stability
            )
        }
    )

    # Connect to robot
    print("🤖 Connecting to SO-101 robot...")
    robot = SO101Follower(robot_config)
    robot.connect()
    print("✅ Robot connected!")

    # Colab server URL (get this from Colab after running ngrok)
    colab_url = "https://your-ngrok-url.ngrok.io"  # Replace with your ngrok URL

    # Control loop parameters
    control_fps = 5  # 5 FPS control loop
    control_interval = 1.0 / control_fps
    timeout = 2.0  # 2 second timeout for network requests

    # Statistics
    frame_count = 0
    success_count = 0
    start_time = time.time()

    try:
        print("🎮 Starting remote GPU-powered control loop...")
        print("🎾 Press Ctrl+C to stop")

        while True:
            loop_start = time.time()

            try:
                # Get robot observation (includes camera image and joint positions)
                obs = robot.get_observation()

                # Extract image and robot state
                image = obs['front']  # Camera image
                robot_state = [
                    obs['shoulder_pan.pos'],
                    obs['shoulder_lift.pos'],
                    obs['elbow_flex.pos'],
                    obs['wrist_flex.pos'],
                    obs['wrist_roll.pos'],
                    obs['gripper.pos']
                ]

                # Compress image for transmission
                _, buffer = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 70])
                image_b64 = base64.b64encode(buffer).decode('utf-8')

                # Prepare payload for Colab
                payload = {
                    'image': image_b64,
                    'robot_state': robot_state
                }

                # Send to Colab for GPU inference
                response = requests.post(f"{colab_url}/infer",
                                       json=payload,
                                       timeout=timeout)

                if response.status_code == 200:
                    result = response.json()
                    if result['success']:
                        action = result['action']

                        # Send action to robot
                        action_dict = {
                            'shoulder_pan.pos': action[0],
                            'shoulder_lift.pos': action[1],
                            'elbow_flex.pos': action[2],
                            'wrist_flex.pos': action[3],
                            'wrist_roll.pos': action[4],
                            'gripper.pos': action[5]
                        }

                        robot.send_action(action_dict)
                        success_count += 1

                        # Print status every 50 frames
                        if frame_count % 50 == 0:
                            elapsed = time.time() - start_time
                            fps = frame_count / elapsed
                            success_rate = success_count / frame_count * 100
                            print(f"📊 Frame {frame_count}: {fps:.1f} FPS, {success_rate:.1f}% success")

                    else:
                        print(f"❌ Inference error: {result.get('error')}")
                else:
                    print(f"❌ HTTP error: {response.status_code}")

            except requests.exceptions.Timeout:
                print("⏰ Inference timeout - network lag")
            except requests.exceptions.RequestException as e:
                print(f"🌐 Network error: {e}")
                time.sleep(1)  # Wait before retrying
            except Exception as e:
                print(f"💥 Local error: {e}")

            frame_count += 1

            # Maintain control loop timing
            loop_time = time.time() - loop_start
            if loop_time < control_interval:
                time.sleep(control_interval - loop_time)

    except KeyboardInterrupt:
        print("\n🛑 Stopping remote control...")

        # Final statistics
        total_time = time.time() - start_time
        avg_fps = frame_count / total_time
        success_rate = success_count / frame_count * 100 if frame_count > 0 else 0

        print("📈 Final Statistics:"        print(".1f"        print(".1f"        print(".1f"    finally:
        print("🔌 Disconnecting robot...")
        robot.disconnect()
        print("👋 Remote control stopped")

if __name__ == "__main__":
    run_remote_inference()