"""
Tests for Android Management System.

This module contains comprehensive tests for both the Android class
and the Flask endpoints that provide Android device management functionality.
"""

import unittest
import json
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aims.android.android import Android
from aims.android.adb import AndroidDevice, NoUniqueDeviceError, DeviceNotFoundError


class TestAndroidClass(unittest.TestCase):
    """Unit tests for the Android class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.android = Android()
        self.mock_device_serial = 'emulator-5554'
        self.mock_device_details = {
            'serial': self.mock_device_serial,
            'model': 'sdk_gphone64_arm64',
            'version': '11',
            'api_level': '30',
            'manufacturer': 'Google',
            'status': 'device'
        }
    
    @patch('aims.android.android.get_devices')
    def test_refresh_devices_success(self, mock_get_devices):
        """Test successful device refresh."""
        mock_devices = ['emulator-5554', 'emulator-5556']
        mock_get_devices.return_value = mock_devices
        
        result = self.android.refresh_devices()
        
        self.assertEqual(result, mock_devices)
        mock_get_devices.assert_called_once_with(adb_path='adb')
    
    @patch('aims.android.android.get_devices')
    def test_refresh_devices_exception(self, mock_get_devices):
        """Test device refresh with exception."""
        mock_get_devices.side_effect = Exception("ADB not found")
        
        result = self.android.refresh_devices()
        
        self.assertEqual(result, [])
    
    @patch('aims.android.android.AndroidDevice')
    @patch('aims.android.android.get_devices')
    def test_get_device_details_success(self, mock_get_devices, mock_android_device):
        """Test successful device details retrieval."""
        mock_get_devices.return_value = [self.mock_device_serial]
        
        mock_device = Mock()
        mock_device.get_prop.side_effect = lambda prop: {
            'ro.product.model': 'sdk_gphone64_arm64',
            'ro.build.version.release': '11',
            'ro.build.version.sdk': '30',
            'ro.product.manufacturer': 'Google'
        }.get(prop)
        mock_android_device.return_value = mock_device
        
        result = self.android.get_device_details()
        
        self.assertEqual(len(result), 1)
        device_info = result[0]
        self.assertEqual(device_info['serial'], self.mock_device_serial)
        self.assertEqual(device_info['model'], 'sdk_gphone64_arm64')
        self.assertEqual(device_info['version'], '11')
        self.assertEqual(device_info['api_level'], '30')
        self.assertEqual(device_info['manufacturer'], 'Google')
        self.assertEqual(device_info['status'], 'device')
    
    @patch('aims.android.android.AndroidDevice')
    @patch('aims.android.android.get_devices')
    def test_get_device_details_offline_device(self, mock_get_devices, mock_android_device):
        """Test device details for offline device."""
        mock_get_devices.return_value = [self.mock_device_serial]
        mock_android_device.side_effect = Exception("Device offline")
        
        result = self.android.get_device_details()
        
        self.assertEqual(len(result), 1)
        device_info = result[0]
        self.assertEqual(device_info['serial'], self.mock_device_serial)
        self.assertEqual(device_info['status'], 'offline')
        self.assertEqual(device_info['model'], 'Unknown')
    
    @patch('aims.android.android.get_devices')
    def test_get_device_details_no_devices(self, mock_get_devices):
        """Test device details when no devices connected."""
        mock_get_devices.return_value = []
        
        result = self.android.get_device_details()
        
        self.assertEqual(result, [])
    
    @patch('aims.android.android.subprocess.Popen')
    @patch('aims.android.android.subprocess.run')
    def test_start_emulator_success(self, mock_run, mock_popen):
        """Test successful emulator start."""
        # Mock 'which emulator' command
        mock_run.return_value = Mock(returncode=0)
        
        # Mock emulator process
        mock_process = Mock()
        mock_process.pid = 1234
        mock_popen.return_value = mock_process
        
        result = self.android.start_emulator('test_avd')
        
        self.assertTrue(result['success'])
        self.assertIn('test_avd', result['message'])
        self.assertEqual(result['pid'], 1234)
        mock_popen.assert_called_once()
    
    @patch('aims.android.android.subprocess.run')
    def test_start_emulator_no_command(self, mock_run):
        """Test emulator start when emulator command not found."""
        mock_run.return_value = Mock(returncode=1)
        
        result = self.android.start_emulator('test_avd')
        
        self.assertFalse(result['success'])
        self.assertIn('Emulator command not found', result['message'])
    
    @patch('aims.android.android.AndroidDevice')
    def test_kill_emulator_success(self, mock_android_device):
        """Test successful emulator kill."""
        mock_device = Mock()
        mock_device.shell.return_value = None
        mock_android_device.return_value = mock_device
        
        result = self.android.kill_emulator(self.mock_device_serial)
        
        self.assertTrue(result['success'])
        self.assertIn('shutdown initiated', result['message'])
        mock_device.shell.assert_called_once_with(['reboot', '-p'])
    
    @patch('aims.android.android.subprocess.run')
    @patch('aims.android.android.AndroidDevice')
    def test_kill_emulator_fallback(self, mock_android_device, mock_run):
        """Test emulator kill fallback method."""
        mock_android_device.side_effect = Exception("Device not responding")
        mock_run.return_value = Mock(returncode=0, stderr='')
        
        result = self.android.kill_emulator(self.mock_device_serial)
        
        self.assertTrue(result['success'])
        self.assertIn('killed', result['message'])
        mock_run.assert_called_once()
    
    @patch('aims.android.android.AndroidDevice')
    def test_list_apps_success(self, mock_android_device):
        """Test successful app listing."""
        mock_device = Mock()
        mock_output = 'package:com.android.systemui\npackage:com.google.android.gms\n'
        mock_device.shell.return_value = (mock_output, '')
        mock_android_device.return_value = mock_device
        
        result = self.android.list_apps(self.mock_device_serial)
        
        self.assertEqual(len(result), 2)
        self.assertIn('com.android.systemui', result)
        self.assertIn('com.google.android.gms', result)
        mock_device.shell.assert_called_once_with(['pm', 'list', 'packages'])
    
    @patch('aims.android.android.AndroidDevice')
    def test_list_apps_exception(self, mock_android_device):
        """Test app listing with exception."""
        mock_android_device.side_effect = Exception("Device not found")
        
        result = self.android.list_apps(self.mock_device_serial)
        
        self.assertEqual(result, [])
    
    @patch('aims.android.android.AndroidDevice')
    def test_get_device_log_success(self, mock_android_device):
        """Test successful log retrieval."""
        mock_device = Mock()
        mock_log = 'I/System: Test log line 1\nI/System: Test log line 2\n'
        mock_device.shell.return_value = (mock_log, '')
        mock_android_device.return_value = mock_device
        
        result = self.android.get_device_log(self.mock_device_serial, lines=50)
        
        self.assertEqual(len(result), 2)
        self.assertIn('Test log line 1', result[0])
        self.assertIn('Test log line 2', result[1])
        mock_device.shell.assert_called_once_with(['logcat', '-d', '-t', '50'])
    
    @patch('aims.android.android.AndroidDevice')
    def test_get_device_log_exception(self, mock_android_device):
        """Test log retrieval with exception."""
        mock_android_device.side_effect = Exception("Device offline")
        
        result = self.android.get_device_log(self.mock_device_serial)
        
        self.assertEqual(result, [])
    
    @patch('aims.android.android.subprocess.Popen')
    @patch('aims.android.android.subprocess.run')
    def test_create_emulator_success(self, mock_run, mock_popen):
        """Test successful emulator creation."""
        # Mock 'which avdmanager' command
        mock_run.return_value = Mock(returncode=0)
        
        # Mock avdmanager process
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = ('Success', '')
        mock_popen.return_value = mock_process
        
        result = self.android.create_emulator('test_avd', 'system-images;android-30;google_apis;x86_64')
        
        self.assertTrue(result['success'])
        self.assertIn('created successfully', result['message'])
        mock_popen.assert_called_once()
    
    @patch('aims.android.android.subprocess.run')
    def test_create_emulator_no_command(self, mock_run):
        """Test emulator creation when avdmanager not found."""
        mock_run.return_value = Mock(returncode=1)
        
        result = self.android.create_emulator('test_avd', 'system-images;android-30;google_apis;x86_64')
        
        self.assertFalse(result['success'])
        self.assertIn('avdmanager command not found', result['message'])


class TestAndroidFlaskEndpoints(unittest.TestCase):
    """Integration tests for Android Flask endpoints."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Import and configure Flask app
        from aims.server import app
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        self.mock_device_details = [{
            'serial': 'emulator-5554',
            'model': 'sdk_gphone64_arm64', 
            'version': '11',
            'api_level': '30',
            'manufacturer': 'Google',
            'status': 'device'
        }]
    
    @patch('aims.server.android_manager.get_device_details')
    def test_androidlist_endpoint_success(self, mock_get_device_details):
        """Test /androidlist endpoint success."""
        mock_get_device_details.return_value = self.mock_device_details
        
        response = self.client.get('/androidlist')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('Found 1 Android devices', data['message'])
        self.assertEqual(len(data['data']), 1)
        self.assertEqual(data['data'][0]['serial'], 'emulator-5554')
    
    @patch('aims.server.android_manager.get_device_details')
    def test_androidlist_endpoint_no_devices(self, mock_get_device_details):
        """Test /androidlist endpoint with no devices."""
        mock_get_device_details.return_value = []
        
        response = self.client.get('/androidlist')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('Found 0 Android devices', data['message'])
        self.assertEqual(len(data['data']), 0)
    
    @patch('aims.server.android_manager.get_device_details')
    def test_androidlist_endpoint_exception(self, mock_get_device_details):
        """Test /androidlist endpoint with exception."""
        mock_get_device_details.side_effect = Exception("ADB error")
        
        response = self.client.get('/androidlist')
        
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Failed to list devices: ADB error')
    
    @patch('aims.server.android_manager.start_emulator')
    def test_startandroidemu_endpoint_success(self, mock_start_emulator):
        """Test /startandroidemu endpoint success."""
        mock_start_emulator.return_value = {'success': True, 'message': 'Emulator test_avd starting', 'pid': 1234}
        
        response = self.client.post('/startandroidemu', 
                                  data=json.dumps({'avd_name': 'test_avd'}),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('starting', data['message'])
        self.assertEqual(data['data']['pid'], 1234)
    
    def test_startandroidemu_endpoint_missing_param(self):
        """Test /startandroidemu endpoint with missing parameter."""
        response = self.client.post('/startandroidemu',
                                  data=json.dumps({}),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Missing required field: avd_name')
    
    def test_startandroidemu_endpoint_invalid_json(self):
        """Test /startandroidemu endpoint with invalid JSON."""
        response = self.client.post('/startandroidemu',
                                  data='invalid json',
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        # Flask returns a generic error for invalid JSON parsing
        self.assertIn('error', data)
    
    def test_startandroidemu_endpoint_wrong_content_type(self):
        """Test /startandroidemu endpoint with wrong content type."""
        response = self.client.post('/startandroidemu',
                                  data='{"avd_name": "test"}')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Content-Type must be application/json')
    
    @patch('aims.server.android_manager.kill_emulator')
    def test_killandroidemu_endpoint_success(self, mock_kill_emulator):
        """Test /killandroidemu endpoint success."""
        mock_kill_emulator.return_value = {'success': True, 'message': 'Emulator emulator-5554 shutdown initiated'}
        
        response = self.client.post('/killandroidemu',
                                  data=json.dumps({'serial': 'emulator-5554'}),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('shutdown initiated', data['message'])
    
    def test_killandroidemu_endpoint_missing_param(self):
        """Test /killandroidemu endpoint with missing parameter."""
        response = self.client.post('/killandroidemu',
                                  data=json.dumps({}),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Missing required field: serial')
    
    @patch('aims.server.android_manager.get_device_log')
    def test_getadblog_endpoint_success(self, mock_get_device_log):
        """Test /getadblog endpoint success."""
        mock_log_lines = ['I/System: Test log line 1', 'I/System: Test log line 2']
        mock_get_device_log.return_value = mock_log_lines
        
        response = self.client.get('/getadblog?serial=emulator-5554&lines=100')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['data']['logs']), 2)
        self.assertIn('Test log line 1', data['data']['logs'][0])
    
    def test_getadblog_endpoint_missing_serial(self):
        """Test /getadblog endpoint with missing serial parameter."""
        response = self.client.get('/getadblog')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Missing required parameter: serial')
    
    @patch('aims.server.android_manager.list_apps')
    def test_listandroidapps_endpoint_success(self, mock_list_apps):
        """Test /listandroidapps endpoint success."""
        mock_apps = ['com.android.systemui', 'com.google.android.gms']
        mock_list_apps.return_value = mock_apps
        
        response = self.client.get('/listandroidapps?serial=emulator-5554')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['data']['apps']), 2)
        self.assertIn('com.android.systemui', data['data']['apps'])
    
    def test_listandroidapps_endpoint_missing_serial(self):
        """Test /listandroidapps endpoint with missing serial parameter."""
        response = self.client.get('/listandroidapps')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Missing required parameter: serial')
    
    @patch('aims.server.android_manager.create_emulator')
    def test_createdroidemu_endpoint_success(self, mock_create_emulator):
        """Test /createdroidemu endpoint success."""
        mock_create_emulator.return_value = {'success': True, 'message': 'Emulator test_avd created successfully'}
        
        response = self.client.post('/createdroidemu',
                                  data=json.dumps({
                                      'name': 'test_avd',
                                      'system_image': 'system-images;android-30;google_apis;x86_64'
                                  }),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('created successfully', data['message'])
    
    def test_createdroidemu_endpoint_missing_params(self):
        """Test /createdroidemu endpoint with missing parameters."""
        response = self.client.post('/createdroidemu',
                                  data=json.dumps({}),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Missing required fields: name, system_image')


if __name__ == '__main__':
    unittest.main()