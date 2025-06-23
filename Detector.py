import cv2
import numpy as np
import pygetwindow as gw
import pyautogui
import time
import re
import easyocr  # Changed from pytesseract to easyocr
from ultralytics import YOLO  # Use ultralytics package

def click_at(click_x, click_y, hold_time=0.25):
    pyautogui.mouseDown(click_x, click_y)
    pyautogui.sleep(hold_time)
    pyautogui.mouseUp(click_x, click_y)

def get_window_bbox(window_title):
    win = None
    for w in gw.getAllWindows():
        if window_title.lower() in w.title.lower():
            win = w
            break
    if win is None:
        raise Exception("Window not found")
    if win.isMinimized:
        raise Exception("Window is minimized. Please restore the window.")
    return (win.left, win.top, win.width, win.height)


def capture_window(window_title):
    x, y, w, h = get_window_bbox(window_title)
    img = pyautogui.screenshot(region=(x, y, w, h))
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    return img

def click_on_rock():
    window_title = "Miscrits"  # Change this to your window's title
    frame = capture_window(window_title)
    x, y, w, h = get_window_bbox(window_title)
    click_x = x + w // 2
    click_y = y + h // 2 - 10
    click_at(click_x, click_y)
    print(f"Clicked in the middle of the window at ({click_x}, {click_y})")

def capture_chance():
    window_title = "Miscrits"
    frame = capture_window(window_title)
    x, y, w, h = get_window_bbox(window_title)

    # Define the box region (example: center 100x40 box)
    box_w, box_h = 47, 25
    box_x = x + 620
    box_y = y + 165

    # Capture the box region
    box_img = pyautogui.screenshot(region=(box_x, box_y, box_w, box_h))
    box_img_cv = cv2.cvtColor(np.array(box_img), cv2.COLOR_RGB2BGR)

    # OCR using easyocr
    reader = easyocr.Reader(['en'], gpu=False)
    result = reader.readtext(box_img_cv, detail=0)
    text = result[0] if result else ""
    print("OCR Result:", text.strip())

    # # Visualize the OCR box on the captured frame
    # vis = frame.copy()
    # cv2.rectangle(vis, (box_x - x, box_y - y), (box_x - x + box_w, box_y - y + box_h), (0, 255, 0), 2)
    # cv2.imshow("OCR Box Visualization", vis)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    return text.strip()

def rarity_check():
    window_title = "Miscrits" 
    frame = capture_window(window_title)
    x, y, w, h = get_window_bbox(window_title)
    # Original values
    px = 845
    py = 65
    color = frame[py, px]  # BGR format
    print(f"Pixel color at ({px},{py}): {color}")
    # # Visualize the pixel location on the captured frame
    # vis = frame.copy()
    # cv2.circle(vis, (px, py), 5, (0, 0, 255), -1)
    # cv2.imshow("Pixel Visualization", vis)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # Define BGR color ranges for each rarity
    rarity_ranges = {
        # Widened ranges for more tolerance
        "exotic":   {"min": np.array([180, 0, 180]),   "max": np.array([255, 60, 255])},   # purple (wider for 226,23,226)
        "legendary": {"min": np.array([0, 60, 160]),   "max": np.array([100, 200, 255])},  # orange (wider)
        "epic":     {"min": np.array([0, 100, 0]),    "max": np.array([100, 255, 100])},   # green (wider)
        "common":   {"min": np.array([60, 60, 60]),   "max": np.array([200, 200, 200])},   # gray (wider)
        "rare":     {"min": np.array([100, 0, 0]),    "max": np.array([255, 100, 100])},   # blue (wider)
    }

    rarity = "unknown"
    for name, rng in rarity_ranges.items():
        if np.all(color >= rng["min"]) and np.all(color <= rng["max"]):
            rarity = name
            break
    print(f"Rarity detected: {rarity}")
    return rarity

def finish_him():
    # Click at (402, 654) relative to the top-left corner of the window
    window_title = "Miscrits" 
    frame = capture_window(window_title)
    x, y, w, h = get_window_bbox(window_title)
    click_x = x + 402
    click_y = y + 654
    click_at(click_x, click_y)
    print(f"Pressed at ({click_x}, {click_y})")
    time.sleep(10)
    # Detect color at (615, 503) relative to the top-left corner of the window
    window_title = "Miscrits"
    frame = capture_window(window_title)
    x, y, w, h = get_window_bbox(window_title)
    px = 615
    py = 600
    color = frame[py, px]  # BGR format
    print(f"Pixel color at ({px},{py}): {color}")
    #  # Visualize the pixel location where color is picked
    # vis = frame.copy()
    # cv2.circle(vis, (px, py), 5, (0, 0, 255), -1)
    # cv2.imshow("Finish Him Pixel Visualization", vis)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    if np.array_equal(color, np.array([254, 254, 254])):
        click_at(px + x, py + y)  # Click at the pixel location
        # # Visualize the click location
        # frame_vis = frame.copy()
        # cv2.circle(frame_vis, (click_x, click_y), 10, (0, 255, 0), 2)
        # cv2.imshow("Click Location Visualization", frame_vis)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        print(f"Clicked at ({click_x}, {click_y}) due to color match [254 254 254]")
        return True
    else:
        finish_him()

