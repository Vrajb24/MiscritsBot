import pyautogui
import pygetwindow as gw
import os
import time
import cv2
import numpy as np
from PIL import Image, ImageDraw
from utils.lowLevel import capture_window, get_window_bbox, click_at

import os
import cv2
import numpy as np
import pygetwindow as gw
import pyautogui
from PIL import Image

def click_on_element(window_title, template_folder, threshold=0.8, visualize=False, click_duration=0, y_offset=10):
    """
    Locates and clicks on an element in the specified window using SIFT+FLANN feature matching.
    
    Args:
        window_title (str): Title of the window to search in
        template_folder (str): Path to folder containing template images
        threshold (float): Lowe's ratio test threshold (0.0-1.0)
        visualize (bool): Whether to show matched keypoints visualization
        click_duration (float): How long to hold the click (in seconds)
        y_offset (int): Vertical offset to apply to the click position
        
    Returns:
        bool: True if element was found and clicked, False otherwise
    """
    # Configuration
    GAMMA_CORRECTION = 1.2
    MIN_MATCH_COUNT = 10
    # Initialize SIFT and FLANN
    sift = cv2.SIFT_create()
    flann = cv2.FlannBasedMatcher(
        dict(algorithm=cv2.FLANN_INDEX_KDTREE, trees=5),
        dict()
    )

    def apply_gamma_correction(img, gamma=GAMMA_CORRECTION):
        invGamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** invGamma) * 255 for i in range(256)], dtype="uint8")
        return cv2.LUT(img, table)

    def preprocess_image(bgr):
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)
        if GAMMA_CORRECTION:
            gray = apply_gamma_correction(gray)
        return gray

    def normalize_descriptors(des):
        # RootSIFT normalization
        des = des.astype("float32")
        des /= (np.linalg.norm(des, axis=1, keepdims=True) + 1e-7)
        return np.sqrt(des)

    def match_and_locate(template_gray, screen_gray, screen_bgr):
        # Detect and describe
        kp1, des1 = sift.detectAndCompute(template_gray, None)
        kp2, des2 = sift.detectAndCompute(screen_gray, None)
        if des1 is None or des2 is None:
            return False, None, None

        des1 = normalize_descriptors(des1)
        des2 = normalize_descriptors(des2)
        matches = flann.knnMatch(des1, des2, k=2)

        # Lowe's ratio test
        good = [m for m, n in matches if m.distance < threshold * n.distance]
        if len(good) < MIN_MATCH_COUNT:
            return False, None, None

        # Compute homography to find object location
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        h, w = template_gray.shape

        if M is not None:
            # Map template corners to screen
            corners = np.float32([[0,0],[0,h-1],[w-1,h-1],[w-1,0]]).reshape(-1,1,2)
            projected = cv2.perspectiveTransform(corners, M).reshape(4,2)
            # bounding rectangle
            x, y, w_box, h_box = cv2.boundingRect(projected)
            # draw matches if requested
            match_img = None
            if visualize:
                match_img = cv2.drawMatches(
                    template_gray, kp1, screen_bgr, kp2, good, None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS
                )
            return True, (x, y, w_box, h_box), match_img

        return False, None, None

    # 1) Find the window
    win = next((w for w in gw.getWindowsWithTitle(window_title) if w.visible), None)
    if not win:
        print(f"Window '{window_title}' not found or not visible.")
        return False

    left, top, width, height = win.left, win.top, win.width, win.height

    # 2) Capture window region
    screenshot = pyautogui.screenshot(region=(left, top, width, height))
    screen_bgr = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    screen_gray = preprocess_image(screen_bgr)

    # 3) Iterate templates
    for fname in os.listdir(template_folder):
        if not fname.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            continue
        path = os.path.join(template_folder, fname)
        tpl_bgr = cv2.imread(path, cv2.IMREAD_COLOR)
        if tpl_bgr is None:
            print(f"Warning: could not load template '{fname}'")
            continue

        tpl_gray = preprocess_image(tpl_bgr)
        found, box, match_vis = match_and_locate(tpl_gray, screen_gray, screen_bgr)
        if found:
            print(f"[✔] Matched template '{fname}'")
            if visualize and match_vis is not None:
                cv2.imshow("Feature Matches", match_vis)
                cv2.waitKey(0)
                cv2.destroyAllWindows()

            # 4) Click the center of the detected bounding box
            x, y, w_box, h_box = box
            center_x = left + x + w_box // 2
            center_y = top + y + h_box // 2 + y_offset
            pyautogui.mouseDown(center_x, center_y)
            pyautogui.sleep(click_duration)
            pyautogui.mouseUp(center_x, center_y)
            return True

    print("[✘] No element found in window.")
    return False



    

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
# =====================================================
# =                 DEPRECATED CODE                   =
# =====================================================

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

