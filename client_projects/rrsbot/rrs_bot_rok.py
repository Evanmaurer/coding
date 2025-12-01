import subprocess
import time
import os
import sys
import random
import numpy as np
from PIL import Image
import io
import cv2
import tempfile

# Common Nox Player installation paths
NOX_PATHS = [
    r"C:\Program Files (x86)\Nox\bin\Nox.exe",
    r"C:\Program Files\Nox\bin\Nox.exe",
    r"D:\Program Files (x86)\Nox\bin\Nox.exe",
    r"D:\Program Files\Nox\bin\Nox.exe",
]

# Rise of Kingdoms package name (common package names)
ROK_PACKAGE_NAME = "com.lilithgame.roc.gp"  # Found package name
# Alternative: "com.lilithgames.rok.offical", "com.lilithgames.rok", etc.

# Nox ADB path (will be found automatically)
NOX_ADB_PATH = None

# Hardcoded button coordinates (top-left x, top-left y, bottom-right x, bottom-right y)
# Format: (x1, y1, x2, y2) where (x1, y1) is top-left and (x2, y2) is bottom-right
BUTTON_COORDS = {
    "initial_search": (38, 517, 81, 556),  # Magnifying glass button
    
    # Resource type selection buttons (when search menu is open)
    "search_food": (409, 601, 483, 667),  # Cropland button
    "search_wood": (608, 601, 670, 674),  # Logging Camp button
    "search_stone": (801, 602, 863, 672),  # Stone Deposit button
    "search_gold": (993, 602, 1055, 672),  # Gold Deposit button (estimated: same width/height as stone)
    
    # Level controls - using image detection now
    "level_plus": None,  # Plus button for level - using image detection
    "level_minus": None,  # Minus button for level - using image detection
    
    # Final SEARCH button (position changes based on selected resource type)
    "final_search_food": (372, 465, 527, 517),  # SEARCH button when food is selected
    "final_search_wood": (565, 465, 718, 513),  # SEARCH button when wood is selected
    "final_search_stone": (758, 465, 911, 513),  # SEARCH button when stone is selected (calculated)
    "final_search_gold": (951, 465, 1104, 513),  # SEARCH button when gold is selected (calculated)
    "final_search": None,  # Generic fallback (will use resource-specific if available)
    
    # Preset buttons for troop selection (5 presets)
    "preset_1": (1094, 262, 1113, 284),  # Top preset
    "preset_2": (1094, 318, 1112, 337),  # Second preset
    "preset_3": (1094, 371, 1112, 390),  # Third preset (fixed typo in user's coords)
    "preset_4": (1094, 428, 1112, 447),  # Fourth preset (fixed typo in user's coords)
    "preset_5": (1094, 480, 1112, 500),  # Fifth preset
    
    # March button
    "march_button": (811, 605, 1046, 665),  # March button to send troops
}

def find_nox_path():
    """Find Nox Player installation path"""
    for path in NOX_PATHS:
        if os.path.exists(path):
            return path
    
    # Try to find it in common locations
    possible_dirs = [
        os.path.expanduser("~"),
        "C:\\",
        "D:\\",
    ]
    
    print("Nox Player not found in common locations.")
    print("Please provide the full path to Nox.exe:")
    user_path = input("Path: ").strip().strip('"')
    if os.path.exists(user_path):
        return user_path
    
    return None

def find_nox_adb():
    """Find Nox Player's ADB executable"""
    global NOX_ADB_PATH
    
    if NOX_ADB_PATH and os.path.exists(NOX_ADB_PATH):
        return NOX_ADB_PATH
    
    # Try to find ADB in Nox bin directory
    nox_path = find_nox_path()
    if nox_path:
        nox_bin_dir = os.path.dirname(nox_path)
        adb_path = os.path.join(nox_bin_dir, "adb.exe")
        if os.path.exists(adb_path):
            NOX_ADB_PATH = adb_path
            return adb_path
    
    # Try common Nox ADB paths
    adb_paths = [
        r"D:\Program Files\Nox\bin\adb.exe",
        r"D:\Program Files (x86)\Nox\bin\adb.exe",
        r"C:\Program Files\Nox\bin\adb.exe",
        r"C:\Program Files (x86)\Nox\bin\adb.exe",
    ]
    
    for adb_path in adb_paths:
        if os.path.exists(adb_path):
            NOX_ADB_PATH = adb_path
            return adb_path
    
    # Fall back to system ADB
    print("Warning: Could not find Nox ADB, using system ADB")
    return "adb"

def check_adb_connection():
    """Check if ADB can connect to Nox emulator"""
    adb_path = find_nox_adb()
    try:
        result = subprocess.run(
            [adb_path, "devices"],
            capture_output=True,
            text=True,
            timeout=5
        )
        devices = result.stdout.strip().split('\n')[1:]  # Skip header
        connected = [d for d in devices if d.strip() and 'device' in d]
        return len(connected) > 0
    except Exception as e:
        print(f"Error checking ADB: {e}")
        return False

def launch_nox():
    """Launch Nox Player"""
    nox_path = find_nox_path()
    if not nox_path:
        print("ERROR: Could not find Nox Player. Please install it or provide the path.")
        return False
    
    print(f"Launching Nox Player from: {nox_path}")
    
    try:
        # Launch Nox Player
        subprocess.Popen([nox_path], shell=True)
        print("Nox Player launched. Waiting for it to start...")
        
        # Wait for Nox to start (adjust time as needed)
        max_wait = 60  # seconds
        wait_interval = 2
        elapsed = 0
        
        while elapsed < max_wait:
            time.sleep(wait_interval)
            elapsed += wait_interval
            
            if check_adb_connection():
                print("Nox Player is ready!")
                return True
            else:
                print(f"Waiting for Nox Player to start... ({elapsed}s)")
        
        print("WARNING: Nox Player may not be fully started. Continuing anyway...")
        return True
        
    except Exception as e:
        print(f"ERROR launching Nox Player: {e}")
        return False

