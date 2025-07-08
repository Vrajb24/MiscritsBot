import cv2
import numpy as np
import pygetwindow as gw
import pyautogui
import time
import re
from datetime import datetime
import easyocr  # Changed from pytesseract to easyocr
import numpy as np
import win32gui
import win32ui
import win32con
from ctypes import windll
import win32api

def get_window_handle(window_title):
    """Gets the handle of the window."""
    handle = win32gui.FindWindow(None, window_title)
    if handle == 0:
        raise Exception("Window not found")
    return handle

def get_window_bbox(hwnd):
    """Gets the bounding box of a window from its handle."""
    rect = win32gui.GetWindowRect(hwnd)
    x = rect[0]
    y = rect[1]
    w = rect[2] - x
    h = rect[3] - y
    return (x, y, w, h)

def click_at(hwnd, click_x, click_y, hold_time=0.25):
    """Sends a click to a window in the background."""
    lParam = win32api.MAKELONG(click_x, click_y)

    win32api.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
    pyautogui.sleep(hold_time)
    win32api.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, lParam)


def capture_window(hwnd):
    """Captures the contents of a window even if it's in the background."""
    x, y, w, h = get_window_bbox(hwnd)

    wDC = win32gui.GetWindowDC(hwnd)
    dcObj = win32ui.CreateDCFromHandle(wDC)
    cDC = dcObj.CreateCompatibleDC()
    dataBitMap = win32ui.CreateBitmap()
    dataBitMap.CreateCompatibleBitmap(dcObj, w, h)
    cDC.SelectObject(dataBitMap)
    cDC.BitBlt((0, 0), (w, h), dcObj, (0, 0), win32con.SRCCOPY)

    # To get the data into a format that OpenCV can use
    signedIntsArray = dataBitMap.GetBitmapBits(True)
    img = np.fromstring(signedIntsArray, dtype='uint8')
    img.shape = (h, w, 4)

    # Free Resources
    dcObj.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, wDC)
    win32gui.DeleteObject(dataBitMap.GetHandle())

    # Drop the alpha channel, and convert to BGR
    return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

def click_on_rock():
    window_title = "Miscrits"
    hwnd = get_window_handle(window_title)
    x, y, w, h = get_window_bbox(hwnd)
    # The new click_at function takes coordinates relative to the window, not the screen
    click_x = w // 2
    click_y = h // 2 - 10
    click_at(hwnd, click_x, click_y)
    print(f"Clicked in the middle of the window at ({click_x}, {click_y})")

def click_on_blighted_bush():
    window_title = "Miscrits"
    hwnd = get_window_handle(window_title)
    x, y, w, h = get_window_bbox(hwnd)
    # The new click_at function takes coordinates relative to the window, not the screen
    click_x = x + 660
    click_y = y + 280
    click_at(hwnd, click_x, click_y)
    print(f"Clicked in the middle of the window at ({click_x}, {click_y})")

def capture_chance(hwnd, reader):
    """
    Captures the "capture chance" text from a background window.

    Args:
        hwnd: The handle of the target window.
        reader: The initialized easyocr.Reader object.
    """
    # 1. Capture the entire window content without bringing it to the front
    frame = capture_window(hwnd) # This is our background-safe capture function

    # 2. Define the Region of Interest (ROI) relative to the window's top-left corner
    # Original coordinates were relative to the screen (x + 620, y + 165).
    # Now they are relative to the window frame, which is just (620, 165).
    roi_x, roi_y = 620, 165
    roi_w, roi_h = 47, 25

    # 3. Crop the captured frame to get only the box we need
    # Using numpy slicing: array[y:y+h, x:x+w]
    box_img_cv = frame[roi_y : roi_y + roi_h, roi_x : roi_x + roi_w]

    # 4. Perform OCR on the cropped region
    # The reader is passed in for efficiency
    result = reader.readtext(box_img_cv, detail=0)
    text = result[0] if result else ""
    print("OCR Result:", text.strip())

    # Optional: Visualize the cropped box to make sure it's correct
    # cv2.imshow("Cropped OCR Box", box_img_cv)
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

