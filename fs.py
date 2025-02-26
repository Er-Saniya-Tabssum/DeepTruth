import os
import cv2
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense

def load_data():
    dataset_path = "D:\\python\\Dataset"
    categories = ["Train", "Validation"]

    images = []
    labels = []

    for label, category in enumerate(categories):
        folder_path = os.path.join(dataset_path, category)

        if not os.path.exists(folder_path):
            print(f"⚠️ Warning: Directory '{folder_path}' not found! Skipping...")
            continue

        print(f"📂 Checking folder: {folder_path}")

        files = os.listdir(folder_path)
        print(f"🔍 Found {len(files)} files in '{category}'")

        for filename in files:
            file_path = os.path.join(folder_path, filename)

            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                img = cv2.imread(file_path)

                if img is None:
                    print(f"❌ ERROR: cv2.imread() failed for '{file_path}'")
                    continue  # Skip this file

                print(f"✅ Loaded '{file_path}', Shape: {img.shape}")

                img = cv2.resize(img, (224, 224))
                images.append(img)
                labels.append(label)  # 0 = Real (Train), 1 = Swapped (Validation)

    images = np.array(images, dtype="float32") / 255.0
    labels = np.array(labels)

    print(f"✅ Successfully loaded {len(images)} images.")

    return images, labels

def create_model():
    model = Sequential()
    model.add(Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Flatten())
    model.add(Dense(128, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))  # Binary classification
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

if __name__ == "__main__":
    images, labels = load_data()

    if len(images) == 0:
        print("🚨 ERROR: No images loaded! Check dataset path and ensure images exist.")
        exit()

    X_train, X_test, y_train, y_test = train_test_split(images, labels, test_size=0.2, random_state=42)

    model = create_model()
    model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=10)

    model.save('face_swap_detection_model.h5')
