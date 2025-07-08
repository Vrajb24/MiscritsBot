# ─── imports ─────────────────────────────────────────────────────────
import cv2, pyautogui, numpy as np, pygetwindow as gw, re, os
from ctypes import windll
import win32gui
from paddleocr import PaddleOCR

# ─── one-time OCR object ─────────────────────────────────────────────
# simplest: English model, all default settings
paddle_reader = PaddleOCR(lang="en", show_log=False)

# # OPTIONAL – use a custom 0-9 + “/” alphabet for even better speed/accuracy
# dict_path = os.path.join(os.path.dirname(__file__), "digit_slash_dict.txt")
# paddle_reader = PaddleOCR(lang="custom",
#                           rec_char_dict_path=dict_path,
#                           show_log=False)

# ─── helper: locate game window ──────────────────────────────────────
def get_window_bbox(window_title: str):
    win = next((w for w in gw.getAllWindows()
                if window_title.lower() in w.title.lower()), None)
    if not win:
        raise RuntimeError(f"Window '{window_title}' not found.")
    if win.isMinimized:
        raise RuntimeError("Window is minimized; restore it first.")
    return win.left, win.top, win.width, win.height


def capture_window(window_title: str):
    x, y, w, h = get_window_bbox(window_title)
    img = pyautogui.screenshot(region=(x, y, w, h))
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


# ─── HP-specific OCR using PaddleOCR 3.x ─────────────────────────────
def box_ocr_hp(x_rel: int, y_rel: int, box_w: int, box_h: int,
               visualize: bool = False, purpose: str = "HP") -> str:
    """
    Read Miscrits HP widgets like 30/120, 99/99, etc.

    Parameters
    ----------
    x_rel, y_rel : int   – ROI top-left inside the window (logical px)
    box_w, box_h : int   – ROI size (px)
    visualize     : bool – show debug windows if True
    purpose       : str  – label printed to console

    Returns
    -------
    str  – recognised text, e.g. "84/92"
    """
    game_title = "Miscrits"
    print(f"[box_ocr_hp] ({x_rel}, {y_rel}, {box_w}, {box_h}) – {purpose}")

    # 1. DPI-aware absolute coords
    xw, yw, _, _ = get_window_bbox(game_title)
    try:
        dpi   = windll.user32.GetDpiForWindow(
                    win32gui.FindWindow(None, game_title))
        scale = dpi / 96
    except Exception:
        scale = 1

    bx, by = int(xw + x_rel * scale), int(yw + y_rel * scale)
    bw, bh = int(box_w * scale), int(box_h * scale)

    # 2. crop ROI ➔ upscale ×4 so tiny glyphs are crisp
    snap = pyautogui.screenshot(region=(bx, by, bw, bh))
    img  = cv2.cvtColor(np.array(snap), cv2.COLOR_RGB2BGR)
    img  = cv2.resize(img, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)

    # 3. OCR – v3.x API: no det/rec/cls kwargs anymore
    paddle_out = paddle_reader.ocr(img, cls=False)   # only angle-cls flag allowed

    # flatten result → one string
    raw = "".join(word[1][0] for line in paddle_out for word in line).strip()

    # 4. Post-clean (same three heuristics)
    raw = re.sub(r"[^0-9/7]", "", raw)                        # keep only expected glyphs
    if "/" not in raw and raw.count("7") == 1:                # lone '7' → slash
        raw = raw.replace("7", "/")
    if "/" not in raw and raw.isdigit() and len(raw) % 2 == 0:  # 9999 → 99/99
        half = len(raw) // 2
        raw  = f"{raw[:half]}/{raw[half:]}"
    if "/" in raw:                                            # HP must ≤ MaxHP
        left, right = raw.split("/", 1)
        if left.isdigit() and right.isdigit():
            while len(left) > 1 and int(left) > int(right):
                left = left[:-1]
            raw = f"{left}/{right}"

    print("► HP-OCR:", raw)

    # 5. Debug windows
    if visualize:
        frame = capture_window(game_title)
        cv2.rectangle(frame, (bx - xw, by - yw),
                      (bx - xw + bw, by - yw + bh), (0, 255, 0), 1)
        cv2.imshow("HP ROI (window)", frame)
        cv2.imshow("Upscaled crop", img)
        cv2.waitKey(0); cv2.destroyAllWindows()

    return raw


# ─── quick manual test ───────────────────────────────────────────────
if __name__ == "__main__":
    txt = box_ocr_hp(977, 79, 70, 30, visualize=False, purpose="Capture Chance")
    cur, max_ = map(int, txt.split("/"))
    print(f"Parsed → {cur}/{max_}")
