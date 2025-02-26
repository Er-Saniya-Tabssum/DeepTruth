import os
import numpy as np
import cv2
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.utils import Sequence
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
# import tensorflow as tf

# Limit TensorFlow memory usage
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        print("GPU memory growth enabled")
    except RuntimeError as e:
        print(e)


# Data Generator class for efficient loading
class DataGenerator(Sequence): #This class inherits from Sequence, making it a custom data generator.
#This is useful when working with large datasets that cannot fit into RA
    def __init__(self, batch_size=32, target_size=(224, 224)):# Defines how many images are processed in one step,
        self.batch_size = batch_size
        self.target_size = target_size
        self.dataset = []

        # Define dataset paths
        self.categories = {
            "Fake": "D:\\python\\Dataset\\Validation\\Fake",
            "Real": "D:\\python\\Dataset\\Validation\\Real"#"D:\python\Dataset\Validation"
        }

        # Load file paths
        for label, (category, folder_path) in enumerate(self.categories.items()):
            if not os.path.exists(folder_path):
                print(f"⚠️ Warning: Directory '{folder_path}' not found! Skipping...")
                continue

            print(f"📂 Checking folder: {folder_path}")

            file_list = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            print(f"🔍 Found {len(file_list)} files in '{category}'")

            for file in file_list:
                self.dataset.append((os.path.join(folder_path, file), label))  # Store file path and label

        np.random.shuffle(self.dataset)  # Shuffle dataset

    def __len__(self):
        return int(np.ceil(len(self.dataset) / self.batch_size))  # Number of batches per epoch

    def __getitem__(self, index):
        batch_data = self.dataset[index * self.batch_size:(index + 1) * self.batch_size]
        batch_images = []
        batch_labels = []

        for file_path, label in batch_data:
            img = cv2.imread(file_path)

            if img is None:
                print(f"❌ Skipped: Unable to read '{file_path}' (Corrupt or unsupported format)")
                continue

            img = cv2.resize(img, self.target_size)
            batch_images.append(img)
            batch_labels.append(label)

        # Normalize images
        batch_images = np.array(batch_images, dtype="float32") / 255.0
        batch_labels = np.array(batch_labels)

        return batch_images, batch_labels


# Define the model  sequential CNN model
def create_model():
    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),#32 filters with 3x3 kernel.ReLU activation to introduce non-linearity.
        #MaxPooling reduces size by half.
        MaxPooling2D(pool_size=(2, 2)),
        Conv2D(64, (3, 3), activation='relu'),#64 filters for deeper feature extraction.
        MaxPooling2D(pool_size=(2, 2)),
        #Flattens the 2D feature maps.
        Flatten(),
        Dense(128, activation='relu'),
        #Fully connected layer with 128 neurons.
        Dense(1, activation='sigmoid')  # Binary classification (Fake vs Real)
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model
# AI_face_detection_model.py


def load_trained_model():
    """ Load and return the pre-trained AI model """
    model = tf.keras.models.load_model("AI_face_detection_model.h5")
    return model

def predict_image(model, image_path):
    """ Process the image and return detection results """

    img = image.load_img(image_path, target_size=(224, 224))  # Adjust size as needed
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) / 255.0  # Normalize

    prediction = model.predict(img_array)[0]  # Assuming binary classification

    is_deepfake = prediction[0] > 0.5  # Adjust threshold as needed
    confidence = prediction[0] * 100  

    return {"deepfake": bool(is_deepfake), "confidence": confidence}

def predict_image_output(model, image_path):
    img = cv2.imread(image_path)
    img = cv2.resize(img, (224, 224))  # Resize for model
    img = img / 255.0  # Normalize
    img = np.expand_dims(img, axis=0)

    prediction = model.predict(img)
    
    return "Fake" if prediction[0][0] > 0.5 else "Real"

# Training loop
if __name__ == "__main__":
    batch_size = 32
    train_generator = DataGenerator(batch_size=batch_size)

    model = create_model()
    model.fit(train_generator, epochs=10)  # Train with data generator

    # Save the model
    model.save('face_swap_detection_model.h5')
    print("✅ Model training complete and saved!")

