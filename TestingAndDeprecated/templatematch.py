import cv2
import numpy as np
import os
from PIL import ImageGrab

# ==== CONFIG ====
TEMPLATE_FOLDER = "templates"
MIN_MATCH_COUNT = 10
GAMMA_CORRECTION = 1.2  # Set to None to disable
SHOW_MATCHES = True


# ==== PREPROCESSING ====

def preprocess_image(img_bgr):
    """ Convert to gray, apply CLAHE, and gamma correction """
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # CLAHE: Adaptive Histogram Equalization
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # Optional gamma correction
    if GAMMA_CORRECTION:
        gray = apply_gamma_correction(gray, gamma=GAMMA_CORRECTION)

    return gray


def apply_gamma_correction(image, gamma=1.5):
    """ Adjust brightness non-linearly """
    invGamma = 1.0 / gamma
    table = np.array([
        ((i / 255.0) ** invGamma) * 255 for i in range(256)
    ]).astype("uint8")
    return cv2.LUT(image, table)


def normalize_descriptors(des):
    """ RootSIFT normalization for brightness resilience """
    des /= (np.linalg.norm(des, axis=1, keepdims=True) + 1e-7)
    return np.sqrt(des)


# ==== SIFT + FLANN SETUP ====
sift = cv2.SIFT_create()
FLANN_INDEX_KDTREE = 1
flann = cv2.FlannBasedMatcher(dict(algorithm=FLANN_INDEX_KDTREE, trees=5), dict())


# ==== SCREEN CAPTURE ====
def capture_screen():
    screenshot = ImageGrab.grab()
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)


# ==== MATCHING LOGIC ====
def match_template(template_img_gray, screen_gray, screen_color, min_matches=MIN_MATCH_COUNT):
    # Keypoints and descriptors
    kp1, des1 = sift.detectAndCompute(template_img_gray, None)
    kp2, des2 = sift.detectAndCompute(screen_gray, None)

    if des1 is None or des2 is None:
        return False, None

    # RootSIFT descriptor normalization
    des1 = normalize_descriptors(des1)
    des2 = normalize_descriptors(des2)

    matches = flann.knnMatch(des1, des2, k=2)

    # Apply Lowe's ratio test
    good = [m for m, n in matches if m.distance < 0.7 * n.distance]

    if len(good) >= min_matches:
        result_img = cv2.drawMatches(template_img_gray, kp1, screen_color, kp2, good, None, flags=2)
        return True, result_img
    return False, None


# ==== TEMPLATE SCANNING ====
def match_any_template(template_folder=TEMPLATE_FOLDER):
    screen_bgr = capture_screen()
    screen_gray = preprocess_image(screen_bgr)

    for fname in os.listdir(template_folder):
        if not fname.lower().endswith(('.png', '.jpg', '.jpeg')):
            continue

        path = os.path.join(template_folder, fname)
        template_bgr = cv2.imread(path, cv2.IMREAD_COLOR)
        if template_bgr is None:
            print(f"Could not read {fname}")
            continue

        template_gray = preprocess_image(template_bgr)

        matched, match_img = match_template(template_gray, screen_gray, screen_bgr)

        if matched:
            print(f"[✔] Match found: {fname}")
            if SHOW_MATCHES:
                cv2.imshow("Matched Keypoints", match_img)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
            return True

    print("[✘] No matches found.")
    return False


# ==== MAIN ====
if __name__ == "__main__":
    match_any_template(template_folder="Elements/OkayButton")
