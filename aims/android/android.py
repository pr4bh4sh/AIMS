"""
Android management module for AIMS.

This module provides an Android class that manages Android devices and emulators
using the existing adb.py module functionality.
"""

import json
import logging
import subprocess
import os
from . import adb
from .adb import AndroidDevice, get_devices, get_device, NoUniqueDeviceError, DeviceNotFoundError


class Android:
    """Android device and emulator management class."""
    
    def __init__(self, adb_path='adb'):
        """Initialize Android manager with optional adb path."""
        self.adb_path = adb_path
        self.logger = logging.getLogger(__name__)
        
    def refresh_devices(self):
        """Get list of connected Android devices using existing adb.get_devices()."""
        try:
            return get_devices(adb_path=self.adb_path)
        except Exception as e:
            self.logger.error(f"Failed to refresh devices: {str(e)}")
            return []
    
    def get_device_details(self, serial=None):
        """Return detailed device information (model, version, API level, status)."""
        try:
            devices = self.refresh_devices()
            if not devices:
                return []
            
            device_details = []
            devices_to_check = [serial] if serial else devices
            
            for device_serial in devices_to_check:
                try:
                    device = AndroidDevice(device_serial, adb_path=self.adb_path)
                    
                    # Get device properties
                    model = device.get_prop('ro.product.model') or 'Unknown'
                    version = device.get_prop('ro.build.version.release') or 'Unknown'
                    api_level = device.get_prop('ro.build.version.sdk') or 'Unknown'
                    manufacturer = device.get_prop('ro.product.manufacturer') or 'Unknown'
                    
                    device_info = {
                        'serial': device_serial,
                        'model': model,
                        'version': version,
                        'api_level': api_level,
                        'manufacturer': manufacturer,
                        'status': 'device'  # If we can get props, it's online
                    }
                    device_details.append(device_info)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to get details for device {device_serial}: {str(e)}")
                    device_details.append({
                        'serial': device_serial,
                        'model': 'Unknown',
                        'version': 'Unknown',
                        'api_level': 'Unknown',
                        'manufacturer': 'Unknown',
                        'status': 'offline'
                    })
            
            return device_details
            
        except Exception as e:
            self.logger.error(f"Failed to get device details: {str(e)}")
            return []
    
    def start_emulator(self, avd_name):
        """Start Android emulator by AVD name."""
        try:
            # Check if emulator command exists
            result = subprocess.run(['which', 'emulator'], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception("Emulator command not found. Make sure Android SDK is properly installed.")
            
            # Start emulator in background
            cmd = ['emulator', '-avd', avd_name, '-no-snapshot-save', '-no-boot-anim']
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.logger.info(f"Started emulator with AVD: {avd_name}, PID: {process.pid}")
            return {'success': True, 'message': f'Emulator {avd_name} starting', 'pid': process.pid}
            
        except Exception as e:
            self.logger.error(f"Failed to start emulator {avd_name}: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    def kill_emulator(self, serial):
        """Stop specific Android emulator."""
        try:
            # First, try to gracefully shutdown via adb
            device = AndroidDevice(serial, adb_path=self.adb_path)
            device.shell(['reboot', '-p'])  # Power off
            
            self.logger.info(f"Sent shutdown command to emulator: {serial}")
            return {'success': True, 'message': f'Emulator {serial} shutdown initiated'}
            
        except Exception as e:
            try:
                # Fallback: kill emulator process
                result = subprocess.run(['adb', '-s', serial, 'emu', 'kill'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    self.logger.info(f"Killed emulator: {serial}")
                    return {'success': True, 'message': f'Emulator {serial} killed'}
                else:
                    raise Exception(f"Kill command failed: {result.stderr}")
                    
            except Exception as e2:
                self.logger.error(f"Failed to kill emulator {serial}: {str(e2)}")
                return {'success': False, 'message': str(e2)}
    
    def list_apps(self, serial):
        """List installed packages on device."""
        try:
            device = AndroidDevice(serial, adb_path=self.adb_path)
            
            # Get list of packages
            output, _ = device.shell(['pm', 'list', 'packages'])
            
            apps = []
            for line in output.strip().split('\n'):
                if line.startswith('package:'):
                    package_name = line.replace('package:', '')
                    apps.append(package_name)
            
            self.logger.info(f"Found {len(apps)} apps on device {serial}")
            return apps
            
        except Exception as e:
            self.logger.error(f"Failed to list apps for device {serial}: {str(e)}")
            return []
    
    def get_device_log(self, serial, lines=100):
        """Get logcat output from device."""
        try:
            device = AndroidDevice(serial, adb_path=self.adb_path)
            
            # Get logcat with specified number of lines
            output, _ = device.shell(['logcat', '-d', '-t', str(lines)])
            
            # Split into lines and return as list for easier JSON serialization
            log_lines = output.strip().split('\n')
            
            self.logger.info(f"Retrieved {len(log_lines)} log lines from device {serial}")
            return log_lines
            
        except Exception as e:
            self.logger.error(f"Failed to get logs for device {serial}: {str(e)}")
            return []
    
    def create_emulator(self, name, system_image, device_definition='pixel'):
        """Create new Android emulator."""
        try:
            # Check if avdmanager exists
            result = subprocess.run(['which', 'avdmanager'], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception("avdmanager command not found. Make sure Android SDK command line tools are installed.")
            
            # Create AVD
            cmd = [
                'avdmanager', 'create', 'avd',
                '-n', name,
                '-k', system_image,
                '-d', device_definition,
                '--force'  # Overwrite if exists
            ]
            
            # Run with echo "no" to avoid license prompts
            process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate(input="no\n")
            
            if process.returncode == 0:
                self.logger.info(f"Created emulator: {name} with system image: {system_image}")
                return {'success': True, 'message': f'Emulator {name} created successfully'}
            else:
                raise Exception(f"avdmanager failed: {stderr}")
                
        except Exception as e:
            self.logger.error(f"Failed to create emulator {name}: {str(e)}")
            return {'success': False, 'message': str(e)}