def attack(number):
    # Use different click positions based on the attack number
    window_title = "Miscrits" 
    frame = capture_window(window_title)
    x, y, w, h = get_window_bbox(window_title)
    
    if number == 1:
        click_x = x + 402
        click_y = y + 654
    elif number == 2:
        click_x = x + 580
        click_y = y + 654
    elif number == 3:
        click_x = x + 780
        click_y = y + 654
    elif number == 4:
        click_x = x + 980
        click_y = y + 654
    else:
        # Default fallback position
        click_x = x + 402
        click_y = y + 654
    click_at(click_x, click_y)
    print(f"Pressed at ({click_x}, {click_y})")

def finish_him():
    attack(1)  # Call the attack function with number 1
    
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
        print(f"Clicked at ({px + x}, {py + y}) due to color match [254 254 254]")
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

def take_screenshot(hwnd):
    """
    Captures a screenshot of a background window and saves it to a file.

    Args:
        hwnd: The handle of the target window.
    """
    # 1. Capture the full window in the background using our custom function.
    # This returns an OpenCV image (NumPy array).
    frame = capture_window(hwnd)

    # 2. Create the filename (this logic remains the same)
    now = datetime.now()
    
    # Create the screenshots directory if it doesn't exist
    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")
        
    filename = f"screenshots/screenshot_{now.strftime('%d-%m-%y-%H-%M-%S')}.png"

    # 3. Save the captured frame using OpenCV's imwrite function
    cv2.imwrite(filename, frame)
    print(f"Saved background screenshot: {filename}")


