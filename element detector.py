import pyautogui
import cv2
import numpy as np
import pygetwindow as gw
import time
from PIL import Image, ImageDraw



def click_on_element(window_title, template_paths, threshold=0.8, visualize=False, click_duration=0, y_offset=10):
    """
    Locates and clicks on an element in the specified window using template matching.
    
    Args:
        window_title (str): Title of the window to search in
        template_paths (list): List of image template paths to match
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
            
            print(f"Found {len(template_boxes)} matches for template {template_path}")
            
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

# Example usage:
time.sleep(2)  # Wait for the window to be ready
click_on_element(
    window_title="Miscrits", 
    template_paths=[r'C:\Users\rocke\Desktop\Miscritsbot\Elements\NextMenuPage\Screenshot 2025-06-27 205732.png']
)
