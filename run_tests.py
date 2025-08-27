#!/usr/bin/env python3
"""
Test runner for AIMS project.

This script runs all tests for the AIMS Android Management System.
"""

import sys
import os
import unittest

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def run_tests():
    """Run all tests and return success/failure."""
    # Discover and run all tests
    loader = unittest.TestLoader()
    test_suite = loader.discover('tests', pattern='test_*.py')
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(test_suite)
    
    # Print summary
    tests_run = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    
    print("\n" + "="*60)
    print(f"Tests run: {tests_run}")
    print(f"Failures: {failures}")
    print(f"Errors: {errors}")
    
    if failures > 0 or errors > 0:
        print("RESULT: FAILED")
        return False
    else:
        print("RESULT: PASSED")
        return True

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)