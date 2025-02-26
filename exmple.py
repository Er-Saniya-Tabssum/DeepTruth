# import cv2
# import os
# import time
# import webbrowser
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.options import Options
# from tkinter import Tk, filedialog
# from selenium import webdriver
# from webdriver_manager.chrome import ChromeDriverManager

# options = webdriver.ChromeOptions()
# driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

# driver.get("https://www.google.com")

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

# # Validate ROI
# if bbox is None or bbox == (0,0,0,0) or bbox[2] <= 0 or bbox[3] <= 0:
#     print("Error: Invalid selection. Please select an object.")
#     exit()

# # Extract selected object
# x, y, w, h = [int(v) for v in bbox]
# selected_object = image[y:y+h, x:x+w]

# # Save the cropped object
# search_path = "selected_object.jpg"
# cv2.imwrite(search_path, selected_object)
# print(f"Object saved as {search_path}")

# # Google Lens URL
# lens_url = "https://lens.google.com/upload"

# # Configure Selenium
# chrome_options = Options()
# chrome_options.add_argument("--start-maximized")  # Maximize browser window
# chrome_options.add_experimental_option("detach", True)  # Keep browser open after script ends

# # Set ChromeDriver path (modify if necessary)
# driver_path = "chromedriver.exe"  # Update with correct path if needed
# service = Service(driver_path)
# driver = webdriver.Chrome(service=service, options=chrome_options)

# # Open Google Lens
# driver.get(lens_url)
# time.sleep(3)  # Wait for page to load

# # Find and upload image
# upload_box = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
# upload_box.send_keys(os.path.abspath(search_path))
import time
import os
import webbrowser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
from tkinter import Tk, filedialog

# Function to select an image file using a dialog
def select_image():
    Tk().withdraw()
    file_path = filedialog.askopenfilename(title="Select an Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.webp")])
    if not file_path:
        print("❌ No file selected. Exiting...")
        exit()
    return file_path

# Function to perform Google Lens image search
def search_image_google_lens(image_path):
    # Ensure the file exists
    if not os.path.exists(image_path):
        print("❌ Error: Image file not found.")
        return

    # Open Google Lens Search
    google_lens_url = "https://lens.google.com/uploadbyurl"
    webbrowser.open(google_lens_url)
    
    # Setup Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)  # Keeps browser open after script ends
    options.add_argument("--start-maximized")  # Start maximized for better view

    # Initialize WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://lens.google.com/")

    try:
        # Wait for the page to load
        time.sleep(3)

        # Click on the "Upload Image" button
        upload_button = driver.find_element(By.XPATH, "//input[@type='file']")
        upload_button.send_keys(image_path)

        print("✅ Image uploaded successfully. Searching for similar images...")

        # Wait for search results to appear
        time.sleep(5)

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        print("✅ Search complete. Check your browser for results.")

# Main execution
if __name__ == "__main__":
    image_path = select_image()
    search_image_google_lens(image_path)
