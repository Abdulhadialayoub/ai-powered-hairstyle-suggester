#!/usr/bin/env python
"""
Test runner script for backend tests.

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py -v           # Verbose output
    python run_tests.py --cov        # With coverage report
    python run_tests.py test_api.py  # Run specific test file
"""

import sys
import pytest

if __name__ == '__main__':
    # Default arguments
    args = [
        'tests/',           # Test directory
        '-v',               # Verbose
        '--tb=short',       # Short traceback format
        '--color=yes',      # Colored output
    ]
    
    # Add user arguments
    if len(sys.argv) > 1:
        args = sys.argv[1:]
    
    # Run pytest
    exit_code = pytest.main(args)
    sys.exit(exit_code)
