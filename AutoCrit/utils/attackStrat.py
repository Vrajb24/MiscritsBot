from utils.lowLevel import capture_window, get_window_bbox, click_at, take_screenshot
from utils.checkers import rarity_check, health_check, capture_chance, check_for_rank_up
from utils.interactors import click_on_element
from utils.trainer import train
import numpy as np
from datetime import datetime
import time
from utils.detectors import detect_element


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
            for step in range(1):
                click_on_element(
                    window_title="Miscrits",
                    template_folder=f"Elements/WhiteClothAttic/Path/{step}",
                    threshold=0.8,
                    visualize=False,
                    click_duration=0,
                    y_offset=0
                )
                time.sleep(5)
            
            return
        
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

def capture_him(rarity):

    now = datetime.now()
    filename = f"captureshots/{rarity}/{rarity}_{now.strftime('%d-%m-%y-%H-%M')}.png"
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

    # time.sleep(2)

    # click_on_element(
    #     window_title="Miscrits",
    #     template_folder="Elements/NextMenuPage",
    #     threshold=0.8,
    #     visualize=False,
    #     click_duration=0,
    #     y_offset=0
    # )
    # print("next page")

    capture_attack()

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
        
        time.sleep(5)
        # Check pixel color at (773, 766)
        window_title = "Miscrits"
        frame = capture_window(window_title)
        x, y, w, h = get_window_bbox(window_title)

        # Get the pixel color at the specified coordinates
        pixel_x, pixel_y = 785, 775
        if pixel_x < frame.shape[1] and pixel_y < frame.shape[0]:
            color = frame[pixel_y, pixel_x]  # BGR format
            # Convert hex 323e4c to BGR (76, 62, 50)
            target_color = np.array([75, 62, 50])
            print(f"Pixel color at ({pixel_x},{pixel_y}): {color}")
            # Visualize the pixel location
            # vis_frame = frame.copy()
            # cv2.circle(vis_frame, (pixel_x, pixel_y), 10, (0, 0, 255), -1)  # Red circle at the pixel position
            # cv2.imshow("Pixel Location", vis_frame)
            # cv2.waitKey(0)  # Wait until a key is pressed (window stays open until manually closed)
            # cv2.destroyAllWindows()
            # Check if color matches with small tolerance
            if np.all(np.abs(color - target_color) < 10):
                print("Needs Healing")
                NeedHeal = True
            else:
                print("No Healing Needed")
                NeedHeal = False

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

        if NeedHeal:
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
        attack(1)
        capture_attack()

