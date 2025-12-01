# RSS Bot for Rise of Kingdoms

A bot that automatically gathers resources (RSS) in Rise of Kingdoms using Nox Player emulator.

## Features

- ✅ Automatically launches Nox Player
- ✅ Launches Rise of Kingdoms game
- ✅ Captures screen from emulator
- ✅ Finds resource nodes (Food, Wood, Stone, Gold)
- ✅ Random click positions to avoid anti-cheat detection
- ✅ Human-like delays and movement patterns

## Installation

1. Install required Python packages:
```bash
pip install -r requirements.txt
```

2. Make sure Nox Player is installed (default: `D:\Program Files\Nox\bin\Nox.exe`)

3. Make sure ADB is accessible (Nox includes its own ADB)

## Usage

Run the bot:
```bash
python rrs_bot_rok.py
```

The bot will:
1. Launch Nox Player (if not running)
2. Launch Rise of Kingdoms
3. Wait for game to load
4. Ask you to choose resource type to gather
5. Start gathering resources

## How It Works

### Anti-Cheat Evasion

The bot uses several techniques to avoid detection:

1. **Random Click Positions**: Instead of clicking the exact center of buttons, it clicks at random positions within the button bounds
2. **Human-like Delays**: Random delays between actions (0.5-1.5 seconds)
3. **Natural Movement**: Waits for animations and uses realistic timing

### Resource Detection

Currently uses color-based detection in HSV color space. You may need to adjust the color ranges in the `find_resource_nodes()` function based on your game version and graphics settings.

### Improving Detection

For better accuracy, you can:

1. **Use Template Matching**: 
   - Take screenshots of resource nodes
   - Save them as template images
   - Use `find_template_on_screen()` function

2. **Adjust Color Ranges**:
   - Edit the `color_ranges` dictionary in `find_resource_nodes()`
   - Use a color picker tool to get exact HSV values

3. **Calibrate Size Filters**:
   - Adjust the `area` filter in `find_resource_nodes()` based on your screen resolution

## Configuration

### Screen Resolution
The bot works with any resolution, but you may need to adjust:
- Resource size filters (in `find_resource_nodes()`)
- Click padding values (in `random_click()`)

### Resource Types
Supported resource types:
- `"all"` - Gather all resource types
- `"food"` - Food only
- `"wood"` - Wood only
- `"stone"` - Stone only
- `"gold"` - Gold only

## Troubleshooting

### Bot can't find resources
- Make sure you're on the world map (not in city)
- Adjust color ranges in `find_resource_nodes()`
- Try using template matching instead

### Clicks not working
- Check ADB connection: `adb devices`
- Make sure Nox Player window is active
- Verify screen coordinates are correct

### Game not launching
- Check if Rise of Kingdoms is installed in Nox
- Verify package name is correct
- Try manually launching the game first

## Future Improvements

- [ ] Template matching for more accurate detection
- [ ] Auto-scrolling to find more resources
- [ ] Return to city when inventory is full
- [ ] Multiple account support
- [ ] GUI interface
- [ ] Resource statistics tracking

## Notes

⚠️ **Warning**: Using bots may violate the game's terms of service. Use at your own risk.

## License

This is a personal project for educational purposes.

