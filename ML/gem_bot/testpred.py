from ultralytics import YOLO

# Load a model
model = YOLO('best2.pt')  # pretrained YOLOv8n model

# Run batched inference on a list of images
screenx_center = 3840/2
screeny_center = 2160/2

decision = {
    "barb_sky": False,
    "wood_sky": False,
    "food_sky": False,
    "gold_sky": False,
    "gem_sky": False,
    "stone_sky": False,
    "barb_zoomed": False,
}

results = model(['F:/coding/screenshots/screenshot_2025-03-30_19-51-10.png'], conf=.13, save=True)  # return a list of Results objects
boxes = results[0].boxes.xyxy.tolist()
classes = results[0].boxes.cls.tolist()
names = results[0].names
confidences = results[0].boxes.conf.tolist()

# Process results list
for box, cls, conf in zip(boxes, classes, confidences):
    x1, y1, x2, y2 = box
    
    center_x = (x1+x2) / 2
    center_y = (y1+y2) / 2

    confidence = conf
    detected_class = cls
    name = names[int(cls)]
    
    if name=="barb_sky":
        decision["barb_sky"] = True
        decision["barb_sky_location"] = (center_x, center_y)
    elif name == "food_sky":
        decision["food_sky"] = True
        decision["food_sky_location"] = (center_x, center_y)
    elif name == "wood_sky":
        decision["wood_sky"] = True
        decision["wood_sky_location"] = (center_x, center_y)
    elif name == "gold_sky":
        decision["gold_sky"] = True
        decision["gold_sky_location"] = (center_x, center_y)
    elif name == "stone_sky":
        decision["stone_sky"] = True
        distance = ((center_x - screenx_center) ** 2 + (center_y - screeny_center) **2) **.5
        if "stone_sky_location" in decision:
            # Calculate if closer
            if distance < decision["stone_sky_distance"]:
                decision["stone_sky_location"] = (center_x, center_y)
                decision["stone_sky_distance"] = distance
        else:
            decision["stone_sky_location"] = (center_x, center_y)
            decision["stone_sky_distance"] = distance
    elif name == "barb_zoomed":
        decision["barb_zoomed"] = True
        distance = ((center_x - screenx_center) ** 2 + (center_y - screeny_center) **2) **.5
        if "barb_zoomed_location" in decision:
            # Calculate if closer
            if distance < decision["barb_zoomed_distance"]:
                decision["barb_zoomed_location"] = (center_x, center_y)
                decision["barb_zoomed_distance"] = distance
        else:
            decision["barb_zoomed_location"] = (center_x, center_y)
            decision["barb_zoomed_distance"] = distance
    
print(decision)