# def click_on_element(window_title, template_folder, threshold=0.8, visualize=False, click_duration=0, y_offset=10):
#     """
#     Locates and clicks on an element in the specified window using template matching.
    
#     Args:
#         window_title (str): Title of the window to search in
#         template_folder (str): Path to folder containing template images
#         threshold (float): Matching threshold (0.0-1.0)
#         visualize (bool): Whether to show visualization of matches
#         click_duration (float): How long to hold the click
#         y_offset (int): Y-offset for click position
        
#     Returns:
#         bool: True if element was found and clicked, False otherwise
#     """
    
#     # Get window info
#     win = None
#     for w in gw.getWindowsWithTitle(window_title):
#         if w.visible:
#             win = w
#             break
    
#     if not win:
#         print(f"Window '{window_title}' not found or not visible.")
#         return False

#     # Get window position and size
#     left, top, width, height = win.left, win.top, win.width, win.height
    
#     # Screenshot only the window region
#     screenshot = pyautogui.screenshot(region=(left, top, width, height))
#     screenshot_array = np.array(screenshot)
#     screenshot_cv = cv2.cvtColor(screenshot_array, cv2.COLOR_RGB2BGR)
    
#     all_boxes = []
    
#     # Get all image files from the template folder
#     image_extensions = ['.png', '.jpg', '.jpeg', '.bmp']
#     template_paths = []
    
#     try:
#         for file in os.listdir(template_folder):
#             if any(file.lower().endswith(ext) for ext in image_extensions):
#                 template_paths.append(os.path.join(template_folder, file))
        
#         print(f"Found {len(template_paths)} template images in folder {template_folder}")
#     except Exception as e:
#         print(f"Error reading template folder {template_folder}: {e}")
#         return False
    
#     if not template_paths:
#         print(f"No image templates found in folder {template_folder}")
#         return False
    
#     # Process each template
#     for template_path in template_paths:
#         try:
#             # Load template
#             template = cv2.imread(template_path, cv2.IMREAD_COLOR)
#             if template is None:
#                 print(f"Warning: Failed to load template {template_path}")
#                 continue
                
#             h, w, _ = template.shape

#             # Template matching
#             result = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
#             loc = np.where(result >= threshold)

#             # Get boxes for this template
#             template_boxes = []
#             for pt in zip(*loc[::-1]):
#                 # Adjust coordinates relative to entire screen
#                 abs_pt = (pt[0] + left, pt[1] + top)
#                 template_boxes.append((abs_pt[0], abs_pt[1], abs_pt[0] + w, abs_pt[1] + h))
            
#             # Add template path info to each box
#             for box in template_boxes:
#                 all_boxes.append((box, template_path))
            
#             print(f"Found {len(template_boxes)} matches for template {os.path.basename(template_path)}")
            
#         except Exception as e:
#             print(f"Error processing template {template_path}: {e}")
    
#     # Visualize the detection
#     if visualize and all_boxes:
#         # Create a copy of the screenshot for visualization
#         vis_img = Image.fromarray(screenshot_array)
#         draw = ImageDraw.Draw(vis_img)
        
#         # Draw boxes on the image (using local coordinates)
#         for box, template_path in all_boxes:
#             # Convert to local coordinates for drawing
#             local_box = (box[0] - left, box[1] - top, box[2] - left, box[3] - top)
#             draw.rectangle(local_box, outline='red', width=2)
        
#         # Display the image
#         vis_img.show()

#     if all_boxes:
#         print(f"Found {len(all_boxes)} matches in total")
#         # Click on the first match (box is at index 0 of the tuple)
#         box = all_boxes[0][0]
#         x1, y1, x2, y2 = box
#         center_x = x1 + (x2 - x1) // 2
#         center_y = y1 + (y2 - y1) // 2 + y_offset
#         pyautogui.mouseDown(center_x, center_y)
#         pyautogui.sleep(click_duration)
#         pyautogui.mouseUp(center_x, center_y)
#         return True
#     else:
#         print("No elements found in window.")
#         return False
    