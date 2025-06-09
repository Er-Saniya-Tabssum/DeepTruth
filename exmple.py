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
