import time
import pyautogui

# Define the region to capture: (left, top, width, height)
region = (1280, 0, 1280, 1440)
  # Change these values as needed

screenshot_count = 0

try:
    while True:
        screenshot = pyautogui.screenshot(region=region)
        filename = f"screenshots/screenshot_{screenshot_count}.png"
        screenshot.save(filename)
        print(f"Saved {filename}")
        screenshot_count += 1
        time.sleep(30)
except KeyboardInterrupt:
    print("Stopped by user.")