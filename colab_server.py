#!/usr/bin/env python3
"""
Colab GPU Server for Remote Robot Control
Provides AI inference service for air hockey robot control
"""

# Install dependencies
!pip install lerobot flask flask-cors opencv-python pyngrok

# Set ngrok auth token (REPLACE WITH YOUR TOKEN)
from pyngrok import ngrok
ngrok.set_auth_token("YOUR_NGROK_AUTH_TOKEN_HERE")  # <-- Add your token here

# Import libraries
from lerobot.policies.act.configuration_act import ACTConfig
from lerobot.policies.act.modeling_act import ACT
from lerobot.configs.types import PolicyFeature, FeatureType
from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
import cv2
import numpy as np
import base64
import json
from PIL import Image
import io
import time

def load_act_model():
    """
    Load the ACT model for air hockey control
    """
    print("🤖 Loading ACT model...")

    # Configure for GPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"📊 Using device: {device}")

    # Download and fix the config
    from huggingface_hub import hf_hub_download
    config_path = hf_hub_download("AIBunCho/air-hockey-5000", "config.json")

    with open(config_path, 'r') as f:
        config_dict = json.load(f)

    # Remove problematic fields
    if 'type' in config_dict:
        del config_dict['type']

    # Convert feature dicts to PolicyFeature objects
    if 'input_features' in config_dict:
        for key, feat_dict in config_dict['input_features'].items():
            config_dict['input_features'][key] = PolicyFeature(
                shape=tuple(feat_dict['shape']),
                type=FeatureType(feat_dict['type'])
            )

    if 'output_features' in config_dict:
        for key, feat_dict in config_dict['output_features'].items():
            config_dict['output_features'][key] = PolicyFeature(
                shape=tuple(feat_dict['shape']),
                type=FeatureType(feat_dict['type'])
            )

    # Create ACTConfig
    config = ACTConfig(**config_dict)
    config.device = device

    # Create and load model
    model = ACT(config)
    model.to(device)
    model.eval()

    print("✅ ACT Model loaded successfully!")
    print(f"📏 Model parameters: {sum(p.numel() for p in model.parameters()) / 1e6:.1f}M")

    return model, device

# Load model globally
model, device = load_act_model()

# Create Flask server
app = Flask(__name__)
CORS(app)

@app.route('/infer', methods=['POST'])
def infer():
    """
    Inference endpoint for robot control
    """
    try:
        start_time = time.time()

        # Get data from request
        data = request.get_json()
        image_b64 = data['image']
        robot_state = data['robot_state']

        # Decode base64 image
        image_data = base64.b64decode(image_b64)
        image = Image.open(io.BytesIO(image_data))
        image = np.array(image)

        # Preprocess image (resize to expected dimensions)
        image = cv2.resize(image, (640, 480))  # Match model expectations
        image = torch.from_numpy(image).permute(2, 0, 1).float() / 255.0
        image = image.unsqueeze(0).to(device)

        # Prepare robot state
        robot_state_tensor = torch.tensor(robot_state).float().unsqueeze(0).to(device)

        # Create batch for ACT model
        batch = {
            'observation.images': [image],
            'observation.state': robot_state_tensor
        }

        # Run inference
        with torch.no_grad():
            actions, (mu, log_sigma) = model(batch)

        # Extract first action (for real-time control)
        action = actions[0, 0].cpu().numpy().tolist()

        # Calculate inference time
        inference_time = time.time() - start_time

        return jsonify({
            'action': action,
            'inference_time': inference_time,
            'success': True
        })

    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'device': device,
        'model_loaded': model is not None
    })

def keep_alive():
    """Keep Colab session alive"""
    import time
    while True:
        time.sleep(300)  # Ping every 5 minutes
        print("💓 Keeping Colab alive...")

if __name__ == '__main__':
    # Start keep-alive thread
    import threading
    threading.Thread(target=keep_alive, daemon=True).start()

    # Start ngrok tunnel
    print("🌐 Starting ngrok tunnel...")
    public_url = ngrok.connect(5000)
    print(f"🚀 Public URL: {public_url}")
    print("📝 Share this URL with your MacBook client")
    print("🔗 Health check: " + public_url.replace('5000', '5000/health'))

    # Start Flask server
    print("🎮 Starting AI inference server...")
    app.run(host='0.0.0.0', port=5000, debug=False)