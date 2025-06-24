import pygetwindow as gw
import pyautogui
import keyboard
import time

def main():
    window_title = input("Enter the exact window title: ")
    try:
        window = gw.getWindowsWithTitle(window_title)[0]
    except IndexError:
        print("Window not found!")
        return

    count = 1
    print("Press 'q' to take a screenshot of the window. Press 'esc' to exit.")
    while True:
        if keyboard.is_pressed('q'):
            # Bring window to front
            window.activate()
            time.sleep(0.2)  # Wait for window to come to front
            left, top, width, height = window.left, window.top, window.width, window.height
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            filename = f"screenshot_{count}.png"
            screenshot.save(filename)
            print(f"Screenshot saved as {filename}")
            count += 1
            time.sleep(0.5)  # Prevent multiple screenshots per press
        if keyboard.is_pressed('esc'):
            print("Exiting.")
            break

if __name__ == "__main__":
    main()