def train_individual(miscrit_no, bonus):
    window_title = "Miscrits"
    x, y, w, h = get_window_bbox(window_title)
    if miscrit_no == 1:
        click_x = x + 390
        click_y = y + 150
    elif miscrit_no == 2:
        click_x = x + 390
        click_y = y + 200
    elif miscrit_no == 3:
        click_x = x + 390
        click_y = y + 250
    elif miscrit_no == 4:
        click_x = x + 390
        click_y = y + 300
    else:
        raise ValueError("miscrit_no must be 1, 2, 3, or 4")
    click_at(click_x, click_y)

    time.sleep(2)

    window_title = "Miscrits"
    frame = capture_window(window_title)
    x, y, w, h = get_window_bbox(window_title)

    # Define the box region (example: 100x40 box at some position)
    box_w, box_h = 150, 50

    box_x = x + 595
    box_y = y + 67

    # Capture the box region
    box_img = pyautogui.screenshot(region=(box_x, box_y, box_w, box_h))
    box_img_cv = cv2.cvtColor(np.array(box_img), cv2.COLOR_RGB2BGR)

    # OCR using easyocr
    reader = easyocr.Reader(['en'], gpu=False)
    result = reader.readtext(box_img_cv, detail=0)
    text1 = result[0] if result else ""

    # Define the box region (example: 100x40 box at some position)
    box_w, box_h = 150, 50

    box_x = x + 670
    box_y = y + 70

    # Capture the box region
    box_img = pyautogui.screenshot(region=(box_x, box_y, box_w, box_h))
    box_img_cv = cv2.cvtColor(np.array(box_img), cv2.COLOR_RGB2BGR)

    # OCR using easyocr
    reader = easyocr.Reader(['en'], gpu=False)
    result = reader.readtext(box_img_cv, detail=0)
    text2 = result[0] if result else ""

    if (text1.strip().lower() == "trainnow"):
        print("level <30:", text1.strip())
    elif(text2.strip().lower() == "trainnow"):
        print("level >=30:", text2.strip())
    else:
        print("Miscrit:",miscrit_no,"Not ready for training:")
        

    if text1.strip().lower() == "train" or text2.strip().lower() == "train":
        return
    elif text1.strip().replace(" ", "").lower() == "trainnow":
        click_x = x + 670
        click_y = y + 90
        click_at(click_x, click_y)
        time.sleep(3)

    elif text2.strip().replace(" ", "").lower() == "trainnow":
        click_x = x + 750
        click_y = y + 90
        click_at(click_x, click_y)
        time.sleep(4)

    #checking for evolution! (at level 10 20 30)
    # Check for evolution with OCR (at level 10, 20, 30)
    window_title = "Miscrits"
    frame = capture_window(window_title)
    x, y, w, h = get_window_bbox(window_title)

    # Define OCR box for evolution text
    box_w, box_h = 158, 33
    box_x = x + 385
    box_y = y + 100

    # Capture the evolution text box region
    evolution_img = pyautogui.screenshot(region=(box_x, box_y, box_w, box_h))
    evolution_img_cv = cv2.cvtColor(np.array(evolution_img), cv2.COLOR_RGB2BGR)

    # OCR using easyocr
    reader = easyocr.Reader(['en'], gpu=False)
    result = reader.readtext(evolution_img_cv, detail=0)
    evolution_text = result[0] if result else ""
    # print("Evolution OCR Result:", evolution_text.strip())

    # If evolution is detected, click to proceed
    if "evolvedl" in evolution_text.strip().lower():
        print("Evolution detected!")
        # Click at the specified coordinates for evolution
        click_x = x + w/2
        click_y = y + h/2
        click_at(click_x, click_y)
        time.sleep(0.25)  # Wait for the evolution animation to finish
        click_x = x + 644
        click_y = y + 611
        click_at(click_x, click_y)
        print(f"Clicked at ({click_x}, {click_y}) to proceed with evolution")
        time.sleep(2)  # Wait for animation or next screen

    click_x = x + w/2
    click_y = y + h/2
    click_at(click_x, click_y)

    time.sleep(3)

    if bonus:
        click_x = x + 570
        click_y = y + 655
        click_at(click_x, click_y)

        time.sleep(3)

        click_x = x + 640
        click_y = y + 655
        click_at(click_x, click_y, hold_time=3)

    else:

        click_x = x + 790
        click_y = y + 655
        click_at(click_x, click_y)

        

    time.sleep(7)

    # New OCR box for "l 170 and h 32 at 455 from left and 207 from top"
    box_w, box_h = 170, 32
    box_x = x + 455
    box_y = y + 207

    box_img = pyautogui.screenshot(region=(box_x, box_y, box_w, box_h))
    box_img_cv = cv2.cvtColor(np.array(box_img), cv2.COLOR_RGB2BGR)

    reader = easyocr.Reader(['en'], gpu=False)
    result = reader.readtext(box_img_cv, detail=0)
    text = result[0] if result else ""
    print("OCR for New Ability:", text.strip())

    if text.strip().replace(" ", "").lower() == "newabilitiesl":
        # Click at (670, 370)
        click_x = x + 670
        click_y = y + 370
        click_at(click_x, click_y)
        time.sleep(2)
        # Click at (650, 426)
        click_x = x + 630
        click_y = y + 426
        click_at(click_x, click_y)
        time.sleep(2)
        # Click at (775, 510)
        click_x = x + 775
        click_y = y + 510
        click_at(click_x, click_y)

def check_for_rank_up():
        window_title = "Miscrits"
        x, y, w, h = get_window_bbox(window_title)
        box_w, box_h = 127, 35
        box_x = x + 523
        box_y = y + 182

        # Capture the box region
        box_img = pyautogui.screenshot(region=(box_x, box_y, box_w, box_h))
        box_img_cv = cv2.cvtColor(np.array(box_img), cv2.COLOR_RGB2BGR)

        # OCR using easyocr
        reader = easyocr.Reader(['en'], gpu=False)
        result = reader.readtext(box_img_cv, detail=0)
        text = result[0] if result else ""
        
        print("Rank Up OCR Result:", text.strip())
        
        # Check if text contains "rank up" (case insensitive)
        if "rank up" in text.strip().lower():
            click_x = x + w/2
            click_y = y + h/2
            click_at(click_x, click_y)
            time.sleep(0.25)
            click_x = x + 642
            click_y = y + 526
            click_at(click_x, click_y)
            print(f"Clicked at ({click_x}, {click_y}) because 'Rank Up' was detected")

