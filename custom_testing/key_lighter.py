import json
import os
import keyboard
import threading
import time
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from rkcu import RKCU
    from rkcu.config import get_base_config
    KEYBOARD_CONTROL_AVAILABLE = True
except ImportError:
    print("RKCU keyboard control not available")
    KEYBOARD_CONTROL_AVAILABLE = False

class KeyLighter:
    def __init__(self):
        self.mapped_keys = {}
        self.light_timers = {}
        self.rk = None
        self.keyboard_connected = False
        
        if KEYBOARD_CONTROL_AVAILABLE:
            try:
                self.rk = RKCU(0x258a, 0x00e0)
                self.keyboard_connected = True
                print("Connected to Royal Kludge keyboard for RGB feedback")
            except Exception as e:
                print(f"Warning: Could not connect to keyboard: {e}")
                self.keyboard_connected = False
        else:
            print("Warning: RKCU library not available. RGB lighting will not work.")
    
    def load_key_mapping(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(script_dir, "keyboard_mapping.json")
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'mapped_keys' in data:
                    self.mapped_keys = data['mapped_keys']
                    print(f"Loaded mapping for {len(self.mapped_keys)} keys")
                    return True
        except FileNotFoundError:
            print(f"Error: keyboard_mapping.json not found in {script_dir}")
        except json.JSONDecodeError:
            print("Error: Invalid JSON in keyboard_mapping.json")
        
        return False
    
    def light_key(self, key_index, duration=0.3):
        if not self.keyboard_connected or not self.rk:
            return
            
        try:
            config = get_base_config()
            # Set brightness to 5 for visibility
            config.ANIMATION_BRIGHTNESS = 5
            config.PER_KEY_RGB.clear_all()
            config.PER_KEY_RGB.set_key_color(key_index, 255, 255, 255)
            self.rk.apply_config(config)
            
            key_str = str(key_index)
            if key_str in self.light_timers:
                self.light_timers[key_str].cancel()
            
            timer = threading.Timer(duration, self.turn_off_key, args=[key_index])
            self.light_timers[key_str] = timer
            timer.start()
        except Exception as e:
            print(f"Error lighting key {key_index}: {e}")
    
    def turn_off_key(self, key_index):
        if not self.keyboard_connected or not self.rk:
            return
            
        try:
            config = get_base_config()
            # Set brightness to 0 when turning off keys
            config.ANIMATION_BRIGHTNESS = 0
            config.PER_KEY_RGB.clear_all()
            self.rk.apply_config(config)
            
            key_str = str(key_index)
            if key_str in self.light_timers:
                del self.light_timers[key_str]
        except Exception as e:
            print(f"Error turning off key {key_index}: {e}")
    
    def on_key_press(self, event):
        key_name = event.name
        if key_name in self.mapped_keys:
            index = self.mapped_keys[key_name]
            print(f"Key '{key_name}' pressed - Index: {index}")
            self.light_key(index)
    
    def start_monitoring(self):
        if not self.load_key_mapping():
            print("Failed to load key mapping. Exiting.")
            return
        
        print("Monitoring keyboard input. Press Ctrl+C to exit.")
        if self.keyboard_connected:
            print("Mapped keys will light up white when pressed.")
        else:
            print("RGB feedback disabled - only console output will show.")
        print()
        
        keyboard.on_press(self.on_key_press)
        
        try:
            keyboard.wait()
        except KeyboardInterrupt:
            print("\nStopping key monitoring...")
        finally:
            if self.keyboard_connected and self.rk:
                try:
                    config = get_base_config()
                    # Set brightness to 0 when cleaning up (no keys pressed)
                    config.ANIMATION_BRIGHTNESS = 0
                    config.PER_KEY_RGB.clear_all()
                    self.rk.apply_config(config)
                except:
                    pass
            
            for timer in self.light_timers.values():
                timer.cancel()

if __name__ == "__main__":
    lighter = KeyLighter()
    lighter.start_monitoring()