def health_check():
    window_title = "Miscrits"
    frame = capture_window(window_title)
    x, y, w, h = get_window_bbox(window_title)

    # Define the box region (example: center 100x40 box)
    box_w, box_h = 60, 20
    box_x = x + 980
    box_y = y + 81

    # Capture the box region
    box_img = pyautogui.screenshot(region=(box_x, box_y, box_w, box_h))
    box_img_cv = cv2.cvtColor(np.array(box_img), cv2.COLOR_RGB2BGR)

    # OCR using easyocr
    reader = easyocr.Reader(['en'], gpu=False)
    result = reader.readtext(box_img_cv, detail=0)
    text = result[0] if result else ""
    print("OCR Result:", text.strip())
    # Extract the number before "/" if present
    match = re.search(r'(\d+)\s*/', text)
    if match:
        number_before_slash = int(match.group(1))
        print("Number before '/':", number_before_slash)
        return number_before_slash
    else:
        print("No number found before '/'")
        return None

    

def capture_attack():

    health = health_check()
    chance = capture_chance()
    rarity = rarity_check()
    if (
        (rarity == "legendary" and int(''.join(filter(str.isdigit, chance))) > 85) or
        (rarity != "legendary" and int(''.join(filter(str.isdigit, chance))) > 90) or
        (health is not None and health < 25)
    ):
        time.sleep(2)
        window_title = "Miscrits" 
        frame = capture_window(window_title)
        x, y, w, h = get_window_bbox(window_title)
        click_x = x + 640
        click_y = y + 170
        click_at(click_x, click_y)

        time.sleep(10)  # Wait for the attack animation to finish
        
        window_title = "Miscrits"
        frame = capture_window(window_title)
        x, y, w, h = get_window_bbox(window_title)
        px = 615 + 30
        py = 600 - 163
        color = frame[py, px]  # BGR format
        print(f"Okay Button color at ({px},{py}): {color}")


        if np.array_equal(color, np.array([21, 111, 205])):

            window_title = "Miscrits" 
            frame = capture_window(window_title)
            x, y, w, h = get_window_bbox(window_title)
            click_x = x + 615 + 30
            click_y = y + 600 - 163
            print(f"Clicked at ({click_x}, {click_y}) to press Okay")
            click_at(click_x, click_y)
            
            time.sleep(7)
            window_title = "Miscrits" 
            frame = capture_window(window_title)
            x, y, w, h = get_window_bbox(window_title)
            click_x = x + 615
            click_y = y + 600
            print(f"Clicked at ({click_x}, {click_y}) to press Continue")
            click_at(click_x, click_y)

            time.sleep(7)
            window_title = "Miscrits" 
            frame = capture_window(window_title)
            x, y, w, h = get_window_bbox(window_title)
            click_x = x + 580
            click_y = y + 475
            print(f"Clicked at ({click_x}, {click_y}) to press Keep")
            click_at(click_x, click_y)
            return
        
        else:
            window_title = "Miscrits"
            x, y, w, h = get_window_bbox(window_title)
            click_x = x + 1100 - 918
            click_y = y + 640
            click_at(click_x, click_y)
            print("prev page")
            time.sleep(2)
            click_at(click_x, click_y)    
            print("prev page")
            time.sleep(2)
            finish_him()
    
    else:
        window_title = "Miscrits" 
        frame = capture_window(window_title)
        x, y, w, h = get_window_bbox(window_title)
        click_x = x + 402 + 200
        click_y = y + 644
        click_at(click_x, click_y)
        print(f"Pressed at ({click_x}, {click_y})")
        capture_attack()

   
def capture_him():
    # Click at (1100, 640) relative to the top-left corner of the window
    window_title = "Miscrits"
    x, y, w, h = get_window_bbox(window_title)
    click_x = x + 1100
    click_y = y + 640
    click_at(click_x, click_y)
    print("next page")
    time.sleep(2)
    click_at(click_x, click_y)    
    print("next page")
    capture_attack()

def take_screenshot():
    screenshot = pyautogui.screenshot(region=region)
    filename = f"screenshots/screenshot_{screenshot_count}.png"
    screenshot.save(filename)
    print(f"Saved {filename}")
    
    

if __name__ == "__main__":
    
    time.sleep(2)   
    region = (1280, 0, 1280, 1440)
    screenshot_count = 0
    for iter in range(200): 

        if iter % 60 == 0 and iter != 0:
            window_title = "Miscrits"
            x, y, w, h = get_window_bbox(window_title)
            click_x = x + 840
            click_y = y + 78
            click_at(click_x, click_y)

            time.sleep(2)

            window_title = "Miscrits"
            x, y, w, h = get_window_bbox(window_title)
            click_x = x + 594
            click_y = y + 423
            click_at(click_x, click_y)
              
        click_on_rock()  # Click in the middle of the window
        time.sleep(7)
        take_screenshot()
        screenshot_count += 1    # Take a screenshot every iteration
        chance_text = capture_chance() 
        if any(c.isalpha() for c in chance_text):
            chance_text = "100"
        try:
            chance_value = int(''.join(filter(str.isdigit, chance_text)))
        except ValueError:
            chance_value = -1

        if 0 <= chance_value <= 100:
            rarity = rarity_check().lower()
            if (
                (rarity == "common" and chance_value <= 28 ) or
                (rarity == "rare" and chance_value <= 20) or
                (rarity == "epic" and chance_value <= 10) or
                (rarity == "exotic" and chance_value <= 1) or
                (rarity == "legendary")
            ):
                print("capture on!")
                capture_him()
            else:
                print(f"Rarity: {rarity}, Capture Chance: {chance_value}")
                print("finish him")
                finish_him()
        else:
            print("Chance not in range 0-100, waiting 20 seconds...")
            time.sleep(20)

        time.sleep(5)  # Wait before the next iteration
    
