import os
import sys
from pathlib import Path

# Add project root to Python path
root_dir = str(Path(__file__).parent.parent)
sys.path.insert(0, root_dir)

# Set test environment
os.environ['APP_ENV'] = 'test'

"""Pytest configuration and fixtures."""

# Common fixtures can be added here
# Currently using the built-in event_loop fixture provided by pytest-asyncio
