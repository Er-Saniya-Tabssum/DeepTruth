import tensorflow as tf
import numpy as np
from PIL import Image
from pathlib import Path

model_path = r"models\custom_cnn\deeptruth_cnn.h5"

print("Loading original model...")
model = tf.keras.models.load_model(model_path, compile=False)

image_files = [
    p for p in Path("uploads").rglob("*")
    if p.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]
    and p.name.lower() != "mask.png"
]

print(f"\nFound {len(image_files)} images\n")

for image_path in image_files:
    try:
        image = Image.open(image_path).convert("RGB")
        image = image.resize((224, 224))

        image_array = np.array(image, dtype=np.float32) / 255.0
        image_array = np.expand_dims(image_array, axis=0)

        prediction = model.predict(image_array, verbose=0)
        score = float(prediction[0][0])

        print(f"Score: {score:.6f} | {image_path}")

    except Exception as error:
        print(f"ERROR | {image_path} | {error}")
