# Generated-by: Cursor (Claude Sonnet 4.5)
"""Unit tests for main module."""

from phd2_exporter.main import get_config


def test_get_config_defaults():
    """Test get_config with default values."""
    args = {}
    phd2host, phd2port, port, rms_samples = get_config(args)

    assert phd2host == "127.0.0.1"
    assert phd2port == 4400
    assert port == 9753
    assert rms_samples == 10


def test_get_config_custom_values():
    """Test get_config with custom values."""
    args = {
        "phd2host": "192.168.1.100",
        "phd2port": 5500,
        "port": 8080,
        "rms_samples": 20,
    }
    phd2host, phd2port, port, rms_samples = get_config(args)

    assert phd2host == "192.168.1.100"
    assert phd2port == 5500
    assert port == 8080
    assert rms_samples == 20


def test_get_config_partial_values():
    """Test get_config with partial values."""
    args = {
        "phd2host": "localhost",
        "port": 9000,
    }
    phd2host, phd2port, port, rms_samples = get_config(args)

    assert phd2host == "localhost"
    assert phd2port == 4400  # default
    assert port == 9000
    assert rms_samples == 10  # default


def test_get_config_none_values():
    """Test get_config with None values."""
    args = {
        "phd2host": None,
        "phd2port": None,
        "port": None,
        "rms_samples": None,
    }
    phd2host, phd2port, port, rms_samples = get_config(args)

    # Should use defaults for None values
    assert phd2host == "127.0.0.1"
    assert phd2port == 4400
    assert port == 9753
    assert rms_samples == 10
