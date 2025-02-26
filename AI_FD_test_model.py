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

# import os
# import cv2
# import numpy as np
# from tensorflow.keras.models import load_model

# # Load trained model
# model = load_model("AI_face_detection_model.h5")

# def predict_images_in_folder(folder_path):
#     if not os.path.exists(folder_path):
#         print(f"❌ ERROR: Folder '{folder_path}' not found!")
#         return

#     image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
#     if not image_files:
#         print("⚠️ No images found in the folder!")
#         return
    
#     total_images = len(image_files)
#     fake_count = 0
    
#     for filename in image_files:
#         image_path = os.path.join(folder_path, filename)
#         img = cv2.imread(image_path)

#         if img is None:
#             print(f"❌ ERROR: Unable to read '{image_path}', skipping...")
#             continue

#         img = cv2.resize(img, (224, 224))  # Resize to match model input
#         img = np.expand_dims(img, axis=0) / 255.0  # Normalize

#         prediction = model.predict(img)[0][0]  # Get probability

#         if prediction < 0.8:
#             print(f"🟢 FAKE: {filename} ({prediction * 100:.2f}%)")
#             fake_count += 1
#         else:
#             print(f"🔵 REAL: {filename} ({(1 - prediction) * 100:.2f}%)")
    
#     fake_percentage = (fake_count / total_images) * 100
#     print(f"\n📊 Total Images: {total_images}")
#     print(f"🟢 Fake Images: {fake_count} ({fake_percentage:.2f}%)")
#     print(f"🔵 Real Images: {total_images - fake_count} ({100 - fake_percentage:.2f}%)")

# # Test with a folder
# folder_path = "D:\\python\\Dataset\\Test\\Real"  # Change to your test folder path
# predict_images_in_folder(folder_path)
