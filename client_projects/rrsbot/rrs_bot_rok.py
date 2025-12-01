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
    
    # Level controls
    "level_plus": None,  # Plus button for level - add coordinates
    "level_minus": None,  # Minus button for level - add coordinates
    
    # Final SEARCH button (position changes based on selected resource type)
    "final_search_food": (372, 465, 527, 517),  # SEARCH button when food is selected
    "final_search_wood": (565, 465, 718, 513),  # SEARCH button when wood is selected
    "final_search_stone": (758, 465, 911, 513),  # SEARCH button when stone is selected (calculated)
    "final_search_gold": (951, 465, 1104, 513),  # SEARCH button when gold is selected (calculated)
    "final_search": None,  # Generic fallback (will use resource-specific if available)
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

def use_search_feature(resource_type="all", level=1, use_coords=True):
    """
    Use the game's search feature to find resources.
    Correct flow:
    1. Click initial search button (magnifying glass icon)
    2. Select resource type (Cropland, Logging Camp, etc.)
    3. Set level using level controls
    4. Click final SEARCH button
    
    Args:
        resource_type: "food", "wood", "stone", "gold", or "all"
        level: Resource level to search for (default: 1)
        use_coords: If True, use hardcoded coordinates (more reliable)
    
    Returns: True if search was successful, False otherwise
    """
    print(f"Using search feature for {resource_type} resources (level {level})...")
    
    # Step 1: Click the initial search button (magnifying glass icon)
    print("Step 1: Clicking initial search button (magnifying glass)...")
    if use_coords and BUTTON_COORDS["initial_search"] is not None:
        # Use hardcoded coordinates
        if click_button_by_coords("initial_search"):
            human_delay(2, 3)  # Wait for search menu to open
        else:
            print("ERROR: Failed to click initial search button using coordinates!")
            return False
    else:
        # Fallback to image detection
        screenshot = capture_screen()
        if screenshot is None:
            print("Failed to capture screen")
            return False
        
        initial_search_button = find_initial_search_button(screenshot)
        if initial_search_button:
            x, y, w, h = initial_search_button
            center_x = x + w // 2
            center_y = y + h // 2
            print(f"Found initial search button at ({center_x}, {center_y})")
            random_click(center_x, center_y, w, h, padding=10)
            human_delay(2, 3)  # Wait for search menu to open
        else:
            print("ERROR: Could not find initial search button!")
            return False
    
    # Step 2: Select resource type (if not "all")
    if resource_type != "all":
        print(f"Step 2: Selecting {resource_type} resource type...")
        button_key = f"search_{resource_type}"
        
        if use_coords and button_key in BUTTON_COORDS and BUTTON_COORDS[button_key] is not None:
            # Use hardcoded coordinates
            if click_button_by_coords(button_key):
                human_delay(1, 2)
            else:
                print(f"Warning: Failed to click {resource_type} button using coordinates")
        else:
            # Fallback to image detection
            screenshot = capture_screen()
            if screenshot is None:
                print("Failed to capture screen after opening search menu")
                return False
            
            res_button = find_resource_type_button(screenshot, resource_type)
            if res_button:
                x, y, w, h = res_button
                center_x = x + w // 2
                center_y = y + h // 2
                print(f"Found {resource_type} button at ({center_x}, {center_y})")
                random_click(center_x, center_y, w, h, padding=5)
                human_delay(1, 2)
            else:
                print(f"Warning: Could not find {resource_type} button, continuing anyway...")
    
    # Step 3: Adjust level if needed
    if level != 1:
        print(f"Step 3: Adjusting level to {level}...")
        
        if use_coords and BUTTON_COORDS["level_plus"] is not None:
            # Use hardcoded coordinates
            print(f"Clicking plus button {level - 1} times...")
            for i in range(level - 1):
                if click_button_by_coords("level_plus"):
                    human_delay(0.4, 0.6)
                else:
                    print(f"Warning: Failed to click plus button on attempt {i+1}")
        else:
            # Fallback to image detection
            screenshot = capture_screen()
            if screenshot is None:
                print("Failed to capture screen for level adjustment")
                return False
            
            controls = find_level_controls(screenshot)
            
            if controls:
                # Click plus button (level - 1) times to increase from level 1
                if 'plus' in controls and level > 1:
                    x, y, w, h = controls['plus']
                    center_x = x + w // 2
                    center_y = y + h // 2
                    print(f"Clicking plus button {level - 1} times...")
                    for i in range(level - 1):
                        random_click(center_x, center_y, w, h, padding=5)
                        human_delay(0.4, 0.6)
            else:
                print("Warning: Could not find level controls, using default level 1")
    
    # Step 4: Find and click final SEARCH button (position depends on resource type)
    print("Step 4: Clicking final SEARCH button...")
    
    if use_coords:
        # Use resource-specific search button if available
        search_button_key = f"final_search_{resource_type}" if resource_type != "all" else "final_search"
        
        # Try resource-specific button first
        if search_button_key in BUTTON_COORDS and BUTTON_COORDS[search_button_key] is not None:
            if click_button_by_coords(search_button_key):
                human_delay(2, 3)  # Wait for search results
                return True
            else:
                print(f"ERROR: Failed to click {search_button_key} using coordinates!")
        
        # Fallback to generic final_search
        if BUTTON_COORDS["final_search"] is not None:
            if click_button_by_coords("final_search"):
                human_delay(2, 3)  # Wait for search results
                return True
            else:
                print("ERROR: Failed to click final SEARCH button using coordinates!")
                return False
        else:
            print("ERROR: No coordinates set for final SEARCH button!")
            return False
    else:
        # Fallback to image detection
        screenshot = capture_screen()
        if screenshot is None:
            print("Failed to capture screen for final search button")
            return False
        
        search_button = find_search_button(screenshot)
        
        if search_button:
            x, y, w, h = search_button
            center_x = x + w // 2
            center_y = y + h // 2
            print(f"Found final SEARCH button at ({center_x}, {center_y})")
            random_click(center_x, center_y, w, h, padding=10)
            human_delay(2, 3)  # Wait for search results
            return True
        else:
            print("ERROR: Could not find final SEARCH button!")
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

