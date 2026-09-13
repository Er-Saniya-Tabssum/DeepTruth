import os
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image

model_path = r"models\custom_cnn\deeptruth_cnn.h5"

img_path = os.environ["DEEPTRUTH_TEST_IMAGE"]

model = tf.keras.models.load_model(model_path, compile=False)

img = image.load_img(img_path, target_size=(224, 224))
img_array = image.img_to_array(img)
img_array = np.expand_dims(img_array, axis=0) / 255.0

prediction = float(model.predict(img_array, verbose=0)[0][0])

print(f"Image: {img_path}")
print(f"Raw model score: {prediction:.6f}")
print(f"Score <= 0.5: {prediction <= 0.5}")
print(f"Score > 0.5: {prediction > 0.5}")