def find_rok_package():
    """Find the Rise of Kingdoms package name"""
    print("Searching for Rise of Kingdoms package...")
    adb_path = find_nox_adb()
    
    try:
        result = subprocess.run(
            [adb_path, "shell", "pm", "list", "packages"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        all_packages = result.stdout.strip().split('\n')
        # Look for packages containing rok, roc, kingdom, or lilith
        rok_packages = []
        for pkg in all_packages:
            pkg_name = pkg.replace("package:", "").strip().lower()
            if any(keyword in pkg_name for keyword in ['rok', 'roc', 'kingdom', 'lilith']):
                rok_packages.append(pkg.replace("package:", "").strip())
        
        if rok_packages:
            print(f"Found potential packages: {rok_packages}")
            return rok_packages
        else:
            print("No Rise of Kingdoms packages found. Trying common package names...")
            return [
                "com.lilithgame.roc.gp",  # Found package name
                "com.lilithgames.rok.offical",
                "com.lilithgames.rok",
                "com.lilithgames.rok.us",
                "com.lilithgames.rok.global",
            ]
    except Exception as e:
        print(f"Error finding packages: {e}")
        return [
            "com.lilithgame.roc.gp",  # Found package name
            "com.lilithgames.rok.offical",
            "com.lilithgames.rok",
            "com.lilithgames.rok.us",
        ]

def get_main_activity(package_name):
    """Get the main activity for a package"""
    adb_path = find_nox_adb()
    try:
        result = subprocess.run(
            [adb_path, "shell", "pm", "dump", package_name],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return None
        
        # Parse the dump to find main activity
        lines = result.stdout.split('\n')
        in_activity = False
        current_activity = None
        
        for line in lines:
            if "android.intent.action.MAIN" in line:
                # Look backwards for activity name
                for i in range(len(lines) - 1, -1, -1):
                    if "Activity" in lines[i] and package_name in lines[i]:
                        # Extract activity name
                        activity_line = lines[i].strip()
                        if package_name in activity_line:
                            # Format: Activity{...} or just the activity name
                            if " " in activity_line:
                                parts = activity_line.split()
                                for part in parts:
                                    if package_name in part and "/" in part:
                                        return part.split()[0] if " " in part else part
                            elif "/" in activity_line:
                                return activity_line.split()[0]
                        break
        
        # Alternative: try common activity names
        common_activities = [
            f"{package_name}/com.harry.engine.MainActivity",  # Found activity for com.lilithgame.roc.gp
            f"{package_name}/com.lilithgames.rok.MainActivity",
            f"{package_name}/.MainActivity",
            f"{package_name}/com.lilithgames.hgame.activity.MainActivity",
            f"{package_name}/com.unity3d.player.UnityPlayerActivity",
        ]
        
        return common_activities
        
    except Exception as e:
        print(f"Error getting main activity: {e}")
        return None

def launch_rise_of_kingdoms():
    """Launch Rise of Kingdoms app using ADB"""
    print("Attempting to launch Rise of Kingdoms...")
    adb_path = find_nox_adb()
    
    # First, find the actual package name
    package_names = find_rok_package()
    
    if not package_names:
        print("ERROR: Could not find Rise of Kingdoms package.")
        return False
    
    # Try multiple launch methods for each package
    for package in package_names:
        print(f"\nTrying package: {package}")
        
        # Method 1: Use monkey command (most reliable)
        try:
            print("  Method 1: Using monkey command...")
            result = subprocess.run(
                [adb_path, "shell", "monkey", "-p", package, "-c", "android.intent.category.LAUNCHER", "1"],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                print(f"  ✓ Successfully launched using monkey! (Package: {package})")
                time.sleep(2)  # Give it time to start
                return True
            else:
                print(f"  ✗ Monkey failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("  ✗ Timeout with monkey command")
        except Exception as e:
            print(f"  ✗ Error with monkey: {e}")
        
        # Method 2: Use am start with intent
        try:
            print("  Method 2: Using am start with intent...")
            result = subprocess.run(
                [adb_path, "shell", "am", "start", "-a", "android.intent.action.MAIN", 
                 "-c", "android.intent.category.LAUNCHER", "-n", f"{package}/.MainActivity"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print(f"  ✓ Successfully launched using am start! (Package: {package})")
                time.sleep(2)
                return True
            else:
                print(f"  ✗ am start failed: {result.stderr}")
        except Exception as e:
            print(f"  ✗ Error with am start: {e}")
        
        # Method 3: Get main activity and launch
        try:
            print("  Method 3: Finding main activity...")
            activities = get_main_activity(package)
            
            if isinstance(activities, list):
                for activity in activities:
                    try:
                        result = subprocess.run(
                            [adb_path, "shell", "am", "start", "-n", activity],
                            capture_output=True,
                            text=True,
                            timeout=10
                        )
                        if result.returncode == 0:
                            print(f"  ✓ Successfully launched with activity: {activity}")
                            time.sleep(2)
                            return True
                    except:
                        continue
            elif activities:
                result = subprocess.run(
                    [adb_path, "shell", "am", "start", "-n", activities],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    print(f"  ✓ Successfully launched with activity: {activities}")
                    time.sleep(2)
                    return True
        except Exception as e:
            print(f"  ✗ Error finding activity: {e}")
        
        # Method 4: Try direct package launch
        try:
            print("  Method 4: Direct package launch...")
            result = subprocess.run(
                [adb_path, "shell", "am", "start", "-a", "android.intent.action.MAIN", 
                 "-c", "android.intent.category.LAUNCHER", "-p", package],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print(f"  ✓ Successfully launched using direct package! (Package: {package})")
                time.sleep(2)
                return True
        except Exception as e:
            print(f"  ✗ Error with direct launch: {e}")
    
    print("\n" + "=" * 50)
    print("ERROR: Could not launch Rise of Kingdoms with any method.")
    print("=" * 50)
    print("\nTroubleshooting steps:")
    print("1. Verify Rise of Kingdoms is installed in Nox Player")
    print("2. Check ADB connection: Run 'adb devices' in terminal")
    print("3. Try manually opening Rise of Kingdoms in Nox Player first")
    print("4. Make sure Nox Player is fully loaded before running this script")
    
    # Show all installed packages for debugging
    print("\nAll installed packages (for debugging):")
    adb_path = find_nox_adb()
    try:
        result = subprocess.run(
            [adb_path, "shell", "pm", "list", "packages"],
            capture_output=True,
            text=True,
            timeout=5
        )
        all_packages = result.stdout.strip().split('\n')[:20]  # Show first 20
        for pkg in all_packages:
            print(f"  {pkg}")
        print("  ... (showing first 20)")
    except:
        pass
    
    return False

# ============================================================================
# RSS GATHERING FUNCTIONS
# ============================================================================

def capture_screen(use_file_method=True):
    """
    Capture screen from Nox emulator using ADB.
    
    Args:
        use_file_method: If True, save to temp file first (more reliable). 
                       If False, use direct binary capture.
    """
    adb_path = find_nox_adb()
    
    if use_file_method:
        # Method 1: Save to file first (more reliable, especially on Windows)
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                tmp_path = tmp_file.name
            
            # Save screenshot directly to local file using ADB exec-out
            # This avoids shell redirection issues
            with open(tmp_path, 'wb') as f:
                process = subprocess.Popen(
                    [adb_path, "exec-out", "screencap", "-p"],
                    stdout=f,
                    stderr=subprocess.PIPE,
                    bufsize=0
                )
                
                stdout, stderr = process.communicate(timeout=10)
                
                if process.returncode == 0 and os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 1000:
                    # Read the image file
                    try:
                        image = Image.open(tmp_path)
                        img_array = np.array(image)
                        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                        
                        # Clean up
                        try:
                            os.remove(tmp_path)
                        except:
                            pass
                        
                        return img_bgr
                    except Exception as img_error:
                        print(f"Error reading image file: {img_error}")
                        if os.path.exists(tmp_path):
                            os.remove(tmp_path)
                        # Fall back to direct method
                        return capture_screen(use_file_method=False)
                else:
                    error_msg = stderr.decode('utf-8', errors='ignore') if stderr else "Unknown error"
                    print(f"Error capturing to file (code {process.returncode}): {error_msg}")
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
                    # Fall back to direct method
                    return capture_screen(use_file_method=False)
                
        except subprocess.TimeoutExpired:
            print("Timeout while capturing screen, trying direct method...")
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except:
                    pass
            return capture_screen(use_file_method=False)
        except Exception as e:
            print(f"Exception in file-based capture: {e}, trying direct method...")
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except:
                    pass
            return capture_screen(use_file_method=False)
    else:
        # Method 2: Direct binary capture (faster but can have issues on Windows)
        try:
            process = subprocess.Popen(
                [adb_path, "shell", "screencap", "-p"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=0
            )
            
            # Read binary data
            stdout_data, stderr_data = process.communicate(timeout=10)
            
            if process.returncode == 0 and stdout_data:
                # Clean up any Windows line ending issues (CRLF -> LF)
                if b'\r\n' in stdout_data:
                    stdout_data = stdout_data.replace(b'\r\n', b'\n')
                
                # Check if we have valid PNG data
                if stdout_data[:8] != b'\x89PNG\r\n\x1a\n':
                    # Try to find PNG signature if it's offset
                    png_start = stdout_data.find(b'\x89PNG\r\n\x1a\n')
                    if png_start > 0:
                        stdout_data = stdout_data[png_start:]
                    elif stdout_data[:4] == b'\x89PNG':
                        # Might be missing the \r\n
                        pass
                    else:
                        print("Warning: Screenshot data doesn't appear to be a valid PNG")
                
                # Convert bytes to PIL Image
                try:
                    image = Image.open(io.BytesIO(stdout_data))
                    img_array = np.array(image)
                    img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                    return img_bgr
                except Exception as img_error:
                    print(f"Error processing image data: {img_error}")
                    print(f"Data length: {len(stdout_data)} bytes")
                    if len(stdout_data) > 0:
                        print(f"First 20 bytes: {stdout_data[:20]}")
                    return None
            else:
                error_msg = stderr_data.decode('utf-8', errors='ignore') if stderr_data else "Unknown error"
                print(f"Error capturing screen (return code {process.returncode}): {error_msg}")
                return None
                
        except subprocess.TimeoutExpired:
            print("Timeout while capturing screen (took longer than 10 seconds)")
            if 'process' in locals():
                process.kill()
            return None
        except Exception as e:
            print(f"Exception capturing screen: {e}")
            import traceback
            traceback.print_exc()
            return None

def random_click(x, y, width=0, height=0, padding=5):
    """
    Click at a random position within a button/area to avoid detection.
    
    Args:
        x, y: Center or top-left coordinates
        width, height: Size of the clickable area (0 = single point click)
        padding: Padding from edges to avoid clicking outside button
    """
    adb_path = find_nox_adb()
    
    if width > 0 and height > 0:
        # Random position within the button bounds
        click_x = random.randint(x + padding, x + width - padding)
        click_y = random.randint(y + padding, y + height - padding)
    else:
        # Small random offset for single point clicks
        offset_x = random.randint(-3, 3)
        offset_y = random.randint(-3, 3)
        click_x = x + offset_x
        click_y = y + offset_y
    
    try:
        # Use ADB to simulate touch
        subprocess.run(
            [adb_path, "shell", "input", "tap", str(click_x), str(click_y)],
            capture_output=True,
            timeout=2
        )
        return True
    except Exception as e:
        print(f"Error clicking at ({click_x}, {click_y}): {e}")
        return False

def click_button_by_coords(button_name):
    """
    Click a button using hardcoded coordinates.
    
    Args:
        button_name: Name of the button (key in BUTTON_COORDS dict)
    
    Returns: True if clicked successfully, False otherwise
    """
    if button_name not in BUTTON_COORDS:
        print(f"Warning: Button '{button_name}' not found in coordinates")
        return False
    
    coords = BUTTON_COORDS[button_name]
    if coords is None:
        print(f"Warning: Coordinates for '{button_name}' not set")
        return False
    
    x1, y1, x2, y2 = coords
    
    # Calculate width and height
    width = x2 - x1
    height = y2 - y1
    
    # Random click within the button bounds
    padding = 5
    click_x = random.randint(x1 + padding, x2 - padding)
    click_y = random.randint(y1 + padding, y2 - padding)
    
    print(f"Clicking {button_name} at ({click_x}, {click_y}) [area: ({x1}, {y1}) to ({x2}, {y2})]")
    
    return random_click(click_x, click_y, 0, 0, padding=0)  # Already calculated random position

def human_delay(min_seconds=0.5, max_seconds=1.5):
    """Add random human-like delay"""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)

def find_search_button(screenshot):
    """
    Find the blue SEARCH button on screen.
    Returns: (x, y, width, height) or None
    """
    if screenshot is None:
        return None
    
    # Convert to HSV for better color detection
    hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
    
    # Bright blue color range for the SEARCH button
    # Adjust these values based on the actual button color
    lower_blue = np.array([100, 150, 150])  # Bright blue
    upper_blue = np.array([130, 255, 255])
    
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    
    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        area = cv2.contourArea(contour)
        # Search button should be reasonably large
        if 2000 < area < 50000:
            x, y, w, h = cv2.boundingRect(contour)
            # Check aspect ratio (should be roughly rectangular)
            aspect_ratio = w / h if h > 0 else 0
            if 1.5 < aspect_ratio < 5.0:  # Wide rectangle
                return (x, y, w, h)
    
    return None

def find_resource_type_button(screenshot, resource_type):
    """
    Find resource type selection buttons (Cropland, Logging Camp, Stone Deposit, Gold Deposit).
    
    Args:
        screenshot: OpenCV image
        resource_type: "food", "wood", "stone", "gold"
    
    Returns: (x, y, width, height) or None
    """
    if screenshot is None:
        return None
    
    hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
    
    # Color ranges for each resource type button
    # Based on the icons: Cropland (yellow/gold), Logging Camp (brown), Stone/Gold (grayscale)
    color_ranges = {
        "food": [  # Cropland - yellow/golden
            (np.array([20, 100, 100]), np.array([30, 255, 255])),
        ],
        "wood": [  # Logging Camp - brown
            (np.array([10, 50, 50]), np.array([25, 255, 255])),
        ],
        "stone": [  # Stone Deposit - gray
            (np.array([0, 0, 50]), np.array([180, 50, 200])),
        ],
        "gold": [  # Gold Deposit - gray with slight yellow
            (np.array([0, 0, 50]), np.array([180, 50, 200])),
        ],
    }
    
    if resource_type not in color_ranges:
        return None
    
    for lower, upper in color_ranges[resource_type]:
        mask = cv2.inRange(hsv, lower, upper)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            # Resource buttons are circular icons
            if 1000 < area < 30000:
                x, y, w, h = cv2.boundingRect(contour)
                # Check if roughly circular/square
                aspect_ratio = w / h if h > 0 else 0
                if 0.7 < aspect_ratio < 1.3:
                    return (x, y, w, h)
    
    return None

def find_level_controls(screenshot):
    """
    Find level selector controls (plus/minus buttons, slider).
    
    Returns: dict with 'plus', 'minus', 'slider' coordinates or None
    """
    if screenshot is None:
        return None
    
    hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
    
    # Light blue color for the plus/minus buttons
    lower_blue = np.array([100, 100, 150])
    upper_blue = np.array([130, 255, 255])
    
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    controls = {}
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if 500 < area < 10000:  # Small square buttons
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h if h > 0 else 0
            if 0.7 < aspect_ratio < 1.3:  # Square buttons
                # Determine if it's plus or minus based on position
                # Plus is usually on the right, minus on the left
                # This is a simple heuristic - you may need to adjust
                center_x = x + w // 2
                screen_width = screenshot.shape[1]
                
                if center_x < screen_width * 0.5:
                    controls['minus'] = (x, y, w, h)
                else:
                    controls['plus'] = (x, y, w, h)
    
    return controls if controls else None

def set_level_to_8():
    """
    Set level directly to 8 without resetting first.
    Just click plus button 7 times to go from level 1 to 8.
    
    Returns: 8 (the level set)
    """
    print("Setting level to 8...")
    
    # Click plus button 7 times to reach level 8 (assuming we start at level 1)
    print("Clicking plus button 7 times to reach level 8...")
    for i in range(7):
        if click_button_by_template("plus_rrslvl.png", threshold=0.7):
            print(f"  Clicked plus button {i+1}/7")
            time.sleep(0.5)  # Small delay between clicks
        else:
            print(f"Warning: Could not find plus button on attempt {i+1}")
            # Try to continue anyway
            time.sleep(0.5)
    
    print("Level set to 8")
    time.sleep(1)  # Wait a moment for level to register
    return 8

def send_march_to_resource(resource_x, resource_y, resource_w, resource_h, preset_number):
    """
    Send a march to a resource by:
    1. Clicking the gather button
    2. Clicking the new troop button
    3. Clicking the preset button (1-5)
    4. Clicking the march button
    
    Args:
        resource_x, resource_y, resource_w, resource_h: Resource coordinates
        preset_number: Which preset to use (1-5)
    
    Returns: True if march was sent successfully, False otherwise
    """
    print(f"Sending march {preset_number} to resource at ({resource_x + resource_w//2}, {resource_y + resource_h//2})...")
    
    
    # Step 2: Click the gather button
    print("  Step 2: Clicking gather button...")
    if not click_button_by_template("gather_rrs.png", threshold=0.7):
        print("  Failed to find gather button")
        return False
    time.sleep(1.5)  # Small delay for game to load
    
    # Step 3: Click the new troop button
    print("  Step 3: Clicking new troop button...")
    if not click_button_by_template("newtroop.png", threshold=0.7):
        print("  Failed to find new troop button")
        return False
    time.sleep(1.5)  # Small delay for game to load
    
    # Step 4: Click the preset button
    if preset_number < 1 or preset_number > 5:
        print(f"  Error: Invalid preset number {preset_number}, must be 1-5")
        return False
    
    preset_key = f"preset_{preset_number}"
    print(f"  Step 4: Clicking preset {preset_number}...")
    if not click_button_by_coords(preset_key):
        print(f"  Failed to click preset {preset_number}")
        return False
    time.sleep(1.0)  # Small delay for game to load
    
    # Step 5: Click the march button
    print("  Step 5: Clicking march button...")
    if not click_button_by_coords("march_button"):
        print("  Failed to click march button")
        return False
    time.sleep(1.5)  # Small delay for game to load
    
    print(f"  ✓ March {preset_number} sent successfully!")
    return True

def select_random_resource(weights=None):
    """
    Select a random resource type with weighted chances.
    
    Args:
        weights: Dict with resource types as keys and weights as values.
                Default: equal weights for all resources.
                Example: {"food": 0.3, "wood": 0.3, "stone": 0.2, "gold": 0.2}
    
    Returns: Resource type string ("food", "wood", "stone", or "gold")
    """
    if weights is None:
        # Default: equal chances for all resources
        weights = {
            "food": 0.25,
            "wood": 0.25,
            "stone": 0.25,
            "gold": 0.25
        }
    
    # Normalize weights to sum to 1.0
    total = sum(weights.values())
    if total > 0:
        weights = {k: v / total for k, v in weights.items()}
    
    # Select based on weights
    rand = random.random()
    cumulative = 0.0
    
    for resource, weight in weights.items():
        cumulative += weight
        if rand <= cumulative:
            return resource
    
    # Fallback to first resource
    return list(weights.keys())[0]

def find_initial_search_button(screenshot):
    """
    Find the initial search button (blue button with magnifying glass icon).
    This is the button you click to open the search menu.
    Returns: (x, y, width, height) or None
    """
    if screenshot is None:
        return None
    
    # Convert to HSV for better color detection
    hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
    
    # Bright blue color range for the search button
    # The button has a bright blue background with a white magnifying glass icon
    lower_blue = np.array([100, 150, 150])  # Bright blue
    upper_blue = np.array([130, 255, 255])
    
    blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
    
    # Also look for white/light gray for the magnifying glass icon
    lower_white = np.array([0, 0, 200])  # Very light/white
    upper_white = np.array([180, 30, 255])
    white_mask = cv2.inRange(hsv, lower_white, upper_white)
    
    # Find contours in blue areas
    contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    candidates = []
    
    for contour in contours:
        area = cv2.contourArea(contour)
        # Search button should be reasonably sized (circular/rounded square)
        if 2000 < area < 50000:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h if h > 0 else 0
            
            # Button is roughly square/rounded (not too wide, not too tall)
            if 0.7 < aspect_ratio < 1.5:
                # Check if there's white inside this blue area (the magnifying glass icon)
                roi_white = white_mask[y:y+h, x:x+w]
                white_pixels = np.sum(roi_white > 0)
                total_pixels = w * h
                white_ratio = white_pixels / total_pixels if total_pixels > 0 else 0
                
                # Should have some white inside (the magnifying glass icon)
                # But not too much (the icon is relatively small compared to button)
                if 0.1 < white_ratio < 0.5:  # 10-50% white (the icon)
                    # Score this candidate
                    score = area * (1 + white_ratio * 2)
                    candidates.append((score, x, y, w, h))
    
    if candidates:
        # Return the best candidate (highest score)
        candidates.sort(reverse=True, key=lambda c: c[0])
        _, x, y, w, h = candidates[0]
        return (x, y, w, h)
    
    # Fallback: If no candidates with white icon found, return largest blue button
    if contours:
        largest = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest)
        if 2000 < area < 50000:
            x, y, w, h = cv2.boundingRect(largest)
            aspect_ratio = w / h if h > 0 else 0
            if 0.7 < aspect_ratio < 1.5:
                return (x, y, w, h)
    
    return None

def use_search_feature(resource_type="all", level="max", use_coords=True):
    """
    Use the game's search feature to find resources.
    Correct flow:
    1. Click initial search button (magnifying glass icon)
    2. Select resource type (Cropland, Logging Camp, etc.)
    3. Set level using level controls
    4. Click final SEARCH button
    
    Args:
        resource_type: "food", "wood", "stone", "gold", or "all"
        level: Resource level to search for ("max" to use highest available, or int for specific level)
        use_coords: If True, use hardcoded coordinates (more reliable)
    
    Returns: True if search was successful, False otherwise
    """
    print(f"Using search feature for {resource_type} resources (level: {level})...")
    
    # Step 1: Click the initial search button (magnifying glass icon) using image detection
    print("Step 1: Clicking initial search button (magnifying glass)...")
    if click_button_by_template("searchglass.png", threshold=0.7):
        print("Found and clicked search glass button")
        time.sleep(2)  # Wait for search menu to open
    else:
        print("ERROR: Could not find search glass button!")
        return False
    
    # Step 2: Select resource type (if not "all") using coordinates
    if resource_type != "all":
        print(f"Step 2: Selecting {resource_type} resource type...")
        button_key = f"search_{resource_type}"
        
        if button_key in BUTTON_COORDS and BUTTON_COORDS[button_key] is not None:
            # Use hardcoded coordinates (we have these already)
            if click_button_by_coords(button_key):
                print(f"Clicked {resource_type} button")
                time.sleep(1)  # Small delay for game to load
            else:
                print(f"Warning: Failed to click {resource_type} button using coordinates")
        else:
            print(f"Warning: No coordinates found for {resource_type} button")
    
    # Step 3: Set level to 8 (always use level 8, no reset needed)
    print("Step 3: Setting level to 8...")
    set_level_to_8()
    time.sleep(1)  # Wait for level to register
    
    # Step 4: Click the search button using image detection
    print("Step 4: Clicking search button...")
    if click_button_by_template("search.png", threshold=0.7):
        print("Found and clicked search button")
        time.sleep(2)  # Wait for search results
        return True
    else:
        print("ERROR: Could not find search button!")
        return False

def find_highlighted_resources(screenshot):
    """
    After using search, find highlighted/selected resources on the map.
    These should be easier to detect than regular resources.
    
    Returns: List of (x, y, width, height) tuples
    """
    if screenshot is None:
        return []
    
    # Search results are often highlighted with a bright color or glow
    # Try detecting bright highlights or specific colors
    
    hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
    
    # Look for bright highlights (common in search results)
    # Yellow/gold highlight
    lower_highlight = np.array([15, 100, 200])
    upper_highlight = np.array([35, 255, 255])
    
    mask = cv2.inRange(hsv, lower_highlight, upper_highlight)
    
    # Also look for bright white/cyan (common highlight colors)
    lower_bright = np.array([100, 0, 200])
    upper_bright = np.array([130, 50, 255])
    mask2 = cv2.inRange(hsv, lower_bright, upper_bright)
    
    # Combine masks
    mask = cv2.bitwise_or(mask, mask2)
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    resources = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if 1000 < area < 50000:  # Resource node size
            x, y, w, h = cv2.boundingRect(contour)
            resources.append((x, y, w, h))
    
    return resources

def find_resource_nodes(screenshot, resource_type="all"):
    """
    Find resource nodes on the screen using template matching or color detection.
    
    Args:
        screenshot: OpenCV image (BGR format)
        resource_type: "food", "wood", "stone", "gold", or "all"
    
    Returns:
        List of (x, y, width, height) tuples for found resources
    """
    if screenshot is None:
        return []
    
    # Convert to HSV for better color detection
    hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
    
    resources = []
    
    # Define color ranges for different resource types
    # These are approximate - you may need to adjust based on your game version
    color_ranges = {
        "food": [
            (np.array([40, 50, 50]), np.array([80, 255, 255])),  # Green/Yellow
        ],
        "wood": [
            (np.array([10, 50, 50]), np.array([30, 255, 255])),  # Brown/Orange
        ],
        "stone": [
            (np.array([0, 0, 100]), np.array([180, 50, 200])),  # Gray
        ],
        "gold": [
            (np.array([20, 100, 100]), np.array([30, 255, 255])),  # Yellow/Gold
        ],
    }
    
    if resource_type == "all":
        types_to_check = ["food", "wood", "stone", "gold"]
    else:
        types_to_check = [resource_type]
    
    for res_type in types_to_check:
        if res_type in color_ranges:
            for lower, upper in color_ranges[res_type]:
                # Create mask for this color range
                mask = cv2.inRange(hsv, lower, upper)
                
                # Find contours
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    area = cv2.contourArea(contour)
                    # Filter by size (adjust based on your screen resolution)
                    if 500 < area < 50000:  # Adjust these values
                        x, y, w, h = cv2.boundingRect(contour)
                        resources.append((x, y, w, h, res_type))
    
    return resources

def find_template_on_screen(screenshot, template_path, threshold=0.7):
    """
    Find a template image on the screen using template matching.
    
    Args:
        screenshot: OpenCV image (BGR format)
        template_path: Path to template image file
        threshold: Matching threshold (0.0 to 1.0)
    
    Returns:
        List of (x, y, width, height) tuples for matches
    """
    if screenshot is None or not os.path.exists(template_path):
        return []
    
    template = cv2.imread(template_path)
    if template is None:
        return []
    
    # Template matching
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= threshold)
    
    matches = []
    for pt in zip(*locations[::-1]):  # Switch x and y coordinates
        matches.append((pt[0], pt[1], template.shape[1], template.shape[0]))
    
    # Remove overlapping matches
    matches = remove_overlapping_matches(matches)
    
    return matches

def find_button_by_template(template_filename, threshold=0.7):
    """
    Find a button on screen using template matching.
    
    Args:
        template_filename: Name of the template image file (e.g., "plus_rrslvl.png")
        threshold: Matching threshold (0.0 to 1.0)
    
    Returns:
        (x, y, width, height) tuple or None if not found
    """
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(script_dir, template_filename)
    
    screenshot = capture_screen()
    if screenshot is None:
        return None
    
    matches = find_template_on_screen(screenshot, template_path, threshold)
    
    if matches:
        # Return the best match (first one after removing overlaps)
        return matches[0]
    
    return None

def click_button_by_template(template_filename, threshold=0.7):
    """
    Find and click a button using template matching.
    
    Args:
        template_filename: Name of the template image file
        threshold: Matching threshold
    
    Returns:
        True if button was found and clicked, False otherwise
    """
    button = find_button_by_template(template_filename, threshold)
    if button:
        x, y, w, h = button
        center_x = x + w // 2
        center_y = y + h // 2
        print(f"Found {template_filename} button at ({center_x}, {center_y})")
        return random_click(center_x, center_y, w, h, padding=5)
    else:
        print(f"Could not find {template_filename} button")
        return False

def wait_for_loading_screen(max_wait=60):
    """
    Wait for loading screen and click on screen every 3 seconds until loading screen is gone.
    
    Args:
        max_wait: Maximum time to wait in seconds
    
    Returns:
        True if loading completed, False if timeout
    """
    print("Waiting for loading screen...")
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        screenshot = capture_screen()
        if screenshot is None:
            print("Failed to capture screen, waiting...")
            time.sleep(3)
            continue
        
        # Check if loading screen is present
        loading_button = find_button_by_template("loading.png", threshold=0.7)
        
        if loading_button:
            # Click on screen (center of screen)
            screen_center_x = screenshot.shape[1] // 2
            screen_center_y = screenshot.shape[0] // 2
            print("Loading screen detected, clicking to continue...")
            random_click(screen_center_x, screen_center_y, 0, 0, padding=0)
            time.sleep(3)  # Wait 3 seconds before checking again
        else:
            print("Loading screen no longer detected. Game loaded!")
            time.sleep(2)  # Small delay to ensure game is ready
            return True
    
    print(f"Timeout waiting for loading screen (waited {max_wait} seconds)")
    return False

def click_outside_map(max_attempts=10):
    """
    Detect and click the outside_map button to go outside the map.
    
    Args:
        max_attempts: Maximum number of attempts to find and click
    
    Returns:
        True if clicked successfully, False otherwise
    """
    print("Looking for outside_map button...")
    
    for attempt in range(max_attempts):
        if click_button_by_template("outside_map.png", threshold=0.7):
            print("Successfully clicked outside_map button")
            time.sleep(2)  # Wait for map to load
            return True
        else:
            print(f"Attempt {attempt + 1}/{max_attempts}: Could not find outside_map button, waiting...")
            time.sleep(2)
    
    print("Failed to find outside_map button after all attempts")
    return False

def remove_overlapping_matches(matches, overlap_threshold=0.5):
    """Remove overlapping matches, keeping the best ones"""
    if not matches:
        return []
    
    # Sort by confidence (if available) or just use first match
    filtered = []
    for match in matches:
        x, y, w, h = match
        overlap = False
        
        for existing in filtered:
            ex, ey, ew, eh = existing
            # Calculate overlap
            overlap_x = max(0, min(x + w, ex + ew) - max(x, ex))
            overlap_y = max(0, min(y + h, ey + eh) - max(y, ey))
            overlap_area = overlap_x * overlap_y
            match_area = w * h
            
            if overlap_area / match_area > overlap_threshold:
                overlap = True
                break
        
        if not overlap:
            filtered.append(match)
    
    return filtered

def gather_rss(resource_type="random", max_resources=10, gather_timeout=300, use_search=True, level="max", resource_weights=None):
    """
    Main RSS gathering function using the search feature (much more reliable!).
    
    Args:
        resource_type: Type of resource to gather ("food", "wood", "stone", "gold", "all", or "random")
                      If "random", will randomly select between food, wood, stone, gold with weighted chances
        max_resources: Maximum number of resources to gather
        gather_timeout: Maximum time to spend gathering (seconds)
        use_search: Use the game's search feature (recommended: True)
        level: Resource level to search for ("max" to use highest available, or int for specific level)
        resource_weights: Dict with resource types as keys and weights as values for random selection.
                         Example: {"food": 0.3, "wood": 0.3, "stone": 0.2, "gold": 0.2}
    """
    print(f"\n{'='*50}")
    print(f"Starting RSS Gathering - Type: {resource_type}, Level: {level}")
    if use_search:
        print("Using game's search feature (recommended)")
    if resource_type == "random":
        print("Using random resource selection with weighted chances")
    print(f"{'='*50}\n")
    
    start_time = time.time()
    resources_gathered = 0
    search_count = 0
    max_searches = 20  # Limit number of searches
    active_marches = 0  # Track how many marches are currently gathering
    max_marches = 5  # Maximum number of marches to use
    
    while resources_gathered < max_resources and search_count < max_searches:
        # Check timeout
        if time.time() - start_time > gather_timeout:
            print(f"Timeout reached. Gathered {resources_gathered} resources.")
            break
        
        if use_search:
            # Select resource type if using random selection
            current_resource_type = resource_type
            if resource_type == "random":
                current_resource_type = select_random_resource(resource_weights)
                print(f"Randomly selected resource type: {current_resource_type}")
            
            # Use the search feature to find resources
            print(f"\n--- Search #{search_count + 1} ---")
            if use_search_feature(current_resource_type, level):
                search_count += 1
                
                # Wait for search results to appear
                human_delay(2, 3)
                
                # Capture screen and find highlighted resources
                screenshot = capture_screen()
                if screenshot is None:
                    print("Failed to capture screen after search")
                    time.sleep(2)
                    continue
                
                # Find highlighted resources from search
                print("Looking for highlighted resources...")
                resources = find_highlighted_resources(screenshot)
                
                if not resources:
                    print("No highlighted resources found. Trying fallback detection...")
                    # Fallback to regular detection
                    resources = find_resource_nodes(screenshot, current_resource_type)
                    # Convert format if needed
                    if resources and len(resources[0]) > 4:
                        resources = [(r[0], r[1], r[2], r[3]) for r in resources]
                
                if resources:
                    print(f"Found {len(resources)} resources")
                    
                    # Sort by distance from center
                    screen_center_x = screenshot.shape[1] // 2
                    screen_center_y = screenshot.shape[0] // 2
                    
                    resources.sort(key=lambda r: 
                        ((r[0] + r[2]//2 - screen_center_x)**2 + 
                         (r[1] + r[3]//2 - screen_center_y)**2)**0.5)
                    
                    # Send all 5 marches to different resources
                    # Use send_march_to_resource function for each resource
                    clicked_this_search = 0
                    resources_to_click = min(max_marches, len(resources))
                    
                    print(f"Sending {resources_to_click} marches to resources...")
                    
                    # Send marches to resources (one per preset)
                    for i, (x, y, w, h) in enumerate(resources[:resources_to_click]):
                        preset_number = (i % 5) + 1  # Cycle through presets 1-5
                        
                        if send_march_to_resource(x, y, w, h, preset_number):
                            clicked_this_search += 1
                            resources_gathered += 1
                            print(f"✓ Sent march {preset_number} to resource (Total: {resources_gathered}/{max_resources})")
                        else:
                            print(f"✗ Failed to send march {preset_number} to resource")
                    
                    if clicked_this_search > 0:
                        print(f"Successfully sent {clicked_this_search} marches to resources")
                        # Wait a bit for all marches to be dispatched
                        time.sleep(3)
                    else:
                        print("No marches were successfully sent this search")
                        time.sleep(2)
                else:
                    print("No resources found after search")
                    time.sleep(3)
            else:
                print("Search feature failed, waiting...")
                time.sleep(3)
        else:
            # Old method: direct pixel detection (less reliable)
            print("Using direct pixel detection (not recommended)...")
            screenshot = capture_screen()
            if screenshot is None:
                print("Failed to capture screen. Waiting...")
                human_delay(2, 4)
                continue
            
            resources = find_resource_nodes(screenshot, resource_type)
            
            if not resources:
                print("No resources found. Scrolling or waiting...")
                human_delay(3, 5)
                continue
            
            # Sort and click (same as before)
            screen_center_x = screenshot.shape[1] // 2
            screen_center_y = screenshot.shape[0] // 2
            
            resources.sort(key=lambda r: 
                ((r[0] + r[2]//2 - screen_center_x)**2 + 
                 (r[1] + r[3]//2 - screen_center_y)**2)**0.5)
            
            for x, y, w, h, res_type in resources[:3]:
                center_x = x + w // 2
                center_y = y + h // 2
                
                print(f"Clicking {res_type} resource at ({center_x}, {center_y})...")
                
                if random_click(center_x, center_y, w, h, padding=10):
                    resources_gathered += 1
                    print(f"✓ Gathered resource #{resources_gathered}/{max_resources}")
                    human_delay(2, 4)
                    human_delay(1, 2)
                    break
            else:
                human_delay(2, 3)
    
    print(f"\n{'='*50}")
    print(f"Gathering complete! Total resources: {resources_gathered}")
    print(f"Total searches performed: {search_count}")
    print(f"{'='*50}\n")

def main():
    """Main function - Fully automated RSS gathering bot"""
    print("=" * 50)
    print("RSS Bot for Rise of Kingdoms - Automated Mode")
    print("=" * 50)
    print("Configuration:")
    print("  - Resource types: Random (food, wood, stone, gold)")
    print("  - Level: Maximum (8)")
    print("  - Marches: 5")
    print("  - Mode: Fully automated (no user input)")
    print("=" * 50)
    
    # Check if Nox is already running
    if check_adb_connection():
        print("Nox Player appears to be already running. Continuing...")
    else:
        # Launch Nox Player
        print("Launching Nox Player...")
        if not launch_nox():
            print("ERROR: Failed to launch Nox Player. Exiting.")
            return
    
    # Wait a bit for everything to settle
    print("Waiting for Nox to initialize...")
    time.sleep(3)
    
    # Launch Rise of Kingdoms
    print("Launching Rise of Kingdoms...")
    if not launch_rise_of_kingdoms():
        print("\nERROR: Failed to launch Rise of Kingdoms. Exiting.")
        return
    
    print("\n" + "=" * 50)
    print("Setup complete! Rise of Kingdoms should be opening.")
    print("Waiting for game to load...")
    print("=" * 50)
    
    # Wait for loading screen and click every 3 seconds until it's gone
    print("Waiting for loading screen to complete...")
    if not wait_for_loading_screen(max_wait=120):
        print("WARNING: Loading screen timeout, continuing anyway...")
    
    # Click outside_map button to go outside the map
    print("\nGoing outside the map...")
    if not click_outside_map(max_attempts=10):
        print("WARNING: Could not click outside_map button, continuing anyway...")
    
    time.sleep(2)  # Small delay after going outside map
    
    # Start automated gathering
    print("\n" + "=" * 50)
    print("Starting automated RSS gathering...")
    print("=" * 50)
    
    # Default settings for automated mode
    resource_type = "random"  # Randomly select between food, wood, stone, gold
    max_resources = 100  # Gather many resources (bot will run continuously)
    level = "max"  # Use maximum level (8)
    use_search = True  # Always use search feature
    gather_timeout = 3600 * 8  # 8 hours timeout (for overnight running)
    
    print(f"Settings:")
    print(f"  - Resource type: {resource_type} (random selection)")
    print(f"  - Max resources: {max_resources}")
    print(f"  - Level: {level} (will be set to 8)")
    print(f"  - Use search: {use_search}")
    print(f"  - Timeout: {gather_timeout // 3600} hours")
    print("=" * 50)
    
    # Start gathering
    gather_rss(
        resource_type=resource_type,
        max_resources=max_resources,
        gather_timeout=gather_timeout,
        use_search=use_search,
        level=level
    )
    
    print("\n" + "=" * 50)
    print("Bot session completed.")
    print("=" * 50)

if __name__ == "__main__":
    main()