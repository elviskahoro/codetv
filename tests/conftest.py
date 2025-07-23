"""Shared test configuration and fixtures for the CodeTV project.

This module provides common pytest fixtures and configuration that can be
used across all test modules in the project.
"""

from typing import Any, AsyncGenerator, Generator
import pytest
import anyio
from unittest.mock import Mock, MagicMock


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Configure anyio backend for async testing.
    
    Returns:
        The backend name to use for anyio testing.
    """
    return "asyncio"


@pytest.fixture
async def mock_async_client() -> AsyncGenerator[Mock, None]:
    """Provide a mock async client for testing.
    
    Yields:
        A mock client that can be used for async API calls.
    """
    mock_client = Mock()
    mock_client.aclose = Mock()
    yield mock_client
    await mock_client.aclose()


@pytest.fixture
def mock_config() -> Generator[MagicMock, None, None]:
    """Provide a mock configuration object.
    
    Yields:
        A mock configuration object with common settings.
    """
    config = MagicMock()
    config.api_key = "test-api-key"
    config.base_url = "https://api.test.com"
    config.timeout = 30
    config.max_retries = 3
    yield config


@pytest.fixture
def sample_data() -> Generator[dict[str, Any], None, None]:
    """Provide sample data for testing.
    
    Yields:
        A dictionary containing sample test data.
    """
    yield {
        "id": "test-id-123",
        "name": "Test Item",
        "value": 42.0,
        "active": True,
        "tags": ["test", "sample"],
        "metadata": {
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z",
        }
    }


@pytest.fixture(autouse=True)
def reset_singletons() -> Generator[None, None, None]:
    """Reset singleton instances between tests.
    
    This fixture automatically runs before each test to ensure
    clean state between test runs.
    
    Yields:
        None
    """
    # Add any singleton reset logic here
    yield
    # Cleanup after test
    pass


# Test markers configuration
pytest_plugins = []

# Custom pytest markers
def pytest_configure(config: Any) -> None:
    """Configure custom pytest markers.
    
    Args:
        config: The pytest configuration object.
    """
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )
