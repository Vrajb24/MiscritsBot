import time
from utils.interactors import click_on_element
from utils.checkers import check_for_rank_up
from utils.lowLevel import get_window_bbox, click_at, capture_window

def train():
    print("Starting training process...")

    click_on_element(
        window_title="Miscrits", 
        template_folder="Elements/TrainButton",
        threshold=0.8,
        visualize=False,
        click_duration=0,
        y_offset=0
    )

    time.sleep(3)

    train_individual(1, False)
    time.sleep(1)
    train_individual(2, False)   
    time.sleep(1)
    train_individual(3, False)
    time.sleep(1)
    train_individual(4, False)
    time.sleep(1)

    click_on_element(
        window_title="Miscrits", 
        template_folder="Elements/CloseButton",
        threshold=0.8,
        visualize=False,
        click_duration=0,
        y_offset=0
    )

    # click_x = x + 995
    # click_y = y + 60
    # click_at(click_x, click_y)
    
    time.sleep(3)
    # Check for rank up notification
    check_for_rank_up()

def train_individual(miscrit_no, bonus):
    window_title = "Miscrits"
    print(f"Training Miscrit {miscrit_no} with bonus: {bonus}")
    x, y, w, h = get_window_bbox(window_title)
    click_x = x + 650
    if miscrit_no == 1:
        click_y = y + 395
    elif miscrit_no == 2:
        click_y = y + 515
    elif miscrit_no == 3:
        click_y = y + 635
    elif miscrit_no == 4:
        click_y = y + 755
    else:
        raise ValueError("miscrit_no must be 1, 2, 3, or 4")
    click_at(click_x, click_y)

    time.sleep(3)

    window_title = "Miscrits"
    frame = capture_window(window_title)
    x, y, w, h = get_window_bbox(window_title)

    Trained=click_on_element(
        window_title="Miscrits",
        template_folder="Elements/TrainNowButton",
        threshold=0.8,
        visualize=False,
        click_duration=0,
        y_offset=0
        )
    
    if not Trained:
        print("Miscrit:", miscrit_no, "Not ready for training")
        return
    else:
        print("Miscrit:", miscrit_no, "Crit training")

    time.sleep(3)

    if bonus:
        
        click_on_element(
            window_title="Miscrits",
            template_folder="Elements/StatsList",
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        
)
        time.sleep(2)

        click_on_element(
            window_title="Miscrits",
            template_folder="Elements/StatBonus",
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )

        time.sleep(3)

        click_on_element(
            window_title="Miscrits",
            template_folder="Elements/ContinueButton", 
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )
        

    else:

        click_on_element(
            window_title="Miscrits",
            template_folder="Elements/ContinueButton", 
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )

    time.sleep(3)
    okayed=click_on_element(
        window_title="Miscrits",
        template_folder="Elements/OkayButton",
        threshold=0.8,
        visualize=False,
        click_duration=0,
        y_offset=0
    )
    if okayed:
        print("Clicked on Okay button after Evolve")
        

    time.sleep(7)



    Enchanted=click_on_element(
        window_title="Miscrits",
        template_folder="Elements/EnchantAbility",
        threshold=0.8,
        visualize=False,
        click_duration=0,
        y_offset=0
    )

    if Enchanted:
        print("Enchanted ability detected, clicking to enchant")
        # Click at the center of the window to proceed with enchanting
        click_x = x + w // 2
        click_y = y + h // 2
        click_at(click_x, click_y)
        time.sleep(0.25)

        click_on_element(
            window_title="Miscrits",
            template_folder="Elements/GoldToEnchantAbility",
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )
        time.sleep(3)
        click_on_element(
            window_title="Miscrits",
            template_folder="Elements/ContinueButton",
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )
    time.sleep(3)
    Evolved=click_on_element(
        window_title="Miscrits",
        template_folder="Elements/EvolveDiag",
        threshold=0.8,
        visualize=False,
        click_duration=0,
        y_offset=0
    )

    if Evolved:
        print("Evolved ability detected, clicking okay")
        time.sleep(2)
        click_on_element(
            window_title="Miscrits",
            template_folder="Elements/OkayButton",
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )

    time.sleep(3)

    check_for_rank_up()