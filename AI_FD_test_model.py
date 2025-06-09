import cv2
import numpy as np
from tensorflow.keras.models import load_model

# Load trained model
model = load_model("AI_face_detection_model.h5")

def predict_image(image_path):
    img = cv2.imread(image_path)

    if img is None:
        print(f"❌ ERROR: Unable to read '{image_path}'")
        return

    img = cv2.resize(img, (224, 224))  # Resize to match model input
    img = np.expand_dims(img, axis=0) / 255.0  # Normalize

    prediction = model.predict(img)[0][0]  # Get probability

    if prediction < 0.8:
        print(f"🟢 Prediction: FAKE ({prediction * 100:.2f}%)")
    else:
        print(f"🔵 Prediction: REAL ({(1 - prediction) * 100:.2f}%)")

# Test with an image
image_path = 'C:\\Users\\saniy\\OneDrive\\Pictures\\Screenshots\\Screenshot 2025-02-15 115402.png'

  # Change to your test image path
predict_image(image_path)


# predict_images_in_folder(folder_path)