def train():
    window_title = "Miscrits"
    x, y, w, h = get_window_bbox(window_title)
    click_x = x + 565
    click_y = y + 70
    click_at(click_x, click_y)

    time.sleep(3)

    train_individual(1, False)
    time.sleep(1)
    train_individual(2, True)   
    time.sleep(1)
    train_individual(3, False)
    time.sleep(1)
    train_individual(4, False)
    time.sleep(1)

    click_x = x + 995
    click_y = y + 60
    click_at(click_x, click_y)
    

    # Check for rank up notification
    check_for_rank_up()
    

    
def check_for_quest_completion():
    
    window_title = "Miscrits"
    x, y, w, h = get_window_bbox(window_title)
    box_w, box_h = 102, 27
    box_x = x + 593
    box_y = y + 453

    box_img = pyautogui.screenshot(region=(box_x, box_y, box_w, box_h))
    box_img_cv = cv2.cvtColor(np.array(box_img), cv2.COLOR_RGB2BGR)

    reader = easyocr.Reader(['en'], gpu=False)
    result = reader.readtext(box_img_cv, detail=0)
    text = result[0] if result else ""

    # print("OCR Result for Quest Completion:", text.strip())
    # # Visualize the OCR box on the captured frame
    # window_title = "Miscrits"
    # frame = capture_window(window_title)
    # cv2.rectangle(
    #     frame,
    #     (box_x - x, box_y - y),
    #     (box_x - x + box_w, box_y - y + box_h),
    #     (0, 255, 0),
    #     2
    # )
    # cv2.imshow("Quest Completion OCR Box", frame)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    if text.strip().lower() == "@koy":
        click_x = box_x + box_w // 2
        click_y = box_y + box_h // 2
        click_at(click_x, click_y)
        time.sleep(0.2)
        click_at(click_x, click_y)  # Click again to confirm
        print(f"Clicked at center of OCR box ({click_x}, {click_y}) because text was 'okay'")

def heal():
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

def click_on_red_gem():
    window_title = "Miscrits"
    x, y, w, h = get_window_bbox(window_title)
    click_x = x + 606
    click_y = y + 301
    click_at(click_x, click_y)

    
    
if __name__ == "__main__":
    
    time.sleep(2)   

    # Initialize the window title and OCR reader
    window_title = "Miscrits"  # The title of the game window
    try:
        hwnd = get_window_handle(window_title) # Get the handle once
        reader = easyocr.Reader(['en'], gpu=False) # Initialize the reader once
    except Exception as e:
        print(e)
        exit()

    region = (1280, 0, 1280, 1440)
    screenshot_count = 0

    print("Initializing OCR Engine...")
    reader = easyocr.Reader(['en'], gpu=False)
    print("Initialization complete.")

    for iter in range(200): 
        
        if iter % 10 == 0 and iter != 0:
            check_for_quest_completion()  # Check for quest completion every 10 iterations
            train()  # Train every 10 
            
        if iter % 50 == 0 and iter != 0:
            heal()
              
        # click_on_rock()  # Blighted Flue
        # click_on_blighted_bush() #Blighted Cubspro
        click_on_red_gem() #Dark Poltergust
        time.sleep(7)
        take_screenshot()
        screenshot_count += 1    # Take a screenshot every iteration
        chance_text = capture_chance(hwnd, reader) 
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
                (rarity == "exotic" and chance_value <= 10) or
                (rarity == "legendary")
            ):
                print("capture on!")
                capture_him()
                check_for_rank_up()

            else:
                print(f"Rarity: {rarity}, Capture Chance: {chance_value}")
                print("finish him")
                finish_him()
        else:
            print("Chance not in range 0-100, waiting 20 seconds...")
            time.sleep(20)

        time.sleep(5)  # Wait before the next iteration  
