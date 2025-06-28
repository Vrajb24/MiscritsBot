import time
import pyautogui

# Define the region to capture: (left, top, width, height)
region = (1280, 0, 1280, 1440)
  # Change these values as needed

screenshot_count = 6

try:
    while True:
        screenshot = pyautogui.screenshot(region=region)
        filename = f"BlightedBush/element_image_{screenshot_count:04d}.png"
        screenshot.save(filename)
        print(f"Saved {filename}")
        screenshot_count += 1
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopped by user.")