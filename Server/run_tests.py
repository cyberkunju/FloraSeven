"""
Test runner for the FloraSeven server.

This script discovers and runs all tests in the tests directory.
"""
import unittest
import os
import sys

def run_tests():
    """Discover and run all tests."""
    # Ensure tests directory exists
    if not os.path.exists('tests'):
        os.makedirs('tests')
        print("Created tests directory")
    
    # Create __init__.py in tests directory if it doesn't exist
    init_file = os.path.join('tests', '__init__.py')
    if not os.path.exists(init_file):
        with open(init_file, 'w') as f:
            f.write('"""Test package for FloraSeven server."""\n')
        print("Created tests/__init__.py")
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
