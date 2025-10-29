#!/usr/bin/env python3
"""
Setup and test iPhone camera connection for LeRobot
"""

import cv2
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_camera_connection():
    """
    Test camera connection and find the correct camera index
    """
    print("🔍 Testing camera connections...")

    # Test first 5 camera indices
    for i in range(5):
        if i == 0: continue
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                height, width = frame.shape[:2]
                print(f"✅ Camera {i}: {width}x{height} - WORKING")
                cap.release()

                # Show preview
                cv2.imshow(f'Camera {i} Preview', frame)
                cv2.waitKey(2000)  # Show for 2 seconds
                cv2.destroyAllWindows()

                return i
            cap.release()

    print("❌ No working cameras found")
    return None

def setup_iphone_camera():
    """
    Setup instructions for iPhone camera
    """
    print("📱 iPhone Camera Setup Instructions:")
    print("=" * 50)
    print("1. On your iPhone:")
    print("   • Go to Settings → General → AirPlay & Handoff")
    print("   • Enable 'Continuity Camera'")
    print()
    print("2. Connect iPhone to Mac via USB cable")
    print()
    print("3. Alternative: Install camera apps")
    print("   • EpocCam (recommended)")
    print("   • iVCam")
    print("   • CamTwist")
    print()
    print("4. Test connection:")
    print("   • Open Photo Booth or FaceTime")
    print("   • iPhone should appear as camera option")
    print()

def keep_camera_alive():
    """
    Keep camera connection alive for testing
    """
    camera_index = test_camera_connection()
    # camera_index = 1

    if camera_index is None:
        setup_iphone_camera()
        return

    print(f"🎥 Keeping camera {camera_index} alive for testing...")
    print("Press 'q' to quit")

    cap = cv2.VideoCapture(camera_index)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Camera connection lost")
            break

        # Add timestamp
        import time
        timestamp = time.strftime("%H:%M:%S")
        cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow('iPhone Camera - LeRobot Ready', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("📷 Camera test complete")

if __name__ == "__main__":
    print("🤖 LeRobot iPhone Camera Setup")
    print("=" * 40)

    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        keep_camera_alive()
    else:
        camera_idx = test_camera_connection()
        if camera_idx is not None:
            print(f"🎯 Use camera index {camera_idx} in your LeRobot commands")
        else:
            setup_iphone_camera()