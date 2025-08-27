import logging
import subprocess
import json
from . import adb
from ..command_line.command_line import CommandLine as cmd


class Android:
    """Android device management class for AIMS framework."""
    
    def __init__(self, adb_path='adb'):
        """Initialize Android manager with adb path."""
        self.adb_path = adb_path
        self.logger = logging.getLogger(__name__)
    
    def refresh_devices(self):
        """Get list of connected Android devices using adb.get_devices()."""
        try:
            devices = adb.get_devices(self.adb_path)
            return devices
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to get devices: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error getting devices: {e}")
            return []
    
    def get_device_details(self, serial):
        """Get detailed device information (model, version, API level, status)."""
        try:
            device = adb.AndroidDevice(serial, adb_path=self.adb_path)
            details = {
                'serial': serial,
                'model': device.get_prop('ro.product.model') or 'Unknown',
                'version': device.get_prop('ro.build.version.release') or 'Unknown',
                'api_level': device.get_prop('ro.build.version.sdk') or 'Unknown',
                'status': 'device',  # If we can get props, device is connected
                'manufacturer': device.get_prop('ro.product.manufacturer') or 'Unknown'
            }
            return details
        except Exception as e:
            self.logger.error(f"Failed to get device details for {serial}: {e}")
            return {
                'serial': serial,
                'model': 'Unknown',
                'version': 'Unknown', 
                'api_level': 'Unknown',
                'status': 'offline',
                'manufacturer': 'Unknown'
            }
    
    def start_emulator(self, avd_name):
        """Start Android emulator by AVD name."""
        try:
            # Use emulator command to start AVD
            result = cmd.execute(f'emulator -avd {avd_name} &')
            if result.error and 'PANIC' in result.error:
                raise Exception(f"Emulator failed to start: {result.error}")
            return {"status": "started", "avd_name": avd_name}
        except Exception as e:
            self.logger.error(f"Failed to start emulator {avd_name}: {e}")
            raise
    
    def kill_emulator(self, serial):
        """Stop specific Android emulator by serial."""
        try:
            # Kill emulator using adb emu kill command
            device = adb.AndroidDevice(serial, adb_path=self.adb_path)
            result = device.shell(['reboot', '-p'])  # Power off
            return {"status": "killed", "serial": serial}
        except Exception as e:
            self.logger.error(f"Failed to kill emulator {serial}: {e}")
            # Alternative method using kill command
            try:
                result = cmd.execute(f'adb -s {serial} emu kill')
                return {"status": "killed", "serial": serial}
            except Exception as e2:
                self.logger.error(f"Alternative kill method also failed: {e2}")
                raise
    
    def list_apps(self, serial):
        """List installed packages on device."""
        try:
            device = adb.AndroidDevice(serial, adb_path=self.adb_path)
            result = device.shell(['pm', 'list', 'packages'])
            
            # Parse package list
            packages = []
            if result and result[0]:
                lines = result[0].strip().split('\n')
                for line in lines:
                    if line.startswith('package:'):
                        package_name = line.replace('package:', '').strip()
                        packages.append(package_name)
            
            return packages
        except Exception as e:
            self.logger.error(f"Failed to list apps for {serial}: {e}")
            return []
    
    def get_device_log(self, serial, lines=100):
        """Get logcat output from device."""
        try:
            device = adb.AndroidDevice(serial, adb_path=self.adb_path)
            # Get recent logcat entries
            result = device.shell(['logcat', '-d', '-t', str(lines)])
            
            if result and result[0]:
                return result[0]
            return ""
        except Exception as e:
            self.logger.error(f"Failed to get device log for {serial}: {e}")
            return f"Error getting log: {e}"
    
    def create_emulator(self, name, system_image, device_definition):
        """Create new Android emulator."""
        try:
            # Create AVD using avdmanager
            cmd_str = f'avdmanager create avd -n {name} -k "{system_image}" -d "{device_definition}"'
            result = cmd.execute(cmd_str)
            
            if result.error and ('Error' in result.error or 'PANIC' in result.error):
                raise Exception(f"Failed to create emulator: {result.error}")
            
            return {
                "status": "created", 
                "name": name,
                "system_image": system_image,
                "device_definition": device_definition
            }
        except Exception as e:
            self.logger.error(f"Failed to create emulator {name}: {e}")
            raise