# Generated-by: Cursor (Claude Sonnet 4.5)
"""Unit tests for RMS calculation."""

import math
from unittest.mock import patch

from phd2_exporter.rms import calculate_and_export_rms, collect_rms_data
from phd2_exporter.state import PHD2State


def test_collect_rms_data_insufficient_data():
    """Test RMS data collection with insufficient data."""
    state = PHD2State()
    state.phd_rms_samples = 5

    data = {
        "RADistanceRaw": 1.0,
        "DECDistanceRaw": 2.0,
        "RADistanceGuide": 3.0,
        "DECDistanceGuide": 4.0,
    }

    with patch("phd2_exporter.rms.get_state", return_value=state):
        result = collect_rms_data(data)
        assert result is False
        assert len(state.phd_rms_data["RADistanceRaw"]) == 1


def test_collect_rms_data_exact_samples():
    """Test RMS data collection with exact number of samples."""
    state = PHD2State()
    state.phd_rms_samples = 3

    data = {
        "RADistanceRaw": 1.0,
        "DECDistanceRaw": 2.0,
        "RADistanceGuide": 3.0,
        "DECDistanceGuide": 4.0,
    }

    with patch("phd2_exporter.rms.get_state", return_value=state):
        # Collect samples - need N+1 calls to get True (N to fill, +1 to trigger calculation)
        # Calls 1-3: build up to 3 samples
        for _ in range(3):
            result = collect_rms_data(data)
            assert result is False

        # Call 4: now we have enough samples to calculate
        result = collect_rms_data(data)
        assert result is True
        assert len(state.phd_rms_data["RADistanceRaw"]) == 3


def test_collect_rms_data_missing_key():
    """Test RMS data collection with missing key."""
    state = PHD2State()
    state.phd_rms_samples = 3

    data = {
        "RADistanceRaw": 1.0,
        "DECDistanceRaw": 2.0,
        # Missing RADistanceGuide and DECDistanceGuide
    }

    with patch("phd2_exporter.rms.get_state", return_value=state):
        result = collect_rms_data(data)
        assert result is False


def test_collect_rms_data_array_limiting():
    """Test that RMS data arrays are limited to correct size."""
    state = PHD2State()
    state.phd_rms_samples = 3

    data = {
        "RADistanceRaw": 1.0,
        "DECDistanceRaw": 2.0,
        "RADistanceGuide": 3.0,
        "DECDistanceGuide": 4.0,
    }

    with patch("phd2_exporter.rms.get_state", return_value=state):
        # Collect 5 samples (more than limit)
        for i in range(5):
            data["RADistanceRaw"] = float(i)
            collect_rms_data(data)

        # Should only keep last 3
        assert len(state.phd_rms_data["RADistanceRaw"]) == 3
        # Should have values 2, 3, 4 (oldest removed)
        assert state.phd_rms_data["RADistanceRaw"] == [2.0, 3.0, 4.0]


def test_calculate_and_export_rms():
    """Test RMS calculation and export."""
    state = PHD2State()
    state.phd_rms_samples = 3
    state.pixel_scale = 2.0
    state.phd_rms_data = {
        "RADistanceRaw": [1.0, 2.0, 3.0],
        "DECDistanceRaw": [2.0, 4.0, 6.0],
        "RADistanceGuide": [0.5, 1.0, 1.5],
        "DECDistanceGuide": [1.0, 2.0, 3.0],
    }

    with (
        patch("phd2_exporter.rms.get_state", return_value=state),
        patch("phd2_exporter.rms.utility_set") as mock_set,
    ):
        calculate_and_export_rms()

        # Should export metrics for all keys including totals
        # RADistanceRaw, DECDistanceRaw, RADistanceGuide, DECDistanceGuide, TotalDistanceRaw, TotalDistanceGuide
        # Each with px and arcsec = 12 calls
        assert mock_set.call_count == 12


def test_calculate_and_export_rms_no_pixel_scale():
    """Test RMS calculation without pixel scale."""
    state = PHD2State()
    state.phd_rms_samples = 3
    state.pixel_scale = 0.0
    state.phd_rms_data = {
        "RADistanceRaw": [1.0, 2.0, 3.0],
        "DECDistanceRaw": [2.0, 4.0, 6.0],
        "RADistanceGuide": [0.5, 1.0, 1.5],
        "DECDistanceGuide": [1.0, 2.0, 3.0],
    }

    with (
        patch("phd2_exporter.rms.get_state", return_value=state),
        patch("phd2_exporter.rms.utility_set") as mock_set,
    ):
        calculate_and_export_rms()

        # Should only export px metrics (6 calls)
        assert mock_set.call_count == 6


def test_calculate_rms_math():
    """Test RMS calculation math is correct."""
    state = PHD2State()
    state.phd_rms_samples = 3
    state.pixel_scale = 0.0
    state.phd_rms_data = {
        "RADistanceRaw": [3.0, 4.0, 5.0],
        "DECDistanceRaw": [0.0, 0.0, 0.0],
        "RADistanceGuide": [0.0, 0.0, 0.0],
        "DECDistanceGuide": [0.0, 0.0, 0.0],
    }

    with (
        patch("phd2_exporter.rms.get_state", return_value=state),
        patch("phd2_exporter.rms.utility_set") as mock_set,
    ):
        calculate_and_export_rms()

        # Find the call for RADistanceRaw
        for call in mock_set.call_args_list:
            if call[0][0] == "phd2_rms" and call[0][2]["source"] == "RADistanceRaw":
                # RMS of [3, 4, 5] = sqrt((9 + 16 + 25) / 3) = sqrt(50/3) ≈ 4.082
                expected = math.sqrt(50.0 / 3.0)
                assert abs(call[0][1] - expected) < 0.001


def test_calculate_rms_total_distance():
    """Test total distance calculation."""
    state = PHD2State()
    state.phd_rms_samples = 2
    state.pixel_scale = 0.0
    state.phd_rms_data = {
        "RADistanceRaw": [3.0, 5.0],
        "DECDistanceRaw": [4.0, 12.0],
        "RADistanceGuide": [0.0, 0.0],
        "DECDistanceGuide": [0.0, 0.0],
    }

    with (
        patch("phd2_exporter.rms.get_state", return_value=state),
        patch("phd2_exporter.rms.utility_set") as mock_set,
    ):
        calculate_and_export_rms()

        # Total should be hypotenuse: sqrt(3^2 + 4^2) = 5, sqrt(5^2 + 12^2) = 13
        # RMS of [5, 13] = sqrt((25 + 169) / 2) = sqrt(97)
        expected = math.sqrt(97.0)

        for call in mock_set.call_args_list:
            if call[0][0] == "phd2_rms" and call[0][2]["source"] == "TotalDistanceRaw":
                assert abs(call[0][1] - expected) < 0.001