def gather_rss(resource_type="all", max_resources=10, gather_timeout=300, use_search=True, level=1):
    """
    Main RSS gathering function using the search feature (much more reliable!).
    
    Args:
        resource_type: Type of resource to gather ("food", "wood", "stone", "gold", "all")
        max_resources: Maximum number of resources to gather
        gather_timeout: Maximum time to spend gathering (seconds)
        use_search: Use the game's search feature (recommended: True)
        level: Resource level to search for (default: 1)
    """
    print(f"\n{'='*50}")
    print(f"Starting RSS Gathering - Type: {resource_type}, Level: {level}")
    if use_search:
        print("Using game's search feature (recommended)")
    print(f"{'='*50}\n")
    
    start_time = time.time()
    resources_gathered = 0
    search_count = 0
    max_searches = 20  # Limit number of searches
    
    while resources_gathered < max_resources and search_count < max_searches:
        # Check timeout
        if time.time() - start_time > gather_timeout:
            print(f"Timeout reached. Gathered {resources_gathered} resources.")
            break
        
        if use_search:
            # Use the search feature to find resources
            print(f"\n--- Search #{search_count + 1} ---")
            if use_search_feature(resource_type, level):
                search_count += 1
                
                # Wait for search results to appear
                human_delay(2, 3)
                
                # Capture screen and find highlighted resources
                screenshot = capture_screen()
                if screenshot is None:
                    print("Failed to capture screen after search")
                    human_delay(2, 3)
                    continue
                
                # Find highlighted resources from search
                print("Looking for highlighted resources...")
                resources = find_highlighted_resources(screenshot)
                
                if not resources:
                    print("No highlighted resources found. Trying fallback detection...")
                    # Fallback to regular detection
                    resources = find_resource_nodes(screenshot, resource_type)
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
                    
                    # Click on closest resources
                    clicked_this_search = 0
                    for x, y, w, h in resources[:5]:  # Try top 5 closest
                        if resources_gathered >= max_resources:
                            break
                        
                        center_x = x + w // 2
                        center_y = y + h // 2
                        
                        print(f"Clicking resource at ({center_x}, {center_y})...")
                        
                        if random_click(center_x, center_y, w, h, padding=10):
                            resources_gathered += 1
                            clicked_this_search += 1
                            print(f"✓ Gathered resource #{resources_gathered}/{max_resources}")
                            
                            # Wait for gathering to start
                            human_delay(2, 3)
                            
                            # Small delay between clicks
                            human_delay(1, 2)
                    
                    if clicked_this_search == 0:
                        print("No resources were successfully clicked this search")
                        human_delay(2, 3)
                else:
                    print("No resources found after search")
                    human_delay(3, 5)
            else:
                print("Search feature failed, waiting...")
                human_delay(3, 5)
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
    """Main function"""
    print("=" * 50)
    print("RSS Bot for Rise of Kingdoms")
    print("=" * 50)
    
    # Check if Nox is already running
    if check_adb_connection():
        print("Nox Player appears to be already running!")
        user_input = input("Do you want to launch Rise of Kingdoms anyway? (y/n): ")
        if user_input.lower() != 'y':
            return
    else:
        # Launch Nox Player
        if not launch_nox():
            return
    
    # Wait a bit for everything to settle
    time.sleep(3)
    
    # Launch Rise of Kingdoms
    if not launch_rise_of_kingdoms():
        print("\nFailed to launch Rise of Kingdoms. Please check the errors above.")
        return
    
    print("\n" + "=" * 50)
    print("Setup complete! Rise of Kingdoms should be opening.")
    print("Waiting for game to load...")
    print("=" * 50)
    
    # Wait for game to fully load
    time.sleep(10)
    
    # Ask user if they want to start gathering
    print("\n" + "=" * 50)
    print("RSS Gathering Options")
    print("=" * 50)
    print("1. Gather all resources")
    print("2. Gather food only")
    print("3. Gather wood only")
    print("4. Gather stone only")
    print("5. Gather gold only")
    print("6. Skip gathering (just launch)")
    print("=" * 50)
    
    choice = input("Enter your choice (1-6): ").strip()
    
    resource_map = {
        "1": "all",
        "2": "food",
        "3": "wood",
        "4": "stone",
        "5": "gold",
    }
    
    if choice in resource_map:
        max_resources = input("How many resources to gather? (default: 10): ").strip()
        max_resources = int(max_resources) if max_resources.isdigit() else 10
        
        level_input = input("Resource level to search for? (default: 1): ").strip()
        level = int(level_input) if level_input.isdigit() else 1
        
        use_search_input = input("Use search feature? (recommended: y/n, default: y): ").strip().lower()
        use_search = use_search_input != 'n'
        
        gather_rss(resource_type=resource_map[choice], max_resources=max_resources, 
                  use_search=use_search, level=level)
    else:
        print("Skipping RSS gathering.")

if __name__ == "__main__":
    main()