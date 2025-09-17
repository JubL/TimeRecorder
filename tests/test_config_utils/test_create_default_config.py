"""Tests for the config_utils module."""

import pathlib
from unittest.mock import Mock, patch

import pytest
import yaml

import src.config_utils as cu


@patch("pathlib.Path.exists")
@patch("pathlib.Path.open")
@patch("yaml.safe_dump")
@pytest.mark.fast
def test_create_default_config_new_file(mock_yaml_dump: Mock, mock_open: Mock, mock_exists: Mock) -> None:
    """Test creating default configuration file when it doesn't exist."""
    mock_exists.return_value = False
    mock_file = Mock()
    mock_open.return_value.__enter__.return_value = mock_file

    cu.create_default_config(pathlib.Path("test_config.yaml"))

    mock_open.assert_called_once()
    mock_yaml_dump.assert_called_once()


@patch("pathlib.Path.exists")
@pytest.mark.fast
def test_create_default_config_existing_file(mock_exists: Mock) -> None:
    """Test creating default configuration when file already exists."""
    mock_exists.return_value = True

    # Should not raise any exception
    cu.create_default_config(pathlib.Path("test_config.yaml"))


@patch("pathlib.Path.exists")
@patch("pathlib.Path.open")
@patch("yaml.safe_dump")
@pytest.mark.fast
def test_create_default_config_yaml_error(mock_yaml_dump: Mock, mock_open: Mock, mock_exists: Mock) -> None:
    """Test create_default_config raises YAMLError when yaml.safe_dump fails."""
    mock_exists.return_value = False
    mock_file = Mock()
    mock_open.return_value.__enter__.return_value = mock_file
    mock_yaml_dump.side_effect = yaml.YAMLError("YAML serialization failed")

    with pytest.raises(yaml.YAMLError, match="YAML serialization failed"):
        cu.create_default_config(pathlib.Path("test_config.yaml"))

    mock_open.assert_called_once()
    mock_yaml_dump.assert_called_once()
