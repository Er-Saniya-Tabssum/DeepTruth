# # import cv2
# # import numpy as np
# # import os
# # import time
# # import requests
# # import webbrowser
# # from bs4 import BeautifulSoup
# # from tkinter import Tk, filedialog

# # # Function to automatically detect the largest object in an image
# # def auto_detect_object(image):
# #     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# #     blurred = cv2.GaussianBlur(gray, (5, 5), 0)
# #     edged = cv2.Canny(blurred, 50, 150)
    
# #     contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# #     if not contours:
# #         print("Error: No object detected.")
# #         return None
    
# #     largest_contour = max(contours, key=cv2.contourArea)
# #     x, y, w, h = cv2.boundingRect(largest_contour)
# #     return (x, y, w, h)

# # # Open file dialog to select image
# # Tk().withdraw()
# # image_path = filedialog.askopenfilename(title="Select an Image", filetypes=[("Image Files", ".png;.jpg;*.jpeg")])

# # if not image_path:
# #     print("Error: No file selected.")
# #     exit()

# # # Load the image
# # print(f"Trying to load image from: {image_path}")
# # image = cv2.imread(image_path)
# # if image is None:
# #     print("Error: Unable to load image. Please check the file path.")
# #     exit()

# # # Allow manual ROI selection
# # cv2.imshow('Select Object', image)
# # bbox = cv2.selectROI('Select Object', image, fromCenter=False, showCrosshair=True)
# # cv2.waitKey(1)
# # cv2.destroyAllWindows()
# # if bbox is None or bbox == (0,0,0,0) or bbox[2] <= 0 or bbox[3] <= 0:
# #     print("Error: Invalid bounding box detected.")
# #     exit()

# # # Initialize the tracker
# # if hasattr(cv2, 'TrackerCSRT_create'):
# #     tracker = cv2.TrackerCSRT_create()
# # elif hasattr(cv2.legacy, 'TrackerCSRT_create'):
# #     tracker = cv2.legacy.TrackerCSRT_create()
# # else:
# #     print("Warning: CSRT Tracker is not available in your OpenCV installation. Object tracking will not work.")
# #     tracker = None

# # # Initialize webcam
# # cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
# # if not cap.isOpened():
# #     print("Error: Could not open webcam.")
# #     exit()

# # try:
# #     while True:
# #         ret, frame = cap.read()
# #         if not ret:
# #             break
        
# #         success, bbox = tracker.update(frame)
# #         if success:
# #             x, y, w, h = [int(v) for v in bbox]
# #             cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
# #         else:
# #             cv2.putText(frame, "Tracking lost", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
# #         cv2.imshow("Image Tracking", frame)
        
# #         key = cv2.waitKey(1) & 0xFF
# #         if key == ord('s'):
# #             if x >= 0 and y >= 0 and x + w <= frame.shape[1] and y + h <= frame.shape[0]:
# #                 tracked_object = frame[y:y+h, x:x+w]
# #             else:
# #                 print("Error: Tracked object is out of bounds.")
# #                 continue
# #             search_path = 'tracked_object.jpg'
# #             cv2.imwrite(search_path, tracked_object)
            
# #             google_url = f'https://www.google.com/searchbyimage?image_url=file://{os.path.abspath(search_path)}'
# #             bing_url = f'https://www.bing.com/images/search?q=imgurl:{os.path.abspath(search_path)}&view=detailv2'
# #             yandex_url = f'https://yandex.com/images/search?rpt=imageview&url={os.path.abspath(search_path)}'
            
# #             webbrowser.open(google_url)
# #             webbrowser.open(bing_url)
# #             webbrowser.open(yandex_url)
# #             print("Searching for the tracked object on Google, Bing, and Yandex...")
        
# #         if key == ord('q'):
# #             break

# # except KeyboardInterrupt:
# #     print("Tracking interrupted by user. Exiting...")
# # finally:
# #     cap.release()
# #     cv2.destroyAllWindows()
# #     print("Tracking stopped.")
# import cv2
# import numpy as np
# import os
# import time
# import webbrowser
# from tkinter import Tk, filedialog

# # Open file dialog to select image
# Tk().withdraw()
# image_path = filedialog.askopenfilename(title="Select an Image", filetypes=[("Image Files", ".png;.jpg;*.jpeg")])

# if not image_path:
#     print("Error: No file selected.")
#     exit()

# # Load the image
# print(f"Trying to load image from: {image_path}")
# image = cv2.imread(image_path)
# if image is None:
#     print("Error: Unable to load image. Please check the file path.")
#     exit()

# # Allow manual ROI selection
# cv2.imshow('Select Object', image)
# bbox = cv2.selectROI('Select Object', image, fromCenter=False, showCrosshair=True)
# cv2.waitKey(1)
# cv2.destroyAllWindows()

# if bbox is None or bbox == (0,0,0,0) or bbox[2] <= 0 or bbox[3] <= 0:
#     print("Error: Invalid bounding box detected.")
#     exit()

# # Initialize the tracker
# tracker = None
# if hasattr(cv2, 'TrackerCSRT_create'):
#     tracker = cv2.TrackerCSRT_create()
# elif hasattr(cv2.legacy, 'TrackerCSRT_create'):
#     tracker = cv2.legacy.TrackerCSRT_create()

# if tracker is None:
#     print("Error: Tracker could not be initialized.")
#     exit()

# # Initialize tracker with the selected ROI
# tracker.init(image, bbox)

# # Initialize webcam
# cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
# if not cap.isOpened():
#     print("Error: Could not open webcam.")
#     exit()

# try:
#     while True:
#         ret, frame = cap.read()
#         if not ret or frame is None:
#             print("Error: Empty frame received from webcam.")
#             break  # Exit loop if frame capture fails

#         success, bbox = tracker.update(frame)
#         if success:
#             x, y, w, h = [int(v) for v in bbox]
#             cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
#         else:
#             cv2.putText(frame, "Tracking lost", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

#         cv2.imshow("Image Tracking", frame)

#         key = cv2.waitKey(1) & 0xFF
#         if key == ord('q'):
#             break  # Quit tracking

# except KeyboardInterrupt:
#     print("Tracking interrupted by user.")

# finally:
#     cap.release()
#     cv2.destroyAllWindows()
#     print("Tracking stopped.")
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
