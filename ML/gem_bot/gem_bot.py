#need to add logic to send march to nodes
import threading
import pyautogui
import keyboard
from PIL import Image
from ultralytics import YOLO
import pydirectinput
import time 
import random

def run_bot(decision):
    # Should we use lightning/met?
    distance_target = 1000
    min_delay = 1  # Minimum delay in seconds
    max_delay = 5  # Maximum delay in seconds

    if "food_sky_location" in decision:
        random_delay = random.uniform(min_delay, max_delay)  # Generate a random float between min_delay and max_delay
        time.sleep(random_delay)
        pyautogui.click(decision["food_sky_location"])
        print("zomming in food")
        if decision["food_zoomed"]:
            random_delay = random.uniform(min_delay, max_delay)  # Generate a random float between min_delay and max_delay
            time.sleep(random_delay)
            pyautogui.click(decision["food_location"])
            print("sending march to food")
            #still need to add logic to send march to food 
            
    elif "wood_sky_location" in decision:
        random_delay = random.uniform(min_delay, max_delay)  # Generate a random float between min_delay and max_delay
        time.sleep(random_delay)
        pyautogui.click(decision["wood_sky_location"])
        print("zomming in wood")
        if decision["wood_zoomed"]:
            random_delay = random.uniform(min_delay, max_delay)  # Generate a random float between min_delay and max_delay
            time.sleep(random_delay)    
            pyautogui.click(decision["wood_location"])
            print("sending march to wood")
            
            
    elif "stone_sky_location" in decision:
        random_delay = random.uniform(min_delay, max_delay)  # Generate a random float between min_delay and max_delay
        time.sleep(random_delay)
        pyautogui.click(decision["stone_sky_location"])
        print("zomming in stone")
        if decision["stone_zoomed"]:
            random_delay = random.uniform(min_delay, max_delay)
            time.sleep(random_delay)   
            pyautogui.click(decision["stone_location"])
            print("sending march to stone")
            
            
    elif "gold_sky_location" in decision:
        random_delay = random.uniform(min_delay, max_delay)  # Generate a random float between min_delay and max_delay
        time.sleep(random_delay)
        pyautogui.click(decision["gold_sky_location"])
        print("zomming in gold")
        if decision["gold_zoomed"]:
            random_delay = random.uniform(min_delay, max_delay)  # Generate a random float between min_delay and max_delay
            time.sleep(random_delay)    
            pyautogui.click(decision["gold_location"])
            print("sending march to gold")
        # still need to add logic to send march to gold
        
    elif "gem_sky_location" in decision:
        random_delay = random.uniform(min_delay, max_delay)  # Generate a random float between min_delay and max_delay
        time.sleep(random_delay)
        pyautogui.click(decision["gem_sky_location"])
        print("zomming in gem")
        if decision["gem_zoomed"]:
            random_delay = random.uniform(min_delay, max_delay)
            time.sleep(random_delay)
            pyautogui.click(decision["gem_location"])
            print("sending march to gem")
            # still need to add logic to send march to gem
            
    """else:
        if decision["tree"] and decision["building"]:
            if decision["tree_distance"] + 300 < decision["building_distance"]:
                pyautogui.moveTo(decision["tree_location"])
                distance_target = decision["tree_distance"]
                print("Going to Tree: ", decision["tree_location"])
            else:
                pyautogui.moveTo(decision["building_location"])
                distance_target = decision["building_distance"]
                print("Going to Building: ", decision["building_location"])
        elif decision["tree"]:
            pyautogui.moveTo(decision["tree_location"])
            distance_target = decision["tree_distance"]
            print("Going to Tree: ", decision["tree_location"])
        elif decision["building"]:
            pyautogui.moveTo(decision["building_location"])
            distance_target = decision["building_distance"]
            print("Going to Building: ", decision["building_location"])
    if distance_target < 300:
        pydirectinput.press('1')
        pydirectinput.press('2')"""

