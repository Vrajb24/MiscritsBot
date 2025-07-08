import pyautogui
import pygetwindow as gw
import cv2
import numpy as np
from datetime import datetime



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


def take_screenshot(filename):
    print("Taking screenshot...") 
    region = (0, 0, 2880, 1800)
    screenshot = pyautogui.screenshot(region=region)
    now = datetime.now()
    screenshot.save(filename)
    print(f"Saved {filename}")