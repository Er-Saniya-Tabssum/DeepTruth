import os
import glob
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image

model_path = r"models\custom_cnn\deeptruth_cnn.h5"
model = tf.keras.models.load_model(model_path, compile=False)

patterns = [
    r"uploads\**\*.jpg",
    r"uploads\**\*.jpeg",
    r"uploads\**\*.png",
    r"uploads\**\*.webp",
]

image_paths = []
for pattern in patterns:
    image_paths.extend(glob.glob(pattern, recursive=True))

image_paths = image_paths[:10]

print(f"Testing {len(image_paths)} images...\n")

for index, img_path in enumerate(image_paths, start=1):
    try:
        img = image.load_img(img_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0) / 255.0

        score = float(model.predict(img_array, verbose=0)[0][0])
        probable_class = "Real" if score > 0.5 else "Fake"

        print(f"{index}. {os.path.basename(img_path)}")
        print(f"   Score: {score:.6f}")
        print(f"   Probable class: {probable_class}\n")

    except Exception as error:
        print(f"{index}. Failed: {error}\n")
