# 🤖 Miscrits Auto-Player Bot

Welcome to the **Miscrits Auto-Player Bot**! This Python-based automation tool is designed to help you efficiently play Miscrits, level up your character and Miscrits, gather gold and potions, and capture rare and legendary Miscrits—all automatically! 🚀

---

## ✨ Features

-   **Automatic Gameplay**: Plays Miscrits for you, battling and leveling up your team.
-   **Resource Gathering**: Collects gold and potions as you play.
-   **Smart Capturing**: Employs a strategic approach to capture Miscrits based on rarity and capture chance.
-   **Elemental Search**: Choose the element you want to search for, and the bot will focus on that area by clicking on corresponding environmental objects.
-   **Legendary Hunter**: Optimized for capturing legendary Miscrits, making your collection grow faster!
-   **Automated Training**: Automatically trains your Miscrits, including applying statistical bonuses.
-   **Health and Rarity Detection**: The bot can check the health and rarity of Miscrits to make strategic decisions.
-   **Flexible Attack Strategies**: The bot uses different attack strategies based on the Miscrit's rarity and capture chance.
-   **Template Matching**: Uses image recognition to find and interact with in-game elements like buttons and items.

---

## 🛠️ Requirements

-   Python 3.7+
-   `pip` (Python package manager)
-   Run the following command to install required packages:
    ```bash
    pip install -r requirements.txt
    ```

---

## 🚀 Getting Started

1.  **Clone this repository:**
    ```bash
    git clone [[https://github.com/Vrajb24/MiscritsBot.git](https://github.com/Vrajb24/MiscritsBot.git)]
    cd miscrits-auto-player-bot
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure your settings:**
    -   The bot is configured to work with the "Miscrits" window title. Ensure your game window has this title.
    -   Place your template images for elements you want the bot to click on inside the `Elements` directory (e.g., `Elements/IcyCrate`, `Elements/SandCastle`).

4.  **Run the bot:**
    ```bash
    python Yoga_detector.py
    ```
    or
    ```bash
    python Detector.py
    ```

---

## ⚙️ Configuration

-   The main configuration for the bot, such as window title and template paths, can be found directly within the Python scripts (`Detector.py`, `Yoga_detector.py`).
-   You can adjust the `threshold` for template matching in the `click_on_element` function calls to make the image recognition more or less strict.
-   The main loop in each script can be modified to change the frequency of actions like training and healing.

---

## 📝 Notes

-   **Use responsibly!** This bot is for educational purposes. Excessive automation may violate Miscrits' terms of service.
-   **No guarantees:** Use at your own risk. The bot may require updates if the game's UI changes.
-   This bot interacts with the screen using `pyautogui` and is best suited for a desktop environment.

---

## 💡 Tips

-   Start the script while the Miscrits game window is open and visible.
-   Monitor the bot occasionally to ensure smooth operation, especially when running for the first time.
-   The bot takes screenshots of its activity, which can be found in the `screenshots` folder. This is useful for debugging.
-   Create high-quality template images for the best results with `click_on_element`.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## 📄 License

This project is licensed under the MIT License.

---

## 🏆 Happy Hunting!

Level up, gather resources, and expand your legendary collection with ease! 🌟

