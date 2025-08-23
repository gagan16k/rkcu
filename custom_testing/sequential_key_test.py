#!/usr/bin/env python3
"""
Sequential Key Test for Royal Kludge Keyboard RGB
Tests each key from 0 to 112 by lighting them up sequentially.
Each key lights up for 1 second with a 2-second interval between keys.
"""

import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from rkcu.config import get_base_config
from rkcu.utils import RKCU

def sequential_key_test():
    
    print("Starting Sequential Key Test...")
    print("Each key will light up in red for 1 second with 2-second intervals.")
    print("Press Ctrl+C to stop the test at any time.")
    
    try:
        rk = RKCU(0x258a, 0x00e0)
        print("Successfully connected to Royal Kludge keyboard!")
        
        for key_index in range(113):
            try:
                print(f"Testing key {key_index}...")
                
                config = get_base_config()
                
                config.ANIMATION_BRIGHTNESS = 5
                
                config.PER_KEY_RGB.clear_all()
                
                config.PER_KEY_RGB.set_key_color_hex(key_index, "ff0000")
                
                rk.apply_config(config)
                
                time.sleep(1)
                
                config.ANIMATION_BRIGHTNESS = 0
                config.PER_KEY_RGB.clear_all()
                rk.apply_config(config)
                    
            except Exception as e:
                print(f"Error testing key {key_index}: {e}")
                continue
        
        print("\nSequential key test completed!")
        print("All keys from 0 to 112 have been tested.")
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"Error during test: {e}")
    finally:
        try:
            config = get_base_config()
            config.ANIMATION_BRIGHTNESS = 0
            config.PER_KEY_RGB.clear_all()
            rk.apply_config(config)
            print("Cleared all custom colors.")
        except:
            pass

def test_specific_key_range(start_key, end_key):
    print(f"Testing keys from {start_key} to {end_key}...")
    
    try:
        rk = RKCU(0x258a, 0x00e0)
        print("Successfully connected to Royal Kludge keyboard!")
        
        for key_index in range(start_key, end_key + 1):
            try:
                print(f"Testing key {key_index}...")
                
                config = get_base_config()
                config.ANIMATION_BRIGHTNESS = 5
                config.PER_KEY_RGB.clear_all()
                config.PER_KEY_RGB.set_key_color_hex(key_index, "ff0000")
                rk.apply_config(config)
                
                time.sleep(1)
                
                config.ANIMATION_BRIGHTNESS = 0
                config.PER_KEY_RGB.clear_all()
                rk.apply_config(config)
                
                if key_index < end_key:
                    time.sleep(2)
                    
            except Exception as e:
                print(f"Error testing key {key_index}: {e}")
                continue
                
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"Error during test: {e}")
    finally:
        try:
            config = get_base_config()
            config.ANIMATION_BRIGHTNESS = 0
            config.PER_KEY_RGB.clear_all()
            rk.apply_config(config)
            print("Cleared all custom colors.")
        except:
            pass

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Sequential Key Test for RK RGB Keyboard")
    parser.add_argument("--start", type=int, default=0, help="Starting key index (default: 0)")
    parser.add_argument("--end", type=int, default=112, help="Ending key index (default: 112)")
    parser.add_argument("--full", action="store_true", help="Run full test from 0 to 112 (default)")
    
    args = parser.parse_args()
    
    if args.full or (args.start == 0 and args.end == 112):
        sequential_key_test()
    else:
        test_specific_key_range(args.start, args.end)
