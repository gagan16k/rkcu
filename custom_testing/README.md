# RKCU Custom Testing Tools

This directory contains various testing and utility scripts for developing and debugging per-key RGB functionality on Royal Kludge keyboards. These tools are primarily designed for developers and advanced users who want to test keyboard functionality, map key indices, or create custom lighting configurations.

## Files Overview

### Configuration Files

#### `complete_red_keyboard.json`
A comprehensive JSON configuration that sets all 113 keys (indices 0-112) to red (`ff0000`). This file is useful for:
- Testing if all keys are responsive to per-key RGB commands
- Verifying complete keyboard coverage
- Serving as a template for full-keyboard configurations

**Usage:**
```bash
python -m rkcu --set-keys-json custom_testing/complete_red_keyboard.json
```

#### `keyboard_mapping.json`
Contains the mapping between physical key names and their corresponding indices for the Royal Kludge keyboard. This file includes:
- Human-readable key names (e.g., "esc", "tab", "space")
- Their corresponding numerical indices used by the RKCU library
- Special keys and function keys mapping

**Structure:**
```json
{
  "mapped_keys": {
    "esc": 0,
    "tab": 2,
    "space": 60,
    ...
  }
}
```

### Testing Scripts

#### `sequential_key_test.py`
**Purpose:** Tests each key individually by lighting them up sequentially from index 0 to 112.

**Features:**
- Lights each key in red for 1 second
- 2-second interval between keys
- Comprehensive coverage of all possible key indices
- Graceful error handling for non-responsive keys
- Ctrl+C interrupt support

**Usage:**
```bash
python sequential_key_test.py
```

**What it does:**
1. Connects to the Royal Kludge keyboard
2. Iterates through key indices 0-112
3. Lights each key in red for 1 second
4. Clears the key and waits 2 seconds before the next key
5. Reports any keys that fail to respond

#### `keyboard_input_mapper.py`
**Purpose:** Interactive tool to map physical keys to their numerical indices by detecting key presses.

**Features:**
- Real-time key press detection
- RGB feedback showing which key index is being mapped
- Automatic skipping of non-responsive indices after timeout
- Saves mapping data to `keyboard_mapping.json`
- Resume capability for interrupted sessions

**Usage:**
```bash
python keyboard_input_mapper.py
```

**How it works:**
1. Lights up the current key index being mapped
2. Waits for you to press the corresponding physical key
3. Records the key press and moves to the next index
4. Auto-skips indices after 5 seconds if no key is found
5. Saves the complete mapping when finished

#### `key_lighter.py`
**Purpose:** Real-time key lighting tool that responds to key presses by lighting up the pressed keys.

**Features:**
- Live key press detection
- Immediate RGB feedback for pressed keys
- Customizable light duration
- Uses the mapping from `keyboard_mapping.json`
- Demo mode for showcasing per-key RGB functionality

**Usage:**
```bash
python key_lighter.py
```

**Interactive commands:**
- Press any key to light it up
- Keys stay lit for a configurable duration
- Great for testing individual key responsiveness

#### `fill_skipped_indices.py`
**Purpose:** Utility to handle gaps in key mapping and fill in missing indices.

**Features:**
- Identifies skipped or unmapped key indices
- Interactive mode to manually map missing keys
- Updates existing mapping files
- Validation of mapping completeness

**Usage:**
```bash
python fill_skipped_indices.py
```

## Creating Custom Configurations

### Basic Template
```json
{
  "comment": "My custom configuration",
  "key_index": "hex_color",
  "0": "ff0000",
  "1": "00ff00",
  "2": "0000ff"
}
```

### Gaming Setup Example
```json
{
  "comment": "Gaming setup - WASD red, numbers blue",
  "14": "ff0000",
  "9": "ff0000", 
  "15": "ff0000",
  "21": "ff0000",
  "7": "0000ff",
  "13": "0000ff",
  "19": "0000ff"
}
```