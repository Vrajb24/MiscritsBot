import time
from datetime import datetime
from utils.checkers import check_for_quest_completion, capture_chance
from utils.interactors import click_on_element, heal
from utils.attackStrat import attack_strat
from utils.lowLevel import take_screenshot
import config

if __name__ == "__main__":
    print("Starting Bot...\n")
    time.sleep(2)   

    # Main bot loop
    for iter in range(config.LOOP_ITERATIONS): 
        check_for_quest_completion()  
        
        # Periodic healing
        if iter % 20 == 0 and iter != 0:
            heal()
              
        # Start fight by clicking on element
        element_clicked = click_on_element(
            window_title="Miscrits", 
            template_folder=config.TEMPLATES["icy_crate"],
            threshold=0.8,
            visualize=False,
            click_duration=0,
            y_offset=0
        )

        time.sleep(7)

        # Record encounter
        now = datetime.now()
        filename = f"screenshots/screenshot_{now.strftime('%d-%m-%y-%H-%M')}.png"
        take_screenshot(filename)

        # Execute combat sequence
        chance_text = capture_chance() 
        print(f"Capture Chance Text: {chance_text}")
        attack_strat(chance_text)

        time.sleep(2)
