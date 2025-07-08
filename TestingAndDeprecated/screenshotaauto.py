import time
import pyautogui

# Define the region to capture: (left, top, width, height)
# - left: X coordinate of the top-left corner
# - top: Y coordinate of the top-left corner
# - width: Width of the region in pixels
# - height: Height of the region in pixels
region = (1402, 626, 263, 237)  # Example: capture a 400x300 region starting at (100,100)

screenshot_count = 6

try:
  while True:
    screenshot = pyautogui.screenshot(region=region)
    filename = f"Elements//IcyCrate/crate_{screenshot_count:04d}.png"
    screenshot.save(filename)
    print(f"Saved {filename}")
    screenshot_count += 1
    
except KeyboardInterrupt:
  print("Stopped by user.")