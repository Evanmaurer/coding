from ultralytics import YOLO
import pyautogui
import cv2
import numpy as np
import time
# Function to detect gem nodes in the game using YOLO
def detect_gem_nodes(model_path):
    # Load the YOLO model
    model = YOLO(model_path)

    # Take a screenshot of the game
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # Run detection
    results = model(screenshot)

    # Display results
    results.show()

# Path to the trained YOLO model
model_path = "best.pt"  # Replace with your trained YOLO model
detect_gem_nodes(model_path)