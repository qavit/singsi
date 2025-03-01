import os
import sys
from pathlib import Path

# Add project root to Python path
root_dir = str(Path(__file__).parent.parent)
sys.path.insert(0, root_dir)

# Set test environment
os.environ['APP_ENV'] = 'test'

# Common fixtures can be added here

"""Pytest configuration and fixtures."""

import asyncio  # noqa: E402
from collections.abc import Generator  # noqa: E402

import pytest  # noqa: E402


@pytest.fixture(scope='session')
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
