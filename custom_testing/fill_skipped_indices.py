import json
import os
import sys
import time

# Add the parent directory to the path to import rkcu modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from rkcu.utils import RKCU
from rkcu.config import get_base_config

def load_mapping_data(filename="keyboard_mapping.json"):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, filename)
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {filename} not found in {script_dir}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {filename}")
        return None

def save_mapping_data(data, filename="keyboard_mapping.json"):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, filename)
    
    try:
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving file: {e}")
        return False

def light_key(rk, key_index, color_hex="ff0000"):
    """Light up a specific key with the given color."""
    try:
        config = get_base_config()
        config.ANIMATION_BRIGHTNESS = 5  # Set brightness to 5 for visibility
        config.PER_KEY_RGB.clear_all()
        config.PER_KEY_RGB.set_key_color_hex(key_index, color_hex)
        rk.apply_config(config)
        return True
    except Exception as e:
        print(f"Error lighting key {key_index}: {e}")
        return False

def turn_off_all_keys(rk):
    """Turn off all keys."""
    try:
        config = get_base_config()
        config.ANIMATION_BRIGHTNESS = 0  # Set brightness to 0 to turn off
        config.PER_KEY_RGB.clear_all()
        rk.apply_config(config)
        return True
    except Exception as e:
        print(f"Error turning off keys: {e}")
        return False

def manual_key_mapping():
    """Manually map keys by lighting them up one by one."""
    data = load_mapping_data()
    if not data:
        return
    
    if not data.get('skipped_indices'):
        print("No skipped indices to fill.")
        return
    
    # Initialize RKCU connection
    try:
        rk = RKCU(0x258a, 0x00e0)
        print("Connected to keyboard device")
    except Exception as e:
        print(f"Error connecting to keyboard: {e}")
        print("Make sure the keyboard is connected and you have the necessary permissions.")
        return
    
    mapped_keys = data.get('mapped_keys', {})
    skipped_indices = data.get('skipped_indices', [])
    newly_mapped = {}
    remaining_skipped = []
    
    print(f"\nFound {len(skipped_indices)} skipped indices to test: {sorted(skipped_indices)}")
    print("\nThis tool will light up each skipped index one by one.")
    print("For each lit key:")
    print("- If you can see a key light up, enter the key name (e.g., 'numpad 1', 'end', 'pause')")
    print("- If no key lights up, just press Enter to skip")
    print("- Type 'quit' to exit\n")
    
    turn_off_all_keys(rk)
    time.sleep(0.5)
    
    try:
        for index in sorted(skipped_indices):
            print(f"\n--- Testing Index {index} ---")
            print("Lighting up index... Look for a red key on your keyboard.")
            
            if light_key(rk, index, "ff0000"):
                time.sleep(0.2)
                
                user_input = input(f"Key name for index {index} (or Enter to skip): ").strip().lower()
                
                if user_input == 'quit':
                    print("Exiting...")
                    break
                elif user_input and user_input != '':
                    if user_input in mapped_keys:
                        print(f"Warning: Key '{user_input}' is already mapped to index {mapped_keys[user_input]}")
                        confirm = input("Do you want to reassign it? (y/n): ").strip().lower()
                        if confirm != 'y':
                            remaining_skipped.append(index)
                            continue
                    
                    newly_mapped[user_input] = index
                    print(f"✓ Mapped '{user_input}' to index {index}")
                else:
                    remaining_skipped.append(index)
                    print(f"⊘ Skipped index {index} (no key visible)")
            else:
                print(f"Failed to light up index {index}")
                remaining_skipped.append(index)
            
            turn_off_all_keys(rk)
            
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
    except Exception as e:
        print(f"Error during mapping: {e}")
    finally:
        turn_off_all_keys(rk)
    
    mapped_keys.update(newly_mapped)
    data['mapped_keys'] = mapped_keys
    data['skipped_indices'] = remaining_skipped
    data['total_keys_mapped'] = len(mapped_keys)
    data['total_indices_skipped'] = len(remaining_skipped)
    
    if save_mapping_data(data):
        print(f"\n=== MAPPING RESULTS ===")
        print(f"Newly mapped keys: {len(newly_mapped)}")
        if newly_mapped:
            for key_name, index in newly_mapped.items():
                print(f"  - '{key_name}' → index {index}")
        print(f"Total keys mapped: {len(mapped_keys)}")
        print(f"Remaining skipped indices: {len(remaining_skipped)}")
        if remaining_skipped:
            print(f"  Indices: {sorted(remaining_skipped)}")
        print("\nMapping data saved successfully!")
    else:
        print("Failed to save updated mapping.")

if __name__ == "__main__":
    manual_key_mapping()
