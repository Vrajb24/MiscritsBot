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
from PIL import Image, ImageDraw
import os
from paddleocr import PaddleOCR

# --------------------------------------------------------- LOW LEVEL FUNCTIONS --------------------------------------------------------- 

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

#  ── module-level one-time import / EasyOCR initialisation ────────────
import easyocr
reader = easyocr.Reader(['en'], gpu=False)

def box_ocr(x_relative, y_relative, box_w, box_h, visualize=False, purpose=""):
    """
    Same arguments / return as before – see previous docstring.
    """
    import cv2, pyautogui, numpy as np
    from ctypes import windll
    import win32gui

    print(f"[box_ocr] ({x_relative},{y_relative},{box_w},{box_h})  – {purpose}")

    # ── 1. window position + DPI scaling ──────────────────────────────
    window_title = "Miscrits"
    x, y, w, h = get_window_bbox(window_title)

    try:
        hwnd   = win32gui.FindWindow(None, window_title)
        dpi    = windll.user32.GetDpiForWindow(hwnd)
        # scale  = dpi / 96.0
        scale = 1.0
    except Exception:
        scale  = 1.0

    bx   = int(x + x_relative * scale)
    by   = int(y + y_relative * scale)
    bw   = int(box_w * scale)
    bh   = int(box_h * scale)

    # ── 2. capture → gray → 4× upscale ───────────────────────────────
    snap     = pyautogui.screenshot(region=(bx, by, bw, bh))
    bgr      = cv2.cvtColor(np.array(snap), cv2.COLOR_RGB2BGR)
    gray     = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    upscale  = 4
    g_big    = cv2.resize(gray, None, fx=upscale, fy=upscale,
                          interpolation=cv2.INTER_CUBIC)

    # ── 3. adaptive threshold *then* light dilation (no erosion) ─────
    bin_img  = cv2.adaptiveThreshold(
                  g_big, 255,
                  cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
                  11, 2)

    kernel   = np.ones((2, 2), np.uint8)
    bin_img  = cv2.dilate(bin_img, kernel, iterations=1)

    # ── 4. OCR pass 1: raw gray  – pass 2: binarised fallback ─────────
    for cand in (g_big, bin_img):
        text = reader.readtext(cand,
                               detail=0,
                               allowlist="0123456789%/")
        if text:                      # got something!
            text = text[0].strip()
            break
    else:
        text = ""

    print("► OCR:", text)

    # ── 5. optional visualisation ────────────────────────────────────
    if visualize:
        frame = capture_window(window_title)
        cv2.rectangle(frame,
                      (int(bx - x), int(by - y)),
                      (int(bx - x + bw), int(by - y + bh)),
                      (0, 255, 0), 1)
        cv2.imshow("window ROI", frame)
        cv2.imshow("gray ×4",  g_big)
        cv2.imshow("binary",   bin_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return text

    
# --------------------------------------------------------- HIGH LEVEL DETECTION FUNCTIONS ---------------------------------------------------------
def detect_element(window_title,
                   template_folder,
                   threshold=0.8,
                   visualize=False):
    """
    Locate one or more template images inside a window.

    Args
    ----
    window_title : str
        Title of the target window.
    template_folder : str
        Folder containing template images (png / jpg / jpeg / bmp).
    threshold : float, optional
        cv2.matchTemplate score threshold.  Default 0.8.
    visualize : bool, optional
        If True, show a window with red rectangles around every match.

    Returns
    -------
    list[tuple[tuple[int, int, int, int], str]]
        A list of (box, template_path) tuples.
        box = (x1, y1, x2, y2) in absolute screen coordinates.
        Empty list means “no match”.
    """
    # -------------- window lookup -----------------
    win = next((w for w in gw.getWindowsWithTitle(window_title) if w.visible),
               None)
    if not win:
        print(f"Window '{window_title}' not found or not visible.")
        return []

    left, top, width, height = win.left, win.top, win.width, win.height

    # -------------- capture window ----------------
    shot_rgb = pyautogui.screenshot(region=(left, top, width, height))
    shot_cv  = cv2.cvtColor(np.array(shot_rgb), cv2.COLOR_RGB2BGR)

    # -------------- gather templates --------------
    image_exts = ('.png', '.jpg', '.jpeg', '.bmp')
    try:
        template_paths = [os.path.join(template_folder, f)
                          for f in os.listdir(template_folder)
                          if f.lower().endswith(image_exts)]
    except Exception as e:
        print(f"Error reading '{template_folder}': {e}")
        return []

    if not template_paths:
        print(f"No templates found in '{template_folder}'.")
        return []

    print(f"Found {len(template_paths)} template images in '{template_folder}'")

    # -------------- match every template ----------
    all_boxes = []
    for t_path in template_paths:
        template = cv2.imread(t_path, cv2.IMREAD_COLOR)
        if template is None:
            print(f"Warning: could not load {t_path}")
            continue

        h, w, _ = template.shape
        res     = cv2.matchTemplate(shot_cv, template, cv2.TM_CCOEFF_NORMED)
        loc_y, loc_x = np.where(res >= threshold)

        boxes = [((x + left,  y + top,
                   x + left + w, y + top + h), t_path)
                 for x, y in zip(loc_x, loc_y)]

        print(f"Template {os.path.basename(t_path)} → {len(boxes)} matches")
        all_boxes.extend(boxes)

    # -------------- optional visualisation --------
    if visualize and all_boxes:
        from PIL import Image, ImageDraw
        vis_img = Image.fromarray(np.array(shot_rgb))
        draw    = ImageDraw.Draw(vis_img)
        for (x1, y1, x2, y2), _ in all_boxes:
            draw.rectangle((x1 - left, y1 - top, x2 - left, y2 - top),
                           outline='red', width=2)
        vis_img.show()

    if all_boxes:
        print(f"Total matches: {len(all_boxes)}")
    else:
        print("No elements found in window.")

    return all_boxes

def click_on_element(window_title, template_folder, threshold=0.8, visualize=False, click_duration=0, y_offset=10):
    """
    Locates and clicks on an element in the specified window using template matching.
    
    Args:
        window_title (str): Title of the window to search in
        template_folder (str): Path to folder containing template images
        threshold (float): Matching threshold (0.0-1.0)
        visualize (bool): Whether to show visualization of matches
        click_duration (float): How long to hold the click
        y_offset (int): Y-offset for click position
        
    Returns:
        bool: True if element was found and clicked, False otherwise
    """
    
    # Get window info
    win = None
    for w in gw.getWindowsWithTitle(window_title):
        if w.visible:
            win = w
            break
    
    if not win:
        print(f"Window '{window_title}' not found or not visible.")
        return False

    # Get window position and size
    left, top, width, height = win.left, win.top, win.width, win.height
    
    # Screenshot only the window region
    screenshot = pyautogui.screenshot(region=(left, top, width, height))
    screenshot_array = np.array(screenshot)
    screenshot_cv = cv2.cvtColor(screenshot_array, cv2.COLOR_RGB2BGR)
    
    all_boxes = []
    
    # Get all image files from the template folder
    image_extensions = ['.png', '.jpg', '.jpeg', '.bmp']
    template_paths = []
    
    try:
        for file in os.listdir(template_folder):
            if any(file.lower().endswith(ext) for ext in image_extensions):
                template_paths.append(os.path.join(template_folder, file))
        
        print(f"Found {len(template_paths)} template images in folder {template_folder}")
    except Exception as e:
        print(f"Error reading template folder {template_folder}: {e}")
        return False
    
    if not template_paths:
        print(f"No image templates found in folder {template_folder}")
        return False
    
    # Process each template
    for template_path in template_paths:
        try:
            # Load template
            template = cv2.imread(template_path, cv2.IMREAD_COLOR)
            if template is None:
                print(f"Warning: Failed to load template {template_path}")
                continue
                
            h, w, _ = template.shape

            # Template matching
            result = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
            loc = np.where(result >= threshold)

            # Get boxes for this template
            template_boxes = []
            for pt in zip(*loc[::-1]):
                # Adjust coordinates relative to entire screen
                abs_pt = (pt[0] + left, pt[1] + top)
                template_boxes.append((abs_pt[0], abs_pt[1], abs_pt[0] + w, abs_pt[1] + h))
            
            # Add template path info to each box
            for box in template_boxes:
                all_boxes.append((box, template_path))
            
            print(f"Found {len(template_boxes)} matches for template {os.path.basename(template_path)}")
            
        except Exception as e:
            print(f"Error processing template {template_path}: {e}")
    
    # Visualize the detection
    if visualize and all_boxes:
        # Create a copy of the screenshot for visualization
        vis_img = Image.fromarray(screenshot_array)
        draw = ImageDraw.Draw(vis_img)
        
        # Draw boxes on the image (using local coordinates)
        for box, template_path in all_boxes:
            # Convert to local coordinates for drawing
            local_box = (box[0] - left, box[1] - top, box[2] - left, box[3] - top)
            draw.rectangle(local_box, outline='red', width=2)
        
        # Display the image
        vis_img.show()

    if all_boxes:
        print(f"Found {len(all_boxes)} matches in total")
        # Click on the first match (box is at index 0 of the tuple)
        box = all_boxes[0][0]
        x1, y1, x2, y2 = box
        center_x = x1 + (x2 - x1) // 2
        center_y = y1 + (y2 - y1) // 2 + y_offset
        pyautogui.mouseDown(center_x, center_y)
        pyautogui.sleep(click_duration)
        pyautogui.mouseUp(center_x, center_y)
        return True
    else:
        print("No elements found in window.")
        return False
    
def capture_chance():

    text = box_ocr(1374, 379, 153, 56, visualize=False, purpose="Capture Chance")

    return text.strip()


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
    

def take_screenshot(filename):
    print("Taking screenshot...") 
    screenshot = pyautogui.screenshot(region=region)
    now = datetime.now()
    screenshot.save(filename)
    print(f"Saved {filename}")

# --------------------------------------------------------- HIGHLEVEL INPUT FUNCTIONS ---------------------------------------------------------

def click_on_target(target_type):
    print(f"Clicking on target: {target_type}")
    window_title = "Miscrits"
    frame = capture_window(window_title)
    x, y, w, h = get_window_bbox(window_title)
    
    if target_type.lower() == "blighted_rock":
        click_x = x + w // 2
        click_y = y + h // 2 - 10
    elif target_type.lower() == "blighted_bush":
        click_x = x + 660
        click_y = y + 280
    elif target_type.lower() == "red_gem":
        click_x = x + 606
        click_y = y + 301
    else:
        raise ValueError("Invalid target type. Use 'rock' or 'blighted_bush'")
    
    click_at(click_x, click_y)
    print(f"Clicked on {target_type} at ({click_x}, {click_y})")


def attack(number):
    # Use different click positions based on the attack number
    window_title = "Miscrits" 
    frame = capture_window(window_title)
    x, y, w, h = get_window_bbox(window_title)
    click_y = y + 1665
    if number == 1:
        click_x = x + 680
    elif number == 2:
        click_x = x + 1196
    elif number == 3:
        click_x = x + 1721
    elif number == 4:
        click_x = x + 2251
    else:
        # Default fallback position
        click_x = x + 680
    click_at(click_x, click_y)
    print(f"Pressed at ({click_x}, {click_y})")


def finish_him():
    attack(1)  # Call the attack function with number 1
    
    time.sleep(5)

    ReadyToTrain = detect_element(
        window_title="Miscrits",
        template_folder="Elements/ReadyToTrain",
        threshold=0.8,
        visualize=False
    )

    
    FightEnded = click_on_element(
        window_title="Miscrits",
        template_folder="Elements/ContinueButton",
        threshold=0.8,
        visualize=False,
        click_duration=0,
        y_offset=0
    )
    
    time.sleep(3)

    if FightEnded:
        print("Clicked on Continue button after fight ended")
        if ReadyToTrain:
            print("Ready to train detected, clicking on Train button")
            train()
        return True
    else:
        finish_him()


def capture_attack():

    health = health_check()
    chance = capture_chance()
    rarity = rarity_check()
    # Extract digits from chance and validate
    chance_digits = ''.join(filter(str.isdigit, chance))
    if not chance_digits:  # If no digits found, set default value
        chance_value = 0
        print(f"No digits found in chance '{chance}', using default value 0")
    elif int(chance_digits) > 100:  # Handle values exceeding 100
        chance_value = 0
        print(f"Chance value exceeded 100: '{chance_digits}', using default value 0")
    else:
        chance_value = int(chance_digits)
    if (
        (rarity == "legendary" and chance_value > 80) or
        (rarity != "legendary" and chance_value > 85) 
    ):
        time.sleep(4)
        

        captured=click_on_element(
            window_title="Miscrits",
            template_folder="Elements/CaptureButton",
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )
        if captured:
            print("Clicked on Capture button")

        time.sleep(10)

        Okayed=click_on_element(
            window_title="Miscrits",   
            template_folder="Elements/OkayButton",
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )
        if Okayed:
            print("Clicked on Okay button after capture")

        else:

            click_on_element(
                window_title="Miscrits",
                template_folder="Elements/PrevMenuPage",
                threshold=0.8,
                visualize=False,
                click_duration=0,
                y_offset=0
            )

            time.sleep(1)

            click_on_element(
                window_title="Miscrits",
                template_folder="Elements/PrevMenuPage",
                threshold=0.8,
                visualize=False,
                click_duration=0,
                y_offset=0
            )

            finish_him()
            return

        time.sleep(5)  # Wait for the attack animation to finish
        
        continued=click_on_element(
            window_title="Miscrits",   
            template_folder="Elements/ContinueButton",
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )

        if continued:
            print("Clicked on Continue button after capture")

        time.sleep(3)

        Okayed = click_on_element(
            window_title="Miscrits",
            template_folder="Elements/OkayButton",
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )
        if Okayed:
            print("Clicked on Okay button on rankup")

        time.sleep(3)

        Okayed = click_on_element(
            window_title="Miscrits",
            template_folder="Elements/OkayButton",
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )
        if Okayed:
            print("Clicked on Okay button on Qest completion")

        time.sleep(3)

        kept = click_on_element(
            window_title="Miscrits",
            template_folder="Elements/KeepButton",
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )
        if kept:    
            print("Clicked on Keep button after capture")

        time.sleep(3)

        healed = click_on_element(
            window_title="Miscrits",
            template_folder="Elements/HealNowButton",
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )
        if healed:
            print("Clicked on Heal button after capture")
            time.sleep(2)
            click_on_element(
                window_title="Miscrits",
                template_folder="Elements/YesButton",
                threshold=0.8,
                visualize=False,
                click_duration=0,
                y_offset=0
            )

    else:
        attack(2)
        capture_attack()

   
def capture_him(rarity):

    now = datetime.now()
    filename = f"captureshots/{rarity}_{now.strftime('%d-%m-%y-%H-%M')}.png"
    take_screenshot(filename)
    # Click at (1100, 640) relative to the top-left corner of the window
    # window_title = "Miscrits"
    # x, y, w, h = get_window_bbox(window_title)
    # click_x = x + 1100
    # click_y = y + 640
    # click_at(click_x, click_y)
    # print("next page")
    # time.sleep(2)
    # click_at(click_x, click_y)    
    # print("next page")
    # capture_attack()

    click_on_element(
        window_title="Miscrits",
        template_folder="Elements/NextMenuPage",
        threshold=0.8,
        visualize=False,
        click_duration=0,
        y_offset=0
    )
    print("next page")

    time.sleep(2)

    click_on_element(
        window_title="Miscrits",
        template_folder="Elements/NextMenuPage",
        threshold=0.8,
        visualize=False,
        click_duration=0,
        y_offset=0
    )
    print("next page")

    capture_attack()
    
def train_individual(miscrit_no, bonus):
    window_title = "Miscrits"
    print(f"Training Miscrit {miscrit_no} with bonus: {bonus}")
    x, y, w, h = get_window_bbox(window_title)
    click_x = x + 650
    if miscrit_no == 1:
        click_y = y + 395
    elif miscrit_no == 2:
        click_y = y + 515
    elif miscrit_no == 3:
        click_y = y + 635
    elif miscrit_no == 4:
        click_y = y + 755
    else:
        raise ValueError("miscrit_no must be 1, 2, 3, or 4")
    click_at(click_x, click_y)

    time.sleep(3)

    window_title = "Miscrits"
    frame = capture_window(window_title)
    x, y, w, h = get_window_bbox(window_title)

    Trained=click_on_element(
        window_title="Miscrits",
        template_folder="Elements/TrainNowButton",
        threshold=0.8,
        visualize=False,
        click_duration=0,
        y_offset=0
        )
    
    if not Trained:
        print("Miscrit:", miscrit_no, "Not ready for training")
        return
    else:
        print("Miscrit:", miscrit_no, "Crit training")

    time.sleep(3)

    if bonus:
        
        click_on_element(
            window_title="Miscrits",
            template_folder="Elements/StatsList",
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        
)
        time.sleep(2)

        click_on_element(
            window_title="Miscrits",
            template_folder="Elements/StatBonus",
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )

        time.sleep(3)

        click_on_element(
            window_title="Miscrits",
            template_folder="Elements/ContinueButton", 
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )
        

    else:

        click_on_element(
            window_title="Miscrits",
            template_folder="Elements/ContinueButton", 
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )

    time.sleep(3)
    okayed=click_on_element(
        window_title="Miscrits",
        template_folder="Elements/OkayButton",
        threshold=0.8,
        visualize=False,
        click_duration=0,
        y_offset=0
    )
    if okayed:
        print("Clicked on Okay button after Evolve")
        

    time.sleep(7)



    Enchanted=click_on_element(
        window_title="Miscrits",
        template_folder="Elements/EnchantAbility",
        threshold=0.8,
        visualize=False,
        click_duration=0,
        y_offset=0
    )

    if Enchanted:
        print("Enchanted ability detected, clicking to enchant")
        # Click at the center of the window to proceed with enchanting
        click_x = x + w // 2
        click_y = y + h // 2
        click_at(click_x, click_y)
        time.sleep(0.25)

        click_on_element(
            window_title="Miscrits",
            template_folder="Elements/GoldToEnchantAbility",
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )
        time.sleep(3)
        click_on_element(
            window_title="Miscrits",
            template_folder="Elements/ContinueButton",
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )
    time.sleep(3)
    Evolved=click_on_element(
        window_title="Miscrits",
        template_folder="Elements/EvolveDiag",
        threshold=0.8,
        visualize=False,
        click_duration=0,
        y_offset=0
    )

    if Evolved:
        print("Evolved ability detected, clicking okay")
        time.sleep(2)
        click_on_element(
            window_title="Miscrits",
            template_folder="Elements/OkayButton",
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )

    time.sleep(3)

    check_for_rank_up()

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


def train():
    print("Starting training process...")

    click_on_element(
        window_title="Miscrits", 
        template_folder="Elements/TrainButton",
        threshold=0.8,
        visualize=False,
        click_duration=0,
        y_offset=0
    )

    time.sleep(3)

    train_individual(1, False)
    time.sleep(1)
    train_individual(2, True)   
    time.sleep(1)
    train_individual(3, True)
    time.sleep(1)
    train_individual(4, True)
    time.sleep(1)

    click_on_element(
        window_title="Miscrits", 
        template_folder="Elements/CloseButton",
        threshold=0.8,
        visualize=False,
        click_duration=0,
        y_offset=0
    )

    # click_x = x + 995
    # click_y = y + 60
    # click_at(click_x, click_y)
    
    time.sleep(3)
    # Check for rank up notification
    check_for_rank_up()
    

    
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

        

def heal():
    print("healing Miscrits")

    click_on_element(
        window_title="Miscrits", 
        template_folder="Elements/HealNowButton",
        threshold=0.8,
        visualize=False,
        click_duration=0,
        y_offset=0
    )



    time.sleep(3)

    click_on_element(
        window_title="Miscrits", 
        template_folder="Elements/YesButton",
        threshold=0.8,
        visualize=False,
        click_duration=0,
        y_offset=0
    )





def attack_strat(chance_text):
    if any(c.isalpha() for c in chance_text):
        chance_text = "100"
    try:
        chance_value = int(''.join(filter(str.isdigit, chance_text)))
    except ValueError:
        chance_value = -1

    if 0 <= chance_value <= 100:
        rarity = rarity_check().lower()
        if (
            (rarity == "common" and chance_value <= 30 ) or
            (rarity == "rare" and chance_value <= 20) or
            (rarity == "epic" and chance_value <= 10) or
            (rarity == "exotic" and chance_value <= 10) or
            (rarity == "legendary")
        ):
            print("capture on!")
            capture_him(rarity=rarity)
            check_for_rank_up()

        else:
            print(f"Rarity: {rarity}, Capture Chance: {chance_value}")
            print("finish him")
            finish_him()
    else:
        print("Chance not in range 0-100, waiting 20 seconds...")
        
        click_on_element(
            window_title="Miscrits",
            template_folder="Elements/ContinueButton",
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )

        time.sleep(2) 

        click_on_element(
            window_title="Miscrits",
            template_folder="Elements/OkayButton",
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )

        time.sleep(2)

        click_on_element(
            window_title="Miscrits",
            template_folder="Elements/YesButton",
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )

        time.sleep(2)

        Retry = click_on_element(
            window_title="Miscrits",
            template_folder="Elements/RetryButton",
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )

        if Retry:
            time.sleep(10)

            Retry = click_on_element(
            window_title="Miscrits",
            template_folder="Elements/RetryButton",
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )

        if Retry:
            time.sleep(10)   

        Account = click_on_element(
            window_title="Miscrits",
            template_folder="Elements/AccountButton",
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )

        if Account or Retry:
            time.sleep(15)
            for step in range(10):
                click_on_element(
                    window_title="Miscrits",
                    template_folder=f"Elements/WayToBlightedFlower/{step}",
                    threshold=0.8,
                    visualize=False,
                    click_duration=0,
                    y_offset=0
                )
                time.sleep(5)
            
            return

    
if __name__ == "__main__":
    
    print("Starting Bot...\n")
    time.sleep(2)   

    # Define the region for screenshots (left, top, width, height)
    region = (0, 0, 2880, 1800)
    for iter in range(2000): 

        check_for_quest_completion()  


        
        # Check for quest completion and train every 10 iterations

        # if iter % 10 == 0 and iter != 0:
        #     train()  
        
        # Heal every 50 iterations
        if iter % 20 == 0 and iter != 0:
            heal()
              
        # Click on object to start fight
        # click_on_target("blighted_bush")
        element_clicked=click_on_element(
        window_title="Miscrits", 
        template_folder="Elements/BlightedFlower",
        threshold=0.8,
        visualize=False,
        click_duration=0,
        y_offset=0
        )

        # click_at(1501, 845)  # Click on the Icy Crate at the specified coordinates
        


        time.sleep(7)

        # Take a screenshot for future reference
        now = datetime.now()
        filename = f"screenshots/screenshot_{now.strftime('%d-%m-%y-%H-%M')}.png"
        take_screenshot(filename)


        chance_text = capture_chance() 
        print(f"Capture Chance Text: {chance_text}")

        attack_strat(chance_text)  # Execute the attack strategy based on the chance and rarity

        time.sleep(2)  # Wait before the next iteration  
