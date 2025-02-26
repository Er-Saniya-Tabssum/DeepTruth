import os
import cv2
import face_recognition
import numpy as np

# Directory containing known face images
KNOWN_FACES_DIR = "known_faces"
TOLERANCE = 0.6  # Lower values make matching stricter
MODEL = "cnn"  # Use 'cnn' for GPU acceleration or 'hog' for CPU-based detection

# Load known faces dynamically (without storing all in memory)
def load_known_faces():
    known_face_encodings = []
    known_face_names = []

    for filename in os.listdir(KNOWN_FACES_DIR):
        file_path = os.path.join(KNOWN_FACES_DIR, filename)
        image = face_recognition.load_image_file(file_path)
        encodings = face_recognition.face_encodings(image)

        if encodings:
            known_face_encodings.append(encodings[0])  # Store only first face found
            known_face_names.append(os.path.splitext(filename)[0])  # Use filename as name

    return known_face_encodings, known_face_names


# Process an image dynamically and check against known faces
def detect_and_verify(image_path, known_face_encodings, known_face_names):
    print(f"Processing: {image_path}")

    unknown_image = face_recognition.load_image_file(image_path)
    unknown_face_encodings = face_recognition.face_encodings(unknown_image)

    if not unknown_face_encodings:
        print("❌ No face found in the image.")
        return

    for unknown_face_encoding in unknown_face_encodings:
        distances = face_recognition.face_distance(known_face_encodings, unknown_face_encoding)
        best_match_index = np.argmin(distances)  # Find closest match

        if distances[best_match_index] < TOLERANCE:
            print(f"✅ Face matched: {known_face_names[best_match_index]}")
        else:
            print("❌ Face not recognized (Unknown).")


# Main Execution
if __name__ == "__main__":
    known_face_encodings, known_face_names = load_known_faces()

    if not known_face_encodings:
        print("⚠️ No known faces found! Please add images to the 'known_faces' folder.")
    else:
        # Test with a single image or loop through a test folder
        TEST_IMAGE_PATH = "test_images/test_image.jpg"
        detect_and_verify(TEST_IMAGE_PATH, known_face_encodings, known_face_names)
