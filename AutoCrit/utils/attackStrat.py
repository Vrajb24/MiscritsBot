from utils.lowLevel import capture_window, get_window_bbox, click_at, take_screenshot
from utils.checkers import rarity_check, health_check, capture_chance, check_for_rank_up
from utils.interactors import click_on_element
from utils.trainer import train
import numpy as np
from datetime import datetime
import time
from utils.detectors import detect_element
import config

#############################################
# ATTACK FUNCTIONS
#############################################

def attack(number):
    # Get window details
    window_title = "Miscrits"
    frame = capture_window(window_title)
    x, y, w, h = get_window_bbox(window_title)
    
    # Calculate center and relative positions
    horizontal_center = x + (w // 2)
    bottom = y + h
    
    # Calculate click positions based on the attack number
    if number == 3:
        click_x = horizontal_center + (w // 12)
    elif number == 2:
        click_x = horizontal_center - (w // 12)
    elif number == 4:
        click_x = horizontal_center + (w // 6) + (w // 12)
    elif number == 1:
        click_x = horizontal_center - (w // 6) - (w // 12)
    else:
        print(f"Invalid attack number: {number}")
        return
    
    # Calculate vertical position
    click_y = bottom - (h // 10)
    
    # Execute the click
    click_at(click_x, click_y)
    print(f"Attack {number} executed at ({click_x}, {click_y})")
    
#############################################
# ATTACK STRATEGY
#############################################

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
            template_folder=config.TEMPLATES["continue_button"],
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )

        # Sleep: 2 seconds ====================================================================================
        time.sleep(2) 

        click_on_element(
            window_title="Miscrits",
            template_folder=config.TEMPLATES["okay_button"],
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )

        # Sleep: 2 seconds ====================================================================================
        time.sleep(2)

        click_on_element(
            window_title="Miscrits",
            template_folder=config.TEMPLATES["yes_button"],
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )

        # Sleep: 2 seconds ====================================================================================
        time.sleep(2)

        Retry = click_on_element(
            window_title="Miscrits",
            template_folder=config.TEMPLATES["retry_button"],
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )

        if Retry:
            # Sleep: 10 seconds ===============================================================================
            time.sleep(10)

            Retry = click_on_element(
            window_title="Miscrits",
            template_folder=config.TEMPLATES["retry_button"],
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )

        if Retry:
            # Sleep: 10 seconds ===============================================================================
            time.sleep(10)   

        Account = click_on_element(
            window_title="Miscrits",
            template_folder=config.TEMPLATES["account_button"],
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )

        if Account or Retry:
            # Sleep: 15 seconds ===============================================================================
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
                # Sleep: 5 seconds ============================================================================
                time.sleep(5)
            
            return
        
#############################################
# COMBAT FUNCTIONS
#############################################

def finish_him():
    attack(1)  # Call the attack function with number 1
    
    # Sleep: 5 seconds ========================================================================================
    time.sleep(5)

    ReadyToTrain = detect_element(
        window_title="Miscrits",
        template_folder=config.TEMPLATES["ready_to_train"],
        threshold=0.8,
        visualize=False
    )

    
    FightEnded = click_on_element(
        window_title="Miscrits",
        template_folder=config.TEMPLATES["continue_button"],
        threshold=0.8,
        visualize=False,
        click_duration=0,
        y_offset=0
    )
    
    # Sleep: 3 seconds ========================================================================================
    time.sleep(3)

    if FightEnded:
        print("Clicked on Continue button after fight ended")
        if ReadyToTrain:
            print("Ready to train detected, clicking on Train button")
            train()
        return True
    else:
        finish_him()

#############################################
# CAPTURE FUNCTIONS
#############################################

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

    if config.CAPTURE_STRAT == 1:
        click_on_element(
            window_title="Miscrits",
            template_folder=config.TEMPLATES["next_menu_page"],
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )
        print("next page")

        time.sleep(2)

        click_on_element(
            window_title="Miscrits",
            template_folder=config.TEMPLATES["next_menu_page"],
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )
        print("next page again")

    elif config.CAPTURE_STRAT == 2:
        click_on_element(
            window_title="Miscrits",
            template_folder=config.TEMPLATES["next_menu_page"],
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )
        print("next page (single click)")

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
        # Sleep: 4 seconds ====================================================================================
        time.sleep(4)
        

        captured=click_on_element(
            window_title="Miscrits",
            template_folder=config.TEMPLATES["capture_button"],
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )
        if captured:
            print("Clicked on Capture button")

        # Sleep: 10 seconds ====================================================================================
        time.sleep(10)

        Okayed=click_on_element(
            window_title="Miscrits",   
            template_folder=config.TEMPLATES["okay_button"],
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )
        if Okayed:
            print("Clicked on Okay button after capture")

        else:

            if config.CAPTURE_STRAT == 1:
                click_on_element(
                    window_title="Miscrits",
                    template_folder=config.TEMPLATES["prev_menu_page"],
                    threshold=0.8,
                    visualize=False,
                    click_duration=0,
                    y_offset=0
                )

                # Sleep: 1 second
                time.sleep(1)

                click_on_element(
                    window_title="Miscrits",
                    template_folder=config.TEMPLATES["prev_menu_page"],
                    threshold=0.8,
                    visualize=False,
                    click_duration=0,
                    y_offset=0
                )
            elif config.CAPTURE_STRAT == 2:
                click_on_element(
                    window_title="Miscrits",
                    template_folder=config.TEMPLATES["prev_menu_page"],
                    threshold=0.8,
                    visualize=False,
                    click_duration=0,
                    y_offset=0
                )

            finish_him()
            return
        
        # Sleep: 5 seconds ====================================================================================
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

        # Sleep: 5 seconds ==================================================================================== 
        time.sleep(5)
        
        continued=click_on_element(
            window_title="Miscrits", 
            template_folder=config.TEMPLATES["continue_button"],  
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )

        if continued:
            print("Clicked on Continue button after capture")

        # Sleep: 3 seconds ====================================================================================
        time.sleep(3)

        Okayed = click_on_element(
            window_title="Miscrits",
            template_folder=config.TEMPLATES["okay_button"],
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )
        if Okayed:
            print("Clicked on Okay button on rankup")

        # Sleep: 3 seconds ====================================================================================
        time.sleep(3)

        Okayed = click_on_element(
            window_title="Miscrits",
            template_folder=config.TEMPLATES["okay_button"],
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )
        if Okayed:
            print("Clicked on Okay button on Qest completion")

        # Sleep: 3 seconds ====================================================================================
        time.sleep(3)

        kept = click_on_element(
            window_title="Miscrits",
            template_folder=config.TEMPLATES["keep_button"],
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )
        if kept:    
            print("Clicked on Keep button after capture")

        # Sleep: 3 seconds ====================================================================================
        time.sleep(3)

        if NeedHeal:
            healed = click_on_element(
                window_title="Miscrits",
                template_folder=config.TEMPLATES["heal_now_button"],
                threshold=0.8,
                visualize=False,
                click_duration=0,
                y_offset=0
            )
            if healed:
                print("Clicked on Heal button after capture")
                # Sleep: 2 seconds =============================================================================
                click_on_element(
                    window_title="Miscrits",
                    template_folder=config.TEMPLATES["yes_button"],
                    threshold=0.8,
                    visualize=False,
                    click_duration=0,
                    y_offset=0
                )

    else:
        if config.CAPTURE_STRAT == 1:
            attack(1)
        elif config.CAPTURE_STRAT == 2:
            attack(2)

        capture_attack()
