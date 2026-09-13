from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from PIL import Image
import io
import base64
import cv2
import numpy as np
import os
from AI_face_detection_model import load_trained_model as load_face_detection_model, predict_image as predict_face_detection ,predict_image_output
from backend.app.config import get_runtime_settings, validate_runtime_settings

  # Import AI functions
# from face_swap_detection_model import load_trained_model, predict_image
app = Flask(__name__, static_folder="static")
CORS(app)

runtime_settings = get_runtime_settings()
validate_runtime_settings(runtime_settings)

# Load AI model only when running in REAL mode.
face_detection_model = None
if runtime_settings["inference_mode"] == "REAL":
    face_detection_model = load_face_detection_model(runtime_settings["resolved_model_path"])


@app.route("/")
def home():
    return send_from_directory("static", "index.html")  # Serve the frontend HTML

@app.route("/healthz")
def healthz():
    return jsonify({"status": "ok", "mode": runtime_settings["inference_mode"]})

# @app.route('/api/face_detect', methods=['POST'])
def face_detect():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image uploaded"}), 400

        image = request.files['image']
        img_path = "temp_face_detect.jpg"
        image.save(img_path)  # Save uploaded image

        # Use AI model for face detection
        result = predict_face_detection(face_detection_model, img_path)

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/face_swap', methods=['POST'])
def face_swap():
    try:
        if 'image1' not in request.files or 'image2' not in request.files:
            return jsonify({"error": "Both images are required"}), 400

        image1 = request.files['image1']
        image2 = request.files['image2']

        img1 = Image.open(image1)
        img2 = Image.open(image2)

        # Placeholder face-swapping logic
        swapped_image = img2  

        img_io = io.BytesIO()
        swapped_image.save(img_io, format='JPEG')
        img_io.seek(0)
        img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')

        return jsonify({"success": True, "swapped_image": img_base64})
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

# Serve static files (CSS, JS, Images)
def process_image_and_detect(image_file):
    """
    This function connects all parts: 
    - Saves the uploaded image
    - Runs AI model detection (deepfake or real)
    - Returns the result to the frontend
    """
    try:
        if runtime_settings["inference_mode"] == "DEMO":
            return {"result": "DEMO_MODE_NO_REAL_INFERENCE", "mode": "DEMO"}

        # Save the uploaded image
        img_path = "uploaded_image.jpg"
        image_file.save(img_path)

        # Run AI model prediction
        result = predict_image_output(face_detection_model, img_path)  # Ensure the function returns "Real" or "Fake"

        # Prepare response for the frontend
        return {"result": result, "mode": "REAL"}

    except Exception as e:
        return {"error": str(e)}

# @app.route("/")
# def image_tracking():
#     return send_from_directory("static", "image_tracking.py")  # Serve the frontend HTML

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory("static", filename)

if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        debug=runtime_settings["environment"] != "production"
    )
