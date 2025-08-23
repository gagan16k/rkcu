#!/usr/bin/env python3
import keyboard
import time
import json
import sys
import os
import threading
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from rkcu.config import get_base_config
    from rkcu.utils import RKCU
    KEYBOARD_CONTROL_AVAILABLE = True
except ImportError:
    KEYBOARD_CONTROL_AVAILABLE = False
    print("Warning: RKCU modules not available. Keyboard lighting features disabled.")


class KeyboardInputMapper:
    
    def __init__(self, enable_rgb_feedback=True, skip_timeout=5):
        self.enable_rgb_feedback = enable_rgb_feedback and KEYBOARD_CONTROL_AVAILABLE
        self.skip_timeout = skip_timeout
        self.current_index = 0
        self.key_mapping = {}
        self.key_sequence = []
        self.mapping_complete = False
        self.skipped_indices = []
        self.skip_timer = None
        
        self.rk = None
        if self.enable_rgb_feedback:
            try:
                self.rk = RKCU(0x258a, 0x00e0)
                print("Connected to Royal Kludge keyboard for RGB feedback")
                self.light_current_index()
                self.start_skip_timer()
            except Exception as e:
                print(f"Could not connect to RGB keyboard: {e}")
                self.enable_rgb_feedback = False
        else:
            self.start_skip_timer()
    
    def start_skip_timer(self):
        if self.mapping_complete:
            return
            
        if self.skip_timer:
            self.skip_timer.cancel()
        
        self.skip_timer = threading.Timer(self.skip_timeout, self.auto_skip_index)
        self.skip_timer.start()
    
    def auto_skip_index(self):
        if self.mapping_complete:
            return
            
        print(f"\nTimeout reached ({self.skip_timeout}s). Auto-skipping index {self.current_index} (no physical key detected)")
        
        self.skipped_indices.append(self.current_index)
        self.current_index += 1
        
        if not self.mapping_complete:
            self.light_current_index()
            print(f"Index {self.current_index} is now lit up (BLUE). Press the corresponding key or wait {self.skip_timeout}s to auto-skip")
            self.start_skip_timer()
    
    def cancel_skip_timer(self):
        if self.skip_timer:
            self.skip_timer.cancel()
            self.skip_timer = None

    def light_current_index(self):
        if not self.enable_rgb_feedback or not self.rk or self.mapping_complete:
            return
            
        try:
            config = get_base_config()
            # Set brightness to 5 for visibility
            config.ANIMATION_BRIGHTNESS = 5
            config.PER_KEY_RGB.clear_all()
            
            for key_info in self.key_sequence:
                config.PER_KEY_RGB.set_key_color_hex(key_info['index'], "00ff00")
            
            config.PER_KEY_RGB.set_key_color_hex(self.current_index, "0080ff")
            self.rk.apply_config(config)
        except Exception as e:
            print(f"Warning: Could not light up key at index {self.current_index}: {e}")
    
    def clear_all_lights(self):
        if not self.enable_rgb_feedback or not self.rk:
            return
            
        try:
            config = get_base_config()
            # Set brightness to 5 for visibility
            config.ANIMATION_BRIGHTNESS = 5
            config.PER_KEY_RGB.clear_all()
            self.rk.apply_config(config)
        except Exception as e:
            print(f"Warning: Could not clear RGB lighting: {e}")
    
    def skip_current_index(self):
        print(f"Skipping index {self.current_index} (no physical key)")
        
        self.skipped_indices.append(self.current_index)
        self.current_index += 1
        
        if not self.mapping_complete:
            self.light_current_index()
            print(f"Index {self.current_index} is now lit up (BLUE). Press the corresponding key or wait {self.skip_timeout}s to auto-skip")
            self.start_skip_timer()

    def on_key_press(self, event):
        if self.mapping_complete:
            return
            
        key_name = event.name.lower().strip()
        
        self.start_skip_timer()
        
        if key_name in self.key_mapping:
            print(f"Key '{key_name}' already mapped to index {self.key_mapping[key_name]}. Ignoring...")
            return
        
        self.key_mapping[key_name] = self.current_index
        self.key_sequence.append({
            'key': key_name,
            'index': self.current_index
        })
        
        print(f"Key '{key_name}' -> Index: {self.current_index}")
        
        if self.enable_rgb_feedback:
            self.highlight_key(self.current_index, "00ff88", 0.5)
        
        self.current_index += 1
        self.light_current_index()
        
        if not self.mapping_complete:
            print(f"Index {self.current_index} is now lit up (BLUE). Press the corresponding key or wait {self.skip_timeout}s to auto-skip")
    
    def on_key_release(self, event):
        pass
    
    def highlight_key(self, key_index, color="00ff00", duration=0.3):
        if not self.enable_rgb_feedback or not self.rk:
            return
            
        try:
            config = get_base_config()
            # Set brightness to 5 for visibility
            config.ANIMATION_BRIGHTNESS = 5
            config.PER_KEY_RGB.clear_all()
            
            for key_info in self.key_sequence:
                if key_info['index'] != key_index:
                    config.PER_KEY_RGB.set_key_color_hex(key_info['index'], "00ff00")
            
            config.PER_KEY_RGB.set_key_color_hex(key_index, "00ff88")
            self.rk.apply_config(config)
            
            time.sleep(duration)
            self.light_current_index()
                
        except Exception as e:
            print(f"Error highlighting key {key_index}: {e}")
    
    def show_statistics(self):
        print("\n" + "="*60)
        print("SEQUENTIAL KEY MAPPING STATISTICS")
        print("="*60)
        
        if not self.key_mapping:
            print("No keys have been mapped yet.")
            return
        
        print(f"Total keys mapped: {len(self.key_mapping)}")
        print(f"Total indices skipped: {len(self.skipped_indices)}")
        if self.skipped_indices:
            print(f"Skipped indices: {', '.join(map(str, self.skipped_indices))}")
        print(f"Key indices range: 0 to {self.current_index - 1}")
        
        print(f"\nKey Mapping Sequence:")
        print("-" * 40)
        for i, key_info in enumerate(self.key_sequence):
            key = key_info['key']
            index = key_info['index']
            print(f"{index:3d}: {key:15}")
        
        if self.skipped_indices:
            print(f"\nSkipped Indices:")
            print("-" * 20)
            for skipped in self.skipped_indices:
                print(f"{skipped:3d}: [NO PHYSICAL KEY]")
        
        if not self.mapping_complete:
            print(f"\nCurrent index: {self.current_index} (lit up in BLUE)")
            print(f"Press the corresponding key or wait {self.skip_timeout}s to auto-skip, or Ctrl+C to finish.")
    
    def export_session_data(self, filename=None):
        if filename is None:
            filename = "keyboard_mapping.json"
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(script_dir, filename)
        
        key_mapping = {}
        for key_info in self.key_sequence:
            key_mapping[key_info['key']] = key_info['index']
        
        detailed_data = {
            "mapped_keys": key_mapping,
            "skipped_indices": self.skipped_indices,
            "total_keys_mapped": len(key_mapping),
            "total_indices_skipped": len(self.skipped_indices),
            "index_range": f"0 to {self.current_index - 1}" if self.current_index > 0 else "None"
        }
        
        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                json.dump(detailed_data, f, indent=2, ensure_ascii=False)
            print(f"Keyboard mapping exported to: {full_path}")
            
            print(f"Total keys mapped: {len(key_mapping)}")
            if len(self.skipped_indices) > 0:
                print(f"Total indices skipped: {len(self.skipped_indices)} ({', '.join(map(str, self.skipped_indices))})")
            if len(key_mapping) > 0:
                print(f"Index range: 0 to {max(key_mapping.values())}")
                
        except Exception as e:
            print(f"Error exporting key mapping: {e}")
        
        return full_path
    
    def run_sequential_mapper(self):
        print("Sequential Keyboard Mapper - Royal Kludge Edition")
        print("=" * 60)
        print("INSTRUCTIONS:")
        print("   1. The current index will light up in BLUE on your keyboard")
        print("   2. Press the physical key that corresponds to that lit position")
        print("   3. The key will flash GREEN to confirm mapping")
        print("   4. The next index will automatically light up in BLUE")
        print(f"   5. If no key is pressed within {self.skip_timeout} seconds, the index auto-skips")
        print("   6. Press Ctrl+C when finished to save the mapping")
        print("")
        print("Note: Each key can only be mapped once!")
        if self.enable_rgb_feedback:
            print("BLUE = Current index to map")
            print("GREEN = Already mapped keys (stay lit)")
            print("BRIGHT GREEN = Confirmation flash")
        print("-" * 60)
        print(f"Index {self.current_index} is now lit up (BLUE). Press the corresponding key or wait {self.skip_timeout}s to auto-skip")
        
        keyboard.on_press(self.on_key_press)
        keyboard.on_release(self.on_key_release)
        
        try:
            keyboard.wait()
            
        except KeyboardInterrupt:
            print(f"\n\nMapping stopped by user at index {self.current_index}")
            self.mapping_complete = True
        
        finally:
            self.cancel_skip_timer()
            keyboard.unhook_all()
            
            if self.enable_rgb_feedback and self.rk:
                try:
                    self.clear_all_lights()
                    print("Cleared keyboard RGB lighting")
                except:
                    pass
            
            self.show_statistics()
            filename = self.export_session_data()
            
            print(f"\nSequential mapping complete!")
            print(f"Mapping saved to: {filename}")
            print(f"Total keys mapped: {len(self.key_mapping)}")
            if len(self.key_mapping) > 0:
                print(f"Index range: 0 to {self.current_index - 1}")
            
            return filename


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Sequential Keyboard Mapper for Royal Kludge RGB Keyboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Sequential Mapping Process:
  1. Run the program
  2. Press keys in the order you want them mapped to indices 0, 1, 2, etc.
  3. Press Ctrl+C when you've mapped all desired keys
  4. The mapping will be automatically exported to JSON

Examples:
  %(prog)s                    # Start sequential mapping
  %(prog)s --no-rgb           # Disable RGB feedback
  %(prog)s --export FILE.json # Export to specific filename
        """
    )
    
    parser.add_argument(
        '--no-rgb', action='store_true',
        help='Disable RGB keyboard feedback'
    )
    parser.add_argument(
        '--export', metavar='FILENAME',
        help='Specify output filename for the mapping (optional)'
    )
    parser.add_argument(
        '--timeout', type=int, default=5, metavar='SECONDS',
        help='Auto-skip timeout in seconds (default: 5)'
    )
    
    args = parser.parse_args()
    
    enable_rgb = not args.no_rgb
    mapper = KeyboardInputMapper(enable_rgb_feedback=enable_rgb, skip_timeout=args.timeout)
    
    filename = mapper.run_sequential_mapper()
    
    if args.export and filename:
        try:
            import shutil
            shutil.copy2(filename, args.export)
            print(f"Mapping also saved to: {args.export}")
        except Exception as e:
            print(f"Error copying to custom filename: {e}")


if __name__ == "__main__":
    main()