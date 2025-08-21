"""
Key mapping utility for RK100 keyboard.
This utility helps determine the correct buffer indices for each key.
"""

class KeyMapper:
    """Utility to help determine correct key buffer indices."""
    
    def __init__(self, per_key_rgb, config):
        self.per_key_rgb = per_key_rgb
        self.config = config
        
    def test_key_mapping(self, test_color=(255, 0, 0)):
        """
        Test each buffer index to determine which physical key it corresponds to.
        This will light up keys one by one so you can identify the correct mapping.
        """
        import time
        from rkcu.utils import RKCU
        
        print("Starting key mapping test...")
        print("Each key will light up in red for 2 seconds.")
        print("Record which physical key lights up for each buffer index.")
        print("Press Ctrl+C to stop the test.\n")
        
        # Initialize RKCU
        try:
            rkcu = RKCU(0x258a, 0x00e0)  # RK100 VID/PID
        except Exception as e:
            print(f"Failed to connect to keyboard: {e}")
            return
        
        try:
            # Test buffer indices from 0 to 60 (RK100 typically has ~61 keys)
            for buffer_index in range(61):
                print(f"Testing buffer index {buffer_index}...")
                
                # Clear all keys first
                self.per_key_rgb.clear_all()
                
                # Set the test key using the proper method
                self.per_key_rgb.set_key_color(buffer_index, test_color[0], test_color[1], test_color[2])
                
                # Apply the configuration using the proper method
                if self.per_key_rgb.has_custom_colors():
                    self.config.CUSTOM_LIGHT_BUFFERS = self.per_key_rgb.get_custom_light_buffers()
                    rkcu.apply_config(self.config)
                
                # Wait for user to observe
                time.sleep(2)
                
                # Ask user to record the result
                physical_key = input(f"Buffer index {buffer_index} -> Which physical key lit up? (Enter key name or 'none'): ").strip()
                if physical_key and physical_key.lower() != 'none':
                    print(f"Recorded: {buffer_index} -> {physical_key}")
                
        except KeyboardInterrupt:
            print("\nMapping test stopped.")
            # Clear all keys
            self.per_key_rgb.clear_all()
            self.config.CUSTOM_LIGHT_BUFFERS = []
            rkcu.apply_config(self.config)
        finally:
            rkcu.close_kb()
            
    def test_specific_buffer_index(self, buffer_index, color=(255, 0, 0)):
        """Test a specific buffer index."""
        from rkcu.utils import RKCU
        
        print(f"Testing buffer index {buffer_index}...")
        
        # Initialize RKCU
        try:
            rkcu = RKCU(0x258a, 0x00e0)  # RK100 VID/PID
        except Exception as e:
            print(f"Failed to connect to keyboard: {e}")
            return
        
        try:
            # Clear all keys
            self.per_key_rgb.clear_all()
            
            # Set the test key
            self.per_key_rgb.set_key_color(buffer_index, color[0], color[1], color[2])
            
            # Apply the configuration
            if self.per_key_rgb.has_custom_colors():
                self.config.CUSTOM_LIGHT_BUFFERS = self.per_key_rgb.get_custom_light_buffers()
                rkcu.apply_config(self.config)
                print(f"Buffer index {buffer_index} should now be lit in red.")
            else:
                print("No custom colors set.")
        finally:
            rkcu.close_kb()
    
    def clear_all_keys(self):
        """Clear all keys."""
        from rkcu.utils import RKCU
        
        # Initialize RKCU
        try:
            rkcu = RKCU(0x258a, 0x00e0)  # RK100 VID/PID
        except Exception as e:
            print(f"Failed to connect to keyboard: {e}")
            return
        
        try:
            self.per_key_rgb.clear_all()
            self.config.CUSTOM_LIGHT_BUFFERS = []
            rkcu.apply_config(self.config)
            print("All keys cleared.")
        finally:
            rkcu.close_kb()
        
    def generate_mapping_code(self, mapping_dict):
        """Generate Python code for the correct key mapping."""
        print("\nGenerated mapping code:")
        print("def _get_rk100_key_mapping(self):")
        print("    return {")
        
        for buffer_index, key_info in sorted(mapping_dict.items()):
            if isinstance(key_info, dict):
                key_name = key_info.get('name', 'Unknown')
                print(f"        {buffer_index}: {buffer_index},  # {key_name}")
            else:
                print(f"        {buffer_index}: {buffer_index},  # {key_info}")
                
        print("    }")


def interactive_mapping_session():
    """Interactive session to help determine key mappings."""
    print("RK100 Key Mapping Utility")
    print("=" * 40)
    print()
    print("This utility will help you determine the correct buffer indices for your RK100 keyboard.")
    print("Make sure your keyboard is connected and the RKCU software is working.")
    print()
    
    try:
        # Try to import and initialize the per-key RGB system
        import sys
        import os
        
        # Add the parent directory to sys.path so we can import from rkcu package
        parent_dir = os.path.dirname(os.path.dirname(__file__))
        sys.path.insert(0, parent_dir)
        
        from rkcu.per_key_rgb import PerKeyRGB
        from rkcu.config import Config, get_base_config
        from rkcu.utils import RKCU
        
        # Initialize
        config = get_base_config()
        per_key_rgb = PerKeyRGB()
        config.PER_KEY_RGB = per_key_rgb
        
        mapper = KeyMapper(per_key_rgb, config)
        
        print("Initialization successful!")
        print()
        print("Options:")
        print("1. Test key mapping (lights up keys one by one)")
        print("2. Test specific buffer index")
        print("3. Generate mapping from known indices")
        print()
        
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == '1':
            mapper.test_key_mapping()
        elif choice == '2':
            try:
                buffer_index = int(input("Enter buffer index to test (0-60): "))
                if 0 <= buffer_index <= 60:
                    mapper.test_specific_buffer_index(buffer_index)
                    input("Press Enter to clear...")
                    mapper.clear_all_keys()
                else:
                    print("Invalid buffer index. Must be between 0 and 60.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        elif choice == '3':
            print("Enter known mappings (format: buffer_index:key_name)")
            print("Example: 0:Esc or 15:Q")
            print("Enter 'done' when finished:")
            
            mapping = {}
            while True:
                entry = input("Mapping: ").strip()
                if entry.lower() == 'done':
                    break
                try:
                    if ':' in entry:
                        buffer_idx, key_name = entry.split(':', 1)
                        mapping[int(buffer_idx)] = key_name
                        print(f"Added: {buffer_idx} -> {key_name}")
                    else:
                        print("Invalid format. Use buffer_index:key_name")
                except ValueError:
                    print("Invalid buffer index. Must be a number.")
                    
            if mapping:
                mapper.generate_mapping_code(mapping)
        else:
            print("Invalid choice.")
            
    except ImportError as e:
        print(f"Error importing modules: {e}")
        print("Make sure you're running this from the correct directory.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    interactive_mapping_session()
