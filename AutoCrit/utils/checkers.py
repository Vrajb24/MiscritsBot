from utils.lowLevel import capture_window, get_window_bbox
import numpy as np
import pyautogui
import easyocr  # Changed from pytesseract to easyocr
import cv2
import re
from utils.interactors import click_on_element
from utils.ocr import box_ocr
import time

def rarity_check():
    window_title = "Miscrits" 
    frame = capture_window(window_title)
    x, y, w, h = get_window_bbox(window_title)
    px = 1945
    py = 136
    color = frame[py, px]  # BGR format
    # print(f"Pixel color at ({px},{py}): {color}")
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



def health_check():
    window_title = "Miscrits"
    frame = capture_window(window_title)
    x, y, w, h = get_window_bbox(window_title)

    # Define the box region (example: center 100x40 box)
    box_w, box_h = 125, 55
    box_x = x + 2280
    box_y = y + 165

    # Capture the box region
    box_img = pyautogui.screenshot(region=(box_x, box_y, box_w, box_h))
    box_img_cv = cv2.cvtColor(np.array(box_img), cv2.COLOR_RGB2BGR)

    # OCR using easyocr
    reader = easyocr.Reader(['en'], gpu=False)
    result = reader.readtext(box_img_cv, detail=0)
    text = result[0] if result else ""
    # print("OCR Result:", text.strip())
    # Extract the number before "/" if present
    match = re.search(r'(\d+)\s*/', text)
    if match:
        number_before_slash = int(match.group(1))
        # print("Number before '/':", number_before_slash)
        print(f"Health detected: {number_before_slash}")
        return number_before_slash
    else:
        print("No number found before '/'")
        return None
    

    
def check_for_rank_up():

    Rankedup=click_on_element(
        window_title="Miscrits",
        template_folder="Elements/Rankup",
        threshold=0.8,
        visualize=False,
        click_duration=0,
        y_offset=0
    )

    if Rankedup:

        click_on_element(
            window_title="Miscrits",
            template_folder="Elements/OkayButton",
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )   

        check_for_rank_up()
        check_for_quest_completion()


def capture_chance():

    text = box_ocr(1374, 379, 153, 56, visualize=False, purpose="Capture Chance")

    return text.strip()

def check_for_quest_completion():
    print("Checking for quest completion")

    quest=click_on_element(
        window_title="Miscrits", 
        template_folder="Elements/OkayButton",
        threshold=0.8,
        visualize=False,
        click_duration=0,
        y_offset=0
    )

    if quest:
        check_for_quest_completion()
        print("Quest completed, checking for another quest...")
    else:
        return
    time.sleep(2)