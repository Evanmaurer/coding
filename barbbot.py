import pydirectinput
import keyboard
import time
import random

time.sleep(5)  # 5-second delay to switch to the game window
counter = 0

# Point(x=2484, y=1184) #search pos
# Point(x=739, y=1318) barb pos
# Point(x=766, y=1116) #search button pos
# Point(x=1289, y=712) barb click pos
# Point(x=1716, y=1017) attack pos
# Point(x=2221, y=434) march pos
# Point(x=1646, y=1099) send march pos
# Point(x=2470, y=529) march out pos
# Point(x=2199, y=659) march out attack pos

while True:
    if keyboard.is_pressed("q"):
        print("Quitting...")
        break
    else:
        print(f"Executing actions, iteration: {counter + 1}")

        # Move to search button position and hold click
        pydirectinput.moveTo(2484, 1184, duration=random.uniform(0.5, 1.5))
        pydirectinput.mouseDown()
        time.sleep(random.uniform(0.5, 1))
        pydirectinput.mouseUp()
        time.sleep(random.uniform(0.5, 2))

        # Move to barb position and hold click
        pydirectinput.moveTo(739, 1318, duration=random.uniform(0.5, 1.5))
        pydirectinput.mouseDown()
        time.sleep(random.uniform(0.5, 1))
        pydirectinput.mouseUp()
        time.sleep(random.uniform(0.5, 2))

        # Move to search button position and hold click
        pydirectinput.moveTo(766, 1116, duration=random.uniform(0.5, 1.5))
        pydirectinput.mouseDown()
        time.sleep(random.uniform(0.5, 1))
        pydirectinput.mouseUp()
        time.sleep(random.uniform(0.5, 2))

        # Move to barb click position and hold click
        pydirectinput.moveTo(1289, 712, duration=random.uniform(0.5, 1.5))
        pydirectinput.mouseDown()
        time.sleep(random.uniform(0.5, 1))
        pydirectinput.mouseUp()
        time.sleep(random.uniform(0.5, 2))

        # Move to attack position and hold click
        pydirectinput.moveTo(1716, 1017, duration=random.uniform(0.5, 1.5))
        pydirectinput.mouseDown()
        time.sleep(random.uniform(0.5, 1))
        pydirectinput.mouseUp()

        # Move to march position and hold click
        pydirectinput.moveTo(2221, 434, duration=random.uniform(0.5, 1.5))
        pydirectinput.mouseDown()
        time.sleep(random.uniform(0.5, 1))
        pydirectinput.mouseUp()

        # Move to send march position and hold click
        pydirectinput.moveTo(1646, 1099, duration=random.uniform(0.5, 1.5))
        pydirectinput.mouseDown()
        time.sleep(random.uniform(0.5, 1))
        pydirectinput.mouseUp()

        # Move to march out position and hold click
        pydirectinput.moveTo(2470, 529, duration=random.uniform(0.5, 1.5))
        pydirectinput.mouseDown()
        time.sleep(random.uniform(0.5, 1))
        pydirectinput.mouseUp()

        # Move to march out attack position and hold click
        pydirectinput.moveTo(2199, 659, duration=random.uniform(0.5, 1.5))
        pydirectinput.mouseDown()
        time.sleep(random.uniform(0.5, 1))
        pydirectinput.mouseUp()

        counter += 1
        print(f"Completed iteration: {counter}")
        time.sleep(random.uniform(120, 180))  # Random delay before the next iteration
    """else:
        time.sleep(random.uniform(120, 180))  # Random delay before the next action
        # Move to search button position and click
        pyautogui.moveTo(2484, 1184, duration=random.uniform(0.5, 1.5))  # Move with a random duration
        pyautogui.mouseDown()
        time.sleep(random.uniform(0.5, 1))
        pyautogui.mouseUp()
        time.sleep(random.uniform(0.5, 2))

        # Move to barb position and click
        pyautogui.moveTo(739, 1318, duration=random.uniform(0.5, 1.5))
        pyautogui.mouseDown()
        time.sleep(random.uniform(0.5, 1))
        pyautogui.mouseUp()
        time.sleep(random.uniform(0.5, 2))

        # Move to search button position and click
        pyautogui.moveTo(766, 1116, duration=random.uniform(0.5, 1.5))
        pyautogui.mouseDown()
        time.sleep(random.uniform(0.5, 1))
        pyautogui.mouseUp()
        time.sleep(random.uniform(0.5, 2))

        # Move to barb click position and click
        pyautogui.moveTo(1289, 712, duration=random.uniform(0.5, 1.5))
        pyautogui.mouseDown()
        time.sleep(random.uniform(0.5, 1))
        pyautogui.mouseUp()
        time.sleep(random.uniform(0.5, 2))

        # Move to attack position and click
        pyautogui.moveTo(1716, 1017, duration=random.uniform(0.5, 1.5))
        pyautogui.mouseDown()
        time.sleep(random.uniform(0.5, 1))
        pyautogui.mouseUp()
        
        pyautogui.moveTo(1646, 1099, duration=random.uniform(0.5, 1.5))
        pyautogui.mouseDown()
        time.sleep(random.uniform(0.5, 1))
        pyautogui.mouseUp()
        
        pyautogui.moveTo(2470, 529, duration=random.uniform(0.5, 1.5))
        pyautogui.mouseDown()
        time.sleep(random.uniform(0.5, 1))
        pyautogui.mouseUp()
        pyautogui.moveTo(2199, 659, duration=random.uniform(0.5, 1.5))
        pyautogui.mouseDown()
        time.sleep(random.uniform(0.5, 1))
        pyautogui.mouseUp()
        counter +=1"""
