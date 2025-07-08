import os
import cv2
import numpy as np
import pyautogui
import pygetwindow as gw


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