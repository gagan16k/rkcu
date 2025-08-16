import hid
from .config import Config

# utility class for RK Color Utility
class RKCU:
    def __init__(self, vid, pid):
        self.device = self.find_kb_hid(vid, pid)
    
    def find_kb_hid(self, vid, pid):
        rk_devices = hid.enumerate(vid, pid)
        if not rk_devices:
            raise IOError("RK keyboard not found. Please check VID and PID.")

        # From the comprehensive test, we know interface 2 works for RK100
        # It has: Interface number: 1, Usage: 1, Usage page: 65280
        # Path contains: Col05 (Collection 5)
        
        # First, try to find the exact working interface (Col05)
        target_interface = None
        for device_info in rk_devices:
            path = device_info['path']
            if isinstance(path, bytes):
                path_str = path.decode('utf-8', errors='ignore')
            else:
                path_str = str(path)
            
            # Look for Col05 in the path (this was the working interface)
            if 'Col05' in path_str and device_info.get('usage_page', 0) == 65280:
                target_interface = device_info
                break
        
        # If Col05 not found, try any interface with usage_page 65280
        if not target_interface:
            for device_info in rk_devices:
                if device_info.get('usage_page', 0) == 65280:
                    target_interface = device_info
                    break
        
        if not target_interface:
            raise IOError("Could not find the configuration interface (usage_page=65280) for the keyboard.")
        
        try:
            path = target_interface['path']
            h = hid.device()
            h.open_path(path)
            return h
        except Exception as e:
            raise IOError(f"Could not open the keyboard configuration interface: {e}")
    
    def apply_config(self, config: Config):
        # We know that send_feature_report works for the RK100
        data_to_send = config.report()
        try:
            result = self.device.send_feature_report(bytes(data_to_send))
            if result != len(data_to_send):
                raise IOError(f"Failed to send complete config. Expected {len(data_to_send)} bytes, sent {result}")
        except Exception as e:
            raise IOError(f"Failed to send config to keyboard: {e}")
    
    def close_kb(self):
        self.device.close()