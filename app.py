# # from flask import Flask, request, jsonify, send_file
# # from flask_cors import CORS
# # from PIL import Image
# # import io
# # import base64

# # app = Flask(__name__)
# # CORS(app)

# # @app.route('/api/face_swap', methods=['POST'])
# # def face_swap():
# #     try:
# #         # Retrieve uploaded images
# #         image1 = request.files['image1']
# #         image2 = request.files['image2']

# #         # Open images with Pillow
# #         img1 = Image.open(image1)
# #         img2 = Image.open(image2)

# #         # 🔴 Placeholder for actual face-swapping logic 🔴
# #         swapped_image = img2  # Replace with real face-swapping logic

# #         # Convert image to Base64
# #         img_io = io.BytesIO()
# #         swapped_image.save(img_io, format='JPEG')
# #         img_io.seek(0)
# #         img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')

# #         return jsonify({"success": True, "swapped_image": img_base64})
    
# #     except Exception as e:
# #         return jsonify({"success": False, "error": str(e)}), 400

# # if __name__ == '__main__':
# #     app.run(debug=True)
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from PIL import Image
# import io
# import base64

# app = Flask(__name__)
# CORS(app)  # Allow frontend requests

# @app.route("/")
# def home():
#     return "Flask Server is Running!"

# @app.route('/detect', methods=['POST'])
# def detect():
#     try:
#         # Check if image was uploaded
#         if 'image' not in request.files:
#             return jsonify({"error": "No image uploaded"}), 400

#         image = request.files['image']
#         img = Image.open(image)

#         # 🔴 Placeholder: Replace with your AI deepfake detection logic 🔴
#         is_deepfake = True  # Example: Assume it's detected
#         confidence = 97.3  # Example confidence score

#         return jsonify({"deepfake": is_deepfake, "confidence": confidence})
    
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# if __name__ == '__main__':
#     app.run(debug=True)
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from PIL import Image
# import io
# import base64
# import cv2
# import numpy as np
# import os
# import time
# import webbrowser
# from tkinter import Tk, filedialog

# app = Flask(__name__)
# CORS(app)

# @app.route("/")
# def home():
#     return "Flask Server is Running!"

# @app.route('/detect', methods=['POST'])
# def detect():
#     try:
#         if 'image' not in request.files:
#             return jsonify({"error": "No image uploaded"}), 400

#         image = request.files['image']
#         img = Image.open(image)

#         # Placeholder AI detection logic
#         is_deepfake = True
#         confidence = 97.3

#         return jsonify({"deepfake": is_deepfake, "confidence": confidence})
    
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app.route('/api/face_swap', methods=['POST'])
# def face_swap():
#     try:
#         image1 = request.files['image1']
#         image2 = request.files['image2']

#         img1 = Image.open(image1)
#         img2 = Image.open(image2)

#         # Placeholder face-swapping logic
#         swapped_image = img2  

#         img_io = io.BytesIO()
#         swapped_image.save(img_io, format='JPEG')
#         img_io.seek(0)
#         img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')

#         return jsonify({"success": True, "swapped_image": img_base64})
    
#     except Exception as e:
#         return jsonify({"success": False, "error": str(e)}), 400

# @app.route('/image_tracking', methods=['GET'])
# def image_tracking():
#     Tk().withdraw()
#     image_path = filedialog.askopenfilename(title="Select an Image", filetypes=[("Image Files", ".png;.jpg;*.jpeg")])

#     if not image_path:
#         return jsonify({"error": "No file selected."})

#     image = cv2.imread(image_path)
#     if image is None:
#         return jsonify({"error": "Unable to load image. Please check the file path."})

#     cv2.imshow('Select Object', image)
#     bbox = cv2.selectROI('Select Object', image, fromCenter=False, showCrosshair=True)
#     cv2.waitKey(1)
#     cv2.destroyAllWindows()

#     if bbox is None or bbox == (0,0,0,0) or bbox[2] <= 0 or bbox[3] <= 0:
#         return jsonify({"error": "Invalid bounding box detected."})

#     tracker = cv2.TrackerCSRT_create() if hasattr(cv2, 'TrackerCSRT_create') else cv2.legacy.TrackerCSRT_create()

#     if tracker is None:
#         return jsonify({"error": "Tracker could not be initialized."})

#     tracker.init(image, bbox)

#     return jsonify({"message": "Tracking initialized. Open webcam to track."})

# if __name__ == '__main__':
#     app.run(debug=True)
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from PIL import Image
import io
import base64
import cv2
import numpy as np
import os
from AI_face_detection_model import load_trained_model as load_face_detection_model, predict_image as predict_face_detection ,predict_image_output
  # Import AI functions
# from face_swap_detection_model import load_trained_model, predict_image
app = Flask(__name__, static_folder="static")
CORS(app)

 # Load AI Model
face_detection_model = load_face_detection_model()
 # Load the face detection model
  # Face detection model


@app.route("/")
def home():
    return send_from_directory("static", "index.html")  # Serve the frontend HTML

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
        # Save the uploaded image
        img_path = "uploaded_image.jpg"
        image_file.save(img_path)

        # Run AI model prediction
        result = predict_image_output(face_detection_model, img_path)  # Ensure the function returns "Real" or "Fake"

        # Prepare response for the frontend
        return {"result": result}

    except Exception as e:
        return {"error": str(e)}

# @app.route("/")
# def image_tracking():
#     return send_from_directory("static", "image_tracking.py")  # Serve the frontend HTML

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory("static", filename)

if __name__ == '__main__':
    app.run(debug=True)