# Function to take screenshots
def take_screenshot(stop_event, model):
    screenx_center = 3840/2
    screeny_center = 2160/2
    pyautogui.FAILSAFE = False

    while not stop_event.is_set():

        decision = {
            "barb_sky": False,
            "wood_sky": False,
            "food_sky": False,
            "gold_sky": False,
            "gem_sky": False,
            "stone_sky": False,
            "barb_zoomed": False,
            "wood_zoomed": False,
            "food_zoomed": False,
            "gold_zoomed": False,
            "gem_zoomed": False,
            "stone_zoomed": False,
        }

        # Take screenshot
        screenshot = pyautogui.screenshot()
        screenshot = Image.frombytes('RGB', screenshot.size, screenshot.tobytes())
        
        results = model([screenshot], conf=.70)  # return a list of Results objects
        boxes = results[0].boxes.xyxy.tolist()
        classes = results[0].boxes.cls.tolist()
        names = results[0].names
        confidences = results[0].boxes.conf.tolist()

        # Process results list
        for box, cls, conf in zip(boxes, classes, confidences):
            x1, y1, x2, y2 = box
            
            center_x = (x1+x2) / 2
            center_y = (y1+y2) / 2

            name = names[int(cls)]
            
            if name=="food_sky":
                decision["food_sky"] = True
                decision["food_sky_location"] = (center_x, center_y)
            if name == "wood_sky":
                decision["wood_sky"] = True
                decision["wood_sky_location"] = (center_x, center_y)
            elif name == "stone_sky":
                decision["stone_sky"] = True
                decision["stone_sky_location"] = (center_x, center_y)
            elif name == "gold_sky":
                decision["gold_sky"] = True
                decision["gold_sky_location"] = (center_x, center_y)
            elif name == "gem_sky":
                decision["gem_sky"] = True
                decision["gem_sky_location"] = (center_x, center_y)
            elif name == "barb_sky":
                decision["barb_sky"] = True
                decision["barb_sky_location"] = (center_x, center_y)
                """distance = ((center_x - screenx_center) ** 2 + (center_y - screeny_center) **2) **.5
                if "barb_sky_location" in decision:
                    # Calculate if closer
                    if distance < decision["tree_distance"]:
                        decision["tree_location"] = (center_x, center_y)
                        decision["tree_distance"] = distance
                else:
                    decision["tree_location"] = (center_x, center_y)
                    decision["tree_distance"] = distance
            elif name == "building":
                decision["building"] = True
                distance = ((center_x - screenx_center) ** 2 + (center_y - screeny_center) **2) **.5
                if "building_location" in decision:
                    # Calculate if closer
                    if distance < decision["building_distance"]:
                        decision["building_location"] = (center_x, center_y)
                        decision["building_distance"] = distance
                else:
                    decision["building_location"] = (center_x, center_y)
                    decision["building_distance"] = distance
            elif name == "fuel":
                decision["fuel"] = True
                distance = ((center_x - screenx_center) ** 2 + (center_y - screeny_center) **2) **.5
                if "fuel_location" in decision:
                    # Calculate if closer
                    if distance < decision["fuel_distance"]:
                        decision["fuel_location"] = (center_x, center_y)
                        decision["fuel_distance"] = distance
                else:
                    decision["fuel_location"] = (center_x, center_y)
                    decision["fuel_distance"] = distance"""
        
        run_bot(decision)
        

# Main function
def main():
    print(pyautogui.KEYBOARD_KEYS)
    model = YOLO('best2.pt')
    stop_event = threading.Event()
    
    # Create and start the screenshot thread
    screenshot_thread = threading.Thread(target=take_screenshot, args=(stop_event, model))
    screenshot_thread.start()

    # Listen for keyboard input to quit the program
    keyboard.wait("q")

    # Set the stop event to end the screenshot thread
    stop_event.set()

    # Wait for the screenshot thread to finish
    screenshot_thread.join()

    print("Program ended.")

if __name__ == "__main__":
    main()