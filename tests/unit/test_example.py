"""Example unit tests demonstrating code quality standards.

This module provides examples of how to write unit tests following
the project's code quality standards, including proper docstrings,
type annotations, and test structure.
"""

from typing import Any
import pytest
from unittest.mock import Mock, patch


class TestExampleFunction:
    """Test cases for example function demonstrating unit test structure."""

    @pytest.mark.unit
    def test_simple_function(self) -> None:
        """Test a simple function with basic assertions.
        
        This test demonstrates the basic structure of a unit test
        with proper docstring format and type annotations.
        """
        # Arrange
        input_value = 42
        expected_result = 84
        
        # Act
        result = input_value * 2
        
        # Assert
        assert result == expected_result

    @pytest.mark.unit
    def test_with_mock(self, mock_config: Mock) -> None:
        """Test using a mock object from conftest fixtures.
        
        Args:
            mock_config: Mock configuration object from conftest.py
        """
        # Arrange
        mock_config.api_key = "test-key"
        
        # Act
        api_key = mock_config.api_key
        
        # Assert
        assert api_key == "test-key"
        mock_config.api_key.assert_not_called()  # It's a property, not a method

    @pytest.mark.unit
    def test_with_sample_data(self, sample_data: dict[str, Any]) -> None:
        """Test using sample data fixture.
        
        Args:
            sample_data: Sample test data from conftest.py
        """
        # Act & Assert
        assert sample_data["id"] == "test-id-123"
        assert sample_data["name"] == "Test Item"
        assert sample_data["value"] == 42.0
        assert sample_data["active"] is True
        assert len(sample_data["tags"]) == 2

    @pytest.mark.unit
    @patch("builtins.len")
    def test_with_patch(self, mock_len: Mock) -> None:
        """Test using patch decorator for mocking built-in functions.
        
        Args:
            mock_len: Mocked len function
        """
        # Arrange
        mock_len.return_value = 5
        test_list = [1, 2, 3]
        
        # Act
        result = len(test_list)
        
        # Assert
        assert result == 5
        mock_len.assert_called_once_with(test_list)

    @pytest.mark.unit
    @pytest.mark.parametrize("input_val,expected", [
        (0, 0),
        (1, 2),
        (5, 10),
        (-3, -6),
    ])
    def test_parametrized(self, input_val: int, expected: int) -> None:
        """Test with parametrized inputs.
        
        Args:
            input_val: Input value to test
            expected: Expected result
        """
        # Act
        result = input_val * 2
        
        # Assert
        assert result == expected

    @pytest.mark.unit
    def test_exception_handling(self) -> None:
        """Test proper exception handling."""
        # Test that the right exception is raised
        with pytest.raises(ZeroDivisionError):
            _ = 1 / 0

    @pytest.mark.unit
    def test_floating_point_comparison(self) -> None:
        """Test floating point numbers with appropriate precision."""
        # Arrange
        result = 0.1 + 0.2
        expected = 0.3
        
        # Assert - use pytest.approx for floating point comparison
        assert result == pytest.approx(expected)


@pytest.mark.asyncio
class TestAsyncExample:
    """Test cases for async functions demonstrating async testing patterns."""

    @pytest.mark.unit
    async def test_async_function(self) -> None:
        """Test an async function with anyio support.
        
        This test demonstrates how to write async unit tests
        using pytest-asyncio and anyio.
        """
        # Arrange
        async def async_double(value: int) -> int:
            """Double a value asynchronously."""
            return value * 2
        
        # Act
        result = await async_double(21)
        
        # Assert
        assert result == 42

    @pytest.mark.unit
    async def test_with_async_mock(self, mock_async_client: Mock) -> None:
        """Test with async mock client.
        
        Args:
            mock_async_client: Async mock client from conftest.py
        """
        # Arrange
        mock_async_client.get_data.return_value = {"status": "success"}
        
        # Act
        result = mock_async_client.get_data()
        
        # Assert
        assert result == {"status": "success"}


class TestErrorCases:
    """Test cases for error handling and edge cases."""

    @pytest.mark.unit
    def test_type_error(self) -> None:
        """Test handling of type errors."""
        with pytest.raises(TypeError):
            # This should raise a TypeError
            "string" + 42  # type: ignore[operator]

    @pytest.mark.unit
    def test_value_error(self) -> None:
        """Test handling of value errors."""
        with pytest.raises(ValueError):
            # This should raise a ValueError
            int("not_a_number")

    @pytest.mark.unit
    def test_empty_list(self) -> None:
        """Test behavior with empty collections."""
        # Arrange
        empty_list: list[int] = []
        
        # Act & Assert
        assert len(empty_list) == 0
        assert not empty_list  # Empty list is falsy

    @pytest.mark.unit
    def test_none_values(self) -> None:
        """Test handling of None values."""
        # Arrange
        test_value = None
        
        # Act & Assert
        assert test_value is None
        assert not test_value  # None is falsy
