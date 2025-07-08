import time
import datetime
from utils.checkers import check_for_quest_completion, capture_chance
from utils.interactors import click_on_element, heal
from utils.attackStrat import attack_strat
from utils.lowLevel import take_screenshot


if __name__ == "__main__":
    
    print("Starting Bot...\n")
    time.sleep(2)   

    # Define the region for screenshots (left, top, width, height)
    region = (0, 0, 2880, 1800)
    for iter in range(2000): 

        check_for_quest_completion()  


        
        # Check for quest completion and train every 10 iterations

        # if iter % 10 == 0 and iter != 0:
        #     train()  
        
        # Heal every 50 iterations
        if iter % 20 == 0 and iter != 0:
            heal()
              
        # Click on object to start fight
        # click_on_target("blighted_bush")
        element_clicked=click_on_element(
        window_title="Miscrits", 
        template_folder="Elements/WhiteClothAttic",
        threshold=0.8,
        visualize=False,
        click_duration=0,
        y_offset=0
        )

        # click_at(1501, 845)  # Click on the Icy Crate at the specified coordinates
        


        time.sleep(7)

        # Take a screenshot for future reference
        now = datetime.now()
        filename = f"screenshots/screenshot_{now.strftime('%d-%m-%y-%H-%M')}.png"
        take_screenshot(filename)


        chance_text = capture_chance() 
        print(f"Capture Chance Text: {chance_text}")

        attack_strat(chance_text)  # Execute the attack strategy based on the chance and rarity

        time.sleep(2)  # Wait before the next iteration  
