# AIMS Testing Documentation

This document describes the comprehensive test suite created for the AIMS Android Management System.

## Test Coverage

The test suite provides comprehensive coverage of both the Android management class and the Flask API endpoints with **30 individual test cases**.

### Unit Tests (15 tests)

Located in `TestAndroidClass`, these tests cover the core `Android` class functionality:

#### Device Management
- ✅ `test_refresh_devices_success` - Test successful device discovery
- ✅ `test_refresh_devices_exception` - Test error handling when ADB fails
- ✅ `test_get_device_details_success` - Test device information retrieval
- ✅ `test_get_device_details_offline_device` - Test handling of offline devices
- ✅ `test_get_device_details_no_devices` - Test when no devices are connected

#### Emulator Management
- ✅ `test_start_emulator_success` - Test successful emulator startup
- ✅ `test_start_emulator_no_command` - Test error when emulator command missing
- ✅ `test_kill_emulator_success` - Test graceful emulator shutdown
- ✅ `test_kill_emulator_fallback` - Test fallback kill method
- ✅ `test_create_emulator_success` - Test AVD creation
- ✅ `test_create_emulator_no_command` - Test error when avdmanager missing

#### App and Log Management
- ✅ `test_list_apps_success` - Test package listing on device
- ✅ `test_list_apps_exception` - Test error handling for app listing
- ✅ `test_get_device_log_success` - Test logcat retrieval
- ✅ `test_get_device_log_exception` - Test error handling for log retrieval

### Integration Tests (15 tests)

Located in `TestAndroidFlaskEndpoints`, these tests cover all Flask API endpoints:

#### `/androidlist` Endpoint
- ✅ `test_androidlist_endpoint_success` - Test successful device listing
- ✅ `test_androidlist_endpoint_no_devices` - Test response when no devices found
- ✅ `test_androidlist_endpoint_exception` - Test error handling

#### `/startandroidemu` Endpoint
- ✅ `test_startandroidemu_endpoint_success` - Test successful emulator start
- ✅ `test_startandroidemu_endpoint_missing_param` - Test missing AVD name parameter
- ✅ `test_startandroidemu_endpoint_invalid_json` - Test invalid JSON handling
- ✅ `test_startandroidemu_endpoint_wrong_content_type` - Test wrong content-type

#### `/killandroidemu` Endpoint
- ✅ `test_killandroidemu_endpoint_success` - Test successful emulator kill
- ✅ `test_killandroidemu_endpoint_missing_param` - Test missing serial parameter

#### `/getadblog` Endpoint
- ✅ `test_getadblog_endpoint_success` - Test successful log retrieval
- ✅ `test_getadblog_endpoint_missing_serial` - Test missing serial parameter

#### `/listandroidapps` Endpoint
- ✅ `test_listandroidapps_endpoint_success` - Test successful app listing
- ✅ `test_listandroidapps_endpoint_missing_serial` - Test missing serial parameter

#### `/createdroidemu` Endpoint
- ✅ `test_createdroidemu_endpoint_success` - Test successful emulator creation
- ✅ `test_createdroidemu_endpoint_missing_params` - Test missing parameters

## Running Tests

### Local Testing

```bash
# Run all tests
python -m unittest discover tests -v

# Run only Android tests
python -m unittest tests.test_android -v

# Run with custom test runner
python run_tests.py
```

### GitHub Actions

Tests are automatically run on:
- Push to `main` and `develop` branches
- Pull requests to `main` and `develop` branches
- Multiple Python versions (3.7, 3.8, 3.9)

The workflow includes:
- Dependency installation via pipenv
- Code linting with flake8
- Full test suite execution
- Server startup smoke test
- Coverage reporting (optional)

## Test Features

### Mocking Strategy
- **External Dependencies**: All ADB commands, subprocess calls, and device interactions are mocked
- **Isolation**: Each test runs independently with clean state
- **Realistic Data**: Mock responses match real Android device output formats

### Error Handling
- **Parameter Validation**: Tests verify proper handling of missing/invalid parameters
- **Content-Type Validation**: Tests ensure JSON content-type requirements
- **Exception Handling**: Tests verify graceful failure handling

### Response Format Validation
- **JSON Structure**: All API responses follow consistent format with `status`, `message`, and `data` fields
- **HTTP Status Codes**: Tests verify correct status codes (200, 400, 500)
- **Data Types**: Tests validate response data types and structures

## Files Created

- `tests/test_android.py` - Main test suite (30 test cases)
- `.github/workflows/test.yml` - GitHub Actions workflow
- `run_tests.py` - Local test runner script
- `Pipfile` - Updated with test dependencies

## Dependencies Added

### Development Dependencies
- `pytest` - Alternative test runner
- `pytest-cov` - Coverage reporting
- `coverage` - Coverage analysis
- `flake8` - Code linting

### Runtime Dependencies (for testing)
- `ipdb` - Interactive debugger (for server.py compatibility)

All tests pass successfully and provide comprehensive coverage of the Android Management System functionality.