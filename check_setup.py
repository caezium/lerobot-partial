#!/usr/bin/env python3

"""
Script to check if all components are working for LeRobot air hockey setup
"""

import cv2
import os

def check_camera():
    """Check if camera is accessible"""
    print("🔍 Checking camera...")
    try:
        cap = cv2.VideoCapture(1)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"✅ Camera works! Frame shape: {frame.shape}")
                cap.release()
                return True
            else:
                print("❌ Camera opened but can't read frames")
        else:
            print("❌ Camera not accessible")
        cap.release()
    except Exception as e:
        print(f"❌ Camera error: {e}")
    return False

def check_serial_port():
    """Check if serial port exists"""
    print("🔍 Checking serial port...")
    port = '/dev/tty.usbmodem5AAF2883661'
    if os.path.exists(port):
        print(f"✅ Serial port exists: {port}")
        # Check permissions
        import stat
        st = os.stat(port)
        if st.st_mode & stat.S_IRUSR and st.st_mode & stat.S_IWUSR:
            print("✅ Serial port has correct permissions")
            return True
        else:
            print("❌ Serial port permissions issue")
            return False
    else:
        print(f"❌ Serial port not found: {port}")
        return False

def check_migrated_model():
    """Check if migrated model exists"""
    print("🔍 Checking migrated model...")
    model_path = 'outputs/migrated_air_hockey_5000'
    required_files = [
        'config.json',
        'model.safetensors',
        'policy_preprocessor.json',
        'policy_postprocessor.json'
    ]

    if os.path.exists(model_path):
        missing_files = []
        for file in required_files:
            if not os.path.exists(os.path.join(model_path, file)):
                missing_files.append(file)

        if not missing_files:
            print(f"✅ Migrated model complete: {model_path}")
            return True
        else:
            print(f"❌ Missing files in migrated model: {missing_files}")
            return False
    else:
        print(f"❌ Migrated model not found: {model_path}")
        return False

def check_python_environment():
    """Check if required packages are available"""
    print("🔍 Checking Python environment...")
    try:
        import lerobot
        print("✅ LeRobot package available")
    except ImportError:
        print("❌ LeRobot package not found")
        return False

    try:
        import torch
        print(f"✅ PyTorch available (version: {torch.__version__})")
    except ImportError:
        print("❌ PyTorch not found")
        return False

    try:
        import cv2
        print(f"✅ OpenCV available (version: {cv2.__version__})")
    except ImportError:
        print("❌ OpenCV not found")
        return False

    return True

def main():
    print("🚀 LeRobot Air Hockey Setup Check")
    print("=" * 40)

    checks = [
        check_python_environment,
        check_camera,
        check_serial_port,
        check_migrated_model
    ]

    results = []
    for check in checks:
        results.append(check())
        print()

    print("📊 Summary:")
    print(f"✅ Passed: {sum(results)}/{len(results)} checks")

    if all(results):
        print("🎉 All checks passed! Ready to run air hockey!")
        print("\nNext steps:")
        print("1. Run: python test_robot_connection.py")
        print("2. If robot connects, run: python run_air_hockey.py")
        print("3. Or for manual control: python teleop_air_hockey.py")
    else:
        print("⚠️  Some checks failed. Please fix issues before proceeding.")

    return all(results)

if __name__ == "__main__":
    main()