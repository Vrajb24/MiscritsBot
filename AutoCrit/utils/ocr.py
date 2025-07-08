#  ── module-level one-time import / EasyOCR initialisation ────────────
import easyocr
reader = easyocr.Reader(['en'], gpu=False)
from utils.lowLevel import capture_window, get_window_bbox

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