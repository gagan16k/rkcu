"""
Per-key RGB functionality based on rangoli project implementation.
Allows setting individual RGB colors for each key on the keyboard.
"""
from typing import Dict, Tuple
from .enums import Animation

class PerKeyRGB:
    """Manages per-key RGB lighting configuration."""
    
    def __init__(self):
        self.custom_colors: Dict[int, Tuple[int, int, int]] = {}
        self.key_buffer_indices = self._get_rk100_key_mapping()
    
    def set_key_color(self, key_index: int, red: int, green: int, blue: int):
        """Set RGB color for a specific key."""
        if not (0 <= red <= 255 and 0 <= green <= 255 and 0 <= blue <= 255):
            raise ValueError("RGB values must be between 0 and 255")
        
        self.custom_colors[key_index] = (red, green, blue)
    
    def set_key_color_hex(self, key_index: int, hex_color: str):
        """Set RGB color for a specific key using hex color code."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            raise ValueError("Hex color must be 6 characters (e.g., 'ff0000' for red)")
        
        try:
            red = int(hex_color[0:2], 16)
            green = int(hex_color[2:4], 16)
            blue = int(hex_color[4:6], 16)
            self.set_key_color(key_index, red, green, blue)
        except ValueError:
            raise ValueError("Invalid hex color format")
    
    def clear_key(self, key_index: int):
        """Remove custom color for a specific key."""
        if key_index in self.custom_colors:
            del self.custom_colors[key_index]
    
    def clear_all(self):
        """Remove all custom colors."""
        self.custom_colors.clear()
    
    def has_custom_colors(self) -> bool:
        """Check if any custom colors are set."""
        return len(self.custom_colors) > 0
    
    def get_custom_light_buffers(self) -> list:
        """Generate the custom light mode buffers for the keyboard."""
        if not self.has_custom_colors():
            return []
        
        BUFFER_SIZE = 65
        CUSTOM_LIGHT_BUFFERS_SIZE = 7
        
        # Create full LED buffer array
        led_full_buffer = bytearray(CUSTOM_LIGHT_BUFFERS_SIZE * BUFFER_SIZE)
        
        # Fill with RGB values for each custom key
        for key_index, (red, green, blue) in self.custom_colors.items():
            if key_index in self.key_buffer_indices:
                buffer_index = self.key_buffer_indices[key_index]
                lbi = buffer_index * 3
                if lbi + 2 < len(led_full_buffer):
                    led_full_buffer[lbi] = red
                    led_full_buffer[lbi + 1] = green
                    led_full_buffer[lbi + 2] = blue
        
        # Create individual buffers
        buffers = []
        led_buffer_index = 0
        
        for i in range(CUSTOM_LIGHT_BUFFERS_SIZE):
            buffer = bytearray(BUFFER_SIZE)
            buffer[0] = 0x0a
            buffer[1] = CUSTOM_LIGHT_BUFFERS_SIZE
            buffer[2] = i + 1
            
            if i == 0:
                buffer[3] = 0x03
                buffer[4] = 0x7e
                buffer[5] = 0x01
                start_index = 6
            else:
                start_index = 3
            
            # Copy LED data
            for buffer_index in range(start_index, BUFFER_SIZE):
                if led_buffer_index < len(led_full_buffer):
                    buffer[buffer_index] = led_full_buffer[led_buffer_index]
                    led_buffer_index += 1
            
            buffers.append(buffer)
        
        return buffers
    
    def _get_rk100_key_mapping(self) -> Dict[int, int]:
        """
        Get the key buffer index mapping for RK100 keyboard.
        This maps logical key indices to their buffer positions in the RGB data array.
        Based on rangoli project's buffer index system.
        
        Note: These buffer indices represent positions in the RGB buffer array,
        where each position corresponds to a specific physical key on the RK100.
        The actual values may need adjustment based on your specific keyboard variant.
        """
        # Buffer indices based on typical RK100 layout
        # These are positions in the RGB data array, not USB keycodes
        return {
            # Row 1 (Function keys and numbers)
            0: 0,    # Esc
            1: 1,    # 1
            2: 2,    # 2  
            3: 3,    # 3
            4: 4,    # 4
            5: 5,    # 5
            6: 6,    # 6
            7: 7,    # 7
            8: 8,    # 8
            9: 9,    # 9
            10: 10,  # 0
            11: 11,  # -
            12: 12,  # =
            13: 13,  # Backspace
            
            # Row 2 (QWERTY)
            14: 14,  # Tab
            15: 15,  # Q
            16: 16,  # W
            17: 17,  # E
            18: 18,  # R
            19: 19,  # T
            20: 20,  # Y
            21: 21,  # U
            22: 22,  # I
            23: 23,  # O
            24: 24,  # P
            25: 25,  # [
            26: 26,  # ]
            27: 27,  # \
            
            # Row 3 (ASDF)
            28: 28,  # Caps Lock
            29: 29,  # A
            30: 30,  # S
            31: 31,  # D
            32: 32,  # F
            33: 33,  # G
            34: 34,  # H
            35: 35,  # J
            36: 36,  # K
            37: 37,  # L
            38: 38,  # ;
            39: 39,  # '
            40: 40,  # Enter
            
            # Row 4 (ZXCV)
            41: 41,  # Left Shift
            42: 42,  # Z
            43: 43,  # X
            44: 44,  # C
            45: 45,  # V
            46: 46,  # B
            47: 47,  # N
            48: 48,  # M
            49: 49,  # ,
            50: 50,  # .
            51: 51,  # /
            52: 52,  # Right Shift
            
            # Row 5 (modifiers and space)
            53: 53,  # Left Ctrl
            54: 54,  # Left Win
            55: 55,  # Left Alt
            56: 56,  # Space
            57: 57,  # Right Alt
            58: 58,  # Right Win
            59: 59,  # Menu
            60: 60,  # Right Ctrl
            
            # Function keys (F1-F12) - typical positions for RK100
            61: 61,  # F1
            62: 62,  # F2
            63: 63,  # F3
            64: 64,  # F4
            65: 65,  # F5
            66: 66,  # F6
            67: 67,  # F7
            68: 68,  # F8
            69: 69,  # F9
            70: 70,  # F10
            71: 71,  # F11
            72: 72,  # F12
            
            # Navigation cluster
            73: 73,  # Print Screen
            74: 74,  # Scroll Lock
            75: 75,  # Pause
            76: 76,  # Insert
            77: 77,  # Home
            78: 78,  # Page Up
            79: 79,  # Delete
            80: 80,  # End
            81: 81,  # Page Down
            
            # Arrow keys
            82: 82,  # Up Arrow
            83: 83,  # Left Arrow
            84: 84,  # Down Arrow
            85: 85,  # Right Arrow
            
            # Numpad
            86: 86,  # Num Lock
            87: 87,  # Numpad /
            88: 88,  # Numpad *
            89: 89,  # Numpad -
            90: 90,  # Numpad 7
            91: 91,  # Numpad 8
            92: 92,  # Numpad 9
            93: 93,  # Numpad +
            94: 94,  # Numpad 4
            95: 95,  # Numpad 5
            96: 96,  # Numpad 6
            97: 97,  # Numpad 1
            98: 98,  # Numpad 2
            99: 99,  # Numpad 3
            100: 100, # Numpad 0
            101: 101, # Numpad .
            102: 102, # Numpad Enter
            
            # Additional keys for complete RK100 layout
            103: 103, # Additional key 1
            104: 104, # Additional key 2
            105: 105, # Additional key 3
            106: 106, # Additional key 4
            107: 107, # Additional key 5
            108: 108, # Additional key 6
            109: 109, # Additional key 7
            110: 110, # Additional key 8
            111: 111, # Additional key 9
            112: 112, # Additional key 10
        }