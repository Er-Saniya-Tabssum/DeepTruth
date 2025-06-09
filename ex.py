import cv2
import os
import webbrowser
from tkinter import Tk, filedialog

# Open file dialog to select image
Tk().withdraw()
image_path = filedialog.askopenfilename(title="Select an Image", filetypes=[("Image Files", ".png;.jpg;*.jpeg")])

if not image_path:
    print("Error: No file selected.")
    exit()

# Load the image
print(f"Trying to load image from: {image_path}")
image = cv2.imread(image_path)
if image is None:
    print("Error: Unable to load image. Please check the file path.")
    exit()

# Allow manual ROI selection
cv2.imshow('Select Object', image)
bbox = cv2.selectROI('Select Object', image, fromCenter=False, showCrosshair=True)
cv2.waitKey(1)
cv2.destroyAllWindows()

# Validate ROI
if bbox is None or bbox == (0,0,0,0) or bbox[2] <= 0 or bbox[3] <= 0:
    print("Error: Invalid selection. Please select an object.")
    exit()

# Extract selected object
x, y, w, h = [int(v) for v in bbox]
selected_object = image[y:y+h, x:x+w]

# Save the cropped object
search_path = "selected_object.jpg"
cv2.imwrite(search_path, selected_object)
print(f"Object saved as {search_path}")

# Open Google Lens upload page
lens_url = "https://lens.google.com/upload"
webbrowser.open(lens_url)

print("Please manually upload the image to Google Lens for search.")
