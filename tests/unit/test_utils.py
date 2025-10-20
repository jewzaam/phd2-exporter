# Generated-by: Cursor (Claude Sonnet 4.5)
"""Unit tests for utils module."""

from unittest.mock import MagicMock, patch

import pytest

from phd2_exporter.utils import (
    create_event_metrics,
    debug,
    make_labels,
    utility_inc,
    utility_set,
)


def test_debug_enabled(capsys):
    """Test debug output when enabled."""
    with patch("phd2_exporter.utils.get_state") as mock_get_state:
        mock_state = MagicMock()
        mock_state.debug = True
        mock_get_state.return_value = mock_state

        debug("test message")
        captured = capsys.readouterr()
        assert "test message" in captured.out


def test_debug_disabled(capsys):
    """Test no debug output when disabled."""
    with patch("phd2_exporter.utils.get_state") as mock_get_state:
        mock_state = MagicMock()
        mock_state.debug = False
        mock_get_state.return_value = mock_state

        debug("test message")
        captured = capsys.readouterr()
        assert "test message" not in captured.out


def test_utility_set_success():
    """Test successful utility_set."""
    with patch("phd2_exporter.utils.metrics_utility") as mock_metrics:
        utility_set("test_metric", 42, {"label": "value"})
        mock_metrics.set.assert_called_once_with("test_metric", 42, {"label": "value"})


def test_utility_set_error():
    """Test utility_set error handling."""
    with patch("phd2_exporter.utils.metrics_utility") as mock_metrics:
        mock_metrics.set.side_effect = Exception("test error")
        with pytest.raises(Exception):
            utility_set("test_metric", 42, {"label": "value"})


def test_utility_inc_success():
    """Test successful utility_inc."""
    with patch("phd2_exporter.utils.metrics_utility") as mock_metrics:
        utility_inc("test_metric", {"label": "value"})
        mock_metrics.inc.assert_called_once_with("test_metric", {"label": "value"})


def test_utility_inc_error():
    """Test utility_inc error handling."""
    with patch("phd2_exporter.utils.metrics_utility") as mock_metrics:
        mock_metrics.inc.side_effect = Exception("test error")
        with pytest.raises(Exception):
            utility_inc("test_metric", {"label": "value"})


def test_make_labels_all_present():
    """Test make_labels with all keys present."""
    data = {"key1": "value1", "key2": "value2", "key3": "value3"}
    labels = make_labels(data, ["key1", "key2"])
    assert labels == {"key1": "value1", "key2": "value2"}


def test_make_labels_missing_keys():
    """Test make_labels with missing keys."""
    data = {"key1": "value1"}
    labels = make_labels(data, ["key1", "key2"])
    assert labels == {"key1": "value1", "key2": 0}


def test_make_labels_empty():
    """Test make_labels with no keys."""
    data = {"key1": "value1"}
    labels = make_labels(data, [])
    assert labels == {}


def test_create_event_metrics():
    """Test create_event_metrics."""
    with patch("phd2_exporter.utils.metrics_utility") as mock_metrics:
        data = {"Event": "TestEvent", "metric1": 42, "metric2": 3.14}
        labels = {"label": "value"}
        create_event_metrics(data, labels, ["metric1", "metric2"])

        assert mock_metrics.set.call_count == 2
        mock_metrics.set.assert_any_call("phd2_TestEvent_metric1", 42, labels)
        mock_metrics.set.assert_any_call("phd2_TestEvent_metric2", 3.14, labels)


def test_create_event_metrics_boolean():
    """Test create_event_metrics with boolean values."""
    with patch("phd2_exporter.utils.metrics_utility") as mock_metrics:
        data = {"Event": "TestEvent", "bool_true": True, "bool_false": False}
        labels = {"label": "value"}
        create_event_metrics(data, labels, ["bool_true", "bool_false"])

        assert mock_metrics.set.call_count == 2
        mock_metrics.set.assert_any_call("phd2_TestEvent_bool_true", 1, labels)
        mock_metrics.set.assert_any_call("phd2_TestEvent_bool_false", 0, labels)


def test_create_event_metrics_missing_key():
    """Test create_event_metrics with missing key."""
    with patch("phd2_exporter.utils.metrics_utility") as mock_metrics:
        data = {"Event": "TestEvent", "metric1": 42}
        labels = {"label": "value"}
        create_event_metrics(data, labels, ["metric1", "missing_metric"])

        # Should only create metric for existing key
        assert mock_metrics.set.call_count == 1
        mock_metrics.set.assert_called_once_with("phd2_TestEvent_metric1", 42, labels)
